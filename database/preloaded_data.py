import sqlite3
import hashlib
import random
import string
import os

def generate_salt():
    salt = os.urandom(32)
    return salt


# Function to hash passwords
def hash_password(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

# Function to initialize the database with preloaded test data
def initialize_with_preloaded_data():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT NOT NULL DEFAULT 'customer',
            salt BLOB
        ); ''')

    # Create reservations table
    cursor.execute('''CREATE TABLE IF NOT EXISTS reservations (
        serial_number INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_name TEXT,
        start_date TEXT,
        start_time TEXT,
        end_date TEXT,
        end_time TEXT,
        total_cost TEXT,
        down_payment REAL,
        customer_name TEXT,
        block_array TEXT,
        refund_amount REAL,
        status TEXT
    );''')

    # Generate salt for each user
    salt_customer1 = generate_salt()
    salt_customer2 = generate_salt()
    salt_scheduler1 = generate_salt()
    salt_scheduler2 = generate_salt()
    salt_admin1 = generate_salt()
    salt_admin2 = generate_salt()
     # Generate sample users with different roles
    users = [
        (12, 'customer1', salt_customer1, 'customer', hash_password('customer1@', salt_customer1)),
        (13, 'customer2', salt_customer2, 'customer', hash_password('customer2@', salt_customer2)),
        (14, 'scheduler1', salt_scheduler1, 'scheduler', hash_password('scheduler1!', salt_scheduler1)),
        (15, 'scheduler2', salt_scheduler2, 'scheduler', hash_password('scheduler2!', salt_scheduler2)),
        (16, 'admin1', salt_admin1, 'admin', hash_password('admin1$', salt_admin1)),
        (17, 'admin2', salt_admin2, 'admin', hash_password('admin2$', salt_admin2))
    ]

    # Insert users into the database
    cursor.executemany('INSERT INTO users (id, username, salt, role, password_hash) VALUES (?, ?, ?, ?, ?)', users)

    # Generate sample reservations for customers
    reservations = [
        (785419885, 'scooper', '2024-05-15', '10:00:00', '2024-05-15', '12:00:00', '2000.0', 1000.0, 'customer1', '0', 0.0, 'Active'),
        (785419883, 'harvester', '2024-05-23', '10:00:00', '2024-05-23', '12:00:00', '176000.0', 44000.0, 'customer1', '0', 0.0, 'Active'),
        (785419884, 'scanner', '2024-05-24', '14:00:00', '2024-05-24', '15:00:00', '990.0', 247.5, 'customer2', '1, 2, 3', 0.0, 'Active')
    ]

    # Insert reservations into the database
    cursor.executemany('''INSERT INTO reservations 
                           (serial_number, equipment_name, start_date, start_time, end_date, end_time, 
                            total_cost, down_payment, customer_name, block_array, refund_amount, status) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', reservations)

    # Commit changes and close connection
    conn.commit()
    conn.close()

# Call the function to initialize the database with preloaded data
initialize_with_preloaded_data()