# database.py
from dotenv import load_dotenv
import os
from mysql.connector import pooling

load_dotenv()

dbconfig = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "expenses_db"),
    "charset": "utf8mb4",
    "use_unicode": True,
}

pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **dbconfig)

def get_db():
    """
    Returns a connection from the pool. Caller must close cursor & conn.
    """
    return pool.get_connection()