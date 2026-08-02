def add_player(conn, tournament_id, form, players):

    c = conn.cursor()

    new_player = form.get("new_player").strip()

    # ❌ إذا فاضي
    if new_player == "":
        return "empty"

    # ❌ إذا مكرر
    if new_player in players:
        return "exists"

    # ✅ إضافة اللاعب
    c.execute(
        "INSERT INTO tournament_players (tournament_id, player_id) VALUES (?, ?)",
        (tournament_id, new_player)
    )

    conn.commit()

    return "success"