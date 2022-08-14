import csv
from cs50 import SQL
from flask import request, session, flash

# Connect database
db = SQL("sqlite:///database.db")


def check_series(title, add):
    series_id = db.execute("SELECT id FROM series WHERE title = ? AND user_id = ?", title, session["user_id"])
    if not series_id:
        if add:
            return db.execute("INSERT INTO series(title, user_id) VALUES(?, ?)", title, session["user_id"])
        else:
            return None
    return series_id[0]["id"]


def series_end(series_id):
    series_end = db.execute("SELECT end_vol FROM series WHERE id = ?", series_id)
    if not series_end or not series_end[0]["end_vol"]:
        return 0
    return series_end[0]["end_vol"]


def series_current(series_id):
    series_current = db.execute("SELECT current FROM series WHERE id = ?", series_id)
    print(series_current)
    if not series_current or not series_current[0]["current"]:
        return 0
    if series_current[0]["current"] == series_end(series_id):
        db.execute("UPDATE series SET status = ? WHERE id = ?", "End", series_id)
    return series_current[0]["current"]


def series_missing(series_id):
    series_missing = db.execute("SELECT id, volume FROM series_missing WHERE series_id = ? ORDER BY volume", series_id)
    if not series_missing:
        return []
    return series_missing


def series_avail(series_id):
    series_avail = db.execute("SELECT volume FROM book WHERE series_id = ? ORDER BY volume", series_id)
    if not series_avail:
        return []
    avail_vol = []
    for row in series_avail:
        avail_vol.append(row["volume"])
    return avail_vol


def query_title(table):
    query = db.execute("SELECT title FROM ? WHERE user_id = ?", table, session["user_id"])
    return [dict["title"] for dict in query]


def insert_book(dict):
    if "series" not in dict.keys():
        series_id = None
    else:
        # Add series if not exist
        series_id = check_series(dict["series"], add=True)

        # Update series current
        volume = int(dict["volume"]) if dict["volume"] != "" else 0
        if volume > series_current(series_id):
            db.execute("UPDATE series SET current = ? WHERE id = ?", volume, series_id)

        # Delete missing volume
        for row in series_missing(series_id):
            if volume == row["volume"]:
                db.execute("DELETE FROM series_missing WHERE id = ?", row["id"])

        # Update missing volumes
        for i in range(1, volume):
            if i not in series_avail(series_id):
                db.execute("INSERT INTO series_missing(series_id, volume) VALUES(?, ?)", series_id, i)

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


def insert_series(dict):
    list_keys = [key for key in dict.keys() if dict[key] != ""]
    keys = ','.join(f'"{key}"' for key in list_keys)
    values = ','.join(f'"{dict[key]}"' for key in list_keys)
    db.execute(f"INSERT INTO series({keys}, user_id) VALUES({values}, ?)", session["user_id"])


def insert_calendar(dict):
    series_id = check_series(dict["series"], add=True)

    list_keys = [key for key in dict.keys() if key != "series" and dict[key] != ""]
    keys = ','.join(f'"{key}"' for key in list_keys)
    values = ','.join(f'"{dict[key]}"' for key in list_keys)
    db.execute(f"INSERT INTO release_calendar({keys}, series_id) VALUES({values}, ?)", series_id)


def upload_file(request):
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


def column_name(name):
    if name.startswith("ac_") or name.startswith("uc_"):
        name = name[3:]
    name = str(name).replace("_", " ").replace(".", " ").strip()
    name = " ".join(word.capitalize() for word in name.split())
    return name
