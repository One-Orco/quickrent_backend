# main.py

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from . import models, schemas, utils, dependencies, database

app = FastAPI()

# Create the database.py tables
models.Base.metadata.create_all(bind=database.engine)

@app.post("/signup", response_model=schemas.Token)
def signup(user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = utils.hash_password(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token = utils.create_access_token(data={"sub": new_user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(dependencies.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = utils.create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

# Example protected route
@app.get("/protected")
def protected_route(user: models.User = Depends(dependencies.get_current_user)):
    return {"message": f"Hello {user.email}, your role is {user.role}"}

# Example admin-only route
@app.get("/admin")
def admin_route(user: models.User = Depends(dependencies.require_role(["admin"]))):
    return {"message": "Welcome Admin!"}
