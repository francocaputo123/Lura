"""
Este es el parser para importar mazos de Anki desde archivos .apkg.
Un archivo .apkg es básicamente un ZIP que tiene:
    - collection.anki21 o collection.anki2: una base de datos SQLite de Anki (Esta VERGA tiene viente millones de formatos que hubo que entender para hacerlos compatibles).
    - Un archivo `media` con un mapa JSON de nombres numericos a nombres reales.
    - Archivos de media numerados (imagenes, audio, etc etc etc), pueden ni siquiera incluir su extensión de archivo.

POR AHORA para la importacion a Lura solo nos interesa el contenido textual de las cartas, por lo que ignoramos los archivos de media y nos concentramos en la base de datos, luego veré cómo corno hago para hacer la importación también de los archivos correspondientes.

Esto es importante, porque, por ejemplo, si vos estás estudiando Alemán, no podés simplemente basarte en los textos, porque después terminás pronunciando "Volkwagen" como "Bolkguajen" en lugar de "Foksvaguen" que es la pronunciación correcta, entonces viene un alemán o un pintor austriaco y te mete una trompada. No sé vos, pero a mí no me interesa que me pegue una trompada un chabón de 2 metros con ascendencia del Sacro Imperio Romano.
"""

import html
import json
import re
import sqlite3
import tempfile
import zipfile
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path


class ImportError(Exception):
    """Error durante la importacion de un archivo .apkg."""

    pass


_BLOCK_TAGS = {
    "br",
    "p",
    "div",
    "li",
    "tr",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "blockquote",
}


class _HTMLStripper(HTMLParser):
    """Elimina etiquetas HTML devolviendo solo el texto plano, que es lo que nos importa, porque no podemos renderizar dicho contenido HTML."""

    def __init__(self):
        super().__init__()
        self._chunks = []
        self._last_was_block = True

    def _add_space(self):
        if self._chunks and not self._last_was_block:
            self._chunks.append(" ")
        self._last_was_block = True

    def handle_starttag(self, tag, attrs):
        """Inserta un espacio antes de etiquetas de bloque."""
        if tag.lower() in _BLOCK_TAGS:
            self._add_space()

    def handle_endtag(self, tag):
        """Inserta un espacio despues de etiquetas de bloque."""
        if tag.lower() in _BLOCK_TAGS:
            self._add_space()

    def handle_data(self, data):
        """Acumula texto plano."""
        self._chunks.append(data)
        self._last_was_block = False

    def handle_entityref(self, name):
        """Decodifica entidades con nombre ('&amp;' => '&', '&lt;' => '<', etc etc.)."""
        self._chunks.append(html.unescape(f"&{name};"))
        self._last_was_block = False

    def handle_charref(self, name):
        """Decodifica entidades numericas (&#1234;)."""
        self._chunks.append(html.unescape(f"&#{name};"))
        self._last_was_block = False

    def get_text(self):
        """Devuelve el texto acumulado."""
        return "".join(self._chunks)


def _find_db(extract_dir):
    """Busca la base de datos de Anki dentro del directorio extraido del apkg

    Args:
        extract_dir: Directorio donde se descomprimio el .apkg.

    Returns:
        Ruta al archivo SQLite, o None si no se encuentra.
    """
    extract_dir = Path(extract_dir)
    for name in ("collection.anki21", "collection.anki2"):
        candidate = extract_dir / name
        if candidate.exists():
            return candidate
    return None


def _load_col(db_connection):
    """Carga los modelos y mazos desde la tabla `col` de la db de Anki

    Args:
        db_connection: Si tenés 2 neuronas, las dos se llevan mal, y no podés intuir esto, es la instancia de la conexión sqlite3 a la base de datos de Anki.

    Returns:
        Tupla (models, decks) donde ambos son diccionarios JSON parseados.

    Raises:
        ImportError: Si la tabla `col` no tiene los datos esperados.
    """

    row = db_connection.execute("SELECT models, decks FROM col LIMIT 1").fetchone()

    if row is None:
        raise ImportError("La base de datos de Anki no contiene la tabla 'col'")

    try:
        models = json.loads(row["models"])
        decks = json.loads(row["decks"])
    except json.JSONDecodeError as exc:
        raise ImportError(f"No se pudo parsear el JSON de Anki: {exc}") from exc

    return models, decks


def _is_cloze(model):
    """Determina si un notetype es de tipo Cloze.
    Anki tiene otro "tipo" de carta llamado Cloze, donde, en lugar de almacenar dos lados de la carta, solo muestra uno. Ese único lado tendría ciertas partes del texto parametrizados. Esta explicación tampoco importa mucho porque esta función está hecha exclusivamente para detectar los clozes y removerlos.

    Args:
        model: El dict del notetype

    Returns:
        True si es un Cloze, False en caso contrario.
    """
    return model.get("type") == 1


def _build_field_index(model):
    """Crea un mapa nombre_de_campo -> indice para un notetype.

    Args:
        model: Diccionario del notetype.

    Returns:
        Diccionario
    """
    return {fld["name"]: idx for idx, fld in enumerate(model.get("flds", []))}


def _strip_html(value):
    """Elimina etiquetas HTML de un string.

    Args:
        value: Texto que puede contener HTML.

    Returns:
        Texto plano.
    """
    if not value:
        return ""

    stripper = _HTMLStripper()
    try:
        stripper.feed(value)
        return stripper.get_text()
    except Exception:
        # Esto es un Fallback por si el HTML esta roto o corrompido
        return re.sub(r"<[^>]+>", "", value)


def _process_conditionals(text, fields, field_index):
    """Procesa los bloques condicionales {{#Campo}}...{{/Campo}}.

    Los bloques positivos se mantienen solo si el campo tiene contenido.
    Los bloques negativos {{^Campo}}...{{/Campo}} se mantienen solo si el
    campo esta vacio.

    Args:
        text: Plantilla de Anki.
        fields: Lista de valores de los campos de la nota.
        field_index: Mapa nombre_de_campo -> indice.

    Returns:
        Plantilla con los condicionales resueltos.
    """

    def _field_has_content(name):
        name = name.strip()
        idx = field_index.get(name)
        if idx is None or idx >= len(fields):
            return False
        return bool(fields[idx].strip())

    def _keep_positive(match):
        return match.group(2) if _field_has_content(match.group(1)) else ""

    def _keep_negative(match):
        return match.group(2) if not _field_has_content(match.group(1)) else ""

    text = re.sub(
        r"\{\{\^([^{}]+)\}\}(.*?)\{\{/\1\}\}",
        _keep_negative,
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"\{\{#([^{}]+)\}\}(.*?)\{\{/\1\}\}",
        _keep_positive,
        text,
        flags=re.DOTALL,
    )
    return text


def _render_template(template, fields, field_index):
    """Renderiza una plantilla de Anki a texto plano.

    Args:
        template: String con la plantilla (qfmt o afmt).
        fields: Lista de valores de los campos de la nota.
        field_index: Mapa nombre_de_campo -> indice.

    Returns:
        Texto plano listo para guardar en Lura.
    """
    text = template or ""
    text = re.sub(r"\{\{type:[^}]+\}\}", "", text)
    text = re.sub(r"\{\{hint:[^}]+\}\}", "", text)
    text = _process_conditionals(text, fields, field_index)
    text = text.replace("{{FrontSide}}", "")

    def _replace_field(match):
        key = match.group(1).strip()
        idx = field_index.get(key)
        if idx is not None and idx < len(fields):
            return fields[idx]
        return ""

    text = re.sub(r"\{\{([^{}:|]+)\}\}", _replace_field, text)

    text = _strip_html(text)
    text = re.sub(r"\[sound:[^\]]+\]", "", text)

    return " ".join(text.split())


def _split_deck_name(full_name):
    """Divide un nombre de mazo Anki en categoria y nombre.

    Anki usa `::` como separador jerarquico. Por ejemplo:
        "Idiomas::Ingles::Gramatica" -> ("Idiomas::Ingles", "Gramatica")

    Args:
        full_name: Nombre completo del mazo en Anki.

    Returns:
        Tupla (category, name).
    """
    parts = full_name.split("::")
    if len(parts) == 1:
        return "Sin categoría", parts[0]
    return "::".join(parts[:-1]), parts[-1]


def parse_apkg(apkg_path):
    """Parsea un archivo .apkg y devuelve los datos listos para poder importar la db que itene adentro

    Args:
        apkg_path: Ruta al archivo .apkg

    Returns:
        Diccionario

    Raises:
        ImportError: Si el archivo no es valido o no se puede parsear.
    """
    apkg_path = Path(apkg_path)
    if not apkg_path.exists():
        raise ImportError(f"No existe el archivo: {apkg_path}")
    if not zipfile.is_zipfile(apkg_path):
        raise ImportError(f"El archivo no es un ZIP valido: {apkg_path}")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(apkg_path, "r") as zf:
            zf.extractall(tmp_path)

        db_path = _find_db(tmp_path)
        if db_path is None:
            raise ImportError(
                "El .apkg no contiene collection.anki21 ni collection.anki2"
            )

        db_connection = sqlite3.connect(str(db_path))
        try:
            db_connection.row_factory = sqlite3.Row
            models, decks = _load_col(db_connection)

            cloze_mids = {mid for mid, m in models.items() if _is_cloze(m)}
            field_indexes = {mid: _build_field_index(m) for mid, m in models.items()}

            deck_cards = defaultdict(list)
            skipped = 0

            cursor = db_connection.execute(
                """
                SELECT c.did, c.ord, c.nid, n.mid, n.flds
                FROM cards c
                JOIN notes n ON c.nid = n.id
            """
            )

            for row in cursor:
                mid = str(row["mid"])
                if mid in cloze_mids:
                    skipped += 1
                    continue

                model = models.get(mid)
                if not model:
                    skipped += 1
                    continue

                field_index = field_indexes.get(mid)
                if not field_index:
                    skipped += 1
                    continue

                fields = row["flds"].split("\x1f")
                templates = model.get("tmpls", [])
                ord_idx = row["ord"]

                if ord_idx < 0 or ord_idx >= len(templates):
                    skipped += 1
                    continue

                template = templates[ord_idx]

                try:
                    front = _render_template(
                        template.get("qfmt", ""), fields, field_index
                    )
                    back = _render_template(
                        template.get("afmt", ""), fields, field_index
                    )
                except Exception:
                    skipped += 1
                    continue

                if not front.strip() or not back.strip():
                    skipped += 1
                    continue

                did = str(row["did"])
                deck_cards[did].append({"front": front, "back": back})

        finally:
            db_connection.close()

    result_decks = []
    for did, cards in deck_cards.items():
        deck_info = decks.get(did, {})
        full_name = deck_info.get("name", "Unknown")
        category, name = _split_deck_name(full_name)

        result_decks.append(
            {
                "name": name,
                "category": category,
                "full_name": full_name,
                "description": "Importado desde Anki",
                "cards": cards,
            }
        )

    return {"decks": result_decks, "skipped": skipped}
