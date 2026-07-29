from tokenize import group
from database.db import get_db
from flask import Flask, render_template , request,redirect, session
from routes.tournament_details import tournament_bp
import sqlite3
import random


# إنشاء قاعدة البيانات والجداول إذا لم تكن موجودة

conn = get_db()
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS players
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    points INTEGER DEFAULT 1200
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS tournaments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    date TEXT,
    status TEXT DEFAULT 'ongoing',
    groups_count INTEGER
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS tournament_players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tournament_id INTEGER,
    player_name TEXT
)
""")


c.execute("""
CREATE TABLE IF NOT EXISTS group_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tournament_id INTEGER,
    group_name TEXT,
    player1 TEXT,
    player2 TEXT,
    score1 INTEGER,
    score2 INTEGER
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tournament_id INTEGER,
    group_name TEXT,
    player_name TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tournament_id INTEGER,
    round TEXT,
    player1 TEXT,
    player2 TEXT,
    score1 INTEGER,
    score2 INTEGER
)
""")





conn.commit()
conn.close()


# إنشاء تطبيق Flask

table_tennis = Flask(__name__)

table_tennis.secret_key = "mysecret123"


# تعريف المسارات

@table_tennis.route("/")
def home():
    return render_template("home.html")

# إضافة لاعب جديد   

@table_tennis.route('/add-player',methods=['POST', 'GET'])
def add_player():

    if request.method == "POST":
        name = request.form["name"]

        conn = get_db()
        c = conn.cursor()

        c.execute("INSERT INTO players (name) VALUES (?)", (name,))

        conn.commit()
        conn.close()

        return redirect("/add-player")

    return render_template("add-player.html")


# عرض جميع اللاعبين 

@table_tennis.route('/players')
def players():

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * From players")
    players = c.fetchall()

    conn.close()
    return render_template('players.html', players=players)




@table_tennis.route('/add-tournament', methods=['GET', 'POST'])
def add_tournament():

    # تأكد إن القائمة موجودة
    if "players" not in session:
        session["players"] = []

    if request.method == "POST":

        # 🟢 إضافة لاعب
        if "add_player" in request.form:

            player = request.form["player"].strip()

            if player == "":
                return render_template("add-tournament.html",
                                       players=session["players"],
                                       error="Please enter a player name")

            if player in session["players"]:
                return render_template("add-tournament.html",
                                       players=session["players"],
                                       error="Player already added")

            players = session["players"]
            players.append(player)
            session["players"] = players

            return redirect("/add-tournament")

        # 🟡 إنشاء بطولة
        elif "create_tournament" in request.form:

            if session["players"] == []:
                return render_template("add-tournament.html",
                                       players=session["players"],
                                       error="Please add players first")

            name = request.form["name"].strip()
            date = request.form["date"].strip()
            groups_count = request.form["groups_count"].strip()

            if not name or not date or not groups_count:
                return render_template("add-tournament.html",
                                       players=session["players"],
                                       error="Please fill all fields",
                                       name=name,
                                       date=date,
                                       groups_count=groups_count)
            
            groups_count = int(groups_count)
            if groups_count < 2:
                return render_template(
                    "add-tournament.html",
                    error="Groups must be at least 2"
                )


            conn = sqlite3.connect("database.db")
            c = conn.cursor()

            c.execute(
                "INSERT INTO tournaments (name, date, groups_count) VALUES (?, ?, ?)",
                (name, date, groups_count)
            )

            tournament_id = c.lastrowid

            for player in session["players"]:
                c.execute(
                    "INSERT INTO tournament_players (tournament_id, player_name) VALUES (?, ?)",
                    (tournament_id, player)
                )

            conn.commit()
            conn.close()

            # تنظيف session
            session["players"] = []

            return redirect("/tournaments")

    return render_template("add-tournament.html", players=session["players"])


# عرض جميع البطولات 

@table_tennis.route("/tournaments")
def tournaments():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM tournaments")
    tournaments = c.fetchall()

    conn.close()

    return render_template("tournaments.html", tournaments=tournaments)

# عرض تفاصيل البطولة مع إمكانية إدخال نتائج المباريات   

table_tennis.register_blueprint(tournament_bp)

if __name__ == "__main__":

    table_tennis.run(debug=True,port=9000)
