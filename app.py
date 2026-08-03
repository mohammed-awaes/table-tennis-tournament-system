import sqlite3
import random
from database.db import get_db
from flask import Blueprint, Flask, render_template , request,redirect, session
from routes.Tournaments import Tournaments_bp
from routes.tournament_details import tournament_details_bp
from routes.add_tournament import add_tournament_dp
from routes.Players import players, players_bp


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
    groups_count INTEGER,
    qualify_top INTEGER DEFAULT 2,
    qualify_bottom INTEGER DEFAULT 0
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS tournament_players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tournament_id INTEGER,
    player_id INTEGER
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
    player_id TEXT
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



# عرض جميع اللاعبين 

table_tennis.register_blueprint(players_bp)





table_tennis.register_blueprint(add_tournament_dp)

# عرض جميع البطولات 

table_tennis.register_blueprint(Tournaments_bp)


table_tennis.register_blueprint(tournament_details_bp)

if __name__ == "__main__":

    table_tennis.run(debug=True,port=9000)
