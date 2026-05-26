from tokenize import group

from flask import Flask, render_template , request,redirect, session
import sqlite3
import random


# إنشاء قاعدة البيانات والجداول إذا لم تكن موجودة

conn = sqlite3.connect("database.db")
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

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute("INSERT INTO players (name) VALUES (?)", (name,))

        conn.commit()
        conn.close()

        return redirect("/add-player")

    return render_template("add-player.html")


# عرض جميع اللاعبين 

@table_tennis.route('/players')
def players():

    conn = sqlite3.connect("database.db")
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

@table_tennis.route('/tournament/<int:id>', methods=['GET', 'POST'])
def tournament_details(id):

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # 🟢 بيانات البطولة
    c.execute("SELECT * FROM tournaments WHERE id = ?", (id,))
    tournament = c.fetchone()
    groups_count = tournament[4]

    # 🟢 اللاعبين
    c.execute("SELECT player_name FROM tournament_players WHERE tournament_id = ?", (id,))
    players = [p[0] for p in c.fetchall()]

    c.execute("""
    SELECT group_name, player_name
    FROM groups
    WHERE tournament_id = ?
    """, (id,))

    rows = c.fetchall()

    groups = {}

    if rows:
        for group_name, player in rows:
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(player)
    else:
        groups = None



    if request.method == "POST":

        # منع التعديل إذا البطولة انتهت
        if tournament[3] != "ongoing":
            return redirect(request.url)

        if "delete_player" in request.form:
            player_to_delete = request.form["delete_player"]

            # حماية
            if player_to_delete not in players:
                return redirect(request.url)

            c.execute(
                "DELETE FROM tournament_players WHERE tournament_id = ? AND player_name = ?",
                (id, player_to_delete)
            )

            conn.commit()

            return redirect(request.url)
        
        if "add_player" in request.form:
            new_player = request.form["new_player"].strip()

            if new_player == "":
                return render_template(
                    "tournament_details.html",
                    tournament=tournament,
                    players=players,
                    error="Please enter a player name"
                )

            if new_player in players:
                return render_template(
                    "tournament_details.html",
                    tournament=tournament,
                    players=players,
                    error="Player already in tournament"
                )

            c.execute(
                "INSERT INTO tournament_players (tournament_id, player_name) VALUES (?, ?)",
                (id, new_player)
            )

            conn.commit()

        if "start_tournament" in request.form:

            # 🛑 منع إعادة التشغيل
            if tournament[3] != "ongoing":
                return redirect(request.url)

            # 🛑 تحقق من عدد اللاعبين
            if len(players) < groups_count:
                return redirect(request.url)

            # 🛑 حماية groups_count
            if not groups_count or groups_count < 2:
                return redirect(request.url)

            # 🔥 حذف المجموعات القديمة
            c.execute("DELETE FROM groups WHERE tournament_id = ?", (id,))

            # 🎲 خلط اللاعبين
            players_copy = players.copy()
            random.shuffle(players_copy)

            # 🧠 إنشاء المجموعات
            groups = {}

            for i in range(groups_count):
                group_name = "Group " + chr(65 + i)
                groups[group_name] = []

            # 🔥 التوزيع الذكي
            for i, player in enumerate(players_copy):
                group_index = i % groups_count
                group_name = "Group " + chr(65 + group_index)
                groups[group_name].append(player)

            # 💾 التخزين
            for group_name, group_players in groups.items():
                for player in group_players:
                    c.execute("""
                        INSERT INTO groups (tournament_id, group_name, player_name)
                        VALUES (?, ?, ?)
                    """, (id, group_name, player))

            # 🏁 تحديث الحالة
            c.execute(
                "UPDATE tournaments SET status='started' WHERE id=?",
                (id,)
            )

            conn.commit()
            return redirect(request.url)
        
        if "save_match" in request.form:

            p1 = request.form["p1"]
            p2 = request.form["p2"]
            group = request.form["group"]

            s1 = request.form["score1"]
            s2 = request.form["score2"]

            c.execute("""
            INSERT INTO group_matches
            (tournament_id, group_name, player1, player2, score1, score2)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (id, group, p1, p2, s1, s2))

            conn.commit()
            return redirect(request.url)
        
        if "calculate_group" in request.form:

            group = request.form["group_name"]

            c.execute("""
            SELECT player1, player2, score1, score2
            FROM group_matches
            WHERE tournament_id=? AND group_name=?
            """, (id, group))

            matches = c.fetchall()

            standings = {}

            for p1, p2, s1, s2 in matches:

                if p1 not in standings:
                    standings[p1] = 0
                if p2 not in standings:
                    standings[p2] = 0

                if s1 > s2:
                    standings[p1] += 3
                else:
                    standings[p2] += 3

        if "generate_knockout" in request.form:

            # جيب ترتيب كل مجموعة
            # خذ أول + ثاني
            # اعمل قرعة

            random.shuffle(players)

            for i in range(0, len(players), 2):
                p1 = players[i]
                p2 = players[i+1]

                c.execute("""
                INSERT INTO matches
                (tournament_id, round, player1, player2)
                VALUES (?, 'round_of_16', ?, ?)
                """, (id, p1, p2))


    return render_template(
        "tournament_details.html",
        tournament=tournament,
        players=players,
        groups=groups,
    )

if __name__ == "__main__":

    table_tennis.run(debug=True,port=9000)
