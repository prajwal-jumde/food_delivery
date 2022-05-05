from database import engine,Base
from models import User,Order,Restaurant,Fooditem


Base.metadata.create_all(bind=engine)
