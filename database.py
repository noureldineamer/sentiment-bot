import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

password = os.getenv("PASSWORD")
user = os.getenv("USER")
host = os.getenv("HOST")
database = os.getenv("DATABASE")

conn = mysql.connector.connect(
        host="localhost",
        user=user,
        password=password,
)

cursor = conn.cursor()
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
cursor.execute(f"USE {database}")
cursor.close()
conn.close()

conn = mysql.connector.connect(
        host="localhost",
        user=user,
        password=password,
        database=database)

cursor = conn.cursor()

cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
               id BIGINT UNIQUE PRIMARY KEY,
               author_name varchar(255),
               author_id BIGINT NOT NULL,
               message VARCHAR(4000),
               message_send_timestamp TIMESTAMP,
               created_at TIMESTAMP,
               updated_at TIMESTAMP)""")

'''
cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
               id INT AUTO_INCREMENT PRIMAY KEY,
               author_name message varchar(4000),
               author_id INT NOT NULL,
               date DATETIME,
               message varchar(4000)
               level ENUM,
               created_at TIMESTAMP,
               updated_at TIMESTAMP
               )
               """)
'''
cursor.close()
conn.close()
