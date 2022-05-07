from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker


########################## for postgreSQL db ################################

host_server = 'localhost'
db_server_port ='5432'
database_name = 'food7'
db_username = 'postgres'
db_password = 'admin'
ssl_mode = 'prefer'

SQLALCHEMY_DB_URL = 'postgresql://{}:{}@{}:{}/{}?sslmode={}'.format(db_username, db_password, host_server, db_server_port, database_name, ssl_mode)
engine=create_engine(SQLALCHEMY_DB_URL,
    echo=True
)

Base=declarative_base()
Session=sessionmaker()