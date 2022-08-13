from cs50 import SQL
from flask import request, session

# Connect database
db = SQL("sqlite:///database.db")

def check_series(title):
    series_id = db.execute("SELECT id FROM series WHERE title = ? AND user_id = ?", title,
                           session["user_id"])
    if not series_id:
        return None
    return series_id[0]["id"]


def series_end(series_id):
    series_end = db.execute("SELECT end_vol FROM series WHERE id = ?", series_id)[0]["end_vol"]
    if not series_end:
        return 0
    return series_end


def series_current(series_id):
    series_current = db.execute("SELECT current FROM series WHERE id = ?", series_id)[0]["current"]
    if not series_current:
        return 0
    if series_current == series_end(series_id):
        db.execute("UPDATE series SET status = ? WHERE series_id = ?", "End", series_id)
    return series_current


def series_missing(series_id):
    series_missing = db.execute("SELECT id, volume FROM series_missing WHERE series_id = ? ORDER BY volume",
                                series_id)
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


def insert_book(dict):
    if "series" not in dict.keys():
        series_id = None
    else:
        # Add series if not exist
        series_id = check_series(dict["series"])
        if not series_id:
            series_id = db.execute("INSERT INTO series(title, user_id) VALUES(?, ?)", dict["series"],
                                   session["user_id"])

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
    print(keys)
    print(values)
    book_id = db.execute(f"INSERT INTO book({keys}, series_id, user_id) VALUES({values}, ?, ?)", series_id,
                         session["user_id"])

    # Add accessories to book
    if request.form.get("ac_type"):
        list_ac_keys = [key for key in dict.keys() if key[0:3] == "ac_" and dict[key] != ""]
        ac_keys = ','.join(f'"{key[3:]}"' for key in list_ac_keys)
        ac_values = ','.join(f'"{dict[key]}"' for key in list_ac_keys)
        db.execute(f"INSERT INTO accessory({ac_keys}, book_id) VALUES({ac_values},?)", book_id)

def insert_series(dict):
    list_keys = [key for key in dict.keys() if  dict[key] != ""]
    keys = ','.join(f'"{key}"' for key in list_keys)
    values = ','.join(f'"{dict[key]}"' for key in list_keys)
    db.execute(f"INSERT INTO series({keys}, user_id) VALUES({values}, ?)", session["user_id"])