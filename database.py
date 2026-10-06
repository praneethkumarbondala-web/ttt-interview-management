import sqlite3


connection = sqlite3.connect("database.db")

cursor = connection.cursor()


# Students table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    branch TEXT,
    email TEXT,
    phone TEXT
    batch Text
)
""")


# Companies table
cursor.execute("""
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    hr_name TEXT,
    hr_phone TEXT,
    hr_email TEXT
)
""")


# Interviews table
cursor.execute("""
CREATE TABLE IF NOT EXISTS interviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    company_id INTEGER,
    interview_date TEXT,
    status TEXT,
    remarks TEXT,

    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (company_id) REFERENCES companies(id)
)
""")


connection.commit()

connection.close()

print("Database created successfully!")