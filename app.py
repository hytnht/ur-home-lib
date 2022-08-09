import os
import env
from random import random
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, flash
from flask_mail import Mail, Message
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

env.setVar()

# Configure session to use filesystem (instead of signed cookies)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["MAIL_USERNAME"] = os.environ["MAIL_USERNAME"]
app.config["MAIL_PASSWORD"] = os.environ["MAIL_PASSWORD"]
app.config["MAIL_DEFAULT_SENDER"] = os.environ["MAIL_DEFAULT_SENDER"]
app.config["MAIL_PORT"] = 587
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_USE_TLS"] = True
mail = Mail(app)
Session(app)

# Connect database
db = SQL("sqlite:///database.db")


# # Make sure API key is set
# if not os.environ.get("API_KEY"):
#     raise RuntimeError("API_KEY not set")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/home")
def home():
    return render_template("homepage.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        # Forget any user_id
        session.clear()

        # Get input
        email = request.form.get("email")
        password = request.form.get("password")

        # Ensure username was submitted
        if not email:
            flash("Please enter your email.", "Error")
            return redirect("/")

        # Ensure password was submitted
        elif not password:
            flash("Please enter your password.", "Error")
            return redirect("/")

        # Query database for email
        user = db.execute("SELECT * FROM user WHERE email = ?", email)

        # Ensure username exists and password is correct
        if len(user) != 1 or not check_password_hash(user[0]["password"], password):
            flash("Invalid username and/or password", "Error")
            return redirect("/")

        # Remember which user has logged in
        session["user_id"] = user[0]["id"]

        # Redirect user to home page
        return redirect("/home")

    else:
        return render_template("_login.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        # Get input
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        # Query database
        check = db.execute("SELECT * FROM user WHERE email = ?", email)

        # Ensure username was submitted
        if not email:
            flash("Please enter your email.", "Error")
            return redirect("/")

        # Ensure password was submitted
        elif not password:
            flash("Please enter your password.", "Error")
            return redirect("/")

        # Ensure confirm password was submitted
        elif not confirm:
            flash("Please re-enter your password for confirmation.", "Error")
            return redirect("/")

        # Ensure password was confirmed
        elif password != confirm:
            flash("Two passwords are not the same.", "Error")
            return redirect("/")

        # Ensure username was not duplicated
        if len(check) != 0:
            flash("Email already exists.", "Error")
            return redirect("/")

        # Insert new user to database
        new_user = db.execute("INSERT INTO user (email, password) VALUES(?, ?)", email,
                              generate_password_hash(password))

        # Send email
        message = Message("You are registered to Your Home Library!", recipients=[email])
        mail.send(message)

        # Log in
        session["user_id"] = new_user

        return redirect("/home")

    else:
        return render_template("_register.html")


@app.route("/forgot", methods=['GET', 'POST'])
def forgot():
    if request.method == "POST":
        # Get input
        global reset_email
        reset_email = request.form.get("email")

        # Query database
        check = db.execute("SELECT email FROM user WHERE email = ?", reset_email)

        # Ensure username was submitted
        if not reset_email:
            flash("Please enter your email.", "Error")
            return redirect("/")

        # Ensure username was existed
        if len(check) == 0:
            flash("Invalid email.", "Error")
            return redirect("/")

        # Set reset code
        global reset_code_created
        reset_code_created = int(random() * 1000000)

        # Send email
        message = Message(
            "You are resetting password for your account at Your Home Library! Please enter the following code: " + reset_code,
            recipients=[reset_email])
        mail.send(message)

        return redirect("/reset-code")

    else:
        return render_template("_forgot.html")


@app.route("/reset-code")
def reset_code():
    if request.method == "POST":
        # Get input
        reset_code = request.form.get("reset-code")

        # Ensure reset code was submitted correctly
        if not reset_code or reset_code != reset_code_created:
            flash("Wrong code.", "Error")
            return redirect("/")

        return redirect("/reset-pass")

    else:
        return render_template("_reset_code.html")


@app.route("/reset-pass")
def reset_pass():
    if request.method == "POST":
        # Get input
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        # Ensure password was submitted
        if not password:
            flash("Please enter your password.", "Error")
            return redirect("/")

        # Ensure confirm password was submitted
        elif not confirm:
            flash("Please re-enter your password for confirmation.", "Error")
            return redirect("/")

        # Ensure password was confirmed
        elif password != confirm:
            flash("Two passwords are not the same.", "Error")
            return redirect("/")

        # Change database
        db.execute("UPDATE user SET password = ? WHERE email = ?", generate_password_hash(password), reset_email)

        # Send email
        message = Message(
            "Your password at Your Home Library has been changed! If it is not yours, reset your password by going to Log In and choosing Forgot Password",
            recipients=[reset_email])
        mail.send(message)

        return redirect("/")

    else:
        return render_template("_reset_pass.html")
