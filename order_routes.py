from urllib import response
from fastapi import APIRouter,Depends,status
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from models import Fooditem, Restaurant, User,Order, UserAddress
from schemas import OrderModel,OrderStatusModel
from database import Session , engine
from fastapi.encoders import jsonable_encoder
import geopy
import common as constants


order_router=APIRouter(
    prefix="/orders",
    tags=['orders']
)


session=Session(bind=engine)


@order_router.post('/',status_code=status.HTTP_201_CREATED)
async def place_an_order(order:OrderModel,Authorize:AuthJWT=Depends()):
    """
        ## Placing an Order
        This requires the following
        - quantity : integer
        - poriton_size: str
        - restaurant: str
        - fooditem: str
    
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
        address=session.query(UserAddress).filter(UserAddress.id==order.address_id).first()
        restaurant_obj = session.query(Restaurant).filter(Restaurant.name==order.restaurant).first()
        fooditem_obj = session.query(Fooditem.price,Fooditem.discount).filter(Fooditem.name==order.fooditem).first()

        if not address:
            return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User address is not proper."
            )           
        #  check if restautant is within 5km radius of the restaurant
        coords_1 = (address.lat, address.long)
        coords_2 = (restaurant_obj.lat, restaurant_obj.long)
        distance = geopy.distance.geodesic(coords_1, coords_2).km
        
        if distance >=5:
            delivery_charges = fooditem_obj.price + constants.NORMAL_DELIVERY
        else:
            delivery_charges = fooditem_obj.price + constants.DISTANT_DELIVERY

        
         
        # TODO calculating order cost
        order_total = fooditem_obj.price * order.quantity
        order_discount = fooditem_obj.discount * order.quantity

        # TODO taxes and delivery charges calculation
        total_payable = (order_total - order_discount)+delivery_charges + order.surge_charge

        new_order=Order(
            portion_size=order.portion_size.upper(),
            quantity=order.quantity
        )
        new_order.user=user
        new_order.restaurant_name=order.restaurant
        new_order.fooditem_name=order.fooditem
        new_order.order_total=order_total
        new_order.discount=order_discount
        new_order.total_payable=total_payable
        session.add(new_order)
        session.commit()

        response={
            "id":new_order.id,
            "restaurant":new_order.restaurant_name,
            "fooditem":new_order.fooditem_name,
            "portion_size":new_order.portion_size.code,
            "quantity":new_order.quantity,
            "order_status":new_order.order_status.code,
            "order_total":order_total,
            "discount":order_discount,
            "total_payable":total_payable,
            "surge_charge":order.surge_charge
        }

        return jsonable_encoder(response)

    except Exception as error:
        print("Error in /order : ",error)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something Went Wrong."
            )


@order_router.get('/')
async def list_all_orders(Authorize:AuthJWT=Depends()):
    """
        ## List all orders
        This lists all  orders made. It can be accessed by superusers  
    """
    try:
        try:
            Authorize.jwt_required()
        except Exception as e:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token"
            )
        current_user=Authorize.get_jwt_subject()
        user=session.query(User).filter(User.username==current_user).first()
        if user.is_staff or user.is_admin:
            orders=session.query(Order).all()
            response = {
                "status":status.HTTP_200_OK,
                "data":orders
            }
            return jsonable_encoder(response)
        else:
            return {
                    "status":status.HTTP_401_UNAUTHORIZED,
                    "message":"You are not a superuser"
                }
    except Exception as error:
        print("Error in /orders : ",error)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something Went Wrong."
            )


@order_router.get('/{id}')
async def get_order_by_id(id:int,Authorize:AuthJWT=Depends()):
    """
        ## Get an order by its ID
        This gets an order by its ID and is only accessed by a superuser    
    """
    try:
        try:
            Authorize.jwt_required()
        except Exception as e:
            return HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token"
            )

        user=Authorize.get_jwt_subject()
        current_user=session.query(User).filter(User.username==user).first()

        if current_user.is_staff or current_user.is_admin:
            order=session.query(Order).filter(Order.id==id).first()
            response = {
                "status":status.HTTP_200_OK,
                "data":order
             }
            return jsonable_encoder(response)
        else:
            return HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not alowed to carry out request"
                )

    except Exception as error:
        print("Error in /orders/id : ",error)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something Went Wrong."
            )


@order_router.get('/user/all')
@order_router.get('/user/{id}/')
async def get_specific_order(id:int=0,Authorize:AuthJWT=Depends()):
    """
        ## Get a specific order by the currently logged in user
        This returns an order by ID for the currently logged in user
    """
    try:
        try:
            Authorize.jwt_required()
        except Exception as e:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token"
            )

        subject=Authorize.get_jwt_subject()
        current_user=session.query(User).filter(User.username==subject).first()
        orders=current_user.orders
        if id:
            orders = [o for o in orders if o.id == id]
        if not orders:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                detail="No order with such id"
            )
        response = {
                "status":status.HTTP_200_OK,
                "data":orders
            }
        return jsonable_encoder(response)
        

    except Exception as error:
        print("Error in /user/order/id/ : ",error)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something Went Wrong."
            )

    
@order_router.put('/status/{id}/')
async def update_order_status(id:int,order:OrderStatusModel,Authorize:AuthJWT=Depends()):
    """
        ## Update an order's status
        This is for updating an order's status and requires ` order_status ` in str format
    """
    try:
        try:
            Authorize.jwt_required()

        except Exception as e:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token")

        username=Authorize.get_jwt_subject()
        current_user=session.query(User).filter(User.username==username).first()
        order_status = Order.ORDER_STATUSES
        order_status = {k:v for k, v in order_status}
        print('order_status',order_status['IN-TRANSIT'])
        new_status=''
        if 'pen' in order.order_status.lower():
            new_status = 'PENDING'
        elif 'tran' in order.order_status.lower():
            new_status = 'IN-TRANSIT'
        elif 'deli' in order.order_status.lower():
            new_status = 'DELIVERED'                       
        if current_user.is_staff or current_user.is_admin:
            order_to_update=session.query(Order).filter(Order.id==id).first()
            order_to_update.order_status=new_status
            session.commit()
            response={  
                    "status":status.HTTP_204_NO_CONTENT,
                    "data":{
                        "id":order_to_update.id,
                        "quantity":order_to_update.quantity,
                        "portion_size":order_to_update.portion_size,
                        "order_status":order_to_update.order_status
                    }
                }
        else:
            print('inside else')
            response ={
                    "status":status.HTTP_401_UNAUTHORIZED,
                    "message":"You are not a superuser"
                }
        return jsonable_encoder(response)
    except Exception as error:
        print("Error in /orders/update/ : ",error)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something Went Wrong."
            )


@order_router.delete('/cancel/{id}')
async def delete_an_order(id:int,Authorize:AuthJWT=Depends()):
    """
        ## Delete an Order
        This deletes an order by its ID
    """
    try:
        try:
            Authorize.jwt_required()

        except Exception as e:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token")
        username=Authorize.get_jwt_subject()
        current_user=session.query(User).filter(User.username==username).first()

        order_to_delete=session.query(Order).filter(Order.id==id).first()
        if (current_user.id == order_to_delete.id) or current_user.is_admin or current_user.is_staff:
            order_to_delete.is_deleted = True
            message = "Successfully cancelled the order. "
            session.commit()
        else:
            message = "Unable to cancel order."
        response ={
                "status":status.HTTP_204_NO_CONTENT,
                "message":message
            }
        return jsonable_encoder(response)
    except Exception as error:
        print("Error in /orders/delete/id/ : ",error)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something Went Wrong."
            )