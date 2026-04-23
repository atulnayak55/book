# seed_db.py
import csv
import sys
from database.database import SessionLocal
from database import models

CSV_FILE_PATH = "/home/atul-nayak/book/unipd_courses_2025.csv"

def seed_database(csv_file_path: str = CSV_FILE_PATH):
    print("🌱 Starting database seeding process...")
    db = SessionLocal()
    
    # We use dictionaries to "cache" IDs in memory.
    # This prevents us from having to ask Postgres "Does DEI exist?" 5,000 times.
    departments_cache = {}
    programs_cache = {}
    subjects_cache = {}
    links_cache = set() # Stores tuples of (program_id, subject_id)

    # Pre-load any existing data just in case you run this script twice
    for d in db.query(models.Department).all():
        departments_cache[d.name] = d.id
    for p in db.query(models.Program).all():
        programs_cache[p.name] = p.id
    for s in db.query(models.Subject).all():
        subjects_cache[s.name] = s.id
    for row in db.execute(models.program_subjects.select()):
        links_cache.add((row.program_id, row.subject_id))

    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            row_count = 0
            for row in reader:
                # 1. Clean the incoming strings
                dept_name = row['department'].strip()
                prog_name = row['program'].strip()
                subj_name = row['subjects'].strip()
                
                # 2. Get or Create Department
                if dept_name not in departments_cache:
                    new_dept = models.Department(name=dept_name)
                    db.add(new_dept)
                    db.commit()
                    db.refresh(new_dept)
                    departments_cache[dept_name] = new_dept.id
                dept_id = departments_cache[dept_name]

                # 3. Get or Create Program
                if prog_name not in programs_cache:
                    new_prog = models.Program(name=prog_name, department_id=dept_id)
                    db.add(new_prog)
                    db.commit()
                    db.refresh(new_prog)
                    programs_cache[prog_name] = new_prog.id
                prog_id = programs_cache[prog_name]

                # 4. Get or Create Subject
                if subj_name not in subjects_cache:
                    new_subj = models.Subject(name=subj_name)
                    db.add(new_subj)
                    db.commit()
                    db.refresh(new_subj)
                    subjects_cache[subj_name] = new_subj.id
                subj_id = subjects_cache[subj_name]

                # 5. Link Program and Subject (The Junction Table)
                if (prog_id, subj_id) not in links_cache:
                    # We execute a raw insert into the Table object
                    db.execute(
                        models.program_subjects.insert().values(
                            program_id=prog_id, 
                            subject_id=subj_id
                        )
                    )
                    db.commit()
                    links_cache.add((prog_id, subj_id))
                    
                row_count += 1
                
                # Print progress every 1000 rows so you know it hasn't frozen
                if row_count % 1000 == 0:
                    print(f"Processed {row_count} rows...")

        print(f"✅ Seeding complete! Successfully mapped Unipd taxonomy.")
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find the CSV file at {csv_file_path}")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database(sys.argv[1] if len(sys.argv) > 1 else CSV_FILE_PATH)
