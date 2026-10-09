from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3


app = Flask(__name__)

# Allow React frontend to access Flask API
CORS(app)


# Initialize Database


def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()



# Register API


@app.route("/api/register", methods=["POST"])
def register():

    # Get JSON data from request body
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")


    # Check username
    if not username:
        return jsonify({
            "message": "Username is required"
        }), 400


    # Check password
    if not password:
        return jsonify({
            "message": "Password is required"
        }), 400


    # Check password length
    if len(password) < 6:
        return jsonify({
            "message": "Password length must be at least 6 characters"
        }), 400


  
    # Intentional Bug:
    # Missing username length validation
    
    # Requirement:
    # Username length >= 6
    
    # Current implementation:
    # No username length check


    try:

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO users(username, password)
            VALUES (?, ?)
            """,
            (username, password)
        )

        conn.commit()
        conn.close()


        return jsonify({
            "message": "Registration_successful"
        }), 200


    except sqlite3.IntegrityError:

        return jsonify({
            "message": "Username already exists"
        }), 400




# Login API

@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")


    if not username:
        return jsonify({
            "message": "Username is required"
        }), 400


    if not password:
        return jsonify({
            "message": "Password is required"
        }), 400



    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT * FROM users
        WHERE username=? AND password=?
        """,
        (username, password)
    )


    user = cursor.fetchone()

    conn.close()


    if user:

        return jsonify({
            "message": "Login successful"
        }), 200


    else:

        return jsonify({
            "message": "Invalid username or password"
        }), 400


# Run Application


if __name__ == "__main__":

    init_db()

    app.run(debug=True)


# 启动 Flask

if __name__ == "__main__":

    init_db()

    app.run(debug=True)