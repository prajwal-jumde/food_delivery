from re import search
import string
from pydantic import BaseModel
from typing import Optional

from models import Fooditem


class SignUpModel(BaseModel):
    id:Optional[int]
    username:str
    email:str
    password:str
    is_staff:Optional[bool]
    is_active:Optional[bool]
    is_admin:Optional[bool]    


    class Config:
        orm_mode=True
        schema_extra={
            'example':{
                "username":"johndoe",
                "email":"johndoe@gmail.com",
                "password":"password",
                "is_staff":False, 
                "is_admin":True,
                "is_active":True
            }
        }



class Settings(BaseModel):
    authjwt_secret_key:str='b4bb9013c1c03b29b9311ec0df07f3b0d8fd13edd02d5c45b2fa7b86341fa405'


class LoginModel(BaseModel):
    username:str
    password:str


class RestaurantModel(BaseModel):
    id:Optional[int]
    name:str
    cuisine:str
    address:str
    latitude:float
    longitude:float

class RestaurantSearchModel(BaseModel):
    id : Optional[int]
    search_text : Optional[str]
    address : Optional[str]
    cuisine : Optional[str]

class OrderModel(BaseModel):
    id:Optional[int]
    quantity:Optional[int] = 1
    order_status:Optional[str]="PENDING"
    portion_size:Optional[str]="SMALL"
    restaurant:str
    fooditem:str
    address_id:int
    surge_charge:Optional[int] = 0


    class Config:
        orm_mode=True
        schema_extra={
            "example":{
                "quantity":2,
                "portion_size":"LARGE",
                "restaurant": "veg restro",     
                "fooditem": "pizza",
                "address_id":1
            }
        }


class OrderStatusModel(BaseModel):
    order_status:Optional[str]="PENDING"

    class Config:
        orm_mode=True
        schema_extra={
            "example":{
                "order_status":"PENDING"
            }
        }

class FoodItemModel(BaseModel):
    id : Optional[int]
    name:str
    is_out_of_stock:bool
    restaurant_name:str
    price:float
    discount:float
    class Config:
        orm_mode=True
        schema_extra={
            "example":{
                "name":"dish1",
                "restaurant":1,
                "price":20.12,
                "discount":4.23,
                "is_out_of_stock":False
            }
        }


class RestaurantSearchModel(BaseModel):
    search_text : Optional[str]
    id : Optional[int]
    
class UserAddressModel(BaseModel):
    address:Optional[str]=""
    pincode:int
    lat:float
    long:float

    class Config:
        orm_mode=True
        schema_extra={
            "example":{
                "address":"india",
                "pincode":332242,
                "lat":12.442211,
                "long":13.553322                
            }
        }