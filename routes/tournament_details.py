import random
import sqlite3
from flask import Blueprint, render_template, request, redirect, session
from database.db import get_db
from services.calculate_group import calculate_group
from services.add_player import add_player
from services.delete_player import delete_player
from services.start_tournament import start_tournament
from services.generate_knockout import generate_knockout
from services.save_match import save_match

tournament_details_bp = Blueprint("tournament_details", __name__)


@tournament_details_bp.route('/tournament/<int:id>', methods=['GET', 'POST'])
def tournament_details(id):

    conn = get_db()
    c = conn.cursor()

    # 🟢 بيانات البطولة
    c.execute("SELECT * FROM tournaments WHERE id = ?", (id,))
    tournament = c.fetchone()
    groups_count = tournament[4]

    # 🟢 اللاعبين
    c.execute("SELECT player_name FROM tournament_players WHERE tournament_id = ?", (id,))
    players = [p[0] for p in c.fetchall()]

    # 🟢 المباريات
    c.execute("""
    SELECT player1, player2, score1, score2
    FROM group_matches
    WHERE tournament_id=?
    """, (id,))
    matches = c.fetchall()

    matches_dict = {}
    for p1, p2, s1, s2 in matches:
        matches_dict[(p1, p2)] = (s1, s2)
        matches_dict[(p2, p1)] = (s2, s1)

    # 🟢 المجموعات
    c.execute("""
    SELECT group_name, player_name
    FROM groups
    WHERE tournament_id = ?
    """, (id,))
    rows = c.fetchall()

    groups = {}
    if rows:
        for group_name, player in rows:
            groups.setdefault(group_name, []).append(player)
    else:
        groups = None

    # 🔥 مهم
    standings_all = session.get("standings_all", {})
    ranks_all = session.get("ranks_all", {})

    if request.method == "POST":

        # 🔥 save match
        if "save_match" in request.form:
            save_match(conn, id, request.form)
            return redirect(request.url)

        # 🔥 calculate group
        if "calculate_group" in request.form:

            group = request.form["group_name"]

            c.execute("""
            SELECT player1, player2, score1, score2
            FROM group_matches
            WHERE tournament_id=? AND group_name=?
            """, (id, group))

            matches = c.fetchall()

            standings, ranks = calculate_group(matches)

            standings_all[group] = standings
            ranks_all[group] = ranks

            session["standings_all"] = standings_all
            session["ranks_all"] = ranks_all

            return redirect(request.url)

        # 🔥 knockout
        if "generate_knockout" in request.form:
            generate_knockout(conn, id, standings_all)
            return redirect(request.url)

        # 🔥 delete player
        if "delete_player" in request.form:
            delete_player(conn, id, request.form, players)
            return redirect(request.url)

        # 🔥 add player
        if "add_player" in request.form:

            result = add_player(conn, id, request.form, players)

            if result == "empty":
                return render_template(
                    "tournament_details.html",
                    tournament=tournament,
                    players=players,
                    error="Please enter a player name"
                )

            if result == "exists":
                return render_template(
                    "tournament_details.html",
                    tournament=tournament,
                    players=players,
                    error="Player already in tournament"
                )

            return redirect(request.url)

        # 🔥 start tournament
        if "start_tournament" in request.form:

            result = start_tournament(conn, id, players, groups_count)

            return redirect(request.url)

    return render_template(
        "tournament_details.html",
        tournament=tournament,
        players=players,
        groups=groups,
        matches_dict=matches_dict,
        standings_all=standings_all,
        ranks_all=ranks_all
    )