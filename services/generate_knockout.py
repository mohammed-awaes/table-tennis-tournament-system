import sqlite3

def generate_knockout(conn, tournament_id, standings_all):

    c = conn.cursor()

    # 🟢 جيب إعدادات البطولة
    c.execute("""
        SELECT qualify_top, qualify_bottom
        FROM tournaments
        WHERE id=?
    """, (tournament_id,))
    
    row = c.fetchone()

    if not row:
        return

    qualify_top = row[0]
    qualify_bottom = row[1]

    upper = []
    lower = []

    # 🔥 1. ترتيب اللاعبين داخل كل مجموعة
    for group_name, players in standings_all.items():

        sorted_players = sorted(
            players.items(),
            key=lambda x: (-x[1]["points"], -x[1]["wins"])
        )

        # 🔝 أعلى
        for i in range(min(qualify_top, len(sorted_players))):
            upper.append((group_name, sorted_players[i][0]))

        # 🔻 أسفل
        for i in range(len(sorted_players) - qualify_bottom, len(sorted_players)):
            if i >= 0:
                lower.append((group_name, sorted_players[i][0]))

    # 🟢 2. تقسيم حسب المجموعات
    def group_players(players_list):
        groups = {}
        for g, p in players_list:
            groups.setdefault(g, []).append(p)
        return groups

    upper_groups = group_players(upper)
    lower_groups = group_players(lower)

    # 🟢 3. عمل cross matches
    def make_cross_matches(groups, stage_name):

        group_names = list(groups.keys())
        matches = []

        for i in range(len(group_names)):

            g1 = group_names[i]
            g2 = group_names[(i + 1) % len(group_names)]

            g1_players = groups[g1]
            g2_players = groups[g2]

            for j in range(min(len(g1_players), len(g2_players))):

                if j % 2 == 0:
                    p1 = g1_players[j]
                    p2 = g2_players[min(j+1, len(g2_players)-1)]
                else:
                    p1 = g2_players[j]
                    p2 = g1_players[min(j+1, len(g1_players)-1)]

                matches.append((p1, p2))

        # 🗄️ حفظ في DB
        for p1, p2 in matches:
            c.execute("""
                INSERT INTO matches (tournament_id, round, player1, player2)
                VALUES (?, ?, ?, ?)
            """, (tournament_id, stage_name, p1, p2))

    # 🔥 Upper Bracket
    if upper_groups:
        make_cross_matches(upper_groups, "upper_round1")

    # 🔥 Lower Bracket
    if lower_groups:
        make_cross_matches(lower_groups, "lower_round1")

    conn.commit()