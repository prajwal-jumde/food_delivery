from email.headerregistry import Address
import imp
from click import exceptions
from fastapi import APIRouter,status,Depends
from fastapi.exceptions import HTTPException
from database.database import Session,engine
from database.schemas import SignUpModel,LoginModel,UserAddressModel
from database.models import User,UserAddress
from fastapi.exceptions import HTTPException
from werkzeug.security import generate_password_hash , check_password_hash
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder
import datetime
from sqlalchemy.orm import load_only

auth_router=APIRouter(
    prefix='/auth',
    tags=['auth']

)


session=Session(bind=engine)

@auth_router.get('/')
async def hello(Authorize:AuthJWT=Depends()):

    """
        ## Sample hello world route
    
    """
    try:
        Authorize.jwt_required()

    except Exception as e:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    return {"message":"Hello World"}


@auth_router.post('/signup',
    status_code=status.HTTP_201_CREATED
)
async def signup(user:SignUpModel):
    """
        ## Create a user
        This requires the following
        ```
                "username":str,
                "email":str,
                "password":str,
                "is_staff":bool,
                "is_active":bool,
                "is_admin":bool

        ```    
    """
    try:
        db_email=session.query(User).filter(User.email==user.email).first()
        if db_email is not None:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with the email already exists"
            )

        db_username=session.query(User).filter(User.username==user.username).first()
        if db_username is not None:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with the username already exists"
            )

        new_user=User(
            username=user.username,
            email=user.email,
            password=generate_password_hash(user.password),
            is_active=True,
        )
        print(new_user)
        if user.is_staff:
            new_user.is_staff=user.is_staff
        elif user.is_admin:
            new_user.is_admin=user.is_admin

        session.add(new_user)
        session.commit()

        return new_user
    except Exception as error:
        print("Error in /signup : ",error)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something Went Wrong."
            )


#login route

@auth_router.post('/login',status_code=200)
async def login(user:LoginModel,Authorize:AuthJWT=Depends()):
    """     
        ## Login a user
        This requires
            ```
                username:str
                password:str
            ```
        and returns a token pair `access` and `refresh`
    """
    try: 
        db_user=session.query(User).filter(User.username==user.username).first()

        if db_user and check_password_hash(db_user.password, user.password):
            expires = datetime.timedelta(hours=10)
            refresh_expires = datetime.timedelta(hours=24)
            access_token=Authorize.create_access_token(subject=db_user.username,expires_time=expires)
            refresh_token=Authorize.create_refresh_token(subject=db_user.username,expires_time=refresh_expires)

            response={
                "access":access_token,
                "refresh":refresh_token,
                "expires":expires,
                "refresh_expires":refresh_expires
            }

            return jsonable_encoder(response)

        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Username Or Password"
        )
    except Exception as error:
        print("Error in /login : ",error)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something Went Wrong."
            )


#refreshing tokens

@auth_router.get('/refresh')
async def refresh_token(Authorize:AuthJWT=Depends()):
    """
    ## Create a fresh token
    This creates a fresh token. It requires an refresh token.
    """
    try:
        try:
            Authorize.jwt_refresh_token_required()

        except Exception as e:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please provide a valid refresh token"
            ) 

        current_user=Authorize.get_jwt_subject()
        access_token=Authorize.create_access_token(subject=current_user)

        return jsonable_encoder({"access":access_token})

    except Exception as error:
        print("Error in /login : ",error)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something Went Wrong."
            )

@auth_router.post('/address')
async def address(user:UserAddressModel,Authorize:AuthJWT=Depends()):
    """
    ## Create a new address
    This creates a new address for a user. It requires -         
        -address:str
        -lat:float
        -long:float
        -pincode"int

    """
    try:
        try:
            Authorize.jwt_required()

        except Exception as e:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please provide a valid token"
            ) 

        current_user=Authorize.get_jwt_subject()
        print('current_user',current_user)
        # add new address
        
        new_user_address=UserAddress(
            user_name=current_user,
            address=user.address,
            pincode=user.pincode,
            lat=user.lat,
            long=user.long,
        )
        new_user_address.user_location = 'SRID=4326;POINT'+'('+str(float(user.long))+' '+ str(float(user.lat))+')'
        session.add(new_user_address)
        session.commit()

        # set is_active of older addresses of user to 0
        old_addresses = session.query(UserAddress).filter(UserAddress.user_name == current_user).filter(UserAddress.id!=new_user_address.id).update({UserAddress.is_active:False}, synchronize_session = False)
        print('old_addresses',old_addresses)
        session.commit()

        response={
            "status":status.HTTP_201_CREATED,
            "data":{
                "id":new_user_address.id,
                "user_name":current_user,
                "address":user.address,
                "pincode":user.pincode,
                "lat":user.lat,
                "long":user.long
            }
        }
        return jsonable_encoder(response)

    except Exception as error:
        print("Error in /address : ",error)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something Went Wrong."
            )

@auth_router.get('/address')
@auth_router.get('/address/{id}')
async def get_address(id:int=0,Authorize:AuthJWT=Depends()):
    """
    Fetches all the addresses of a user.
    """
    try:
        try:
            Authorize.jwt_required()

        except Exception as e:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please provide a valid token"
            ) 

        user=Authorize.get_jwt_subject()
        fields = ['id','is_active','created_at','lat','long','address','pincode']
        current_user_address=session.query(UserAddress).filter(UserAddress.user_name==user)
        if id:
            current_user_address = current_user_address.filter(UserAddress.id == id)
        current_user_address = current_user_address.options(load_only(*fields)).all()

        response = {
                "status":status.HTTP_200_OK,
                "data":current_user_address
             }
        return jsonable_encoder(response)

    except Exception as error:
        print("Error in /address : ",error)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something Went Wrong."
            )
