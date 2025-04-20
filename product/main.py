from fastapi import FastAPI, HTTPException
from fastapi import Depends
from sqlalchemy.orm import Session
from .import schemas
from .import models
from .database import engine,get_db
from fastapi import status


from passlib.context import CryptContext # to create the context and hash mechanism

models.Base.metadata.create_all(engine)


pwd_context = CryptContext(schemes=["bcrypt"])


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

