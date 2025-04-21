from fastapi import APIRouter
from fastapi.params import Depends 
from ..import models, schemas
from ..database import get_db
from sqlalchemy.orm import Session
from passlib.context import CryptContext

router = APIRouter(
    tags=["Sellers"],
    prefix='/seller'
)


pwd_context = CryptContext(schemes=["bcrypt"])

@router.post('/', response_model=schemas.DisplaySeller)
def create_seller(request: schemas.Seller, db: Session = Depends(get_db)):
    hashed_pwd = pwd_context.hash(request.password)
    new_seller = models.Seller(
        username=request.username,
        email=request.email,
        password=hashed_pwd
    )
    db.add(new_seller)
    db.commit()
    db.refresh(new_seller)
    return new_seller


