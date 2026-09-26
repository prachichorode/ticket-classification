import mysql.connector


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Prachi@123",
        database="ticket_system_v2"
    )