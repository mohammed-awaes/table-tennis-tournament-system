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


            conn = get_db()
            c = conn.cursor()

            c.execute(
                "INSERT INTO tournaments (name, date, groups_count) VALUES (?, ?, ?)",
                (name, date, groups_count)
            )

            tournament_id = c.lastrowid

            for player in session["players"]:
                c.execute(
                    "INSERT INTO tournament_players (tournament_id, player_id) VALUES (?, ?)",
                    (tournament_id, player)
                )

            conn.commit()
            conn.close()

            # تنظيف session
            session["players"] = []

            return redirect("/tournaments")

    return render_template("add-tournament.html", players=session["players"])