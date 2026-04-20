# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# The connection string matches the environment variables and ports in your docker-compose.yml
# Format: postgresql://<user>:<password>@<host>:<port>/<db_name>
SQLALCHEMY_DATABASE_URL = "postgresql://user:password123@localhost:5432/bobooks"

# The engine is the core interface to the database
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal will be used to create individual database sessions for our requests
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the class that all our models will inherit from
Base = declarative_base()

# This is a FastAPI dependency we will use to inject database sessions into our routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()