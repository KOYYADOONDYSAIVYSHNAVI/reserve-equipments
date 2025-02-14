import sqlite3

connection = sqlite3.connect('data.db')

def delete_data(connection):
    cursor = connection.cursor()
    cursor.execute('''DROP TABLE IF EXISTS reservations''')
    cursor.execute('''DROP TABLE IF EXISTS users''')
    cursor.execute('''DROP TABLE IF EXISTS operation_history;''')
    print(cursor.fetchall())
    connection.commit()
    

def main():
    delete_data(connection)
    cursor = connection.cursor()
    print(cursor.fetchall())
    

if __name__ == "__main__":
    main()
