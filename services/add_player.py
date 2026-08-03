def add_player(conn, tournament_id, form, players):

    c = conn.cursor()

    new_player = form.get("new_player")

    if not new_player:
        return "empty"

    new_player = new_player.strip()

    if new_player == "":
        return "empty"

    # 🔍 هل موجود في players table؟
    c.execute("SELECT id FROM players WHERE name=?", (new_player,))
    row = c.fetchone()

    if row:
        player_id = row[0]
    else:
        # ➕ أضف لاعب جديد
        c.execute(
            "INSERT INTO players (name, points) VALUES (?, ?)",
            (new_player, 1200)
        )
        player_id = c.lastrowid

    # ❌ هل موجود في البطولة؟
    c.execute("""
    SELECT id FROM tournament_players
    WHERE tournament_id=? AND player_id=?
    """, (tournament_id, player_id))

    if c.fetchone():
        return "exists"

    # ✅ أضف للبطولة
    c.execute("""
    INSERT INTO tournament_players (tournament_id, player_id)
    VALUES (?, ?)
    """, (tournament_id, player_id))

    conn.commit()

    return "success"