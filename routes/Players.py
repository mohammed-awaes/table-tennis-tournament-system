import sqlite3
from flask import Blueprint, render_template, request, redirect, session
from database.db import get_db

players_bp = Blueprint("players", __name__)









@players_bp.route('/players')
def players():

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT id, name, points FROM players")
    players = c.fetchall()

    players_sorted = sorted(players, key=lambda x: x[2], reverse=True)

    ranks = {}

    for i, player in enumerate(players_sorted):
        ranks[player[0]] = i + 1

    conn.close()
    return render_template('players.html', players=players, ranks=ranks)