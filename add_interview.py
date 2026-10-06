import sqlite3


connection = sqlite3.connect("database.db")

cursor = connection.cursor()


student_id = input("Enter student ID: ")
company_id = input("Enter company ID: ")
interview_date = input("Enter interview date (YYYY-MM-DD): ")
status = input("Enter status (Selected/Rejected/Pending): ")
remarks = input("Enter remarks: ")


cursor.execute("""
INSERT INTO interviews
(student_id, company_id, interview_date, status, remarks)
VALUES (?, ?, ?, ?, ?)
""", (
    student_id,
    company_id,
    interview_date,
    status,
    remarks
))


connection.commit()

connection.close()


print("Interview added successfully!")