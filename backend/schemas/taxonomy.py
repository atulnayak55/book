# schemas/taxonomy.py
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

# --- SUBJECTS ---
class SubjectBase(BaseModel):
    name: str

class SubjectCreate(SubjectBase):
    pass

class SubjectResponse(SubjectBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- PROGRAMS ---
class ProgramBase(BaseModel):
    name: str
    department_id: int

class ProgramCreate(ProgramBase):
    pass

class ProgramResponse(ProgramBase):
    id: int
    # We include subjects here so the frontend can easily show which exams belong to this course
    subjects: List[SubjectResponse] = [] 
    model_config = ConfigDict(from_attributes=True)

# --- DEPARTMENTS ---
class DepartmentBase(BaseModel):
    name: str

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentResponse(DepartmentBase):
    id: int
    # We include programs here so a user can click "DEI" and instantly see all DEI degrees
    programs: List[ProgramResponse] = []
    model_config = ConfigDict(from_attributes=True)