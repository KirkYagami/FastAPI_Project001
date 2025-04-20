from fastapi import FastAPI
from .import models
from .database import engine
from routers import product, seller

models.Base.metadata.create_all(engine)


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

app.include_router(product.router)
app.include_router(seller.router)



@app.get("/")
def root():
    return {"message": "FastAPI is working!"}

@app.get("/health")
def healthcheck():
    return {"status": "ok"}


