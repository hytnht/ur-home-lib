import csv
import env
import os

from datetime import datetime
from random import random
from flask import Flask, redirect, render_template, request, session, flash, g, json, url_for
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from helpers import *

app = Flask(__name__)

# Set env variables
env.setVar()

# Configure
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["MAIL_USERNAME"] = os.environ["MAIL_USERNAME"]
app.config["MAIL_PASSWORD"] = os.environ["MAIL_PASSWORD"]
app.config["MAIL_DEFAULT_SENDER"] = os.environ["MAIL_DEFAULT_SENDER"]
app.config["MAIL_PORT"] = 587
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_USE_TLS"] = True
app.config['UPLOAD_FOLDER'] = "./static/upload"
mail = Mail(app)
Session(app)


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


# <editor-fold desc="Display functions">
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/library")
def library():
    # Query database
    books = db.execute("SELECT * FROM book WHERE user_id = ?", session["user_id"])

    # If database was not blank
    if len(books) > 0:
        columns = [key for key in books[0].keys() if "id" not in key]
        return render_template("library.html", content="_table.html", table_head=columns, table_data=books,
                               series=query_title("series"), books=query_title("book"), delete="book",
                               username=session["username"])

    return render_template("library.html", content="_blank.html", username=session["username"])


@app.route("/series")
def series():
    # Query database
    series = db.execute("SELECT * FROM series WHERE user_id = ?", session["user_id"])

    # If database was not blank
    if len(series) > 0:
        columns = [key for key in series[0].keys() if "id" not in key]
        return render_template("series.html", content="_table.html", table_head=columns, table_data=series,
                               series=query_title("series"), books=query_title("book"), delete="series",
                               username=session["username"])

    return render_template("series.html", content="_blank.html", username=session["username"])


@app.route("/accessory")
def accessory():
    # Query database
    accessories = db.execute(
        "SELECT accessory.*, book.title FROM book "
        "JOIN accessory ON book.id = accessory.book_id WHERE book.user_id = ?",
        session["user_id"])

    # If database was not blank
    if len(accessories) > 0:
        columns = [key for key in accessories[0].keys() if "id" not in key]
        return render_template("accessory.html", content="_table.html", table_head=columns, table_data=accessories,
                               series=query_title("series"), books=query_title("book"), delete="accessory",
                               username=session["username"])

    return render_template("accessory.html", content="_blank.html", username=session["username"])


@app.route("/log")
def log():
    # Query database
    log = db.execute("SELECT log.*, book.title FROM log JOIN book ON log.book_id = book.id WHERE user_id = ?",
                     session["user_id"])

    # If database was not blank
    if len(log) > 0:
        columns = [key for key in log[0].keys() if "id" not in key]
        return render_template("log.html", content="_table.html", table_head=columns, table_data=log,
                               series=query_title("series"), books=query_title("book"), delete="log",
                               username=session["username"])

    return render_template("log.html", content="_blank.html", username=session["username"])


@app.route("/calendar")
def calendar():
    calendar = db.execute("SELECT rc.*, series.title FROM release_calendar rc "
                          "JOIN series ON rc.series_id = series.id WHERE series.user_id = ?", session["user_id"])
    print(json.dumps(calendar))
    if request.args.get("display") == "calendar":
        return render_template("calendar.html", content="_calendar.html", mode="calendar", data=json.dumps(calendar),
                               username=session["username"])
    else:
        if len(calendar) > 0:
            columns = [key for key in calendar[0].keys() if "id" not in key]
            return render_template("calendar.html", content="_table.html", mode="table",
                                   table_head=columns, table_data=calendar,
                                   series=query_title("series"), books=query_title("book"), delete="calendar",
                                   username=session["username"])
        return render_template("calendar.html", content="_blank.html", mode="table", username=session["username"])


@app.route("/mass-upload")
def mass_upload():
    return render_template("mass_upload.html")


# </editor-fold>

# <editor-fold desc="Insert functions">
@app.route("/new-book", methods=['POST'])
def new_book():
    # Ensure title was submitted
    if not request.form.get("title"):
        flash("Please enter the book's title.", "Error")
        return '', 204

    # Ensure volume was an integer
    if request.form.get("volume") != "" and not request.form.get("volume").isdigit():
        flash("Volume can only be an integer or blank.", "Error")
        return '', 204

    insert_book(request.form.to_dict())

    flash("Book inserted.", "Success")
    return redirect("/library")


@app.route("/new-series", methods=['POST'])
def new_series():
    # Ensure title was submitted
    if not request.form.get("title"):
        flash("Please enter the series' title.", "Error")
        return '', 204

    # Ensure title was not duplicate:
    if check_series(request.form.get("title"), add=False):
        flash("This series' title was existed.", "Error")

    insert_series(request.form.to_dict())

    flash("Series inserted.", "Success")
    return redirect("/series")


@app.route("/new-calendar", methods=['POST'])
def new_calendar():
    # Ensure series title was submitted
    if not request.form.get("series"):
        flash("Please enter the series' title.", "Error")
        return '', 204

    # Ensure date was submitted
    if not request.form.get("date"):
        flash("Please enter the date", "Error")
        return '', 204

    insert_calendar(request.form.to_dict())

    flash("Release date inserted.", "Success")
    return redirect("/calendar")


# @app.route("/new-column", methods=['GET', 'POST'])
# def new_column():

# </editor-fold>

# <editor-fold desc="Delete functions">
@app.route("/delete-book", methods=['POST'])
def delete_book():
    for id in request.form.keys():
        # Retrieve book information
        series_id = db.execute("SELECT series_id FROM book WHERE id = ?", id)
        if not series_id:
            pass
        else:
            series_id = series_id[0]["series_id"]

        volume = db.execute("SELECT volume FROM book WHERE id = ?", id)
        if not volume:
            pass
        else:
            volume = volume[0]["volume"]

        next_current = 0

        # Update series current
        if volume == series_current(series_id):
            avail_vol = series_avail(series_id)
            if len(avail_vol) > 2:
                next_current = avail_vol[-2]
            db.execute("UPDATE series SET current = ? WHERE id = ?", next_current, series_id)

        # Delete missing volume
        for row in series_missing(series_id):
            if next_current < row["volume"] < int(volume):
                db.execute("DELETE FROM series_missing WHERE id = ?", row["id"])

    ids = ','.join(f'"{key}"' for key in request.form.keys())

    # Delete from accessory table
    db.execute(f"DELETE FROM accessory WHERE book_id IN ({ids})")

    # Delete from book table
    db.execute(f"DELETE FROM book WHERE id IN ({ids})")

    flash("Book deleted. Series updated.", "Success")
    return redirect("/library")


@app.route("/delete-series", methods=['POST'])
def delete_series():
    ids = ','.join(f'"{key}"' for key in request.form.keys())

    # Update book table
    db.execute(f"UPDATE book SET series_id = ? WHERE series_id IN ({ids})", None)

    # Delete release date
    db.execute(f"DELETE FROM release_calendar WHERE series_id IN ({ids})")

    # Delete from series table
    db.execute(f"DELETE FROM series WHERE id IN ({ids})")

    flash("Series deleted. Books in series updated.", "Success")
    return redirect("/series")


@app.route("/delete-accessory", methods=['POST'])
def delete_accessory():
    ids = ','.join(f'"{key}"' for key in request.form.keys())

    # Delete from accessory table
    db.execute(f"DELETE FROM accessory WHERE id IN ({ids})")

    flash("Accessory deleted.", "Success")
    return redirect("/accessory")


@app.route("/delete-calendar", methods=['POST'])
def delete_calendar():
    ids = ','.join(f'"{key}"' for key in request.form.keys())

    # Delete from release calendar table
    db.execute(f"DELETE FROM release_calendar WHERE id IN ({ids})")

    flash("Release date deleted.", "Success")
    return redirect("/calendar")


# </editor-fold>

# <editor-fold desc="Login functions">
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
        session["user_id"] = user[0]["id"]
        session["username"] = email.partition("@")[0]

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
        session["user_id"] = new_user
        session["username"] = email.partition("@")[0]

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


# </editor-fold>

# <editor-fold desc="Mass upload functions">
@app.route("/upload-book", methods=['POST'])
def upload_book():
    data = upload_file(request.files)
    for dict in data:
        insert_book(dict)

    flash("File uploaded.", "Success")
    return redirect("/mass-upload")


@app.route("/upload-series", methods=['POST'])
def upload_series():
    data = upload_file(request.files)
    for dict in data:
        insert_series(dict)

    flash("File uploaded.", "Success")
    return redirect("/mass-upload")


@app.route("/upload-calendar", methods=['POST'])
def upload_calendar():
    data = upload_file(request.files)
    for dict in data:
        insert_calendar(dict)

    flash("File uploaded.", "Success")
    return redirect("/mass-upload")

# </editor-fold>
