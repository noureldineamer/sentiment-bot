import os
from dotenv import load_dotenv
import mysql.connector

def create_database():
        load_dotenv()

        password = os.getenv("PASSWORD")
        user = os.getenv("USER")
        host = os.getenv("HOST")
        database = os.getenv("DATABASE")

        conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
        )

        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        cursor.execute(f"USE {database}")
        cursor.close()
        conn.close()

        conn = mysql.connector.connect(
                host=host,
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

        cursor.execute("""
                CREATE TABLE IF NOT EXISTS log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                author_name VARCHAR(255) DEFAULT 'System',
                author_id VARCHAR(32) DEFAULT 'System',
                message VARCHAR(4000),
                level ENUM('INFO', 'WARNING', 'ERROR', 'DEBUG') NOT NULL,
                date DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)""")

        cursor.close()
        conn.close()
