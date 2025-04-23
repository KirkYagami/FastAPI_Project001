from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.params import Depends
from ..database import get_db
from ..import models, schemas
from typing import List
from product.routers.login import get_current_user


router = APIRouter(
    tags=['Products'],
    prefix='/product'
)


@router.get('/', response_model=List[schemas.DisplayProduct])
def products(db: Session = Depends(get_db), current_user:schemas.Seller=Depends(get_current_user)):
    products = db.query(models.Product).all()
    return products


# @router.get('/product/{id}', response_model=schemas.DisplayProduct)
# def product(id, db: Session = Depends(get_db)):
#     product = db.query(models.Product).filter(models.Product.id==id).first()
#     return product


@router.get('/{id}', response_model=schemas.DisplayProduct)
def product(id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )
    return product


@router.delete('/{id}')
def delete(id, db: Session = Depends(get_db)):
    db.query(models.Product).filter(models.Product.id==id).delete(synchronize_session=False)
    db.commit()
    return {f'Deleted: Product with id :- {id}'}


@router.put('/{id}', status_code=status.HTTP_201_CREATED)
def update(id, request: schemas.Product, db: Session = Depends(get_db) ):
    product = db.query(models.Product).filter(models.Product.id==id)
    if not product.first():
        return {"Not Found"}
    else:
        product.update(request.model_dump())
        db.commit()
        return {'Updated product !'}


@router.post('/',status_code=status.HTTP_201_CREATED, response_model=schemas.DisplayProduct)
def add(request: schemas.Product, db: Session = Depends(get_db)):
    new_product = models.Product(
        name=request.name, 
        description=request.description, 
        price=request.price,
        seller_id = 1
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product



