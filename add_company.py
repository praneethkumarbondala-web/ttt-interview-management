import sqlite3


connection = sqlite3.connect("database.db")

cursor = connection.cursor()


company_name = input("Enter company name: ")
hr_name = input("Enter HR name: ")
hr_phone = input("Enter HR phone: ")
hr_email = input("Enter HR email: ")


cursor.execute("""
INSERT INTO companies (company_name, hr_name, hr_phone, hr_email)
VALUES (?, ?, ?, ?)
""", (company_name, hr_name, hr_phone, hr_email))


connection.commit()

connection.close()


print("Company added successfully!")