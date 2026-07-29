def calculate_group(matches):

    standings = {}

    # 🧠 حساب النقاط
    for p1, p2, s1, s2 in matches:

        # إنشاء اللاعب
        if p1 not in standings:
            standings[p1] = {"points": 0, "wins": 0}
        if p2 not in standings:
            standings[p2] = {"points": 0, "wins": 0}

        # تحويل القيم
        s1 = int(s1)
        s2 = int(s2)

        # الحساب
        if s1 > s2:
            standings[p1]["points"] += 3
            standings[p1]["wins"] += 1
        elif s2 > s1:
            standings[p2]["points"] += 3
            standings[p2]["wins"] += 1
        else:
            standings[p1]["points"] += 1
            standings[p2]["points"] += 1

    # 🔥 ترتيب اللاعبين
    sorted_players = sorted(
        standings.items(),
        key=lambda x: (x[1]["points"], x[1]["wins"]),
        reverse=True
    )

    # 🔥 بناء الرانك
    ranks = {}

    for i, (player, data) in enumerate(sorted_players):

        if i == 0:
            ranks[player] = 1
        else:
            prev_player, prev_data = sorted_players[i - 1]

            # نفس النقاط + نفس الفوز = نفس الترتيب
            if data["points"] == prev_data["points"] and data["wins"] == prev_data["wins"]:
                ranks[player] = ranks[prev_player]
            else:
                ranks[player] = i + 1

    return standings, ranks