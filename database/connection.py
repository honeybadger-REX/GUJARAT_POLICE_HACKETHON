import os
from mysql.connector import pooling


db_pool = pooling.MySQLConnectionPool(
    pool_name="gujarat_police_pool",
    pool_size=10,
    pool_reset_session=True,
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "root"),
    database=os.getenv("DB_NAME", "gujarat_police")
)


def get_db():
    return db_pool.get_connection()

from pymongo import MongoClient

client = MongoClient(
    "localhost:27017",
    maxPoolSize=50,
    minPoolSize=5,
    maxIdleTimeMS=60000,
    serverSelectionTimeoutMS=5000
)
def get_mongo_db():
    mogodb =  client["CCTV_ai"]
    return mogodb