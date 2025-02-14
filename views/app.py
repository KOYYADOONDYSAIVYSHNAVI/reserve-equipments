import requests
import datetime
from datetime import timedelta
import math
import re
import sqlite3
import hashlib
import os
import uuid
import io

connection = sqlite3.connect('../database/data.db')
#connection = sqlite3.connect('../database/data.db')
BASE_URL = "http://127.0.0.1:8000"  

def create_users_table(connection):
    try:
        current = connection.cursor()
        table_data = """ 
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                salt BLOB,  -- Add the salt column here
                password_hash TEXT,
                role TEXT NOT NULL DEFAULT 'customer'
            ); """
        current.execute(table_data)

        # Add the ALTER TABLE statement to add the salt column if it doesn't exist
        alter_query = """
            PRAGMA table_info(users);
        """
        current.execute(alter_query)
        table_info = current.fetchall()
        salt_exists = any('salt' in column for column in table_info)
        if not salt_exists:
            current.execute("ALTER TABLE users ADD COLUMN salt BLOB;")
    
        connection.commit()
    except sqlite3.Error as e:
        print("Error occured while creating users table:", e)

def modify_users_table(connection):
    current = connection.cursor()
    alter_query = """ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'customer';"""
    try:
        current.execute(alter_query)
        connection.commit()
    except sqlite3.OperationalError:
        pass

def create_reservations_table(connection):
    try:
        current = connection.cursor()
        table_data = """ CREATE TABLE IF NOT EXISTS reservations (
                serial_number INTEGER PRIMARY KEY AUTOINCREMENT,
                equipment_name text,
                start_date text,
                start_time text,
                end_date text,
                end_time text,
                total_cost text,
                down_payment real,
                customer_name real,
                block_array text,
                refund_amount real,
                status text
            ); """
        current.execute(table_data)
        connection.commit()
    except sqlite3.Error as e:
        print("Error occured while creating reservations table:", e)

def create_operation_history_table(connection):
    try:
        current = connection.cursor()
        current.execute('''CREATE TABLE IF NOT EXISTS operation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            timestamp TEXT,
            operation TEXT
        )''')
        connection.commit()
    except sqlite3.Error as e:
        print("Error occured while creating reservations table:", e)


def log_operation(username, operation, connection):
    try:
        current = connection.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current.execute("INSERT INTO operation_history (user, timestamp, operation) VALUES (?, ?, ?)",
                        (username, timestamp, operation))
        connection.commit()
    except sqlite3.Error as e:
        print("Error occured while creating reservations table:", e)

def list_tables(connection):
    try:
        cursor = connection.cursor()
        sql_query = '''SELECT * FROM reservations;'''
        cursor.execute(sql_query)
        print(cursor.fetchall())
    except sqlite3.Error as e:
        print("Error occured while creating reservations table:", e)

def is_username_taken(username, cursor):
    try:
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
        count = cursor.fetchone()[0]
        return count > 0
    except sqlite3.Error as e:
        print("Error occured while creating reservations table:", e)
        return True

def register_user(username, password, role):
    try:
        if role == 1:
            role = "customer"
        elif role == 2:
            role = "admin"
        elif role == 3:
            role = "scheduler"
        else:
            print("Invalid role!")
            return

        current = connection.cursor()

        if is_username_taken(username, current):
            print("Username already taken!")
            return
        else:
            salt = os.urandom(32)
            hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

            sql_query = "INSERT INTO users (username, salt, password_hash, role) VALUES (?, ?, ?, ?)"
            current.execute(sql_query, (username, salt, hashed_password, role))
            connection.commit()
            log_operation(username, "Registration", connection)
            print("Registration successful!")
    except sqlite3.Error as e:
        print("Error occurred while registering user:", e)

def login(username, password, role):
    try:
        if role == 1:
            role = "customer"
        elif role == 2:
            role = "admin"
        elif role == 3:
            role = "scheduler"
        else:
            print("Invalid role!")
            return None
        if is_temporary_password(password):
            print("Please change your temporary password")
            change_password(username)
        current = connection.cursor()
        current.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_row = current.fetchone()
        if user_row:
            stored_salt = user_row[4]
            stored_password_hash = user_row[2]
            hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), stored_salt, 100000)
            #user = None
            if hashed_password == stored_password_hash and user_row[3] == role:
                user = {
                    "id": user_row[0],
                    "username": user_row[1],
                    "role": user_row[3]
                }
                log_operation(username, "Login", connection)
                print("Login successful!")
                return user
        else:
            print("Invalid username or password.")
            return None
    except sqlite3.Error as e:
        print("Error occurred while registering user:", e)


def is_temporary_password(password):
    try:
        return password.startswith('temp_')
    except Exception as e:
        print(f"Error in is_temporary_password: {e}")
        return False

def change_password(username):
    try:
        new_password = input("Enter new password: ")
        new_salt = os.urandom(32)
        new_password_hash = hashlib.pbkdf2_hmac('sha256', new_password.encode('utf-8'), new_salt, 100000)
        current = connection.cursor()
        current.execute("UPDATE users SET password_hash = ?, salt = ? WHERE username = ?", (new_password_hash, new_salt, username))
        connection.commit()
        log_operation(username, "Password Change", connection)
        print("Password changed successfully.")
    except Exception as e:
        print(f"Error in change password:{e}")


create_reservations_table(connection)
create_operation_history_table(connection)

def calculate_cost(equipment_name, start_date, start_time, end_time):
    try:
        # Base charges
        hourly_charge = {
            "scanner": 990,
            "scooper": 1000,
            "harvester": 88000
        }

        # Calculate total hours and total cost
        total_hours = (end_time.hour + end_time.minute / 60) - (start_time.hour + start_time.minute / 60)
        total_cost = hourly_charge[equipment_name.lower()] * total_hours

        if start_date - datetime.timedelta(days=14) > datetime.datetime.now().date():
            down_payment = total_cost * 0.25
        else:
            down_payment = total_cost * 0.5

        return total_cost, down_payment
    except Exception as e:
        print(f"Error in calculate cost:{e}")

def make_reservation(logged_in_user):
    try:
        while(True):
            block_array = ""
            equipment_name = input("Enter equipment name: ")
            equipment_names = ["scanner", "harvester", "scooper"]
            if(equipment_name not in equipment_names):
                print("choose a valid machine name")
                continue

            date_str = input("Enter date (YYYY-MM-DD): ")
            if(not datetime.datetime.strptime(date_str, "%Y-%m-%d")):
                print("please enter the date in ISO format")
                continue

            start_time_str = input("Enter start time (HH:MM): ")
            if(not datetime.datetime.strptime(start_time_str, "%H:%M")):
                print("please enter the time in HH:MM format")

            end_time_str = input("Enter end time (HH:MM): ")
            if(not datetime.datetime.strptime(end_time_str, "%H:%M")):
                print("please enter the time in HH:MM format")

            if logged_in_user["role"] == "customer":
                customer_name = logged_in_user['username']
            else:  # For scheduler, allow input of customer name
                customer_name = input("Enter customer name: ")

            start_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            start_time = datetime.datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.datetime.strptime(end_time_str, "%H:%M").time()

            total_cost, down_payment = calculate_cost(equipment_name, start_date, start_time, end_time)

            if(equipment_name == "scanner"):
                blocks = input("Enter block numbers between in a comma separated list (eg. w, x, y, z): ")
                block_array = blocks.split(", ")
                pattern = re.compile(r"^(\w+)(,\s*\w+)*$")
                if(not pattern.match(blocks)):
                    print("Please enter in x, y, z format")
                    continue
                amount_of_blocks = len(block_array)
                time_needed = 0
                if(amount_of_blocks%4 == 0):
                    time_needed = amount_of_blocks * 30 + 120
                else:
                    time_needed = amount_of_blocks * 30 + math.floor(amount_of_blocks/4)*12

                start_datetime = datetime.datetime.combine(start_date, start_time)
                end_datetime = datetime.datetime.combine(start_date, end_time)
                if(start_datetime + timedelta(minutes = time_needed) > end_datetime):
                    print("Not enough time provided for the equipment")
                    continue
                else:
                    break
            else:
                break

        # Make reservation request to server
        reservation_data = {
            "equipment_name": equipment_name,
            "start_date": start_date.isoformat(),
            "start_time": start_time_str,
            "end_date": start_date.isoformat(),
            "end_time": end_time_str,
            "total_cost": total_cost,
            "down_payment": down_payment,
            "customer_name": customer_name,
            "block_array": blocks if equipment_name == "scanner" else None,  # Include block array for scanner only
            "refund_amount": 0,
            "status": "Active"
        }

        if is_valid_reservation(reservation_data):
            response = requests.post(f"{BASE_URL}/reservations/", json=reservation_data)
            if response.status_code == 200:
                log_operation(logged_in_user['username'], f"Reservation: {equipment_name} from {start_date} {start_time} to {end_time} for {customer_name}", connection)
                print("Reservation created successfully!")
            else:
                print("Failed to make reservation")
        else:
            print("Invalid reservation details.")
    except Exception as e:
        print(f"Error in make reservation: {e}")

def get_reservation_data(serial_number):
    try:
        current = connection.cursor()
        sql_query = "SELECT * FROM reservations WHERE serial_number = ?"
        current.execute(sql_query, (serial_number,))
        reservation = current.fetchone()
        if reservation:
            reservation_data = {
                "serial_number": reservation[0],
                "equipment_name": reservation[1],
                "start_date": reservation[2],
                "start_time": reservation[3],
                "end_date": reservation[4],
                "end_time": reservation[5],
                "total_cost": reservation[6],
                "down_payment": reservation[7],
                "customer_name": reservation[8],
                "block_array": reservation[9],
                "refund_amount": reservation[10],
                "status": reservation[11]
            }
            return reservation_data
        else:
            print("Reservation not found.")
            return None
    except Exception as e:
        print(f"Error in get reservation data: {e}")

def cancel_reservation(logged_in_user):
    try:
        role = logged_in_user["role"]
        serial_number = input("Enter serial number of reservation to cancel: ")
        if not serial_number.isdigit():
            print("Serial number must only contain digits")
            return
        serial_number = int(serial_number)
        
        if role == "customer":
            current_user = logged_in_user["username"]
            reservation_data = get_reservation_data(serial_number)
            if reservation_data and reservation_data["customer_name"] == current_user:
                cancel_reservation_by_serial_number(serial_number, logged_in_user)
            else:
                print("You can only cancel your own reservations.")
        elif role == "scheduler":
            cancel_reservation_by_serial_number(serial_number, logged_in_user)
        else:
            print("Only customers can cancel their own reservations. Schedulers can cancel any reservation.")
    except Exception as e:
        print(f"Error in cancel reservation:{e}")

def cancel_reservation_by_serial_number(serial_number, logged_in_user):
    try:
        reservation_data = get_reservation_data(serial_number)
        if reservation_data:
            response = requests.delete(f"{BASE_URL}/reservations/{serial_number}")
            if response.status_code == 200:
                log_operation(logged_in_user['username'], f"Canceled reservation: {serial_number}", connection)
                print(f"Reservation {serial_number} canceled successfully.")
            else:
                print(f"Failed to cancel reservation {serial_number}.")
        else:
            print("Reservation not found.")
    except Exception as e:
        print(f"Error in cancel reservation by serial number:{e}")


def list_reservations(logged_in_user):
    print("Choose option for listing reservations:")
    print("1. For any given date range")
    print("2. For a given customer for a given date range")
    print("3. For a given machine for a given date range")
    option = input("Enter your choice: ")

    if option == "1":
        start_date_str = input("Enter start date (YYYY-MM-DD): ")
        if(not datetime.datetime.strptime(start_date_str, "%Y-%m-%d")):
            print("please enter the date in ISO format")
        end_date_str = input("Enter end date (YYYY-MM-DD): ")
        if(not datetime.datetime.strptime(end_date_str, "%Y-%m-%d")):
            print("please enter the date in ISO format")
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
        list_reservations_by_date_range(start_date, end_date, logged_in_user)
    elif option == "2":
        customer_name = input("Enter customer name: ")
        start_date_str = input("Enter start date (YYYY-MM-DD): ")
        if(not datetime.datetime.strptime(start_date_str, "%Y-%m-%d")):
            print("please enter the date in ISO format")
        end_date_str = input("Enter end date (YYYY-MM-DD): ")
        if(not datetime.datetime.strptime(end_date_str, "%Y-%m-%d")):
            print("please enter the date in ISO format")
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
        list_reservations_by_customer(customer_name, start_date, end_date, logged_in_user)
    elif option == "3":
        equipment_name = input("Enter equipment name: ")
        start_date_str = input("Enter start date (YYYY-MM-DD): ")
        if(not datetime.datetime.strptime(start_date_str, "%Y-%m-%d")):
            print("please enter the date in ISO format")
        end_date_str = input("Enter end date (YYYY-MM-DD): ")
        if(not datetime.datetime.strptime(end_date_str, "%Y-%m-%d")):
            print("please enter the date in ISO format")
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
        list_reservations_by_machine(equipment_name, start_date, end_date, logged_in_user)
    else:
        print("Invalid option")

def get_reservation_info(reservation):
    try:
        serial_number = reservation[0]
        equipment_name = reservation[1]
        start_date = reservation[2]
        start_time = reservation[3]
        end_date = reservation[4]
        end_time = reservation[5]
        total_cost = reservation[6]
        down_payment = reservation[7]
        customer_name = reservation[8]
        block_array = reservation[9]
        status = reservation[10]
        refund_amount = reservation[11]
        
        info = f"Serial Number: {serial_number}\n" \
            f"Equipment Name: {equipment_name}\n" \
            f"Start Date: {start_date}\n" \
            f"Start Time: {start_time}\n" \
            f"End Date: {end_date}\n" \
            f"End Time: {end_time}\n" \
            f"Total Cost: {total_cost}\n" \
            f"Down Payment: {down_payment}\n" \
            f"Customer Name: {customer_name}\n" \
            f"Block Array: {block_array}\n" \
            f"Refund Amount: {refund_amount}\n" \
            f"Status: {status}\n"
        
        return info
    except sqlite3.Error as e:
        print("Error occured while retrieving reservation data:", e)
        return None

def list_reservations_by_date_range(start_date, end_date, logged_in_user):
    try:
        if logged_in_user['role'] == 'customer':
            sql_query = '''SELECT * FROM reservations WHERE start_date BETWEEN ? AND ? AND customer_name = ?'''
            cursor = connection.cursor()
            cursor.execute(sql_query, (start_date.isoformat(), end_date.isoformat(), logged_in_user['username']))
        elif logged_in_user['role'] == 'scheduler':
            sql_query = '''SELECT * FROM reservations WHERE start_date BETWEEN ? AND ? '''
            cursor = connection.cursor()
            cursor.execute(sql_query, (start_date.isoformat(), end_date.isoformat()))
        else:
            print("Invalid role for listing reservations.")
            return
        reservations = cursor.fetchall()
        print("Reservations for the given date range:")
        for reservation in reservations:
            if reservation[11] == "Active":
                print(get_reservation_info(reservation))
        log_operation(logged_in_user['username'], f"Listed reservations by date range: {start_date} to {end_date}", connection)
    except sqlite3.Error as error:
        print("Error executing SQL query:", error)

def list_reservations_by_customer(customer_name, start_date, end_date, logged_in_user):
    try:
        if logged_in_user["role"] == "customer" and customer_name != logged_in_user['username']:
            print("You can only view your own reservations.")
            return
        sql_query = '''SELECT * FROM reservations WHERE customer_name=? AND start_date BETWEEN ? AND ?'''
        cursor = connection.cursor()
        cursor.execute(sql_query, (customer_name, start_date.isoformat(), end_date.isoformat()))
        reservations = cursor.fetchall()
        print(f"Reservations for customer {customer_name} for the given date range:")
        for reservation in reservations:
            if reservation[10] == "Active":
                print(get_reservation_info(reservation))
        log_operation(logged_in_user['username'], f"Listed reservations by customer: {customer_name} for the date range: {start_date} to {end_date}", connection)
    except sqlite3.Error as error:
        print("Error executing SQL query:", error)

def list_reservations_by_machine(equipment_name, start_date, end_date, logged_in_user):
    try:
        if logged_in_user['role'] == 'customer':
            sql_query = '''SELECT * FROM reservations WHERE equipment_name=? AND start_date BETWEEN ? AND ? AND customer_name = ?'''
            cursor = connection.cursor()
            cursor.execute(sql_query, (equipment_name, start_date.isoformat(), end_date.isoformat(), logged_in_user['username']))
        elif logged_in_user['role'] == 'scheduler':
            sql_query = '''SELECT * FROM reservations WHERE equipment_name=? AND start_date BETWEEN ? AND ?'''
            cursor = connection.cursor()
            cursor.execute(sql_query, (equipment_name, start_date.isoformat(), end_date.isoformat()))
        else:
            print("Invalid role for listing reservations.")
            return
        reservations = cursor.fetchall()
        print(f"Reservations for machine {equipment_name} for the given date range:")
        for reservation in reservations:
            if reservation[10] == "Active":
                print(get_reservation_info(reservation))
        log_operation(logged_in_user['username'], f"Listed reservations by machine: {equipment_name} for the date range: {start_date} to {end_date}", connection)
    except sqlite3.Error as error:
        print("Error executing SQL query:", error)

def list_transactions(logged_in_user):
    try:
        s_date_str = input("Enter start date (YYYY-MM-DD): ")
        e_date_str = input("Enter end date (YYYY-MM-DD): ")
        s_date = datetime.datetime.strptime(s_date_str, "%Y-%m-%d").date()
        e_date = datetime.datetime.strptime(e_date_str, "%Y-%m-%d").date()
        
        if logged_in_user['role'] == 'customer':
            sql_query = '''SELECT * FROM reservations WHERE start_date BETWEEN ? AND ? AND customer_name = ?'''
            cursor = connection.cursor()
            cursor.execute(sql_query, (s_date.isoformat(), e_date.isoformat(), logged_in_user['username']))
        elif logged_in_user["role"] == "scheduler":
            sql_query = '''SELECT * FROM reservations WHERE start_date BETWEEN ? AND ?'''
            cursor = connection.cursor()
            cursor.execute(sql_query, (s_date.isoformat(), e_date.isoformat()))
        else:
            print("Invalid role for listing transactions.")
            return
        transactions = cursor.fetchall()

        print(f"List of transactions from {s_date} to {e_date}:")
        for transaction in transactions:
            print(get_reservation_info(transaction))
        log_operation(logged_in_user['username'], f"Listed transactions for the date range: {s_date} to {e_date}", connection)
    except (sqlite3.Error, ValueError) as error:
        print("Error:", error)
    
def generate_temporary_password():
    return str(uuid.uuid4())

def add_user(logged_in_user):
    try:
        if logged_in_user["role"] != "admin":
            print("Only admins can add new users")
            return 
        username = input("Enter username: ")
        role = int(input("Enter user role (1: customer, 2: admin, 3: scheduler):"))
        if role not in [1,2,3]:
            print("Invalid role. Please choose from '1: customer', '2: admin', or '3: scheduler'.")
            return
        temp_password = "temp_"+generate_temporary_password()
        # Register the user with the temporary password
        register_user(username, temp_password, role)
        log_operation(logged_in_user["username"], f"User Addition: {username} with role {role}", connection)
        print(f"User '{username}' added successfully with temporary password: {temp_password}")
    except Exception as e:
        print("An error occured while adding user:", e)

def remove_user(logged_in_user):
    try:
        if logged_in_user["role"] != "admin":
            print("Only admins can remove users.")
            return

        username = input("Enter username of the user to remove: ")

        # Check if the user exists
        if not user_exists(username):
            print(f"User '{username}' does not exist.")
            return
        
        # Check if the user is the last admin
        if is_last_admin(username):
            print("Cannot remove the last admin.")
            return

        # Remove the user
        delete_user_reservations(username)
        delete_user_from_table(username)
        log_operation(logged_in_user["username"], f"User Removal: {username}", connection)
        print(f"User '{username}' removed successfully.")
    except Exception as e:
        print("An error occured while removing user:", e)

def delete_user_reservations(username):
    try:
        current = connection.cursor()

        # Get reservation IDs associated with the user
        current.execute("""SELECT serial_number FROM reservations WHERE customer_name = ?""", (username,))
        reservation_ids = current.fetchall()

        if not reservation_ids:
            print(f"No reservations found for user '{username}'.")
            return

        # Delete reservations one by one
        for reservation_id in reservation_ids:
            print(reservation_id[0])
            current.execute("""DELETE FROM reservations WHERE serial_number = ?""", (reservation_id[0],))

        connection.commit()
        print(f"Reservations deleted successfully for user '{username}'.")
    except Exception as e:
        print("An error occurred while deleting reservations:", e)

def delete_user_from_table(username):
    try:
        current = connection.cursor()
        current.execute("""DELETE FROM users WHERE username = ?""", (username,))
        connection.commit()
        print(f"User '{username}' deleted from the users table.")
    except Exception as e:
        print("An error occurred while deleting user from the users table:", e)

def user_exists(username):
    current = connection.cursor()
    current.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
    count = current.fetchone()[0]
    return count > 0

def is_last_admin(username):
    current = connection.cursor()
    current.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    admin_count = current.fetchone()[0]
    return admin_count > 1 and user_exists(username) and get_user_role(username) == 'admin'

def get_user_role(username):
    current = connection.cursor()
    current.execute("SELECT role FROM users WHERE username = ?", (username,))
    role = current.fetchone()
    if role:
        return role[0]
    else:
        return None

def change_user_role(logged_in_user):
    if logged_in_user["role"] != "admin":
        print("Only admins can change user roles.")
        return

    username = input("Enter username of the user whose role you want to change: ")
    if not user_exists(username):
        print(f"User '{username}' does not exist.")
        return

    current_role = get_user_role(username)
    if current_role == 'admin':
        print("Cannot change the role of another admin.")
        return
        
    new_role = int(input("Enter the new role (1: customer, 2: admin, 3: scheduler): "))
    if new_role not in [1, 2, 3]:
        print("Invalid role. Please choose from '1: customer', '2: admin', or '3: scheduler'.")
        return
    if new_role == 1:
        new_role = "customer"
    elif new_role == 2:
        new_role = "admin"
    elif new_role == 3:
        new_role = "scheduler"
    else:
        print("Invalid role!")
        return None

    # Update the user's role in the database
    current = connection.cursor()
    current.execute("UPDATE users SET role = ? WHERE username = ?", (new_role, username))
    connection.commit()

    log_operation(logged_in_user["username"], f"Role Change: {username} to {new_role}", connection)
    print(f"User '{username}' role changed successfully to {new_role}.")

def reset_password(logged_in_user):
    if logged_in_user["role"] != "admin":
        print("You do not have permission to reset passwords.")
        return

    # Get the username of the user whose password needs to be reset
    username_to_reset = input("Enter the username of the user whose password you want to reset: ")

    # Generate a temporary password
    temporary_password = "temp_"+generate_temporary_password()

    print("Temporary password generated: ", temporary_password)
    # Update the temporary password in the database
    update_temp_password(username_to_reset, temporary_password)
    log_operation(logged_in_user["username"], f"Password Reset: {username_to_reset}", connection)

def is_valid_reservation(reservation):
    start_date_str = str(reservation["start_date"]) + " " + str(reservation["start_time"])
    end_date_str = str(reservation["end_date"]) + " " + str(reservation["end_time"])
    time_in = datetime.datetime.strptime(start_date_str, "%Y-%m-%d %H:%M")
    time_out = datetime.datetime.strptime(end_date_str, "%Y-%m-%d %H:%M")

    day_of_week = time_in.strftime("%A")
    today = datetime.datetime.now()
    #checking for station being open
    if(day_of_week == "Sunday"):
        print("Not open Sundays!")
        return False
    elif(day_of_week == "Saturday" and (int(time_in.strftime("%H")) < 10 or int(time_out.strftime("%H")) > 16)):
        print("You must choose a time between 10:00 and 16:00 on Saturdays!")
        return False
    elif(int(time_in.strftime("%H")) < 9 or int(time_out.strftime("%H")) > 18):
        print("You must choose a time between 9:00 and 18:00 on Monday through Fridays!")
        return False
    #checking that it's in the next 30 days
    elif(today > time_in  or time_in > today + timedelta(days=30)):
            print("You must choose a day within the next 30 days!")
            return False
    #making sure the times entered are on the half hour
    elif((time_in.strftime("%M") not in ["00", "30"]) or (time_out.strftime("%M") not in ["00", "30"])):
        print("You must choose a start and end time that start on the hour or half hour!")
        return False
    else:      
        #check for no overlaps
        num_of_scoopers = 4
        num_of_scanners = 3
        num_of_harvesters = 1
        
        list_of_reservations = []

        get_rows_query = '''SELECT * from reservations'''
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(get_rows_query)
        
        for row in cursor.fetchall():
            list_of_reservations.append(row)
        if(list_of_reservations):
            for created_reservation in list_of_reservations:
                start_time_str = created_reservation["start_time"]
                start_time_parts = start_time_str.split(":")
                start_time_without_seconds = ":".join(start_time_parts[:2])
                end_time_str = created_reservation["end_time"]
                end_time_parts = end_time_str.split(":")
                end_time_without_seconds = ":".join(end_time_parts[:2])
                data_time_in = datetime.datetime.strptime(created_reservation["start_date"] + " " + start_time_without_seconds, "%Y-%m-%d %H:%M")
                data_time_out = datetime.datetime.strptime(created_reservation["end_date"] + " " + end_time_without_seconds, "%Y-%m-%d %H:%M")
                if(reservation["start_date"] == created_reservation["start_date"]):
                    if(reservation["equipment_name"] == "harvester" and created_reservation["equipment_name"] == "harvester"):
                        if(data_time_in <= time_in <= data_time_out + timedelta(hours=6) or data_time_in <= time_out + timedelta(hours=6) <= data_time_out or (data_time_in >= time_in and data_time_out + timedelta(hours=6) <= time_out) ):
                            print("harvester is in use or in cooldown, please choose another time.")
                            return False
                    elif(created_reservation["equipment_name"] == "harvester" and reservation["equipment_name"] == "scanner"):
                        if(data_time_in <= time_in <= data_time_out or data_time_in <= time_out <= data_time_out or (data_time_in >= time_in and data_time_out <= time_out)):
                        #if the harvester is in use but not on cooldown this is included to see if scanners can be used
                            num_of_harvesters-=1    
                            if(num_of_harvesters < 1):
                                print("Scanners can't be used at the same time as the harvester please choose a different time.")
                                return False
                    elif(reservation["equipment_name"] == "scooper" and created_reservation["equipment_name"] == "scooper"):
                        if(data_time_in <= time_in <= data_time_out or data_time_in <= time_in <= data_time_out or (data_time_in >= time_in and data_time_out <= time_out)):
                            if(num_of_scoopers > 0):
                                num_of_scoopers -= 1
                            else:
                                print("All the scoopers are in use try a different time.")
                                return False
                    elif(reservation["equipment_name"] == "scanner" and created_reservation["equipment_name"] == "scanner"):
                        if(data_time_in <= time_in <= data_time_out or data_time_in <= time_in <= data_time_out or (data_time_in >= time_in and data_time_out <= time_out)):
                            if(reservation["block_array"] and created_reservation["block_array"]):
                                reservation_blocks = set(reservation["block_array"].split(", "))
                                created_reservation_blocks = set(created_reservation["block_array"].split(", "))
                                if(reservation_blocks.intersection(created_reservation_blocks)):
                                    print("This block is being scanned at this time please choose a different time.")
                                    return False
                                if(num_of_scanners > 0):
                                    num_of_scanners -= 1
                                else:
                                    print("Three scanners are in use now, you must choose another time.")
                                    return False
                            # if(num_of_harvesters < 1):
                            #     print("Scanners can't be used at the same time as the harvester please choose a different time.")
                            #     return False
    #if the false conditions are never hit, returns true
    return True

def print_operation_history():
    connection = sqlite3.connect('../database/data.db')
    current = connection.cursor()
    sql_query = '''SELECT user, timestamp, operation FROM operation_history'''
    current.execute(sql_query)
    operation_history = current.fetchall()
    print("Operation History:")
    for entry in operation_history:
        print(f"User: {entry[0]}, Timestamp: {entry[1]}, Operation: {entry[2]}")
    connection.close()

def update_temp_password(username, new_password):
    # Connect to the SQLite database
    new_salt = os.urandom(32)
    new_password_hash = hashlib.pbkdf2_hmac('sha256', new_password.encode('utf-8'), new_salt, 100000)
    current = connection.cursor()
    current.execute("UPDATE users SET password_hash = ?, salt = ? WHERE username = ?", (new_password_hash, new_salt, username))
    connection.commit()
    print("Temporary password updated successfully in the database.")
    
def main():
    create_reservations_table(connection)
    list_tables(connection)
    create_users_table(connection)
    modify_users_table(connection)
    logged_in_user = None
    while True:

        if not logged_in_user:
            print("\n Choose Operation: ")
            print("1. Register")
            print("2. Login")
            print("3. Exit")
            auth_choice = input("Enter your choice: ")
            if auth_choice == "1":
                username = input("Enter username: ")
                password = input("Enter password: ")
                print("\n Enter user role: ")
                print("1: Customer")
                print("2: Admin")
                print("3: Scheduler")
                role = input("Enter your choice: ")
                if role not in ["1", "2", "3"]:
                    print("Invalid option. Enter 1, 2, or 3")
                else:
                    register_user(username, password, int(role))
            elif auth_choice == "2":
                username = input("Enter username: ")
                print("\n Choose Operation: ")
                print("1. Enter password")
                print("2. Change password")
                option = input("Enter your choice: ")
                if option == "1":
                    password = input("Enter password: ")
                    print("\n Enter user role: ")
                    print("1: Customer")
                    print("2: Admin")
                    print("3: Scheduler")
                    role = input("Enter your choice: ")
                    if role not in ["1", "2", "3"]:
                        print("Invalid option. Enter 1, 2, or 3")
                    else:
                        logged_in_user = login(username, password, int(role))
                elif option == "2":
                    new_temp_password = "temp_"+generate_temporary_password()
                    update_temp_password(username, new_temp_password)
                    print(f"Temporary password generated {new_temp_password}. Please log in with your temporary password.")

                else:
                    print("Invalid option. Enter 1 or 2")
                
            elif auth_choice == "3":
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please enter a number from 1 to 3.")
        else:
            if logged_in_user["role"] == "customer":
                print("\nChoose operation:")
                print("1. Make reservation")
                print("2. Cancel reservation")
                print("3. List reservations")
                print("4. List Transactions")
                print("5. Change Password")
                print("6. Logout")
                choice = input("Enter your choice: ")

                if choice == "1":
                    make_reservation(logged_in_user)
                elif choice == "2":
                    cancel_reservation(logged_in_user)
                elif choice == "3":
                    list_reservations(logged_in_user)
                elif choice == "4":
                    list_transactions(logged_in_user)
                elif choice == "5":
                    new_temp_password = "temp_"+generate_temporary_password()
                    update_temp_password(username, new_temp_password)
                    print(f"Temporary password generated {new_temp_password}. Please log in with your temporary password.")
                    return None
                elif choice == "6":
                    print("Logging out...")
                    logged_in_user = None
                else:
                    print("Invalid choice. Please enter a number from 1 to 6.")
            elif logged_in_user["role"] == "admin":
                print("\nChoose operation:")
                print("1. Add User")
                print("2. Remove User")
                print("3. Change User Role")
                print("4. Reset Password")
                print("5. Display Operation History")
                print("6. Logout")
                choice = input("Enter your choice: ")

                if choice == "1":
                    add_user(logged_in_user)
                elif choice == "2":
                    remove_user(logged_in_user)
                elif choice == "3":
                    change_user_role(logged_in_user)
                elif choice == "4":
                    reset_password(logged_in_user)
                elif choice == "5":
                    print_operation_history()
                elif choice == "6":
                    print("Logging out...")
                    logged_in_user = None
                else:
                    print("Invalid choice. Please enter a number from 1 to 5.")
            elif logged_in_user["role"] == "scheduler":
                print("\nChoose operation:")
                print("1. Make reservation")
                print("2. Cancel reservation")
                print("3. List reservations")
                print("4. List Transactions")
                print("5. Logout")
                choice = input("Enter your choice: ")

                if choice == "1":
                    make_reservation(logged_in_user)
                elif choice == "2":
                    cancel_reservation(logged_in_user)
                elif choice == "3":
                    list_reservations(logged_in_user)
                elif choice == "4":
                    list_transactions(logged_in_user)
                elif choice == "5":
                    print("Logging out...")
                    logged_in_user = None
                else:
                    print("Invalid choice. Please enter a number from 1 to 5.")

if __name__ == "__main__":
    main()