from fastapi import APIRouter, Depends, status, HTTPException
from ..import schemas, models
from ..database import get_db
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

# created by: openssl rand -hex 32
SECRET_KEY = "cfc8e7affd31d3756ff676539b489628a064f410bd3f2f0374ab0eba8eed69c9"
ALGORITHM ="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def generate_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode,key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post('/login')
def login(request:OAuth2PasswordRequestForm=Depends() , db: Session = Depends(get_db)):
    seller = db.query(models.Seller).filter(models.Seller.username==request.username).first()
    if not seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="username is not in our db.")
    
    if not pwd_context.verify(request.password, seller.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid pwd")
    
    # generate JWT token
    access_token = generate_token(
        data = {"sub": seller.username}
    )
    return {'access_token':access_token, 'token_type': 'bearer' }

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
 
