"""Authentication endpoints: register, login, me"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    get_password_hash, verify_password, create_access_token,
    get_current_active_user, settings
)
from app.models import Shop, User, UserRole
from app.schemas import (
    UserRegisterRequest, UserCreate, UserResponse, TokenResponse, UserUpdate
)

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: UserRegisterRequest, db: Session = Depends(get_db)):
    """Register a new shop owner with a new shop."""
    # Check if email already exists
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create the shop
    shop = Shop(name=data.shop_name)
    db.add(shop)
    db.flush()

    # Create the owner user
    user = User(
        shop_id=shop.id,
        name=data.name,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        role=UserRole.owner,
        phone=data.phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with email and password, returns JWT token."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="User account is inactive")

    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
def get_me(current_user=Depends(get_current_active_user)):
    """Returns the currently authenticated user's profile."""
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
def update_me(data: UserUpdate, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Update own profile (name, phone)."""
    if data.name:
        current_user.name = data.name
    if data.phone is not None:
        current_user.phone = data.phone
    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user)
