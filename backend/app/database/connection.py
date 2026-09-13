import mysql.connector
 
 
def get_db():
    """New connection per call — never share one connection across requests."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="gujarat_police"
    )
 