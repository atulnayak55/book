from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import secrets
from sqlalchemy.orm import Session

from core.security import hash_opaque_token
from database import models


OTP_TTL_MINUTES = 10


@dataclass
class PendingSignupPayload:
    name: str
    email: str
    unipd_id: str | None
    hashed_password: str
    expires_at: datetime


def _generate_otp_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def _build_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=OTP_TTL_MINUTES)


def cleanup_expired_pending_signups(db: Session) -> None:
    db.query(models.PendingSignup).filter(
        models.PendingSignup.expires_at <= datetime.now(timezone.utc)
    ).delete(synchronize_session=False)
    db.commit()


def create_or_replace_pending_signup(
    db: Session,
    *,
    name: str,
    email: str,
    unipd_id: str | None,
    hashed_password: str,
) -> tuple[models.PendingSignup, str]:
    cleanup_expired_pending_signups(db)
    otp_code = _generate_otp_code()
    expires_at = _build_expiry()

    db_pending_signup = db.query(models.PendingSignup).filter(
        models.PendingSignup.email == email
    ).first()

    if db_pending_signup is None:
        db_pending_signup = models.PendingSignup(
            email=email,
            name=name,
            unipd_id=unipd_id,
            hashed_password=hashed_password,
            otp_hash=hash_opaque_token(otp_code),
            expires_at=expires_at,
        )
        db.add(db_pending_signup)
    else:
        db_pending_signup.name = name
        db_pending_signup.unipd_id = unipd_id
        db_pending_signup.hashed_password = hashed_password
        db_pending_signup.otp_hash = hash_opaque_token(otp_code)
        db_pending_signup.expires_at = expires_at

    db.commit()
    db.refresh(db_pending_signup)
    return db_pending_signup, otp_code


def verify_pending_signup(db: Session, *, email: str, otp_code: str) -> PendingSignupPayload | None:
    cleanup_expired_pending_signups(db)
    db_pending_signup = db.query(models.PendingSignup).filter(
        models.PendingSignup.email == email
    ).first()
    if db_pending_signup is None:
        return None
    if db_pending_signup.otp_hash != hash_opaque_token(otp_code):
        return None

    payload = PendingSignupPayload(
        name=db_pending_signup.name,
        email=db_pending_signup.email,
        unipd_id=db_pending_signup.unipd_id,
        hashed_password=db_pending_signup.hashed_password,
        expires_at=db_pending_signup.expires_at,
    )
    db.delete(db_pending_signup)
    db.commit()
    return payload


def resend_pending_signup_otp(db: Session, *, email: str) -> tuple[models.PendingSignup, str] | None:
    cleanup_expired_pending_signups(db)
    db_pending_signup = db.query(models.PendingSignup).filter(
        models.PendingSignup.email == email
    ).first()
    if db_pending_signup is None:
        return None

    otp_code = _generate_otp_code()
    db_pending_signup.otp_hash = hash_opaque_token(otp_code)
    db_pending_signup.expires_at = _build_expiry()
    db.commit()
    db.refresh(db_pending_signup)
    return db_pending_signup, otp_code
