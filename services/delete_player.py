def delete_player(conn, tournament_id, form, players):

    c = conn.cursor()

    player_id = form.get("delete_player")

    # ❌ حماية: إذا اللاعب مش موجود
    if player_id not in players:
        return False

    # ✅ حذف اللاعب
    c.execute("""
        DELETE FROM tournament_players
        WHERE tournament_id=? AND player_id=?
    """, (tournament_id, player_id))
    conn.commit()

    return True