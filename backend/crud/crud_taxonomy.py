# crud/crud_taxonomy.py
from sqlalchemy.orm import Session
from database import models
from schemas import taxonomy as taxonomy_schemas

# --- GETTERS ---
def get_departments(db: Session):
    return db.query(models.Department).all()

def get_programs(db: Session, department_id: int = None):
    query = db.query(models.Program)
    if department_id:
        query = query.filter(models.Program.department_id == department_id)
    return query.all()

def get_subjects(db: Session):
    return db.query(models.Subject).all()

# --- SETTERS (For you to populate the database) ---
def create_department(db: Session, department: taxonomy_schemas.DepartmentCreate):
    db_dept = models.Department(name=department.name)
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    return db_dept

def create_program(db: Session, program: taxonomy_schemas.ProgramCreate):
    db_prog = models.Program(name=program.name, department_id=program.department_id)
    db.add(db_prog)
    db.commit()
    db.refresh(db_prog)
    return db_prog

def create_subject(db: Session, subject: taxonomy_schemas.SubjectCreate):
    db_subj = models.Subject(name=subject.name)
    db.add(db_subj)
    db.commit()
    db.refresh(db_subj)
    return db_subj

# --- THE JUNCTION: Linking a Subject to a Program ---
def link_subject_to_program(db: Session, program_id: int, subject_id: int):
    program = db.query(models.Program).filter(models.Program.id == program_id).first()
    subject = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    
    if program and subject and subject not in program.subjects:
        program.subjects.append(subject)
        db.commit()
    return program