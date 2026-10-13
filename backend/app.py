from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os


app = Flask(__name__)

# Allow React frontend to access Flask API
CORS(app)


def has_mutation(name):
    """Return whether an evaluation-only defect is enabled."""
    # Preserve the original MVP's seeded username-length defect when no
    # evaluation override is provided. Set AI_TEST_MUTATIONS="" to disable it.
    enabled = os.getenv("AI_TEST_MUTATIONS")
    if enabled is None:
        return name == "missing_username_min_length"
    return name in {item.strip() for item in enabled.split(",") if item.strip()}


def database_path():
    return os.getenv("AI_TEST_DB", "users.db")


# Initialize Database


def init_db():
    conn = sqlite3.connect(database_path())
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
    if not has_mutation("missing_password_min_length") and len(password) < 6:
        return jsonify({
            "message": "Password length must be at least 6 characters"
        }), 400



    # The default demo intentionally keeps this defect for the MVP.
    # Evaluation can also toggle it explicitly with AI_TEST_MUTATIONS.
    if not has_mutation("missing_username_min_length") and len(username) < 6:
        return jsonify({
            "message": "Username length must be at least 6 characters"
        }), 400

    try:

        conn = sqlite3.connect(database_path())
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

        if has_mutation("duplicate_username_allowed"):
            return jsonify({
                "message": "Registration_successful"
            }), 200

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



    conn = sqlite3.connect(database_path())
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


    if has_mutation("invalid_password_accepted") and username:
        return jsonify({
            "message": "Login successful"
        }), 200

    if has_mutation("nonexistent_user_accepted") and not user:
        return jsonify({
            "message": "Login successful"
        }), 200

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

    app.run(
        debug=os.getenv("FLASK_DEBUG", "1") == "1",
        port=int(os.getenv("PORT", "5000")),
    )
