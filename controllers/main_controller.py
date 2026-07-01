from db.connection import Database


def load_deck_groups():
    """
    Carga los mazos agrupados por categoria con los conteos de cada carta.
    Los conteos representan las cartas que hay que estudiar hoy:
        - Nuevas: nunca estudiadas (repetitions = 0).
        - Aprendiendo: en fase de aprendizaje y con next_review <= hoy.
        - Repasar: en revision y con next_review <= hoy.

    Returns:
        Lista de diccionarios
    """
    db = Database()
    db.connect()
    db_connection = db.get_connection()

    decks = db_connection.execute(
        "SELECT id, name, category FROM decks ORDER BY category, name"
    ).fetchall()

    groups = {}
    for deck in decks:
        counts = db_connection.execute(
            """
            SELECT
                id,
                COALESCE(SUM(CASE WHEN repetitions = 0 THEN 1 ELSE 0 END), 0) AS new,
                COALESCE(SUM(CASE WHEN repetitions > 0 AND interval < 1 AND next_review <= date('now') THEN 1 ELSE 0 END), 0) AS learning,
                COALESCE(SUM(CASE WHEN repetitions > 0 AND interval >= 1 AND next_review <= date('now') THEN 1 ELSE 0 END), 0) AS review
            FROM cards
            WHERE deck_id = ?
            """,
            (deck["id"],),
        ).fetchone()

        category = deck["category"] or "Sin categoría"
        deck_info = {
            "id" : deck["id"],
            "name": deck["name"],
            "new": counts["new"],
            "learning": counts["learning"],
            "review": counts["review"],
        }

        groups.setdefault(category, []).append(deck_info)

    return [
        {"category": category, "decks": decks_in_category}
        for category, decks_in_category in groups.items()
    ]
