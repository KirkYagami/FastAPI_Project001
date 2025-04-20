from fastapi import FastAPI, HTTPException
from fastapi import Depends
from sqlalchemy.orm import Session
from .import schemas
from .import models
from .database import engine, SessionLocal
from fastapi import status

from passlib.context import CryptContext # to create the context and hash mechanism


models.Base.metadata.create_all(engine)


pwd_context = CryptContext(schemes=["bcrypt"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from fastapi import FastAPI

app = FastAPI(
    title="Products API",
    description="Get details for all the products on our website",
    terms_of_service="https://www.google.com",
    contact={
        "Developer name": "Nikhil Sharma",
        "website": "https://www.google.com",
        "email": "Er.NikhilSharma7@gmail.com",
    },
    license_info={
        "name": "LICENCE",
        "url": "https://www.google.com",
    },
    # docs_url="/api-documentation",
    # redoc_url=None
)



@app.get("/")
def root():
    return {"message": "FastAPI is working!"}

@app.get("/health")
def healthcheck():
    return {"status": "ok"}

@app.get('/products', response_model=list[schemas.DisplayProduct], tags=['Products'])
def products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return products



# @app.get('/product/{id}', response_model=schemas.DisplayProduct)
# def product(id, db: Session = Depends(get_db)):
#     product = db.query(models.Product).filter(models.Product.id==id).first()
#     return product


@app.get('/product/{id}', response_model=schemas.DisplayProduct, tags=['Products'])
def product(id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )
    return product





@app.delete('/product/{id}', tags=['Products'])
def delete(id, db: Session = Depends(get_db)):
    db.query(models.Product).filter(models.Product.id==id).delete(synchronize_session=False)
    db.commit()
    return {f'Deleted: Product with id :- {id}'}


@app.put('/product/{id}', status_code=status.HTTP_201_CREATED, tags=['Products'])
def update(id, request: schemas.Product, db: Session = Depends(get_db) ):
    product = db.query(models.Product).filter(models.Product.id==id)
    if not product.first():
        return {"Not Found"}
    else:
        product.update(request.model_dump())
        db.commit()
        return {'Updated product !'}


@app.post('/product',status_code=status.HTTP_201_CREATED, response_model=schemas.DisplayProduct, tags=['Products'])
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


@app.post('/seller', response_model=schemas.DisplaySeller, tags=['Sellers'])
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

