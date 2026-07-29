import random

def generate_knockout(conn, tournament_id, standings_all):

    c = conn.cursor()

    qualified_players = []

    # 🧠 خذ أول + ثاني من كل مجموعة
    for group, standings in standings_all.items():

        sorted_players = sorted(
            standings.items(),
            key=lambda x: (x[1]["points"], x[1]["wins"]),
            reverse=True
        )

        # Top 2
        for i in range(min(2, len(sorted_players))):
            player_name = sorted_players[i][0]
            qualified_players.append(player_name)

    # ❌ إذا ما في عدد كافي
    if len(qualified_players) < 2:
        return "not_enough_players"

    # 🎲 خلط اللاعبين
    random.shuffle(qualified_players)

    # 🔥 حذف مباريات قديمة (اختياري)
    c.execute("DELETE FROM matches WHERE tournament_id=?", (tournament_id,))

    # 🎮 إنشاء مباريات
    for i in range(0, len(qualified_players), 2):

        if i + 1 >= len(qualified_players):
            break

        p1 = qualified_players[i]
        p2 = qualified_players[i + 1]

        c.execute("""
        INSERT INTO matches (tournament_id, round, player1, player2)
        VALUES (?, 'quarter_final', ?, ?)
        """, (tournament_id, p1, p2))

    conn.commit()

    return "success"