import sqlalchemy

sql_config = dict(
    host='localhost', 
    database='mrt', 
    user='root', 
    password='00000000', 
    port='3306', 
    schema='mrt',
)
engine = sqlalchemy.create_engine(f"mysql+pymysql://{sql_config['user']}:{sql_config['password']}@{sql_config['host']}:{sql_config['port']}/{sql_config['schema']}")
