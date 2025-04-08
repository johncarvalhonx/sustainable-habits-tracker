import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, date
from pydantic import BaseModel
from typing import List, Optional

# Configurations
SECRET_KEY = "your_secret_key_here"  # Replace with a secure key in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database setup using SQLite for simplicity
SQLALCHEMY_DATABASE_URL = "sqlite:///./habits.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme definition
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI(title="Sustainable Habits Tracker API")

# ----------------------
# Database Models
# ----------------------

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    habits = relationship("Habit", back_populates="owner")
    entries = relationship("HabitEntry", back_populates="user")


class Habit(Base):
    __tablename__ = "habits"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="habits")
    entries = relationship("HabitEntry", back_populates="habit")


class HabitEntry(Base):
    __tablename__ = "habit_entries"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, default=date.today)
    habit_id = Column(Integer, ForeignKey("habits.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    habit = relationship("Habit", back_populates="entries")
    user = relationship("User", back_populates="entries")

# Create all tables
Base.metadata.create_all(bind=engine)

# ----------------------
# Pydantic Schemas
# ----------------------

class UserCreate(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class HabitCreate(BaseModel):
    name: str
    description: Optional[str] = None

class HabitOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True

class HabitEntryCreate(BaseModel):
    habit_id: int
    date: Optional[date] = None

class HabitEntryOut(BaseModel):
    id: int
    date: date
    habit_id: int

    class Config:
        orm_mode = True

class Summary(BaseModel):
    habit_id: int
    habit_name: str
    weekly_count: int
    monthly_count: int

# ----------------------
# Utility Functions
# ----------------------

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user(db, email=email)
    if user is None:
        raise credentials_exception
    return user

# ----------------------
# API Endpoints
# ----------------------

@app.post("/signup", response_model=UserOut)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    if get_user(db, email=user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(email=user.email, hashed_password=get_password_hash(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/habits", response_model=HabitOut)
def create_habit(habit: HabitCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_habit = Habit(name=habit.name, description=habit.description, owner_id=current_user.id)
    db.add(new_habit)
    db.commit()
    db.refresh(new_habit)
    return new_habit

@app.get("/habits", response_model=List[HabitOut])
def list_habits(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Habit).filter(Habit.owner_id == current_user.id).all()

@app.post("/track", response_model=HabitEntryOut)
def track_habit(entry: HabitEntryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entry_date = entry.date if entry.date else date.today()
    habit = db.query(Habit).filter(Habit.id == entry.habit_id, Habit.owner_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    new_entry = HabitEntry(habit_id=entry.habit_id, date=entry_date, user_id=current_user.id)
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry

@app.get("/summary", response_model=List[Summary])
def get_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    today = date.today()
    one_week_ago = today - timedelta(days=7)
    one_month_ago = today - timedelta(days=30)
    
    habits = db.query(Habit).filter(Habit.owner_id == current_user.id).all()
    summaries = []
    for habit in habits:
        weekly_count = db.query(func.count(HabitEntry.id)).filter(
            HabitEntry.habit_id == habit.id,
            HabitEntry.date >= one_week_ago,
            HabitEntry.user_id == current_user.id
        ).scalar()
        monthly_count = db.query(func.count(HabitEntry.id)).filter(
            HabitEntry.habit_id == habit.id,
            HabitEntry.date >= one_month_ago,
            HabitEntry.user_id == current_user.id
        ).scalar()
        summaries.append(Summary(
            habit_id=habit.id,
            habit_name=habit.name,
            weekly_count=weekly_count,
            monthly_count=monthly_count
        ))
    return summaries

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
