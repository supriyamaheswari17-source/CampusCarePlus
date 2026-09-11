import os

from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


# Create Flask application
app = Flask(__name__)

CORS(app)


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_db_connection():

    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "campuscare"),
        port=int(os.getenv("DB_PORT", "3306"))
    )


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route("/")
def home():

    return jsonify({
        "message": "CampusCarePlus Backend is running successfully! 🚀"
    })


# --------------------------------------------------
# STUDENT LOGIN
# --------------------------------------------------

@app.route("/student-login", methods=["POST"])
def student_login():

    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")


    if not email or not password:

        return jsonify({
            "message": "Email and password are required."
        }), 400


    try:

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)


        cursor.execute(
            """
            SELECT *
            FROM students
            WHERE email = %s AND password = %s
            """,
            (email, password)
        )


        student = cursor.fetchone()


        cursor.close()
        db.close()


        if student:

            return jsonify({
                "message": "Login successful! 🎉"
            })


        return jsonify({
            "message": "Invalid email or password."
        }), 401


    except Exception as error:

        print("STUDENT LOGIN ERROR:", error)

        return jsonify({
            "message": "Unable to connect to database."
        }), 500


# --------------------------------------------------
# ADMIN LOGIN
# --------------------------------------------------

@app.route("/admin-login", methods=["POST"])
def admin_login():

    data = request.get_json() or {}

    username = data.get("username")
    password = data.get("password")


    if not username or not password:

        return jsonify({
            "message": "Username and password are required."
        }), 400


    try:

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)


        cursor.execute(
            """
            SELECT *
            FROM admin
            WHERE username = %s AND password = %s
            """,
            (username, password)
        )


        admin = cursor.fetchone()


        cursor.close()
        db.close()


        if admin:

            return jsonify({
                "message": "Admin login successful! 🎉"
            })


        return jsonify({
            "message": "Invalid username or password."
        }), 401


    except Exception as error:

        print("ADMIN LOGIN ERROR:", error)

        return jsonify({
            "message": "Unable to connect to database."
        }), 500


# --------------------------------------------------
# STUDENT REGISTRATION
# --------------------------------------------------

@app.route("/register", methods=["POST"])
def register():

    data = request.get_json() or {}


    name = data.get("name")
    roll_number = data.get("roll_number")
    department = data.get("department")
    email = data.get("email")
    password = data.get("password")


    if not all([
        name,
        roll_number,
        department,
        email,
        password
    ]):

        return jsonify({
            "message": "All fields are required."
        }), 400


    try:

        db = get_db_connection()
        cursor = db.cursor()


        # Check whether email already exists
        cursor.execute(
            "SELECT id FROM students WHERE email = %s",
            (email,)
        )


        existing_student = cursor.fetchone()


        if existing_student:

            cursor.close()
            db.close()

            return jsonify({
                "message": "A student with this email already exists."
            }), 409


        # Check whether roll number already exists
        cursor.execute(
            "SELECT id FROM students WHERE roll_number = %s",
            (roll_number,)
        )


        existing_roll = cursor.fetchone()


        if existing_roll:

            cursor.close()
            db.close()

            return jsonify({
                "message": "This roll number is already registered."
            }), 409


        cursor.execute(
            """
            INSERT INTO students
            (name, roll_number, department, email, password)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                name,
                roll_number,
                department,
                email,
                password
            )
        )


        db.commit()


        cursor.close()
        db.close()


        return jsonify({
            "message": "Student registered successfully! 🎉"
        }), 201


    except Exception as error:

        print("REGISTRATION ERROR:", error)

        return jsonify({
            "message": "Unable to register student."
        }), 500


# --------------------------------------------------
# SUBMIT COMPLAINT
# --------------------------------------------------

@app.route("/submit-complaint", methods=["POST"])
def submit_complaint():

    data = request.get_json() or {}


    student_email = data.get("student_email")
    title = data.get("title")
    category = data.get("category")
    location = data.get("location")
    description = data.get("description")


    if not all([
        student_email,
        title,
        category,
        location,
        description
    ]):

        return jsonify({
            "message": "All complaint fields are required."
        }), 400


    try:

        db = get_db_connection()
        cursor = db.cursor()


        cursor.execute(
            """
            INSERT INTO complaints
            (
                student_email,
                title,
                category,
                location,
                description
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                student_email,
                title,
                category,
                location,
                description
            )
        )


        db.commit()


        complaint_id = cursor.lastrowid


        cursor.close()
        db.close()


        return jsonify({
            "message": "Complaint submitted successfully! 🎉",
            "complaint_id": complaint_id
        }), 201


    except Exception as error:

        print("COMPLAINT ERROR:", error)

        return jsonify({
            "message": "Unable to submit complaint."
        }), 500


# --------------------------------------------------
# GET ALL COMPLAINTS
# --------------------------------------------------

@app.route("/complaints", methods=["GET"])
def get_complaints():

    try:

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)


        cursor.execute(
            """
            SELECT *
            FROM complaints
            ORDER BY created_at DESC
            """
        )


        complaints = cursor.fetchall()


        cursor.close()
        db.close()


        return jsonify(complaints)


    except Exception as error:

        print("GET COMPLAINTS ERROR:", error)

        return jsonify({
            "message": "Unable to load complaints."
        }), 500


# --------------------------------------------------
# UPDATE COMPLAINT STATUS
# --------------------------------------------------

@app.route("/update-status/<int:complaint_id>", methods=["PUT"])
def update_status(complaint_id):

    data = request.get_json() or {}

    status = data.get("status")


    allowed_statuses = [
        "Pending",
        "In Progress",
        "Resolved"
    ]


    if status not in allowed_statuses:

        return jsonify({
            "message": "Invalid complaint status."
        }), 400


    try:

        db = get_db_connection()
        cursor = db.cursor()


        cursor.execute(
            """
            UPDATE complaints
            SET status = %s
            WHERE id = %s
            """,
            (status, complaint_id)
        )


        db.commit()


        if cursor.rowcount == 0:

            cursor.close()
            db.close()

            return jsonify({
                "message": "Complaint not found."
            }), 404


        cursor.close()
        db.close()


        return jsonify({
            "message": "Complaint status updated successfully! ✅"
        })


    except Exception as error:

        print("UPDATE STATUS ERROR:", error)

        return jsonify({
            "message": "Unable to update complaint status."
        }), 500


# --------------------------------------------------
# GET STUDENT COMPLAINTS
# --------------------------------------------------

@app.route("/student-complaints/<email>", methods=["GET"])
def student_complaints(email):

    try:

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)


        cursor.execute(
            """
            SELECT
                id,
                title,
                category,
                location,
                description,
                status,
                created_at
            FROM complaints
            WHERE student_email = %s
            ORDER BY created_at DESC
            """,
            (email,)
        )


        complaints = cursor.fetchall()


        cursor.close()
        db.close()


        return jsonify(complaints)


    except Exception as error:

        print("STUDENT COMPLAINT ERROR:", error)

        return jsonify({
            "message": "Unable to load student complaints."
        }), 500


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=True
    )
