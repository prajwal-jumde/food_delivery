from typing import Optional
from urllib import response
from fastapi import APIRouter,Depends,status,Request
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from database.models import Restaurant, User,Order,Fooditem
from database.schemas import OrderModel,OrderStatusModel,RestaurantModel, RestaurantSearchModel,FoodItemModel
from database.database import Session , engine
from fastapi.encoders import jsonable_encoder

fooditem_router=APIRouter(
    prefix="/fooditem",
    tags=['fooditem']
)

session=Session(bind=engine)

@fooditem_router.post('',status_code=status.HTTP_201_CREATED)
async def add_fooditem(fooditem:FoodItemModel,Authorize:AuthJWT=Depends()):
    """
        ## add a fooditem
        This requires the following
        - "name":"dish1",
        - "restaurant":1,
        - "price":20.12,
        - "discount":4.23
        - "is_out_of_stock:False
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
        print('admin --- ',user.is_admin,user.is_staff)
        if not (user.is_admin) and not (user.is_staff) :
            return HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not Authorized to view this page."
            )            
        new_fooditem=Fooditem(
            name=fooditem.name,
            restaurant_name=fooditem.restaurant,
            price=fooditem.price,
            discount=fooditem.discount,
            is_out_of_stock=fooditem.is_out_of_stock
        )

        session.add(new_fooditem)
        session.commit()

        response={
            "status":status.HTTP_201_CREATED,
            "data":{
                "name":new_fooditem.name,
                "restaurant":new_fooditem.restaurant_name,
                "id":new_fooditem.id,
                "price":new_fooditem.price,
                "is_out_of_stock":new_fooditem.is_out_of_stock
            }
        }

        return jsonable_encoder(response)

    except Exception as error:
        print("Error in /fooditem : ",error)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something Went Wrong."
            )


@fooditem_router.get('')
@fooditem_router.get('{id}')
async def list_all_fooditem(request:Request,Authorize:AuthJWT=Depends(),id:int=0 ):
    """
        ## List all fooditem
        This lists all fooditem in a restaurant. It can be accessed by any user
    """
    try:
        print(len(request.query_params))
        print(dict(request.query_params))
        try:
            Authorize.jwt_required()
        except Exception as e:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token"
            )

        fooditem=session.query(Fooditem)
        if request.query_params and 'search_text' in  dict(request.query_params) and dict(request.query_params)['search_text']:
            search_text = "%{}%".format(dict(request.query_params)['search_text'])
            print(search_text)
            fooditem = fooditem.filter(Fooditem.name.like(search_text))
        if id:
            fooditem = fooditem.filter(Fooditem.id==id)          
        fooditem = fooditem.all()

        response ={
            "status":status.HTTP_200_OK,
            "data":jsonable_encoder(fooditem)
        }
        return response
       
    except Exception as error:
        print("Error in /fooditem : ",error)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something Went Wrong."
            )


@fooditem_router.put('/update/{id}/')
async def update_restaurant(id:int,request:FoodItemModel,Authorize:AuthJWT=Depends()):
    """
        ## Updating an fooditem
        This udates an fooditem and requires the following fields
        - name : str
    """
    try:

        try:
            Authorize.jwt_required() 
        except Exception as e:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token")

        current_user=Authorize.get_jwt_subject()
        user=session.query(User).filter(User.username==current_user).first()
        if not (user.is_admin) and not (user.is_staff) :
            return HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not Authorized to view this page."
            ) 
            
        fooditem_to_update=session.query(Fooditem).filter(Fooditem.id==id).first()

        fooditem_to_update.name=request.name
        fooditem_to_update.is_out_of_stock=request.is_out_of_stock
        fooditem_to_update.restaurant_name=request.restaurant_name
        fooditem_to_update.price=request.price
        fooditem_to_update.discount=request.discount
        session.commit()

        response={
                "status":status.HTTP_204_NO_CONTENT,
                "data":{
                    "id":fooditem_to_update.id,
                    "name":fooditem_to_update.name,
                    "restaurant_name":fooditem_to_update.restaurant_name,
                    "price":fooditem_to_update.price,
                    "discount":fooditem_to_update.discount
                    }
                }

        return jsonable_encoder(response)
    except Exception as error:
        print("Error in /fooditem/update/ : ",error)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something Went Wrong."
            )

    

@fooditem_router.delete('/delete/{id}/')
async def delete_a_fooditem(id:int,Authorize:AuthJWT=Depends()):
    """
        ## Delete an Fooditem
        This deletes an order by its ID
    """
    try:
        try:
            Authorize.jwt_required()
        except Exception as e:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token")

        current_user=Authorize.get_jwt_subject()
        user=session.query(User).filter(User.username==current_user).first()
        if not (user.is_admin) and not (user.is_staff) :
            return HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not Authorized to view this page."
            ) 

        fooditem_to_update=session.query(Fooditem).filter(Fooditem.id==id).first()
        fooditem_to_update.is_deleted=True
        session.commit()

        response={
                "status":status.HTTP_204_NO_CONTENT,
                "data":{
                    "id":fooditem_to_update.id,
                    "name":fooditem_to_update.name
                    }
                }

        return response
    except Exception as error:
        print("Error in /fooditem/delete/id/ : ",error)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something Went Wrong."
            )