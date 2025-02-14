import pytest
import requests
import os
import uvicorn
import sys
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.api import app
from multiprocessing import Process
import sqlite3


# Define a function to start the server
def start_server():
    uvicorn.run(app, host="http://127.0.0.1", port=8000)
@pytest.fixture(scope="module")

def test_server():    
    # Start the server in a separate process
    server_process = Process(target=start_server)
    server_process.start()
    yield
    server_process.terminate()    

connection = sqlite3.connect('../database/test_data.db')
def test_list_reservations_by_date():
    reservation_data = {
        "start_date": "2024-05-22",
        "end_date":"2024-05-25"
    }
    cursor = connection.cursor()
    cursor.execute(f'''
        SELECT * FROM reservations
        WHERE (start_date BETWEEN "2024-05-22" AND "2024-05-25")
    ''')
    assert  cursor.fetchall() == [(785419883, 'harvester', '2024-05-23', '10:00:00', '2024-05-23', '12:00:00', '176000.0', 44000.0, 'customer1', '0', 0.0, 'Active'), 
    (785419884, 'scanner', '2024-05-24', '14:00:00', '2024-05-24', '15:00:00', '990.0', 247.5, 'customer2', '1,2,3', 0.0, 'Active')]

def test_list_reservations_by_customer():
    reservation_data = {
        "start_date": "2024-05-22",
        "end_date":"2024-05-25",
        "customer_name": "customer1"
    }
    cursor = connection.cursor()
    cursor.execute(f'''
        SELECT * FROM reservations
        WHERE (start_date BETWEEN "2024-05-22" AND "2024-05-25") 
        AND (customer_name = "customer1")
    ''')

    assert  cursor.fetchall() == [(785419883, 'harvester', '2024-05-23', '10:00:00', '2024-05-23', '12:00:00', '176000.0', 44000.0, 'customer1', '0', 0.0, 'Active')]


def test_list_reservations_by_machine():
    reservation_data = {
        "start_date": "2024-05-22",
        "end_date":"2024-05-25",
        "equipment_name": "scanner"
    }
    cursor = connection.cursor()
    cursor.execute(f'''
        SELECT * FROM reservations
        WHERE (start_date BETWEEN "2024-05-22" AND "2024-05-25") 
        AND (equipment_name = "scanner")
    ''')

    assert  cursor.fetchall() == [(785419884, 'scanner', '2024-05-24', '14:00:00', '2024-05-24', '15:00:00', '990.0', 247.5, 'customer2', '1,2,3', 0.0, 'Active')]

def test_make_reservation():
    date = "2024-05-23"
    reservation_data = {
        "serial_number": 785419889,

        "customer_name": "customer1",
        "equipment": "scooper",
        "date": date,
        "start_time": "10:00",
        "end_time": "12:00",

    }
    cursor = connection.cursor()
    cursor.execute(f'''
        INSERT INTO reservations (serial_number, equipment_name, start_date, start_time, end_date, end_time, total_cost,
        down_payment, customer_name, block_array, refund_amount, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (785419889, "scooper", "2024-05-15", "10:00:00", "2024-05-15", "12:00:00", "2000.0", 1000.0, "customer1", "0", 0.0, "Active"))
    cursor.execute('''
        SELECT * FROM reservations
        WHERE customer_name = "customer1"
    ''')
    
    assert cursor.fetchall() == [(785419883, "harvester", "2024-05-23", "10:00:00", "2024-05-23", "12:00:00", "176000.0", 44000.0, "customer1", "0", 0.0, "Active"),
    (785419885, "scooper", "2024-05-15", "10:00:00", "2024-05-15", "12:00:00", "2000.0", 1000.0, "customer1", "0", 0.0, "Active"),
    (785419887, "scooper", "2024-05-18", "12:00:00", "2024-05-18", "14:00:00", "2000.0", 1000.0, "customer1", "0", 0.0, "Active"),
    (785419889, "scooper", "2024-05-15", "10:00:00", "2024-05-15", "12:00:00", "2000.0", 1000.0, "customer1", "0", 0.0, "Active")]

def test_cancel_reservation():
    cursor = connection.cursor()
    cursor.execute(f'''
        DELETE FROM reservations
        WHERE serial_number = "785419889"
    ''')
    cursor.execute("SELECT * from reservations")

    assert cursor.fetchall() == [(785419883, 'harvester', '2024-05-23', '10:00:00', '2024-05-23', '12:00:00', '176000.0', 44000.0, 'customer1', '0', 0.0, 'Active'), 
                               (785419884, 'scanner', '2024-05-24', '14:00:00', '2024-05-24', '15:00:00', '990.0', 247.5, 'customer2', '1,2,3', 0.0, 'Active'), 
                               (785419885, 'scooper', '2024-05-15', '10:00:00', '2024-05-15', '12:00:00', '2000.0', 1000.0, 'customer1', '0', 0.0, 'Active'),
                               (785419887, "scooper", "2024-05-18", "12:00:00", "2024-05-18", "14:00:00", "2000.0", 1000.0, "customer1", "0", 0.0, "Active")]

def test_list_transactions():
    cursor = connection.cursor()
    cursor.execute('''
        SELECT * FROM operation_history
        WHERE (timestamp BETWEEN "2024-05-22" AND "2024-05-25") AND
        (operation = "transaction")
    ''')
    assert cursor.fetchall() == []

if __name__ == "__main__":
    pytest.main()