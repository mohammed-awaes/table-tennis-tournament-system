import random

def start_tournament(conn, tournament_id, players, groups_count):

    c = conn.cursor()

    # ❌ تحقق من عدد اللاعبين
    if len(players) < groups_count:
        return "not_enough_players"

    # ❌ تحقق من groups_count
    if not groups_count or groups_count < 2:
        return "invalid_groups"

    # 🔥 حذف المجموعات القديمة
    c.execute("DELETE FROM groups WHERE tournament_id = ?", (tournament_id,))

    # 🎲 خلط اللاعبين
    players_copy = players.copy()
    random.shuffle(players_copy)

    # 🧠 إنشاء المجموعات
    groups = {}

    for i in range(groups_count):
        group_name = "Group " + chr(65 + i)  # A, B, C...
        groups[group_name] = []

    # 🔥 توزيع اللاعبين
    for i, player in enumerate(players_copy):
        group_index = i % groups_count
        group_name = "Group " + chr(65 + group_index)
        groups[group_name].append(player)

    # 💾 تخزين في DB
    for group_name, group_players in groups.items():
        for player in group_players:
            c.execute("""
                INSERT INTO groups (tournament_id, group_name, player_name)
                VALUES (?, ?, ?)
            """, (tournament_id, group_name, player))

    # 🏁 تحديث الحالة
    c.execute(
        "UPDATE tournaments SET status='started' WHERE id=?",
        (tournament_id,)
    )

    conn.commit()

    return "success"