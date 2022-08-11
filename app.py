import os
import env

from random import random
from datetime import datetime
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, flash, g
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


@app.route("/library")
def library():
    # Query database
    books = db.execute("SELECT * FROM book WHERE user_id = ?", session["user_id"])

    # Get columns' names
    if len(books) > 0:
        columns = books[0].keys()
        return render_template("library.html", content="_table.html", table_head=columns, table_data=books,
                               username=g.username)

    return render_template("library.html", content="_blank.html", username=g.username)


@app.route("/new-book", methods=['POST'])
def insert_book():
    # Ensure title was submitted
    if not request.form.get("title"):
        flash("Please enter the book's title.", "Error")
        return '', 204

    if request.form.get("series"):
        # Add series if not exist
        series_id = db.execute("SELECT id FROM series WHERE title = ? AND user_id = ?", request.form.get("series"),
                               session["user_id"])[0]["id"]
        if not series_id:
            series_id = db.execute("INSERT INTO series(title, user_id) VALUES(?, ?)", request.form.get("series"),
                                   session["user_id"])

        # Update series
        series_end = db.execute("SELECT end_vol FROM series WHERE id = ?", series_id)[0]["end_vol"]
        series_missing = db.execute("SELECT id, volume FROM series_missing WHERE series_id = ? ORDER BY volume",
                                    series_id)
        series_avail = db.execute("SELECT volume FROM book WHERE series_id = ? ORDER BY volume", series_id)

        # Update series status
        if request.form.get("volume") == series_end:
            db.execute("UPDATE series SET status = ? WHERE series_id = ?", "End", series_id)

        avail_vol = []
        missing_vol = []
        for row in series_missing:
            missing_vol.append(row["volume"])
        for row in series_avail:
            avail_vol.append(row["volume"])

        # Delete missing volume
        if request.form.get("volume") in missing_vol:
            db.execute("DELETE FROM series_missing WHERE id = ?", row["id"])

        # Update missing volumes, only if volume is an integer
        try:
            for i in range(1, int(request.form.get("volume"))):
                if i not in avail_vol:
                    db.execute("INSERT INTO series_missing(series_id, volume) VALUEs(?, ?)", series_id, i)
        except:
            pass

    # Add new book to database
    list_keys = [key for key in request.form.keys() if key[0:3] != "ac_" and key != "series"]
    keys = ','.join(f'"{key}"' for key in list_keys)
    values = ','.join(f'"{request.form.get(key)}"' for key in list_keys)
    book_id = db.execute(f"INSERT INTO book({keys}, series_id, user_id) VALUES({values})", series_id,
                         session["user_id"])

    # Add accessories to book
    list_ac_keys = [key for key in request.form.keys() if key[0:3] == "ac_"]
    ac_keys = ','.join(f'"{key}"' for key in list_ac_keys)
    ac_values = ','.join(f'"{request.form.get(key)}"' for key in list_ac_keys)
    db.execute(f"INSERT INTO book({ac_keys}, book_id) VALUES({ac_values})", book_id)

    return render_template("_insert.html")


# Login functions
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        # Forget any user_id
        session.clear()

        # Get input
        email = request.form.get("email")
        password = request.form.get("password")

        # Ensure email was submitted
        if not email:
            flash("Please enter your email.", "Error")
            return redirect("/")

        # Ensure password was submitted
        elif not password:
            flash("Please enter your password.", "Error")
            return redirect("/")

        # Query database for email
        user = db.execute("SELECT * FROM user WHERE email = ?", email)

        # Ensure email exists and password is correct
        if len(user) != 1 or not check_password_hash(user[0]["password"], password):
            flash("Invalid email and/or password", "Error")
            return redirect("/")

        # Remember which user has logged in
        g.username = email.partition("@")[0]
        session["user_id"] = user[0]["id"]

        # Redirect user to home page
        return redirect("/library")

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

        # Ensure email was submitted
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

        # Ensure email was not duplicated
        if len(check) > 0:
            flash("Email already exists.", "Error")
            return redirect("/")

        # Insert new user to database
        new_user = db.execute("INSERT INTO user (email, password, date) VALUES(?, ?)", email,
                              generate_password_hash(password), datetime.now())

        # Send email
        message = Message("You are registered to Your Home Library!", recipients=[email])
        mail.send(message)

        # Log in
        g.username = email.partition("@")[0]
        session["user_id"] = new_user

        return redirect("/library")

    else:
        return render_template("_register.html")


@app.route("/forgot", methods=['GET', 'POST'])
def forgot():
    if request.method == "POST":
        # Get input
        email = request.form.get("email")

        # Query database
        check = db.execute("SELECT email FROM user WHERE email = ?", email)

        # Ensure email was submitted
        if not email:
            flash("Please enter your email.", "Error")
            return redirect("/")

        # Ensure email was existed
        if len(check) == 0:
            flash("Invalid email.", "Error")
            return redirect("/")

        # Set reset code and email globally
        g.reset_code_created = str(random() * 1000000)[-6:]
        g.reset_email = email

        # Send email
        message = Message(
            "You are resetting password for your account at Your Home Library! Please enter the following code: "
            + str(g.reset_code_created),
            recipients=[g.reset_email])
        mail.send(message)

        return '', 204

    else:
        return render_template("_forgot.html")


@app.route("/reset-code", methods=['GET', 'POST'])
def reset_code():
    if request.method == "POST":
        # Get input
        code = request.form.get("code")

        # Ensure reset code was submitted correctly
        if not code or code != g.reset_code_created:
            flash("Wrong code.", "Error")
            return redirect("/")

        return '', 204

    else:
        return render_template("_reset_code.html")


@app.route("/reset-pass", methods=['GET', 'POST'])
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
        db.execute("UPDATE user SET password = ? WHERE email = ?", generate_password_hash(password), g.reset_email)

        # Send email
        message = Message(
            "Your password at Your Home Library has been changed! If it is not yours, reset your password by going to Log In and choosing Forgot Password",
            recipients=[g.reset_email])
        mail.send(message)

        # Release global variables
        g.reset_code_created = None
        g.reset_email = None

        return redirect("/")

    else:
        return render_template("_reset_pass.html")
