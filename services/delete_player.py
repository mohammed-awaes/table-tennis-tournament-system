def delete_player(conn, tournament_id, form, players):

    c = conn.cursor()

    player_to_delete = form.get("delete_player")

    # ❌ حماية: إذا اللاعب مش موجود
    if player_to_delete not in players:
        return False

    # ✅ حذف اللاعب
    c.execute(
        "DELETE FROM tournament_players WHERE tournament_id = ? AND player_name = ?",
        (tournament_id, player_to_delete)
    )

    conn.commit()

    return True