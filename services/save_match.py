def save_match(conn, tournament_id, form):

    c = conn.cursor()

    p1 = form.get("p1")
    p2 = form.get("p2")
    group = form.get("group")

    s1 = form.get("score1")
    s2 = form.get("score2")

    # ❌ تحقق من الإدخال
    if not p1 or not p2 or s1 == "" or s2 == "":
        return "invalid"

    # 🔍 هل المباراة موجودة؟
    c.execute("""
    SELECT id FROM group_matches
    WHERE tournament_id=? AND group_name=? AND player1=? AND player2=?
    """, (tournament_id, group, p1, p2))

    existing = c.fetchone()

    if existing:
        # 🔄 update
        c.execute("""
        UPDATE group_matches
        SET score1=?, score2=?
        WHERE id=?
        """, (s1, s2, existing[0]))
    else:
        # ➕ insert
        c.execute("""
        INSERT INTO group_matches
        (tournament_id, group_name, player1, player2, score1, score2)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (tournament_id, group, p1, p2, s1, s2))

    conn.commit()

    return "success"