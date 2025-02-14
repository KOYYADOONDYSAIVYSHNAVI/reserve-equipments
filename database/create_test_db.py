import sqlite3

connection = sqlite3.connect('data.db')

def create_test_db():
    test_connection = sqlite3.connect('test_data.db')
    with open("test_data.sql", "r") as file:
        queries = file.read()
    cursor = test_connection.cursor()
    # cursor.execute('''PRAGMA database_list''')
    cursor.executescript(queries)
    print(cursor.fetchall())

def main():
    create_test_db()

if __name__ == "__main__":
    main()
