import sqlalchemy
from google.cloud.sql.connector import Connector
# from dotenv import load_dotenv
# load_dotenv()

# import os
# db_user = os.environ["DB_USER"]
# db_password = os.environ["DB_PASSWORD"]
# db_name = os.environ["DB_NAME"]
# project_id = os.environ["PROJECT_ID"]
# region_name = os.environ["REGION_NAME"]
# instance_name = os.environ["INSTANCE_NAME"]

db_user = "root"
db_password = ""
db_name = "mrt"
project_id = "utility-cyclist-394109"
region_name = "us-central1"
instance_name = "mysql-instance"

# initialize Connector object
connector = Connector()

# function to return the database connection
def getconn():
    conn = connector.connect(
        f"{project_id}:{region_name}:{instance_name}",
        "pymysql",
        user=db_user,
        password=db_password,
        db=db_name
    )
    return conn

# create connection pool
engine = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)

# sql_config = dict(
#     # host='localhost', 
#     host='mysql-db',
#     database='mrt', 
#     user='root', 
#     password='00000000', 
#     port='3306', 
#     schema='mrt',
# )
# engine = sqlalchemy.create_engine(f"mysql+pymysql://{sql_config['user']}:{sql_config['password']}@{sql_config['host']}:{sql_config['port']}/{sql_config['schema']}")

# cloud-sql-python-connector python-dotenv