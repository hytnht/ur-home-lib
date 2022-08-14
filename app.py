import env
import os

from datetime import datetime
from random import random
from flask import Flask, redirect, render_template, request, session, flash, g, json, url_for
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
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
mail = Mail(app)
Session(app)


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
@login_required
def library():
    # Query database
    books = db.execute("SELECT * FROM book WHERE user_id = ?", session["user_id"])

    # If database was not blank
    if len(books) > 0:
        columns = [key for key in books[0].keys() if "id" not in key]
        return render_template("layout.html", title="Library", content="_table.html",
                               table_head=columns, table_data=books,
                               series=query_title("series"), books=query_title("book"),
                               custom=custom_column("book"), sr_custom=custom_column("series"),
                               pb_custom=custom_column("release_calendar"), lg_custom=custom_column("log"),
                               delete="book",
                               username=session["username"])

    return render_template("layout.html", title="Library", content="_blank.html", username=session["username"])


@app.route("/series")
@login_required
def series():
    # Query database
    series = db.execute("SELECT * FROM series WHERE user_id = ?", session["user_id"])

    # If database was not blank
    if len(series) > 0:
        columns = [key for key in series[0].keys() if "id" not in key]
        return render_template("layout.html", title="Series", content="_table.html",
                               table_head=columns, table_data=series,
                               series=query_title("series"), books=query_title("book"),
                               custom=custom_column("book"), sr_custom=custom_column("series"),
                               pb_custom=custom_column("release_calendar"), lg_custom=custom_column("log"),
                               delete="series",
                               username=session["username"])

    return render_template("layout.html", title="Series", content="_blank.html", username=session["username"])


@app.route("/accessory")
@login_required
def accessory():
    # Query database
    accessories = db.execute(
        "SELECT accessory.*, book.title FROM book "
        "JOIN accessory ON book.id = accessory.book_id WHERE book.user_id = ?",
        session["user_id"])

    # If database was not blank
    if len(accessories) > 0:
        columns = [key for key in accessories[0].keys() if "id" not in key]
        return render_template("layout.html", title="Accessories", content="_table.html",
                               table_head=columns, table_data=accessories,
                               series=query_title("series"), books=query_title("book"),
                               custom=custom_column("book"), sr_custom=custom_column("series"),
                               pb_custom=custom_column("release_calendar"), lg_custom=custom_column("log"),
                               delete="accessory",
                               username=session["username"])

    return render_template("layout.html", title="Accessories", content="_blank.html", username=session["username"])


@app.route("/log")
@login_required
def log():
    # Query database
    log = db.execute("SELECT log.*, book.title FROM log JOIN book ON log.book_id = book.id WHERE user_id = ?",
                     session["user_id"])

    # If database was not blank
    if len(log) > 0:
        columns = [key for key in log[0].keys() if "id" not in key]
        return render_template("layout.html", title="Library", content="_table.html",
                               table_head=columns, table_data=log,
                               series=query_title("series"), books=query_title("book"),
                               custom=custom_column("book"), sr_custom=custom_column("series"),
                               pb_custom=custom_column("release_calendar"), lg_custom=custom_column("log"),
                               delete="log",
                               username=session["username"])

    return render_template("layout.html", title="Library", content="_blank.html", username=session["username"])


@app.route("/calendar")
@login_required
def calendar():
    calendar = db.execute("SELECT rc.*, series.title FROM release_calendar rc "
                          "JOIN series ON rc.series_id = series.id WHERE series.user_id = ?", session["user_id"])
    if request.args.get("display") == "calendar":
        return render_template("calendar.html", content="_calendar.html", mode="calendar", data=json.dumps(calendar),
                               username=session["username"])
    else:
        if len(calendar) > 0:
            columns = [key for key in calendar[0].keys() if "id" not in key]
            return render_template("calendar.html", content="_table.html", mode="table",
                                   table_head=columns, table_data=calendar,
                                   custom=custom_column("book"), sr_custom=custom_column("series"),
                                   pb_custom=custom_column("release_calendar"), lg_custom=custom_column("log"),
                                   series=query_title("series"), books=query_title("book"),
                                   delete="calendar",
                                   username=session["username"])
        return render_template("calendar.html", content="_blank.html", mode="table", username=session["username"])


# </editor-fold>

# <editor-fold desc="Insert functions">
@app.route("/new-book", methods=['POST'])
@login_required
def new_book():
    # Ensure title was submitted
    if not request.form.get("title"):
        flash("Please enter the book's title.", "Error")
        return redirect("/library")

    # Ensure volume was an integer
    if request.form.get("volume") != "" and not request.form.get("volume").isdigit():
        flash("Volume can only be an integer or blank.", "Error")
        return redirect("/library")

    insert_book(request.form.to_dict())

    flash("Book inserted.", "Success")
    return redirect("/library")


@app.route("/new-series", methods=['POST'])
@login_required
def new_series():
    # Ensure title was submitted
    if not request.form.get("title"):
        flash("Please enter the series' title.", "Error")
        return redirect("/series")

    # Ensure title was not duplicate:
    if check_exist("series", request.form.get("title"), add=False):
        flash("This series' title was existed.", "Error")

    insert_series(request.form.to_dict())

    flash("Series inserted.", "Success")
    return redirect("/series")


@app.route("/new-calendar", methods=['POST'])
@login_required
def new_calendar():
    # Ensure series title was submitted
    if not request.form.get("series"):
        flash("Please enter the series' title.", "Error")
        return redirect("/calendar")

    # Ensure date was submitted
    if not request.form.get("date"):
        flash("Please enter the date", "Error")
        return redirect("/calendar")

    insert_calendar(request.form.to_dict())

    flash("Release date inserted.", "Success")
    return redirect("/calendar")


@app.route("/new-log", methods=['POST'])
@login_required
def new_log():
    # Ensure date title was submitted
    if not request.form.get("date"):
        flash("Please enter the date.", "Error")
        return redirect("/log")

    # Ensure activity was submitted
    if not request.form.get("activities"):
        flash("Please enter the activity", "Error")
        return redirect("/log")

    # Ensure book title was submitted
    if not request.form.get("title"):
        flash("Please enter the book title", "Error")
        return redirect("/log")

    book_id = check_exist("book", request.form.get("title"), add="True")

    list_keys = [key for key in request.form.keys() if
                 "id" not in key and key != "title" and request.form.get(key) != ""]
    keys = ','.join(f'"{key}"' for key in list_keys)
    values = ','.join(f'"{request.form.get(key)}"' for key in list_keys)
    db.execute(f"INSERT INTO log({keys}, book_id) VALUES({values}, ?)", book_id)

    flash("Log updated.", "Success")
    return redirect("/log")


@app.route("/new-column", methods=['POST'])
@login_required
def new_column():
    table = request.form.get("table")
    if not table or table not in ["accessory", "book", "log", "release_calendar", "series"]:
        flash("Wrong table.", "Error")
        return redirect("/library")

    type = request.form.get("type")
    if not type or type not in ["text", "number", "date"]:
        flash("Wrong type.", "Error")
        return redirect("/library")
    if type == "number":
        type = "REAL"

    name = "uc_" + secure_filename(request.form.get("name")).replace(".", "_").strip().lower()
    db.execute("ALTER TABLE ? ADD ? ?", table, name, type)
    db.execute("INSERT INTO user_custom(name, table_name, user_id) VALUES(?,?,?)", name, table, session["user_id"])

    flash("New column added.", "Success")
    return redirect("/library")


# </editor-fold>

# <editor-fold desc="Delete functions">
@app.route("/delete-book", methods=['POST'])
@login_required
def delete_book():
    if not request.form.keys() or len(request.form.keys()) == 0:
        flash("No item was selected.", "Error")
        return redirect("/library")

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
@login_required
def delete_series():
    if not request.form.keys() or len(request.form.keys()) == 0:
        flash("No item was selected.", "Error")
        return redirect("/series")

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
@login_required
def delete_accessory():
    if not request.form.keys() or len(request.form.keys()) == 0:
        flash("No item was selected.", "Error")
        return redirect("/accessory")

    ids = ','.join(f'"{key}"' for key in request.form.keys())

    # Delete from accessory table
    db.execute(f"DELETE FROM accessory WHERE id IN ({ids})")

    flash("Accessory deleted.", "Success")
    return redirect("/accessory")


@app.route("/delete-calendar", methods=['POST'])
@login_required
def delete_calendar():
    if not request.form.keys() or len(request.form.keys()) == 0:
        flash("No item was selected.", "Error")
        return redirect("/calendar")

    ids = ','.join(f'"{key}"' for key in request.form.keys())

    # Delete from release calendar table
    db.execute(f"DELETE FROM release_calendar WHERE id IN ({ids})")

    flash("Release date deleted.", "Success")
    return redirect("/calendar")


@app.route("/delete-log", methods=['POST'])
@login_required
def delete_log():
    if not request.form.keys() or len(request.form.keys()) == 0:
        flash("No item was selected.", "Error")
        return redirect("/log")

    ids = ','.join(f'"{key}"' for key in request.form.keys())

    # Delete from release calendar table
    db.execute(f"DELETE FROM log WHERE id IN ({ids})")

    flash("Log deleted.", "Success")
    return redirect("/log")


@app.route("/delete-column", methods=['POST'])
@login_required
def delete_column():
    table = request.form.get("table")
    if not table or table not in ["accessory", "book", "log", "release_calendar", "series"]:
        flash("Wrong table.", "Error")
        return redirect("/library")

    name = "uc_" + secure_filename(request.form.get("name")).replace(".", "_").strip().lower()

    if name not in custom_column(table):
        flash("Wrong column name.", "Error")
        return redirect("/library")

    db.execute("ALTER TABLE ? DROP COLUMN ?", table, name)
    db.execute("DELETE FROM user_custom WHERE name = ? AND table_name = ? AND user_id = ?", name, table,
               session["user_id"])

    flash("Column deleted.", "Success")
    return redirect("/library")


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


@app.route("/log-out")
def logout():
    session.clear()
    return redirect("/")


# </editor-fold>

# <editor-fold desc="Mass upload functions">
@app.route("/mass-upload", methods=['POST'])
@login_required
def mass_upload():
    data = upload_file(request.files)
    table = request.form.get("table")

    if table == "book":
        for dict in data:
            insert_book(dict)
        flash("File uploaded.", "Success")
        return redirect("/library")
    elif table == "series":
        for dict in data:
            insert_series(dict)
        flash("Series uploaded.", "Success")
        return redirect("/series")
    elif table == "calendar":
        for dict in data:
            insert_calendar(dict)
        flash("Calendar uploaded.", "Success")
        return redirect("/calendar")
    else:
        flash("Wrong table.", "Error")
        return redirect("/library")


# </editor-fold>

@app.route("/export-data")
@login_required
def export():
    book_data = db.execute("SELECT * FROM book "
                           "JOIN accessory ON accessory.book_id = book.id "
                           "JOIN log ON log.book_id = book.id "
                           "WHERE user_id = ?", session["user_id"])
    series_data = db.execute("SELECT * FROM series "
                             "JOIN release_calendar rc ON rc.series_id = series.id "
                             "WHERE user_id = ?", session["user_id"])

    with open("./static/export/book_data.csv", "w") as file_book:
        writer = csv.writer(file_book, delimiter=';')
        writer.writerow(book_data[0].keys())
        for data in book_data:
            writer.writerow(data.values())

    with open("./static/export/series_data.csv", "w") as file_series:
        writer = csv.writer(file_series, delimiter=';')
        writer.writerow(series_data[0].keys())
        for data in series_data:
            writer.writerow(data.values())

    flash(f"Your book data is exported in {os.path.realpath(file_book.name)}", "Success")
    flash(f"Your series data is exported in {os.path.realpath(file_series.name)}", "Success")
    return redirect("/library")


@app.route("/download-template")
@login_required
def get_template():
    book = db.execute("SELECT * FROM book WHERE user_id = ?", session["user_id"])
    series = db.execute("SELECT * FROM series WHERE user_id = ?", session["user_id"])
    calendar = db.execute("SELECT rc.* FROM release_calendar rc "
                          "JOIN series ON rc.series_id = series.id"
                          " WHERE user_id = ?", session["user_id"])

    with open("./static/export/template.csv", "w") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow("Columns for book table:")
        writer.writerow(book[0].keys())
        writer.writerow("Columns for series table:")
        writer.writerow(series[0].keys())
        writer.writerow("Columns for calendar table:")
        writer.writerow(calendar[0].keys())

    flash(f"Your templated is downloaded in {os.path.realpath(file.name)}", "Success")
    return redirect("/library")


app.jinja_env.globals.update(column_name=column_name)
