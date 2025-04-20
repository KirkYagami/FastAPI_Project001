


'''
creating a database model to create a table inside our db
'''
from sqlalchemy import Column, Integer, String, ForeignKey
from .database import Base
from sqlalchemy.orm import relationship

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    price = Column(Integer)
    seller_id = Column(Integer, ForeignKey('sellers.id'))
    seller = relationship("Seller", back_populates="products")



class Seller(Base):
    __tablename__ = 'sellers'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String)
    password = Column(String)
    products = relationship("Product", back_populates="seller")


"""

The relationship() function in SQLAlchemy defines how two ORM models are related at the Python level. It allows you to access related objects directly without manually querying the database.

This establishes a bidirectional relationship between Product and Seller. Specifically:
From a Product object, you can access its associated Seller via product.seller.
From a Seller object, you can access all associated Product objects via seller.products.

"""