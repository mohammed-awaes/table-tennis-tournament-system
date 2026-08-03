import random

def start_tournament(conn, tournament_id, players, groups_count):

    c = conn.cursor()

    # 🛑 تحقق
    if len(players) < groups_count:
        return "not_enough_players"

    if not groups_count or groups_count < 2:
        return "invalid_groups"

    # 🧹 حذف المجموعات القديمة
    c.execute("DELETE FROM groups WHERE tournament_id = ?", (tournament_id,))

    # 🎲 خلط اللاعبين
    players_copy = players.copy()
    random.shuffle(players_copy)

    # 🧠 إنشاء المجموعات
    groups = {}

    for i in range(groups_count):
        group_name = "Group " + chr(65 + i)
        groups[group_name] = []

    # 🔥 توزيع اللاعبين
    for i, player in enumerate(players_copy):
        group_index = i % groups_count
        group_name = "Group " + chr(65 + group_index)
        groups[group_name].append(player)

    # 💾 التخزين (🔥 المهم)
    for group_name, group_players in groups.items():
        for player in group_players:

            player_id = player[0]  # 👈 مهم جداً

            c.execute("""
                INSERT INTO groups (tournament_id, group_name, player_id)
                VALUES (?, ?, ?)
            """, (tournament_id, group_name, player_id))

    # 🏁 تحديث الحالة
    c.execute(
        "UPDATE tournaments SET status='started' WHERE id=?",
        (tournament_id,)
    )

    conn.commit()

    return "success"