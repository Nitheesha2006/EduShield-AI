
import sqlite3
import pandas as pd
import hashlib
import secrets

DB_NAME = "edushield.db"


# ==================================================
# DATABASE CONNECTION
# ==================================================

def connect():
    return sqlite3.connect(DB_NAME)


# ==================================================
# PASSWORD HASHING
# ==================================================

def hash_password(password, salt=None):

    if salt is None:
        salt = secrets.token_hex(16)

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        200000
    ).hex()

    return f"{salt}${hashed}"


def verify_password(password, stored):

    try:
        salt, old_hash = stored.split("$")

        return secrets.compare_digest(
            hash_password(password, salt).split("$")[1],
            old_hash
        )

    except Exception:
        return False


# ==================================================
# CREATE DATABASE AND TABLES
# ==================================================

def create_database():

    con = connect()

    # USERS TABLE
    con.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # STUDENT RECORDS TABLE
    con.execute("""
        CREATE TABLE IF NOT EXISTS student_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            attendance REAL,
            internal_marks REAL,
            assignment_score REAL,
            study_hours REAL,
            missed_assignments INTEGER,
            predicted_risk TEXT
        )
    """)

    # CHECK EXISTING COLUMNS
    columns = [
        row[1] for row in con.execute(
            "PRAGMA table_info(student_records)"
        ).fetchall()
    ]

    # ADD USER EMAIL COLUMN
    if "user_email" not in columns:

        con.execute("""
            ALTER TABLE student_records
            ADD COLUMN user_email TEXT
        """)

    # REFRESH COLUMN LIST
    columns = [
        row[1] for row in con.execute(
            "PRAGMA table_info(student_records)"
        ).fetchall()
    ]

    # ADD ASSESSMENT DATE COLUMN
    if "assessment_date" not in columns:

        con.execute("""
            ALTER TABLE student_records
            ADD COLUMN assessment_date TEXT
        """)

    # CREATE DEFAULT ADMIN ACCOUNT
    admin = con.execute(
        "SELECT id FROM users WHERE email = ?",
        ("admin@edushield.ai",)
    ).fetchone()

    if not admin:

        con.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (
            "EduShield Administrator",
            "admin@edushield.ai",
            hash_password("Admin@12345"),
            "admin"
        ))

    con.commit()
    con.close()


# ==================================================
# STUDENT REGISTRATION
# ==================================================

def register_user(name, email, password):

    con = connect()

    try:

        con.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, 'student')
        """, (
            name.strip(),
            email.strip().lower(),
            hash_password(password)
        ))

        con.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        con.close()


# ==================================================
# USER LOGIN
# ==================================================

def login_user(email, password):

    con = connect()

    user = con.execute("""
        SELECT id, name, email, password, role
        FROM users
        WHERE email = ?
    """, (
        email.strip().lower(),
    )).fetchone()

    con.close()

    if user and verify_password(password, user[3]):

        return {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "role": user[4]
        }

    return None


# ==================================================
# SAVE STUDENT ACADEMIC RECORDS
# ==================================================

def save_student_records(data, user_email=None):

    data = data.rename(columns={
        "Student_Name": "student_name",
        "Attendance": "attendance",
        "Internal_Marks": "internal_marks",
        "Assignment_Score": "assignment_score",
        "Study_Hours": "study_hours",
        "Missed_Assignments": "missed_assignments",
        "Predicted_Risk": "predicted_risk"
    })

    columns = [
        "student_name",
        "attendance",
        "internal_marks",
        "assignment_score",
        "study_hours",
        "missed_assignments",
        "predicted_risk"
    ]

    records = data[columns].copy()

    # ASSIGN RECORD TO STUDENT EMAIL
    records["user_email"] = (
        user_email.strip().lower()
        if user_email
        else None
    )

    # SAVE ASSESSMENT DATE AND TIME
    records["assessment_date"] = (
        pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    con = connect()

    try:

        records.to_sql(
            "student_records",
            con,
            if_exists="append",
            index=False
        )

        con.commit()

    finally:

        con.close()


# ==================================================
# GET STUDENT ACADEMIC RECORDS
# ==================================================

def get_student_records(user_email=None):

    con = connect()

    try:

        if user_email:

            data = pd.read_sql_query("""
                SELECT * FROM student_records
                WHERE user_email = ?
                ORDER BY id DESC
            """, con, params=(
                user_email.strip().lower(),
            ))

        else:

            data = pd.read_sql_query("""
                SELECT * FROM student_records
                ORDER BY id DESC
            """, con)

        return data

    finally:

        con.close()


# ==================================================
# INITIALIZE DATABASE
# ==================================================

create_database()
