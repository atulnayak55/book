import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from core.config import settings


ALLOWED_IMAGE_TYPES = {
    "image/gif": ".gif",
    "image/jpg": ".jpg",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
ALLOWED_IMAGE_EXTENSIONS = {".gif", ".jpeg", ".jpg", ".png", ".webp"}
HEADER_BYTES = 32
READ_CHUNK_SIZE = 1024 * 1024


def _detect_image_extension(header: bytes) -> str | None:
    if header.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if header.startswith((b"GIF87a", b"GIF89a")):
        return ".gif"
    if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        return ".webp"
    return None


def save_validated_image(*, file: UploadFile, upload_dir: Path, filename_prefix: str = "") -> str:
    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only GIF, JPEG, PNG, and WebP images are allowed",
        )

    original_extension = Path(file.filename or "").suffix.lower()
    if original_extension and original_extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported image file extension",
        )

    upload_dir.mkdir(parents=True, exist_ok=True)
    file_id = f"{filename_prefix}{uuid.uuid4().hex}"
    temp_path = upload_dir / f"{file_id}.upload"

    header = bytearray()
    total_bytes = 0

    try:
        with temp_path.open("wb") as buffer:
            while True:
                chunk = file.file.read(READ_CHUNK_SIZE)
                if not chunk:
                    break

                total_bytes += len(chunk)
                if total_bytes > settings.upload_max_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail=f"Images must be {settings.upload_max_bytes // (1024 * 1024)} MB or smaller",
                    )

                remaining_header_bytes = HEADER_BYTES - len(header)
                if remaining_header_bytes > 0:
                    header.extend(chunk[:remaining_header_bytes])

                buffer.write(chunk)

        if total_bytes == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

        detected_extension = _detect_image_extension(bytes(header))
        expected_extension = ALLOWED_IMAGE_TYPES[content_type]
        if detected_extension is None or detected_extension != expected_extension:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Uploaded file content does not match the declared image type",
            )

        final_path = upload_dir / f"{file_id}{detected_extension}"
        temp_path.replace(final_path)
        return final_path.name
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise
