from dataclasses import field
from fastapi import APIRouter,Depends,status,Request
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from models import Restaurant, User,Order
from schemas import OrderModel,OrderStatusModel,RestaurantModel, RestaurantSearchModel
from database import Session , engine
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func
from geoalchemy2 import Geometry,Geography
from sqlalchemy.orm import load_only

restaurants_router=APIRouter(
    prefix="/restaurant",
    tags=['restaurant']
)


session=Session(bind=engine)



@restaurants_router.post('',status_code=status.HTTP_201_CREATED)
async def add_restaurant(restaurant:RestaurantModel,Authorize:AuthJWT=Depends()):
    """
        ## add a restaurant
        This requires the following
        - quantity : integer
        - poriton_size: str
    
    """
    try:
        try:
            Authorize.jwt_required()
        except Exception as e:
            return HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token"
            )

        current_user=Authorize.get_jwt_subject()
        user=session.query(User).filter(User.username==current_user).first()

        if not user.is_admin:
            return HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not Authorized to view this page."
            )            
        new_restaurant=Restaurant(
            name=restaurant.name,
            cuisine=restaurant.cuisine,
            address=restaurant.address
        )
        if restaurant.latitude:
             new_restaurant.lat= restaurant.latitude
        if restaurant.longitude:
             new_restaurant.long= restaurant.longitude

        new_restaurant.user=user
        # adding geometry field
        new_restaurant.restaurant_location = 'SRID=4326;POINT'+'('+str(float(restaurant.longitude))+' '+ str(float(restaurant.latitude))+')'
        session.add(new_restaurant)
        session.commit()

        response={
            "status":status.HTTP_201_CREATED,
            "data":{
                "name":new_restaurant.name,
                "cuisine":new_restaurant.cuisine,
                "id":new_restaurant.id,
                "address":new_restaurant.address
                }
        }

        return jsonable_encoder(response)

    except Exception as error:
        print("Error in /order : ",error)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something Went Wrong."
            )


@restaurants_router.get('')
@restaurants_router.get('/{id}')
async def list_all_restaurant(request:Request,Authorize:AuthJWT=Depends(),id:int=0 ):
    """
        ## List all orders
        This lists all  orders made. It can be accessed by any  
    """
    try:
        try:
            Authorize.jwt_required()
        except Exception as e:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token"
            )
        # import pdb;pdb.set_trace()
        restaurants=session.query(Restaurant)
        current_user=Authorize.get_jwt_subject()
        user=session.query(User).filter(User.username==current_user).first()
        params={}
        if request.query_params:
            params = dict(request.query_params)
        if 'search_text' in  params and params['search_text']:
            restaurants = restaurants.filter(Restaurant.name.like("'%" + str(request.search_text) +"%'"))
        if 'address' in  params and params['address']:
            restaurants = restaurants.filter(Restaurant.address.like("'%" + str(request.address) +"%'"))
        if 'cuisine' in  params and params['cuisine']:
            restaurants = restaurants.filter(Restaurant.cuisine.like("'%" + str(request.cuisine) +"%'"))
        if id:
            restaurants = restaurants.filter(Restaurant.id==id)         
        
        # Storing the location of the restaurant
        if not(current_user.is_admin) and not (current_user.is_staff):
            user_lat = params['lat']
            user_long = params['long']
            point = 'POINT'+'('+str(float(user_long))+' '+ str(float(user_lat))+')'
            restaurants = restaurants.filter(func.ST_DWithin(Restaurant.restaurant_location, point, 3000))

        fields = ['id','name','cuisine','is_deleted','created_at','lat','long','address']
        restaurants = restaurants.options(load_only(*fields)).all()
        response={
                    "status":status.HTTP_200_OK,
                    "data":jsonable_encoder(restaurants)
                }
        return response
       
    except Exception as error:
        print("Error in /orders : ",error)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something Went Wrong."
            )


@restaurants_router.put('/update/{id}/')
async def update_restaurant(id:int,request:RestaurantModel,Authorize:AuthJWT=Depends()):
    """
        ## Updating an restaurants
        This udates an restaurants and requires the following fields
        - name : str
        - cuisine : str
        - address : str
        - latitude : float
        - longitude : float 
    """
    try:
        try:
            Authorize.jwt_required() 

        except Exception as e:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token")

        restaurant_to_update=session.query(Restaurant).filter(Restaurant.id==id).first()

        restaurant_to_update.name=request.name
        restaurant_to_update.cuisine=request.cuisine
        restaurant_to_update.address=request.address
        restaurant_to_update.latitude=request.latitude
        restaurant_to_update.longitude=request.longitude
        session.commit()

        response={
                    "status":status.HTTP_204_NO_CONTENT,
                    "data":{
                        "id":restaurant_to_update.id,
                        "name":restaurant_to_update.name,
                        "cuisine":restaurant_to_update.cuisine,
                        "address":restaurant_to_update.address,
                        "latitude":restaurant_to_update.latitude,
                        "longitude":restaurant_to_update.longitude
                    }
                }

        return jsonable_encoder(response)
    except Exception as error:
        print("Error in /restaurant/update/id/ : ",error)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something Went Wrong."
            )

    

@restaurants_router.delete('/delete/{id}/')
async def delete_an_restaurant(id:int,Authorize:AuthJWT=Depends()):
    """
        ## Delete an Restaurant
        This deletes an order by its ID
    """
    try:
        try:
            Authorize.jwt_required()

        except Exception as e:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token")
        restaurant_to_delete=session.query(Restaurant).filter(Restaurant.id==id).first()
        restaurant_to_delete.is_deleted=True
        session.commit()

        response={
                "status":status.HTTP_204_NO_CONTENT,
                "data":{
                    "id":restaurant_to_delete.id,
                    "name":restaurant_to_delete.name
                    }
                }

        return jsonable_encoder(response)
    except Exception as error:
        print("Error in /restaurant/delete/id/ : ",error)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something Went Wrong."
            )