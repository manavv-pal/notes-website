import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"


# DATABASE INIT
def init_db():
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)
    # notes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
       user_id INTEGER,
        title TEXT,
        content TEXT,
        date TEXT,
        favorite INTEGER DEFAULT 0,
        category TEXT
    )
""")
    conn.commit()
    conn.close()


init_db()


# HOME
@app.route("/", methods=["GET", "POST"])
def home():

    if "user_id" not in session:
        return redirect("/login")

    category = request.form.get("category")
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")

        date = datetime.now().strftime("%d-%m-%Y")

        user_id = session.get("user_id")

        if title and content:
            cursor.execute(
                "INSERT INTO notes (user_id, title, content, date, category) VALUES (?, ?, ?, ?, ?)",
                (user_id, title, content, date, category),
            )
            conn.commit()

        return redirect(url_for("home"))

    cursor.execute(
        "SELECT * FROM notes WHERE user_id = ? ORDER BY favorite DESC, id DESC", (session["user_id"],)
    )

    notes = cursor.fetchall()
    conn.close()

    return render_template("index.html", notes=notes)


@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("notes.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)", (username, password)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("notes.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password),
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]
            print("LOGIN SUCCESS:", session)
            return redirect("/")
        else:
            return "Invalid login"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/login")


# FAVORITE
@app.route("/favorite/<int:id>")
def favorite(id):
    if "user_id" not in session:
        return redirect("/login")
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    cursor.execute("SELECT favorite FROM notes WHERE id = ?", (id,))
    current = cursor.fetchone()[0]

    new_value = 0 if current == 1 else 1

    cursor.execute("UPDATE notes SET favorite = ? WHERE id = ?", (new_value, id))

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


# DELETE
@app.route("/delete/<int:id>")
def delete(id):
    if "user_id" not in session:
        return redirect("/login")
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM notes WHERE id = ?", (id,))
    conn.commit()

    conn.close()
    return redirect(url_for("home"))


# EDIT
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if "user_id" not in session:
        return redirect("/login")
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")

        cursor.execute(
            "UPDATE notes SET title = ?, content = ? WHERE id = ?", (title, content, id)
        )

        conn.commit()
        return redirect(url_for("home"))

    cursor.execute("SELECT * FROM notes WHERE id = ?", (id,))
    note = cursor.fetchone()
    conn.close()

    return render_template("edit.html", note=note)


if __name__ == "__main__":
    app.run(debug=True)
