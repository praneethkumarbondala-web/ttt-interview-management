import os
from flask import Flask, render_template, request, redirect, send_file, session
import sqlite3
from openpyxl import Workbook
from io import BytesIO


app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY")


@app.before_request
def require_login():

    if request.endpoint in ["login", "static"]:
        return

    if "logged_in" not in session:
        return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":

            session["logged_in"] = True

            return redirect("/")

        return render_template(
            "login.html",
            error="Invalid username or password"
        )

    return render_template("login.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


def get_db_connection():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    return connection

@app.route("/subjects")
def subjects():
    return render_template("subjects.html")

@app.route("/sql")
def sql():
    return render_template("sql.html")

@app.route("/sql-questions")
def sql_questions():
    return render_template("sql_questions.html")

@app.route("/interview-questions")
def interview_questions():
    return render_template("interview_questions.html")

@app.route("/spark")
def spark():
    return render_template("spark.html")

@app.route("/spark-questions")
def spark_questions():
    return render_template("spark_questions.html")

@app.route("/cloud")
def cloud():
    return render_template("cloud.html")

@app.route("/cloud-questions")
def cloud_questions():
    return render_template("cloud_questions.html")

@app.route("/etl")
def etl():
    return render_template("etl.html")

@app.route("/etl-questions")
def etl_questions():
    return render_template("etl_questions.html")

@app.route("/hadoop")
def hadoop():
    return render_template("hadoop.html")

@app.route("/hadoop-questions")
def hadoop_questions():
    return render_template("hadoop_questions.html")

@app.route("/python")
def python():
    return render_template("python.html")

@app.route("/python-questions")
def python_questions():
    return render_template("python_questions.html")


@app.route("/course/python")
def python_course():
    return render_template("python_course.html")

@app.route("/course/sql")
def sql_course():
    return render_template("sql_course.html")

@app.route("/course/aws")
def aws_course():
    return render_template("aws_course.html")

@app.route("/course/pyspark")
def pyspark_course():
    return render_template("pyspark_course.html")

@app.route("/course/ai")
def ai_course():
    return render_template("ai_course.html")

@app.route("/course/all-in-one")
def all_in_one_course():
    return render_template("all_in_one_course.html")

@app.route("/")
def dashboard():

    connection = get_db_connection()

    companies = connection.execute("""
    SELECT *
    FROM companies
    ORDER BY company_name
""").fetchall()

    search = request.args.get("search", "")
    batch = request.args.get("batch", "")

    query = """
        SELECT * FROM students
        WHERE 1=1
    """

    params = []

    if batch:
        query += " AND batch = ?"
        params.append(batch)

    if search:
        query += """
            AND (
                name LIKE ?
                OR branch LIKE ?
                OR email LIKE ?
                OR phone LIKE ?
            )
        """

        params.extend([
            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        ])

    query += " ORDER BY name"

    students = connection.execute(
        query,
        params
    ).fetchall()


    if batch:

        total_interviews = connection.execute("""
            SELECT COUNT(*)
            FROM interviews
            JOIN students
                ON interviews.student_id = students.id
            WHERE students.batch = ?
        """, (batch,)).fetchone()[0]

        selected = connection.execute("""
            SELECT COUNT(*)
            FROM interviews
            JOIN students
                ON interviews.student_id = students.id
            WHERE students.batch = ?
            AND interviews.status = 'selected'
        """, (batch,)).fetchone()[0]

        rejected = connection.execute("""
            SELECT COUNT(*)
            FROM interviews
            JOIN students
                ON interviews.student_id = students.id
            WHERE students.batch = ?
            AND interviews.status = 'rejected'
        """, (batch,)).fetchone()[0]

        pending = connection.execute("""
            SELECT COUNT(*)
            FROM interviews
            JOIN students
                ON interviews.student_id = students.id
            WHERE students.batch = ?
            AND interviews.status = 'pending'
        """, (batch,)).fetchone()[0]

    else:

        total_interviews = connection.execute(
            "SELECT COUNT(*) FROM interviews"
        ).fetchone()[0]

        selected = connection.execute(
            "SELECT COUNT(*) FROM interviews WHERE status = 'selected'"
        ).fetchone()[0]

        rejected = connection.execute(
            "SELECT COUNT(*) FROM interviews WHERE status = 'rejected'"
        ).fetchone()[0]

        pending = connection.execute(
            "SELECT COUNT(*) FROM interviews WHERE status = 'pending'"
        ).fetchone()[0]


    connection.close()

    return render_template(
        "dashboard.html",
        students=students,
        total_interviews=total_interviews,
        selected=selected,
        rejected=rejected,
        pending=pending,
        search=search,
        batch=batch,
        companies=companies
    )

@app.route("/add-student", methods=["GET", "POST"])
def add_student():

    connection = get_db_connection()

    if request.method == "POST":

        name = request.form["name"]
        branch = request.form["branch"]
        batch = request.form["batch"]
        email = request.form["email"]
        phone = request.form["phone"]

        connection.execute("""
    INSERT INTO students (name, branch, batch, email, phone)
    VALUES (?, ?, ?, ?, ?)
""", (
    name,
    branch,
    batch,
    email,
    phone
))

        connection.commit()
        connection.close()

        return redirect("/")

    connection.close()

    return render_template("add_student.html")


@app.route("/add-company", methods=["GET", "POST"])
def add_company():

    connection = get_db_connection()

    if request.method == "POST":

        company_name = request.form["company_name"]
        hr_name = request.form["hr_name"]
        hr_phone = request.form["hr_phone"]
        hr_email = request.form["hr_email"]

        connection.execute("""
            INSERT INTO companies
            (company_name, hr_name, hr_phone, hr_email)
            VALUES (?, ?, ?, ?)
        """, (
            company_name,
            hr_name,
            hr_phone,
            hr_email
        ))

        connection.commit()
        connection.close()

        return redirect("/")

    connection.close()

    return render_template("add_company.html")

@app.route("/edit-student/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):

    connection = get_db_connection()

    student = connection.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    if request.method == "POST":

        name = request.form["name"]
        branch = request.form["branch"]
        batch = request.form["batch"]
        email = request.form["email"]
        phone = request.form["phone"]

        connection.execute("""
            UPDATE students
                 SET name = ?, branch = ?, batch = ?, email = ?, phone = ?
                 WHERE id = ?
        """, (
            name,
            branch,
            batch,
            email,
            phone,
            student_id
        ))

        connection.commit()
        connection.close()

        return redirect(f"/student/{student_id}")

    connection.close()

    return render_template(
        "edit_student.html",
        student=student
    )

@app.route("/student/<int:student_id>")
def student_details(student_id):

    connection = get_db_connection()

    student = connection.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    interviews = connection.execute("""
        SELECT
            interviews.id,
            interviews.interview_date,
            interviews.status,
            interviews.remarks,
            companies.company_name,
            companies.hr_name,
            companies.hr_phone,
            companies.hr_email
        FROM interviews
        LEFT JOIN companies
            ON interviews.company_id = companies.id
        WHERE interviews.student_id = ?
        ORDER BY interviews.interview_date DESC
    """, (student_id,)).fetchall()

    total_interviews = connection.execute("""
        SELECT COUNT(*)
        FROM interviews
        WHERE student_id = ?
    """, (student_id,)).fetchone()[0]

    selected = connection.execute("""
        SELECT COUNT(*)
        FROM interviews
        WHERE student_id = ?
        AND status = 'selected'
    """, (student_id,)).fetchone()[0]

    rejected = connection.execute("""
        SELECT COUNT(*)
        FROM interviews
        WHERE student_id = ?
        AND status = 'rejected'
    """, (student_id,)).fetchone()[0]

    pending = connection.execute("""
        SELECT COUNT(*)
        FROM interviews
        WHERE student_id = ?
        AND status = 'pending'
    """, (student_id,)).fetchone()[0]

    connection.close()

    return render_template(
        "student_details.html",
        student=student,
        interviews=interviews,
        total_interviews=total_interviews,
        selected=selected,
        rejected=rejected,
        pending=pending
    )

@app.route("/delete-student/<int:student_id>", methods=["POST"])
def delete_student(student_id):

    connection = get_db_connection()

    connection.execute(
        "DELETE FROM interviews WHERE student_id = ?",
        (student_id,)
    )

    connection.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    connection.commit()
    connection.close()

    return redirect("/")

@app.route("/edit-interview/<int:interview_id>", methods=["GET", "POST"])
def edit_interview(interview_id):

    connection = get_db_connection()

    interview = connection.execute("""
        SELECT * FROM interviews
        WHERE id = ?
    """, (interview_id,)).fetchone()

    students = connection.execute(
        "SELECT * FROM students"
    ).fetchall()

    companies = connection.execute(
        "SELECT * FROM companies"
    ).fetchall()

    if request.method == "POST":

        student_id = request.form["student_id"]
        company_id = request.form["company_id"]
        interview_date = request.form["interview_date"]
        status = request.form["status"]
        remarks = request.form["remarks"]

        connection.execute("""
            UPDATE interviews
            SET student_id = ?,
                company_id = ?,
                interview_date = ?,
                status = ?,
                remarks = ?
            WHERE id = ?
        """, (
            student_id,
            company_id,
            interview_date,
            status,
            remarks,
            interview_id
        ))

        connection.commit()
        connection.close()

        return redirect(f"/student/{student_id}")

    connection.close()

    return render_template(
        "edit_interview.html",
        interview=interview,
        students=students,
        companies=companies
    )

@app.route("/delete-interview/<int:interview_id>", methods=["POST"])
def delete_interview(interview_id):

    connection = get_db_connection()

    interview = connection.execute("""
        SELECT student_id
        FROM interviews
        WHERE id = ?
    """, (interview_id,)).fetchone()

    if interview:

        student_id = interview["student_id"]

        connection.execute(
            "DELETE FROM interviews WHERE id = ?",
            (interview_id,)
        )

        connection.commit()
        connection.close()

        return redirect(f"/student/{student_id}")

    connection.close()

    return redirect("/")

@app.route("/companies")
def companies():

    connection = get_db_connection()

    companies = connection.execute(
        "SELECT * FROM companies"
    ).fetchall()

    connection.close()

    return render_template(
        "companies.html",
        companies=companies
    )

@app.route("/add-interview", methods=["GET", "POST"])
def add_interview():

    connection = get_db_connection()

    students = connection.execute(
        "SELECT * FROM students"
    ).fetchall()

    companies = connection.execute(
        "SELECT * FROM companies"
    ).fetchall()

    if request.method == "POST":

        student_id = request.form["student_id"]
        company_id = request.form["company_id"]
        interview_date = request.form["interview_date"]
        status = request.form["status"]
        remarks = request.form["remarks"]

        connection.execute("""
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

        return redirect("/")

    connection.close()

    return render_template(
        "add_interview.html",
        students=students,
        companies=companies
    )
@app.route("/download-hr-excel")
def download_hr_excel():

    connection = get_db_connection()

    companies = connection.execute("""
        SELECT company_name, hr_name, hr_phone, hr_email
        FROM companies
        ORDER BY company_name
    """).fetchall()

    connection.close()


    workbook = Workbook()

    sheet = workbook.active
    sheet.title = "HR Details"


    sheet.append([
        "Company Name",
        "HR Name",
        "HR Phone",
        "HR Email"
    ])


    for company in companies:

        sheet.append([
            company["company_name"],
            company["hr_name"],
            company["hr_phone"],
            company["hr_email"]
        ])


    file = BytesIO()

    workbook.save(file)

    file.seek(0)


    return send_file(
        file,
        as_attachment=True,
        download_name="HR_Details.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.route("/hr-details")
def hr_details():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM companies ORDER BY company_name")
    companies = cursor.fetchall()

    conn.close()

    return render_template("hr_details.html", companies=companies)

if __name__ == "__main__":
    app.run(debug=True)


