import importlib

from db.connection import Database

# `tools.import` no se puede importar directamente porque `import` es una palabra reservada de Python, por eso lo importamos así.
anki_import = importlib.import_module("tools.import")


class ImportError(Exception):
    """Error durante la importacion de un mazo."""

    pass


class DeckCollisionError(ImportError):
    """Error cuando el mazo a importar ya existe en Lura."""

    pass


def import_apkg(path):
    """Importa un archivo .apkg en la base de datos de Lura.

    El proceso es: primero se verifica que ningun mazo con el mismo nombre exista, y despues se insertan los datos.

    Args:
        path: Ruta al archivo .apkg.

    Returns:
        Diccionario con el resultado de la importación

    Raises:
        ImportError: Si el archivo no se puede parsear por 'x' o 'y' motivo.
        DeckCollisionError: Si algun mazo del .apkg ya existe en Lura, por ejemplo, no puede haber dos mazos con el nombre 'B1_Wortliste_DTZ_Goethe'.
    """
    try:
        data = anki_import.parse_apkg(path)
    except anki_import.ImportError as exc:
        raise ImportError(str(exc)) from exc

    db = Database()
    db.connect()
    db_connection = db.get_connection()

    for deck in data["decks"]:
        existing = db_connection.execute(
            "SELECT id FROM decks WHERE name = ? AND category = ?",
            (deck["name"], deck["category"]),
        ).fetchone()
        if existing:
            raise DeckCollisionError(
                f"El mazo '{deck['full_name']}' ya existe en Lura."
            )

    total_decks = 0
    total_cards = 0

    for deck in data["decks"]:
        cursor = db_connection.execute(
            "INSERT INTO decks (name, category, description) VALUES (?, ?, ?)",
            (deck["name"], deck["category"], deck.get("description", "")),
        )
        deck_id = cursor.lastrowid
        total_decks += 1

        for card in deck["cards"]:
            db_connection.execute(
                "INSERT INTO cards (deck_id, front, back) VALUES (?, ?, ?)",
                (deck_id, card["front"], card["back"]),
            )
            total_cards += 1

    db_connection.commit()

    return {
        "decks_imported": total_decks,
        "cards_imported": total_cards,
        "skipped": data["skipped"],
    }
