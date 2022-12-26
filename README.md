
## How to run the Project
- Install Postgreql
- Install Python
- Create PostGIS extension in Postgreql
- Git clone the project with ``` git clone https://github.com/jod35/Pizza-Delivery-API.git```
- Create your virtualenv with `Pipenv` or `virtualenv` and activate it.
- Install the requirements with ``` pip install -r requirements.txt ```
- Set Up your PostgreSQL database and set its URI in your ```database.py```
- Set Up your sqlalchemy.url in your ```alembic.ini```
```
engine=create_engine('postgresql://postgres:<username>:<password>@localhost/<db_name>',
    echo=True
)
```

- Create your database by running 
``` alembic revision --autogenerate -m "initial commit" ```
- Create new migration with (not mandateory)
```alembic revision -m "create/alter/delete changes"```
```alembic upgrade head ```
- Finally run the API
``` uvicorn main:app ``

type of users
-customers
-admin
-staff

https://www.jennifergd.com/post/7/
https://stackoverflow.com/questions/37827468/find-the-nearest-location-by-latitude-and-longitude-in-postgresql
https://stackoverflow.com/questions/37827468/find-the-nearest-location-by-latitude-and-longitude-in-postgresql
https://stackoverflow.com/questions/64097564/error-with-inserting-a-point-into-a-geometry-point-typed-column-in-postgress-w
