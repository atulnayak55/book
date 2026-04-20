# routers/taxonomy.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from schemas import taxonomy as taxonomy_schemas
from crud import crud_taxonomy

router = APIRouter(prefix="/taxonomy", tags=["Taxonomy (Unipd Map)"])

# --- DEPARTMENTS ---
@router.get("/departments", response_model=List[taxonomy_schemas.DepartmentResponse])
def read_departments(db: Session = Depends(get_db)):
    return crud_taxonomy.get_departments(db)

@router.post("/departments", response_model=taxonomy_schemas.DepartmentResponse)
def create_department(department: taxonomy_schemas.DepartmentCreate, db: Session = Depends(get_db)):
    return crud_taxonomy.create_department(db=db, department=department)

# --- PROGRAMS ---
@router.post("/programs", response_model=taxonomy_schemas.ProgramResponse)
def create_program(program: taxonomy_schemas.ProgramCreate, db: Session = Depends(get_db)):
    return crud_taxonomy.create_program(db=db, program=program)

# --- SUBJECTS ---
@router.post("/subjects", response_model=taxonomy_schemas.SubjectResponse)
def create_subject(subject: taxonomy_schemas.SubjectCreate, db: Session = Depends(get_db)):
    return crud_taxonomy.create_subject(db=db, subject=subject)

# --- LINKING ---
@router.post("/programs/{program_id}/subjects/{subject_id}", response_model=taxonomy_schemas.ProgramResponse)
def link_program_subject(program_id: int, subject_id: int, db: Session = Depends(get_db)):
    """Link an existing subject (like Calculus 1) to an existing program (like Information Engineering)."""
    program = crud_taxonomy.link_subject_to_program(db, program_id=program_id, subject_id=subject_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program or Subject not found")
    return program