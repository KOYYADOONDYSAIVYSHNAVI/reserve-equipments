from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import datetime
import sqlite3

# Define request models
class ReservationRequest(BaseModel):
    """
    Request model for making a reservation.
    """
    equipment_name: str
    start_date: datetime.date
    start_time: datetime.time
    end_date: datetime.date
    end_time: datetime.time
    total_cost: float
    down_payment: float
    customer_name: str
    block_array: Optional[str]
    refund_amount: float
    status: str

class CancelReservationRequest(BaseModel):
    """
    Request model for cancelling a reservation.
    """
    serial_number: int

class DateRangeRequest(BaseModel):
    """
    Request model for specifying a date range.
    """
    start_date: datetime.date
    end_date: datetime.date

class Reservation:
    """
    Class representing a reservation.
    """
    def __init__(self, equipment_name, start_date, start_time, 
                 end_date, end_time, total_cost, down_payment, customer_name, 
                 status, refund_amount, block_array):
        self.equipment_name = equipment_name
        self.start_date = start_date
        self.start_time = start_time
        self.end_date = end_date
        self.end_time = end_time,
        self.total_cost = total_cost,
        self.down_payment = down_payment,
        self.customer_name = customer_name
        self.block_array = block_array
        self.refund_amount = refund_amount
        self.status = status

connection = sqlite3.connect('../database/data.db')

class Station13:
    """
    Class representing Station13, a reservation management system.
    """
    def __init__(self):
        self.connection = sqlite3.connect('../database/data.db')

    def make_reservation(self, reservation_request: ReservationRequest):
        current = self.connection.cursor()
        reservation = reservation_request.dict()
        if reservation['equipment_name'] == "scanner" and reservation['block_array'] is None:
            raise HTTPException(status_code=400, detail="Block array is required for scanner equipment.")

        if reservation['start_time'].minute not in [0, 30] or reservation['end_time'].minute not in [0, 30]:
            raise HTTPException(status_code=400, detail="Reservation times must start and end on the hour or half hour.")

        if reservation['block_array'] is None:
            reservation['block_array'] = "0"  # Set block_array to 0 if None
        sql_query = '''INSERT INTO reservations(equipment_name, start_date, start_time, end_date, 
                    end_time, total_cost, down_payment, customer_name, block_array, refund_amount, status)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?)'''
        current.execute(sql_query, (reservation['equipment_name'], str(reservation['start_date']), 
                                   str(reservation['start_time']), str(reservation['end_date']),
                                   str(reservation['end_time']), reservation['total_cost'], 
                                   reservation['down_payment'], reservation['customer_name'], 
                                   reservation['block_array'], 0, "Active",))
        self.connection.commit()
        return {
            "total_cost": reservation['total_cost'],
            "down_payment": reservation['down_payment']
        }

    def calculate_refund(self, down_payment, start_date, cancel_date):
        days_difference = (start_date - cancel_date).days
        if days_difference >= 7:
            refund_percentage = 0.75
        else:
            refund_percentage = 0.5	
        refund_amount = float(down_payment) * refund_percentage
        return refund_amount
    
    def cancel_reservation(self, serial_number):
        current = self.connection.cursor()
        sql_query = '''SELECT * FROM reservations WHERE serial_number = ?'''
        current.execute(sql_query, (serial_number,))
        reservation = current.fetchone()
        if reservation:
            down_payment = reservation[6]
            start_date = datetime.datetime.strptime(reservation[2], "%Y-%m-%d").date()
            cancel_date = datetime.datetime.now().date()
            refund_amount = self.calculate_refund(down_payment, start_date, cancel_date)
            sql_query = '''UPDATE reservations SET status = ?, refund_amount = ? WHERE serial_number = ?'''
            current.execute(sql_query, ("Cancelled", refund_amount, serial_number))
            self.connection.commit()
            return {"message": "Reservation cancelled successfully", "refund_amount": refund_amount}
        else:
            raise HTTPException(status_code=404, detail="Reservation not found")

station = Station13()

app = FastAPI()

@app.post("/reservations/")
async def make_reservation(reservation: ReservationRequest):
    response = station.make_reservation(reservation)
    return {"message": "Reservation made successfully", "reservation_details": response}

@app.delete("/reservations/{serial_number}")
async def cancel_reservation(serial_number: int):
    response = station.cancel_reservation(serial_number)
    return {"message": response["message"], "refund_amount": response["refund_amount"]}