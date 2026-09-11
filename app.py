import os
from flask import Flask, request, jsonify,send_from_directory
from flask_cors import CORS
import mysql.connector
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)
# MySQL connection
import os

db = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME", "railway"),
    port=int(os.getenv("DB_PORT", "53935"))
)

@app.route("/")
def home():
    return send_from_directory("campus.html")
@app.route("/student-login-page")
def student_login_page():
    return send_from_directory("student-login.html")
@app.route("/student-login", methods=["POST"])
def student_login():
    data = request.get_json()

    email = data.get("email")
    password=data.get("password")

    cursor = db.cursor(dictionary=True)

    query = "SELECT * FROM students WHERE email = %s and password=%s"
    cursor.execute(query, (email,password))

    student = cursor.fetchone()

    cursor.close()

    if student:
        return jsonify({"message": "Login successful! 🎉"})
    else:
        return jsonify({"message": "Invalid email or password"}), 401
@app.route("/admin-login", methods=["POST"])
def admin_login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM admin WHERE username = %s AND password = %s",
        (username, password)
    )

    admin = cursor.fetchone()
    cursor.close()

    if admin:
        return jsonify({"message": "Admin login successful! 🎉"})
    else:
        return jsonify({"message": "Invalid username or password."}), 401
@app.route("/student-register")
def student_register_page():
    return send_from_directory(".", "student-register.html")
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    print("REGISTER DATA:", data)

    name = data.get("name")
    roll_number = data.get("roll_number")
    department = data.get("department")
    email = data.get("email")
    password = data.get("password")

    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO students (name, roll_number, department, email, password) VALUES (%s, %s, %s, %s, %s)",
        (name, roll_number, department, email, password)
    )

    db.commit()
    cursor.close()

    return jsonify({"message": "Student registered successfully!"})
@app.route("/submit-complaint", methods=["POST"])
def submit_complaint():
    data = request.get_json()

    student_email = data.get("student_email")
    title = data.get("title")
    category = data.get("category")
    description = data.get("description")

    cursor = db.cursor()

    cursor.execute(
        """INSERT INTO complaints
        (student_email, title, category, description)
        VALUES (%s, %s, %s, %s)""",
        (student_email, title, category, description)
    )

    db.commit()
    cursor.close()

    return jsonify({"message": "Complaint submitted successfully! 🎉"})
@app.route("/complaint")
def complaint_page():
    return send_from_directory("..","complaint.html")
@app.route("/admin")
def admin_page():
    return send_from_directory("..", "admin-login.html")
@app.route("/admin-dashboard")
def admin_dashboard():
    return send_from_directory("..", "admin-dashboard.html")


@app.route("/complaints", methods=["GET"])
def get_complaints():
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM complaints ORDER BY created_at DESC")

    complaints = cursor.fetchall()

    cursor.close()

    return jsonify(complaints) 
@app.route("/update-status/<int:complaint_id>", methods=["PUT"])
def update_status(complaint_id):
    data = request.get_json()

    status = data.get("status")

    cursor = db.cursor()

    cursor.execute(
        "UPDATE complaints SET status = %s WHERE id = %s",
        (status, complaint_id)
    )

    db.commit()
    cursor.close()

    return jsonify({"message": "Complaint status updated successfully!"}) 
@app.route("/campus.css")
def campus_css():
    return send_from_directory("..", "campus.css")

@app.route("/student-status")
def student_status():
    return send_from_directory("..", "student-status.html")


@app.route("/student-complaints/<email>")
def student_complaints(email):
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, title, category, description, status, created_at "
        "FROM complaints WHERE student_email = %s "
        "ORDER BY created_at DESC",
        (email,)
    )

    complaints = cursor.fetchall()

    cursor.close()

    return jsonify(complaints)
if __name__=="__main__":
    app.run(debug=True)