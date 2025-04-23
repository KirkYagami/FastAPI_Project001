from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt # pip install python-jose
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional

# Initialize FastAPI app
app = FastAPI(title="JWT Authentication Demo")

# Define user models
class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

# For demo purposes, we'll use a simple in-memory user database
# In a real application, you would use a proper database
fake_users_db = {
    "kirkyagami": {
        "username": "kirkyagami",
        "full_name": "Kirk Yagami",
        "email": "KirkYagami@example.com",
        "hashed_password": "$2b$12$kajUfA2SQ2./KkH7DW4oMeOpFpSPc8JA5gdPvbESg51GHMU33iqsq",  # "123456"
        "disabled": False,
    }
}

# Set up password hashing functionality
pwd_context = CryptContext(schemes=["bcrypt"])

# OAuth2 configuration with password flow
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configures OAuth2's "password flow: It expects clients to send a token in the Authorization header (e.g., Bearer <token>).

# JWT configuration
SECRET_KEY = "77b80a3c1934a2275754f16c024350a1e3c528ed002e7cb265e927a23b3cf18b"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiration time

# Token model
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Generate password hash
def get_password_hash(password):
    return pwd_context.hash(password)

# Get user from database
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

# Authenticate user
def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# Create access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Create JWT token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Get current user from token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Define credential exception
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
            
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
        
    # Get user from database
    user = get_user(fake_users_db, username=token_data.username)
    
    if user is None:
        raise credentials_exception
        
    return user

# Get active user (an additional check for account status)
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Token endpoint for user login
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Authenticate the user
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token with expiration time
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Return token
    return {"access_token": access_token, "token_type": "bearer"}

# Protected route - requires valid token
@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# Another protected route that returns additional user information
@app.get("/users/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]

# Public route - no authentication required
@app.get("/")
def read_root():
    return {"message": "Welcome to the JWT Authentication API"}

# Route to add a new user (simplified for demo)
@app.post("/users/", response_model=User)
async def create_user(username: str, password: str, email: str = None, full_name: str = None):
    if username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(password)
    fake_users_db[username] = {
        "username": username,
        "email": email,
        "full_name": full_name,
        "hashed_password": hashed_password,
        "disabled": False
    }
    
    return {
        "username": username,
        "email": email,
        "full_name": full_name,
        "disabled": False
    }

# Run the FastAPI app with: uvicorn main:app --reload
