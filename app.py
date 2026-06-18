from flask import Flask, render_template, request, redirect, url_for, flash
import re
from database import get_db_connection, create_users_table

app = Flask(__name__)

# Secret key is required for flash messages to work securely.
app.secret_key = "change_this_secret_key"


def is_valid_email(email):
    """
    Uses a simple regular expression to check whether the email address
    follows a valid email format.
    """
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(email_pattern, email)


def validate_user_form(full_name, email, phone, bio):
    """
    Validates form input before saving it to the database.
    Returns an error message if validation fails, otherwise returns None.
    """

    # Checks that all required fields have been completed.
    if not full_name or not email or not phone or not bio:
        return "All fields are required."

    # Checks that the full name has a reasonable minimum length.
    if len(full_name) < 3:
        return "Full name must be at least 3 characters long."

    # Checks that the email address format is valid.
    if not is_valid_email(email):
        return "Please enter a valid email address."

    # Checks that the phone number contains only digits and is long enough.
    if not phone.isdigit() or len(phone) < 10:
        return "Phone number must contain at least 10 digits."

    return None


@app.route("/")
def home():
    """
    Redirects users from the home page to the registration page.
    """
    return redirect(url_for("register"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Displays the registration form and processes submitted user data.
    """

    if request.method == "POST":
        full_name = request.form.get("full_name").strip()
        email = request.form.get("email").strip()
        phone = request.form.get("phone").strip()
        bio = request.form.get("bio").strip()

        error = validate_user_form(full_name, email, phone, bio)

        if error:
            flash(error, "error")
            return render_template(
                "register.html",
                full_name=full_name,
                email=email,
                phone=phone,
                bio=bio
            )

        connection = get_db_connection()

        try:
            # Inserts the validated user data into the SQLite database.
            connection.execute(
                """
                INSERT INTO users (full_name, email, phone, bio)
                VALUES (?, ?, ?, ?)
                """,
                (full_name, email, phone, bio)
            )

            connection.commit()
            flash("User registered successfully.", "success")
            return redirect(url_for("users"))

        except Exception:
            flash("This email address is already registered.", "error")

        finally:
            connection.close()

    return render_template("register.html")


@app.route("/users")
def users():
    """
    Retrieves and displays all stored users dynamically from the database.
    """

    connection = get_db_connection()

    # Fetches all users from the database so they can be shown on the page.
    users_list = connection.execute(
        "SELECT * FROM users ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return render_template("users.html", users=users_list)


@app.route("/profile/<int:user_id>")
def profile(user_id):
    """
    Displays the full profile information for a selected user.
    """

    connection = get_db_connection()

    user = connection.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    connection.close()

    if user is None:
        flash("User not found.", "error")
        return redirect(url_for("users"))

    return render_template("profile.html", user=user)


@app.route("/update/<int:user_id>", methods=["GET", "POST"])
def update(user_id):
    """
    Preloads existing user data into an update form and saves edited details.
    """

    connection = get_db_connection()

    user = connection.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    if user is None:
        connection.close()
        flash("User not found.", "error")
        return redirect(url_for("users"))

    if request.method == "POST":
        full_name = request.form.get("full_name").strip()
        email = request.form.get("email").strip()
        phone = request.form.get("phone").strip()
        bio = request.form.get("bio").strip()

        error = validate_user_form(full_name, email, phone, bio)

        if error:
            flash(error, "error")
            return render_template(
                "update.html",
                user=user,
                full_name=full_name,
                email=email,
                phone=phone,
                bio=bio
            )

        try:
            # Updates the selected user's record using their unique user ID.
            connection.execute(
                """
                UPDATE users
                SET full_name = ?, email = ?, phone = ?, bio = ?
                WHERE id = ?
                """,
                (full_name, email, phone, bio, user_id)
            )

            connection.commit()
            flash("User profile updated successfully.", "success")
            return redirect(url_for("profile", user_id=user_id))

        except Exception:
            flash("This email address is already used by another user.", "error")

        finally:
            connection.close()

    connection.close()

    return render_template("update.html", user=user)


if __name__ == "__main__":
    # Creates the users table before the Flask application starts.
    create_users_table()
    app.run(debug=True)