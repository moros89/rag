import mysql.connector
from load_config import read_json_config

# Connect to MySQL database
def connect_to_mysql():
    config = read_json_config("./documents/config.json")

    # config = read_json_config("./documents/remote_config.json")

    conn = mysql.connector.connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
        database=config["database"]
    )
    return conn

public_db_connection = connect_to_mysql()