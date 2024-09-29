from mysql.connector import Connect, ProgrammingError
from mysql.connector.pooling import MySQLConnectionPool
from load_config import config

# Connect to MySQL database
def connect_to_mysql():
    conn = Connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
        database=config["database"]
    )

    return conn

def connection_pool_to_mysql():
    connection_pool = MySQLConnectionPool(
        pool_name="local_pool",
        pool_size=10,
        pool_reset_session=True,
        host=config["host"],
        user=config["user"],
        password=config["password"],
        database=config["database"]
    )

    return connection_pool

def query_users(username):
    cursor = public_db_connection.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user is None:
            code = 404
        else:
            code = 200
    except ProgrammingError as error:
        print("Failed to insert into MySQL table {}".format(error))
    finally:
        cursor.close()
        return code

public_db_connection = connect_to_mysql()
public_db_connection_pool = connection_pool_to_mysql()
