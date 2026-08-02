import sqlite3
from flask import Blueprint, render_template, request, redirect, session
from database.db import get_db



Tournaments_bp = Blueprint("Tournaments", __name__)


@Tournaments_bp.route("/tournaments")
def tournaments():
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM tournaments")
    tournaments = c.fetchall()

    conn.close()

    return render_template("tournaments.html", tournaments=tournaments)