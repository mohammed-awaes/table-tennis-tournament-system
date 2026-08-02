def add_player(conn, tournament_id, form, players):

    c = conn.cursor()

    name = form.get("new_player").strip()

    if name == "":
        return "empty"

    # 🔥 check if player exists globally
    c.execute("SELECT id FROM players WHERE name = ?", (name,))
    existing = c.fetchone()

    if existing:
        player_id = existing[0]
    else:
        # ➕ create new player
        c.execute(
            "INSERT INTO players (name) VALUES (?)",
            (name,)
        )
        player_id = c.lastrowid

    # 🔥 check if already in tournament
    c.execute("""
        SELECT id FROM tournament_players
        WHERE tournament_id=? AND player_id=?
    """, (tournament_id, player_id))

    if c.fetchone():
        return "exists"

    # 🔥 insert into tournament
    c.execute("""
        INSERT INTO tournament_players (tournament_id, player_id)
        VALUES (?, ?)
    """, (tournament_id, player_id))

    conn.commit()

    return "ok"