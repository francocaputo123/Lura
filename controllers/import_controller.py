import importlib
import shutil
from pathlib import Path

from db.connection import Database

# `tools.import` no se puede importar directamente porque `import` es una palabra reservada de Python, por eso lo importamos así.
anki_import = importlib.import_module("tools.import")

PUBLIC_MEDIA_DIR = Path(__file__).parent.parent / "public" / "media"


class ImportError(Exception):
    """Error durante la importacion de un mazo."""

    pass


class DeckCollisionError(ImportError):
    """Error cuando el mazo a importar ya existe en Lura."""

    pass


def _unique_filename(directory, filename):
    """Devuelve un nombre de archivo unico dentro del directorio

    Si `filename` ya existe, le agrega un sufijo numerico antes de la
    extension: archivo.png -> archivo_2.png -> archivo_3.png.
    """
    candidate = directory / filename
    if not candidate.exists():
        return filename

    stem = Path(filename).stem
    suffix = Path(filename).suffix
    counter = 2
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        candidate = directory / new_name
        if not candidate.exists():
            return new_name
        counter += 1


def import_apkg(path):
    """Importa un archivo .apkg en la base de datos de Lura.

    Extrae los archivos de media a public/media/<deck_id>/ para evitar
    colisiones entre mazos.

    Args:
        path: Ruta al archivo .apkg.

    Returns:
        Diccionario con el resultado de la importación

    Raises:
        ImportError: Si el archivo no se puede parsear.
        DeckCollisionError: Si algun mazo del .apkg ya existe en Lura.
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
    total_media_refs = 0
    copied_files = set()

    media_dir = data.get("media_dir")

    try:
        for deck in data["decks"]:
            cursor = db_connection.execute(
                "INSERT INTO decks (name, category, description) VALUES (?, ?, ?)",
                (deck["name"], deck["category"], deck.get("description", "")),
            )
            deck_id = cursor.lastrowid
            total_decks += 1

            deck_media_dir = PUBLIC_MEDIA_DIR / str(deck_id)
            deck_media_dir.mkdir(parents=True, exist_ok=True)

            for card in deck["cards"]:
                raw_front = card["front"]
                raw_back = card["back"]

                media_refs = anki_import._extract_media_refs(raw_front)
                media_refs.extend(anki_import._extract_media_refs(raw_back))

                front = anki_import._strip_media_refs(raw_front)
                back = anki_import._strip_media_refs(raw_back)

                cursor = db_connection.execute(
                    "INSERT INTO cards (deck_id, front, back) VALUES (?, ?, ?)",
                    (deck_id, front, back),
                )
                card_id = cursor.lastrowid
                total_cards += 1

                seen_refs = set()
                for filename, media_type in media_refs:
                    ref_key = (filename, media_type)
                    if ref_key in seen_refs:
                        continue
                    seen_refs.add(ref_key)

                    final_filename = filename
                    if media_dir:
                        src = Path(media_dir) / filename
                        if src.exists():
                            final_filename = _unique_filename(deck_media_dir, filename)
                            dst = deck_media_dir / final_filename
                            shutil.copy2(src, dst)
                            copied_files.add(str(dst))

                    try:
                        db_connection.execute(
                            "INSERT INTO card_media (card_id, filename, media_type) VALUES (?, ?, ?)",
                            (card_id, final_filename, media_type),
                        )
                        total_media_refs += 1
                    except Exception:
                        # Si ya existe (mismo card_id, filename, media_type), ignorar.
                        continue

        db_connection.commit()
    finally:
        temp_dir = data.get("temp_dir")
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)

    return {
        "decks_imported": total_decks,
        "cards_imported": total_cards,
        "skipped": data["skipped"],
        "media_files_copied": len(copied_files),
        "media_refs_stored": total_media_refs,
    }
