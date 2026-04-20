# main.py
from fastapi import FastAPI
from database.database import engine
from database import models

# Import both of your routers!
from routers import users, auth , taxonomy

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bobooks API",
    description="Hyper-local textbook marketplace for Unipd",
    version="0.1.0"
)

# Connect BOTH routers to the app
app.include_router(auth.router)
app.include_router(users.router) 
app.include_router(taxonomy.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Bobooks API!"}