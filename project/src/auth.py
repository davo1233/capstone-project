from datetime import datetime, timedelta
from typing import Union
from fastapi import Depends, Header
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from src.database import Session, get_user_details, lookup_username_db, create_new_user_db
from src.data import UserIn

# Change and add scopes here
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login",
)

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "ChadGPT"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30




############################
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# For register
def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
#############################################

# Register - To add additional checks, email etc.
def register(newUser: UserIn, db: Session):
    existing_user = lookup_username_db(db, username=newUser.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    else:
        newUser.password = get_password_hash(newUser.password)
        create_new_user_db(db, newUser)
    # Create Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": newUser.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Login
def user_login(username: str, password: str, db: Session):
    user_id = lookup_username_db(db, username)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user_details(db, user_id)
    # Failed login
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Create Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



# Token Verification 
def check_token(token:str = Header(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Username is the unique identifier for now
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token - please re-login",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username



