import os

files = {
    "backend/requirements.txt": """fastapi
uvicorn
sqlalchemy
alembic
pydantic
pydantic-settings
python-jose[cryptography]
passlib[bcrypt]
psycopg2-binary
email-validator
""",
    "backend/alembic.ini": """[alembic]
script_location = alembic
sqlalchemy.url = postgresql://postgres:postgres@localhost:5432/smartllm
""",
    "backend/app/__init__.py": "",
    "backend/app/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import setup_exception_handlers
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Production-ready FastAPI backend for SmartLLM Cloud",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_exception_handlers(app)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to SmartLLM Cloud API"}
""",
    "backend/app/core/config.py": """from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartLLM Cloud API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "super-secret-key-for-development-only-change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/smartllm"

    class Config:
        env_file = ".env"

settings = Settings()
""",
    "backend/app/core/security.py": """from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: str | any, expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt
""",
    "backend/app/core/exceptions.py": """from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.warning(f"AppException: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )
""",
    "backend/app/core/logging.py": """import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
""",
    "backend/app/db/session.py": """from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
""",
    "backend/app/models/base.py": """from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
""",
    "backend/app/models/user.py": """from sqlalchemy import Column, String, Boolean, DateTime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.models.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
""",
    "backend/app/schemas/user.py": """from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
""",
    "backend/app/schemas/token.py": """from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
""",
    "backend/app/api/dependencies.py": """from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.config import settings
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user
""",
    "backend/app/crud/user.py": """from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
""",
    "backend/app/api/v1/router.py": """from fastapi import APIRouter
from app.api.v1.endpoints import auth, health, users

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
""",
    "backend/app/api/v1/endpoints/health.py": """from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.dependencies import get_db

router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Check DB connectivity
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "degraded", "db": "disconnected", "details": str(e)}
""",
    "backend/app/api/v1/endpoints/auth.py": """from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.crud.user import get_user_by_email
from app.core.security import verify_password, create_access_token
from app.schemas.token import Token

router = APIRouter()

@router.post("/login", response_model=Token)
def login_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer"
    }
""",
    "backend/app/api/v1/endpoints/users.py": """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db, get_current_user
from app.schemas.user import UserResponse, UserCreate
from app.crud.user import get_user_by_email, create_user
from app.models.user import User
from app.core.exceptions import AppException

router = APIRouter()

@router.post("/", response_model=UserResponse)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    user = get_user_by_email(db, email=user_in.email)
    if user:
        raise AppException(message="Email already registered", status_code=400)
    return create_user(db, user_in)

@router.get("/me", response_model=UserResponse)
def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user
""",
    "backend/alembic/env.py": """from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.models.base import Base
from app.core.config import settings
from app.models.user import User # Import all models here

# add your model's MetaData object here
target_metadata = Base.metadata

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def run_migrations_offline() -> None:
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.DATABASE_URL
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
""",
    "backend/README.md": """# SmartLLM Cloud - Backend API

## Setup Instructions

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup**
   Ensure PostgreSQL is running and accessible at the connection string in `app/core/config.py` or `.env`.
   
   Generate initial migration:
   ```bash
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

4. **Run Development Server**
   ```bash
   uvicorn app.main:app --reload
   ```

## Swagger Documentation
Once running, visit:
`http://localhost:8000/docs`
"""
}

for path, content in files.items():
    full_path = os.path.join(r"c:\Users\admin\Desktop\aitoken2", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("FastAPI backend generated successfully in the 'backend' folder!")
