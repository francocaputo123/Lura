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
import shutil
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
    """Elimina etiquetas HTML devolviendo texto plano, preservando saltos de linea entre bloques."""

    def __init__(self):
        super().__init__()
        self._chunks = []
        self._last_was_block = True

    def _add_newline(self):
        if self._chunks and not self._chunks[-1].endswith("\n"):
            self._chunks.append("\n")
        self._last_was_block = True

    def handle_starttag(self, tag, attrs):
        """Inserta un salto de linea antes de etiquetas de bloque."""
        if tag.lower() in _BLOCK_TAGS:
            self._add_newline()

    def handle_endtag(self, tag):
        """Inserta un salto de linea despues de etiquetas de bloque."""
        if tag.lower() in _BLOCK_TAGS:
            self._add_newline()

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


def _extract_media(extract_dir):
    """Extrae los archivos de media del .apkg a un subdirectorio temporal.

    Anki almacena los archivos de media con nombres numericos y un mapa JSON
    (`media`) que indica el nombre real de cada archivo. Esta funcion copia
    los archivos numerados a un subdirectorio usando sus nombres reales.

    Args:
        extract_dir: Directorio donde se descomprimio el .apkg.

    Returns:
        Tupla (media_dir, filenames) donde media_dir es el directorio que
        contiene los archivos con nombres reales y filenames es la lista de
        esos nombres. Si no hay media, devuelve (None, []).
    """
    extract_dir = Path(extract_dir)
    media_dir = extract_dir / "_lura_media"
    media_dir.mkdir(parents=True, exist_ok=True)

    media_map_path = extract_dir / "media"
    if not media_map_path.exists():
        return None, []

    try:
        media_map = json.loads(media_map_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, []

    extracted = []
    for numeric_name, real_name in media_map.items():
        src = extract_dir / str(numeric_name)
        if not src.exists():
            continue

        dst = media_dir / real_name
        try:
            dst.write_bytes(src.read_bytes())
            extracted.append(real_name)
        except Exception:
            continue

    return media_dir, extracted


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
    """Elimina etiquetas HTML de un string, preservando etiquetas <img>.

    Las etiquetas <img> se conservan para que el desarrollador de las
    tarjetas pueda renderizarlas desde public/media.

    Args:
        value: Texto que puede contener HTML.

    Returns:
        Texto plano con etiquetas <img> conservadas.
    """
    if not value:
        return ""

    # Preserva etiquetas <img> reemplazandolas por marcadores temporales.
    img_tags = []

    def _preserve_img(match):
        img_tags.append(match.group(0))
        return f"__IMG_{len(img_tags) - 1}__"

    text = re.sub(r"<img[^>]*>", _preserve_img, value, flags=re.IGNORECASE)

    stripper = _HTMLStripper()
    try:
        stripper.feed(text)
        text = stripper.get_text()
    except Exception:
        # Esto es un Fallback por si el HTML esta roto o corrompido
        text = re.sub(r"<[^>]+>", "", text)

    # Restaura las etiquetas <img>.
    for idx, tag in enumerate(img_tags):
        text = text.replace(f"__IMG_{idx}__", tag)

    return text


def _process_conditionals(text, fields, field_index):
    """Procesa los bloques condicionales {{#Campo}}...{{/Campo}}.

    Los bloques positivos se mantienen solo si el campo tiene contenido.
    Los bloques negativos {{^Campo}}...{{/Campo}} se mantienen solo si el
    campo esta vacio.

    Soporta sintaxis de filtros de add-ons como {{#furigana:Campo}}.

    Args:
        text: Plantilla de Anki.
        fields: Lista de valores de los campos de la nota.
        field_index: Mapa nombre_de_campo -> indice.

    Returns:
        Plantilla con los condicionales resueltos.
    """

    def _field_has_content(name):
        name = name.strip()
        # Soporta {{#filter:Campo}}.
        if ":" in name and not name.startswith(("type:", "hint:")):
            name = name.split(":", 1)[1].strip()
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


def _normalize_whitespace(text):
    """Normaliza espacios en blanco preservando saltos de linea.

    Colapsa espacios multiples en uno solo, pero mantiene saltos de linea
    provenientes de etiquetas de bloque HTML.

    Args:
        text: Texto a normalizar.

    Returns:
        Texto normalizado.
    """
    lines = text.splitlines()
    normalized_lines = []
    for line in lines:
        line = line.strip()
        line = " ".join(line.split())
        if line:
            normalized_lines.append(line)
    return "\n".join(normalized_lines)


def _remove_front_from_back(front, back):
    """Elimina el texto frontal del dorso si aparece como repeticion.

    Esto mejora mazos reversibles donde la plantilla afmt incluye tanto la
    pregunta como la respuesta. Si la limpieza deja el dorso vacio, se
    conserva el original.

    Args:
        front: Texto renderizado de la cara frontal.
        back: Texto renderizado de la cara dorsal.

    Returns:
        Texto dorsal limpio, o el original si la limpieza lo vacia.
    """
    front_stripped = front.strip()
    if not front_stripped or front_stripped not in back:
        return back

    cleaned = back.replace(front_stripped, "", 1)
    cleaned = re.sub(r"^[,.\s:]+", "", cleaned)
    cleaned = re.sub(r"[,.\s:]+$", "", cleaned)
    cleaned = _normalize_whitespace(cleaned)

    return cleaned if cleaned.strip() else back


def _extract_media_refs(text):
    """Extrae referencias a archivos de media desde el texto de una carta.

    Reconoce etiquetas <img src="..."> y marcadores [sound:...].

    Args:
        text: Texto de la carta (frente o dorso).

    Returns:
        Lista de tuplas (filename, media_type) sin duplicados.
    """
    refs = []

    for match in re.finditer(r'<img[^>]*src=["\']([^"\']+)["\'][^>]*>', text, flags=re.IGNORECASE):
        refs.append((match.group(1).strip(), "image"))

    for match in re.finditer(r"\[sound:([^\]]+)\]", text):
        refs.append((match.group(1).strip(), "audio"))

    # Elimina duplicados preservando el orden.
    seen = set()
    unique_refs = []
    for ref in refs:
        if ref not in seen:
            seen.add(ref)
            unique_refs.append(ref)

    return unique_refs


def _strip_media_refs(text):
    """Elimina las referencias a media del texto, dejandolo plano.

    Args:
        text: Texto que puede contener <img> o [sound:...].

    Returns:
        Texto limpio sin referencias a media.
    """
    text = re.sub(r"<img[^>]*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\[sound:[^\]]+\]", "", text)
    return _normalize_whitespace(text)


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

    # Elimina funciones de input y hints que no tienen sentido en Lura.
    text = re.sub(r"\{\{type:[^}]+\}\}", "", text)
    text = re.sub(r"\{\{hint:[^}]+\}\}", "", text)

    # Resuelve condicionales.
    text = _process_conditionals(text, fields, field_index)

    # FrontSide es la cara frontal ya renderizada; en texto plano la omitimos
    # para no repetir la pregunta en la respuesta.
    text = text.replace("{{FrontSide}}", "")

    # Filtros de add-ons: {{furigana:Campo}}, {{kanji:Campo}}, etc.
    def _replace_filter(match):
        content = match.group(1).strip()
        if ":" not in content:
            return match.group(0)
        filter_name, field_name = content.split(":", 1)
        filter_name = filter_name.strip()
        field_name = field_name.strip()
        # Ignora los filtros type/hint ya procesados arriba.
        if filter_name in ("type", "hint"):
            return ""
        idx = field_index.get(field_name)
        if idx is not None and idx < len(fields):
            return fields[idx]
        return ""

    text = re.sub(r"\{\{([^{}:|]+:[^{}:|]+)\}\}", _replace_filter, text)

    # Sustituye referencias simples a campos.
    def _replace_field(match):
        key = match.group(1).strip()
        idx = field_index.get(key)
        if idx is not None and idx < len(fields):
            return fields[idx]
        return ""

    text = re.sub(r"\{\{([^{}:|]+)\}\}", _replace_field, text)

    # Limpia HTML pero conserva etiquetas <img> y referencias [sound:...].
    text = _strip_html(text)

    return _normalize_whitespace(text)


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
    """Parsea un archivo .apkg y devuelve los datos listos para importar.

    Args:
        apkg_path: Ruta al archivo .apkg.

    Returns:
        Diccionario:
        {
            "decks": [...],
            "skipped": int,
            "media_dir": "...",  # Directorio temporal con media extraida
            "temp_dir": "..."    # Directorio temporal general (para cleanup)
        }

    Raises:
        ImportError: Si el archivo no es valido o no se puede parsear.
    """
    apkg_path = Path(apkg_path)
    if not apkg_path.exists():
        raise ImportError(f"No existe el archivo: {apkg_path}")
    if not zipfile.is_zipfile(apkg_path):
        raise ImportError(f"El archivo no es un ZIP valido: {apkg_path}")

    tmp = tempfile.mkdtemp()
    tmp_path = Path(tmp)

    try:
        with zipfile.ZipFile(apkg_path, "r") as zf:
            zf.extractall(tmp_path)

        db_path = _find_db(tmp_path)
        if db_path is None:
            raise ImportError(
                "El .apkg no contiene collection.anki21 ni collection.anki2"
            )

        media_dir, _ = _extract_media(tmp_path)

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
                    qfmt = template.get("qfmt", "")
                    afmt = template.get("afmt", "")

                    front = _render_template(qfmt, fields, field_index)
                    back = _render_template(afmt, fields, field_index)
                    back = _remove_front_from_back(front, back)
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
    except Exception:
        shutil.rmtree(tmp, ignore_errors=True)
        raise

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

    return {
        "decks": result_decks,
        "skipped": skipped,
        "media_dir": str(media_dir) if media_dir else None,
        "temp_dir": tmp,
    }
