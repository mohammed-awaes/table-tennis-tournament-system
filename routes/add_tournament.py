import sqlite3
from flask import Blueprint, render_template, request, redirect, session
from database.db import get_db

add_tournament_dp = Blueprint("add_tournament", __name__)

@add_tournament_dp.route('/add-tournament', methods=['GET', 'POST'])
def add_tournament():

    # تأكد إن القائمة موجودة
    if "players" not in session:
        session["players"] = []

    if request.method == "POST":

        # 🟢 إضافة لاعب
        if "add_player" in request.form:

            player = request.form["player"].strip()

            if player == "":
                return render_template(
                    "add-tournament.html",
                    players=session["players"],
                    error="Please enter a player name"
                )

            if player in session["players"]:
                return render_template(
                    "add-tournament.html",
                    players=session["players"],
                    error="Player already added"
                )

            players = session["players"]
            players.append(player)
            session["players"] = players
            return redirect("/add-tournament")

        # 🟡 إنشاء بطولة
        elif "create_tournament" in request.form:

            if session["players"] == []:
                return render_template(
                    "add-tournament.html",
                    players=session["players"],
                    error="Please add players first"
                )

            name = request.form["name"].strip()
            date = request.form["date"].strip()
            groups_count = request.form["groups_count"].strip()

            # 🔥 الجديد
            qualify_top = request.form.get("qualify_top", "2")
            qualify_bottom = request.form.get("qualify_bottom", "0")

            if not name or not date or not groups_count:
                return render_template(
                    "add-tournament.html",
                    players=session["players"],
                    error="Please fill all fields",
                    name=name,
                    date=date,
                    groups_count=groups_count
                )

            groups_count = int(groups_count)
            qualify_top = int(qualify_top)
            qualify_bottom = int(qualify_bottom)

            if groups_count < 2:
                return render_template(
                    "add-tournament.html",
                    players=session["players"],
                    error="Groups must be at least 2"
                )

            conn = get_db()
            c = conn.cursor()

            # 🟢 إنشاء البطولة (🔥 عدلنا هنا)
            c.execute("""
                INSERT INTO tournaments 
                (name, date, groups_count, qualify_top, qualify_bottom)
                VALUES (?, ?, ?, ?, ?)
            """, (name, date, groups_count, qualify_top, qualify_bottom))

            tournament_id = c.lastrowid

            # 🔥 إضافة اللاعبين
            for player_name in session["players"]:

                c.execute("SELECT id FROM players WHERE name=?", (player_name,))
                row = c.fetchone()

                if row:
                    player_id = row[0]
                else:
                    c.execute(
                        "INSERT INTO players (name, points) VALUES (?, 1200)",
                        (player_name,)
                    )
                    player_id = c.lastrowid

                c.execute(
                    "INSERT INTO tournament_players (tournament_id, player_id) VALUES (?, ?)",
                    (tournament_id, player_id)
                )

            conn.commit()
            conn.close()

            session["players"] = []

            return redirect("/tournaments")

    return render_template("add-tournament.html", players=session["players"])