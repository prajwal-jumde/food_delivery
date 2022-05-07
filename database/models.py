from tokenize import Floatnumber
from database.database import Base
from sqlalchemy import Column,Integer,Boolean,Text,String,ForeignKey,DateTime,Numeric,Float
from sqlalchemy.orm import relationship
from sqlalchemy_utils.types import ChoiceType
from geoalchemy2 import Geography

import datetime

class User(Base):
    __tablename__='user'
    id=Column(Integer,primary_key=True)
    username=Column(String(255),unique=True)
    email=Column(String(80),unique=True)
    password=Column(Text,nullable=True)
    is_staff=Column(Boolean,default=False)
    is_admin = Column(Boolean,default=False)
    is_active=Column(Boolean,default=False)
    orders=relationship('Order',back_populates='user')
    restaurants=relationship('Restaurant',back_populates='user')
    created_at= Column(DateTime, default=datetime.datetime.utcnow)
    user_address=relationship('UserAddress',back_populates='user')
    def __repr__(self):
        return f"<User {self.username}"

class Restaurant(Base):
    __tablename__='restaurants'
    id=Column(Integer,primary_key=True)
    name=Column(String(255),unique=True)
    cuisine = Column(String(255),nullable=True)
    is_deleted=Column(Boolean,default=False)
    created_at= Column(DateTime, default=datetime.datetime.utcnow)
    lat =  Column(Numeric(precision=9, scale=6),nullable=True)
    long =  Column(Numeric(precision=9, scale=6),nullable=True)
    address = Column(String(255),unique=True)
    user_id=Column(Integer,ForeignKey('user.id'))
    orders=relationship('Order',back_populates='restaurants')
    fooditems=relationship('Fooditem',back_populates='restaurants')
    user=relationship('User',back_populates='restaurants')
    restaurant_location = Column(Geography(geometry_type='POINT', srid=4326))
    def __repr__(self):
        return f"<Restaurant {self.name}"

class Order(Base):

    ORDER_STATUSES=(
        ('PENDING','pending'),
        ('IN-TRANSIT','in-transit'),
        ('DELIVERED','delivered')

    )

    PORTION_SIZES=(
        ('SMALL','small'),
        ('MEDIUM','medium'),
        ('LARGE','large'),
        ('EXTRA-LARGE','extra-large')
    )


    __tablename__='orders'
    id=Column(Integer,primary_key=True)
    quantity=Column(Integer,nullable=False)
    order_status=Column(ChoiceType(choices=ORDER_STATUSES),default="PENDING")
    portion_size=Column(ChoiceType(choices=PORTION_SIZES),default="SMALL")
    user_id=Column(Integer,ForeignKey('user.id'))
    user=relationship('User',back_populates='orders')
    restaurants = relationship('Restaurant',back_populates='orders')
    restaurant_name=Column(String(255), ForeignKey('restaurants.name'),nullable=True)
    fooditem_name=Column(String(255), ForeignKey('fooditems.name'),nullable=True)
    fooditems = relationship('Fooditem',back_populates='orders')
    order_total = Column(Float)
    discount = Column(Float)
    total_payable = Column(Float)
    is_deleted=Column(Boolean,default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    address_id = Column(Integer)
    def __repr__(self):
        return f"<Order {self.id}>"



class Fooditem(Base):
    __tablename__='fooditems'
    id=Column(Integer,primary_key=True)
    name=Column(String(255),unique=True)
    is_deleted=Column(Boolean,default=False)
    is_out_of_stock = Column(Boolean,default=False)
    created_at= Column(DateTime, default=datetime.datetime.utcnow)
    restaurant_name=Column(String(255), ForeignKey('restaurants.name'),nullable=True)
    orders=relationship('Order',back_populates='fooditems')
    restaurants=relationship('Restaurant',back_populates='fooditems')
    price = Column(Float)
    discount = Column(Float)
    # user=relationship('User',back_populates='fooditems')

    def __repr__(self):
        return f"<Fooditem {self.name}"

class UserAddress(Base):
    __tablename__='user_address'
    id=Column(Integer,primary_key=True)
    address=Column(String(255),unique=True)
    pincode=Column(Integer)
    lat =  Column(Numeric(precision=9, scale=6),nullable=True)
    long =  Column(Numeric(precision=9, scale=6),nullable=True)
    user_name = Column(String(255), ForeignKey('user.username'))
    user = relationship('User',back_populates='user_address')
    is_deleted=Column(Boolean,default=False)
    is_active=Column(Boolean,default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user_location = Column(Geography(geometry_type='POINT', srid=4326))

    def __repr__(self):
        return f"<UserAddress {self.address}"