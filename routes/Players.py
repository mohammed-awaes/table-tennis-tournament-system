import sqlite3
from flask import Blueprint, render_template, request, redirect, session
from database.db import get_db




players_bp = Blueprint("players", __name__)



@players_bp.route('/players')
def players():

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * From players")
    players = c.fetchall()

    conn.close()
    return render_template('players.html', players=players)