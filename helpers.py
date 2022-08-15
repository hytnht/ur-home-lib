import csv
from functools import wraps

from cs50 import SQL
from flask import request, session, flash, redirect

# Connect database
db = SQL("sqlite:///database.db")


# Check if a title (book or series) was existed in database, if not decide to add it or not
def check_exist(table, title, add):
    if not table or not title:
        return None
    id = db.execute("SELECT id FROM ? WHERE title = ? AND user_id = ?", table, title, session["user_id"])
    if not id:
        if add:
            return db.execute("INSERT INTO ?(title, user_id) VALUES(?, ?)", table, title, session["user_id"])
        else:
            return None
    return id[0]["id"]


# Return series' end volume
def series_end(series_id):
    if not series_id:
        return 0
    series_end = db.execute("SELECT end_vol FROM series WHERE id = ?", series_id)
    if not series_end or not series_end[0]["end_vol"]:
        return 0
    return series_end[0]["end_vol"]


# Return series' current volume
def series_current(series_id):
    if not series_id:
        return 0
    series_current = db.execute("SELECT current FROM series WHERE id = ?", series_id)
    if not series_current or not series_current[0]["current"]:
        return 0
    if series_current[0]["current"] == series_end(series_id):
        db.execute("UPDATE series SET status = 'End' WHERE id = ?", series_id)
    return series_current[0]["current"]


# Return series' missed volumes
def series_missing(series_id):
    if not series_id:
        return []
    series_missing = db.execute("SELECT volume FROM series_missing WHERE series_id = ? ORDER BY volume", series_id)
    if not series_missing:
        return []
    return [row["volume"] for row in series_missing]


# Return series' available volumes
def series_avail(series_id):
    if not series_id:
        return []
    series_avail = db.execute("SELECT volume FROM book WHERE series_id = ? ORDER BY volume", series_id)
    if not series_avail:
        return []
    return [row["volume"] for row in series_avail]


# Query column in user database
def by_user(column, table):
    if not column or not table:
        return []
    query = db.execute(f"SELECT DISTINCT {column} FROM {table} WHERE user_id = {session['user_id']}")
    return [dict[column] for dict in query]


# Update series based on insert/update book
def update_series(series_id, volume):
    if not series_id or not volume:
        return None

    # Update series current
    if volume > series_current(series_id):
        db.execute("UPDATE series SET current = ? WHERE id = ?", volume, series_id)

    # Delete missing volume now available
    missed = series_missing(series_id)
    if volume in missed:
        db.execute("DELETE FROM series_missing WHERE series_id = ? AND  volume = ?", series_id, volume)

    # Update new missing volumes
    avail = series_avail(series_id)
    print(avail)
    print(missed)
    for i in range(1, volume):
        if i not in avail and i not in missed:
            db.execute("INSERT INTO series_missing(series_id, volume) VALUES(?, ?)", series_id, i)


# Insert new book to table
def insert_book(dict):
    if not dict:
        return None
    if not dict["series"] or "series" not in dict.keys():
        series_id = None
    else:
        # Add series if not exist
        series_id = check_exist("series", dict["series"], add=True)
        # Update series current
        if dict["volume"] != "":
            update_series(series_id, int(dict["volume"]))

    # Add new book to database
    list_keys = [key for key in dict.keys() if key[0:3] != "ac_" and key != "series" and dict[key] != ""]
    keys = ','.join(f'"{key}"' for key in list_keys)
    values = ','.join(f'"{dict[key]}"' for key in list_keys)
    book_id = db.execute(f"INSERT INTO book({keys}, series_id, user_id) VALUES({values}, ?, ?)", series_id,
                         session["user_id"])

    # Add accessories to book
    if request.form.get("ac_type"):
        list_ac_keys = [key for key in dict.keys() if key[0:3] == "ac_" and dict[key] != ""]
        ac_keys = ','.join(f'"{key[3:]}"' for key in list_ac_keys)
        ac_values = ','.join(f'"{dict[key]}"' for key in list_ac_keys)
        db.execute(f"INSERT INTO accessory({ac_keys}, book_id) VALUES({ac_values},?)", book_id)

    return book_id


# Insert new series to table
def insert_series(dict):
    list_keys = [key for key in dict.keys() if dict[key] != ""]
    keys = ','.join(f'"{key}"' for key in list_keys)
    values = ','.join(f'"{dict[key]}"' for key in list_keys)
    series_id = db.execute(f"INSERT INTO series({keys}, user_id) VALUES({values}, ?)", session["user_id"])
    return series_id


# Insert new release date to table
def insert_calendar(dict):
    if not dict:
        return None
    series_id = check_exist("series", dict["series"], add=True)

    list_keys = [key for key in dict.keys() if key != "series" and dict[key] != ""]
    keys = ','.join(f'"{key}"' for key in list_keys)
    values = ','.join(f'"{dict[key]}"' for key in list_keys)
    calendar_id = db.execute(f"INSERT INTO release_calendar({keys}, series_id) VALUES({values}, ?)", series_id)
    return calendar_id


# Check and read file uploaded
def upload_file(request):
    if not request:
        return []
    # Ensure file was uploaded
    if not request:
        flash("Please upload a csv file.", "Error")

    file = request["file"]

    if file.filename == "":
        flash("Please select a file.", "Error")
        return []

    # Ensure file uploaded was csv
    if file.filename.rsplit('.', 1)[1].lower() != "csv":
        flash("Only accept csv file.", "Error")
        return []

    # Get file data
    file.seek(0)
    reader = file.read().decode("utf-8-sig")
    data = [{k: v for k, v in row.items()} for row in csv.DictReader(reader.splitlines(), skipinitialspace=True)]

    return data


# Convert column name in database to display in frontend
def column_name(name):
    if not name:
        return ""
    if name.startswith("ac_") or name.startswith("uc_"):
        name = name[3:]
    name = str(name).replace("_", " ")
    name = " ".join(word.capitalize() for word in name.split())
    return name


# Return list of user custom columns
def custom_column(table):
    if not table:
        return []
    custom = db.execute("SELECT name FROM user_custom WHERE table_name = ? AND user_id = ?", table, session["user_id"])
    return [row["name"] for row in custom]


# Check if user logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function
