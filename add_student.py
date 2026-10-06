import sqlite3


connection = sqlite3.connect("database.db")

cursor = connection.cursor()


name = input("Enter student name: ")
branch = input("Enter branch: ")
email = input("Enter email: ")
phone = input("Enter phone: ")


cursor.execute("""
INSERT INTO students (name, branch, email, phone)
VALUES (?, ?, ?, ?)
""", (name, branch, email, phone))


connection.commit()

connection.close()

print("Student added successfully!")