import sqlite3
from pathlib import Path

class Database:
    """ Singleton de conexión a SQLite. """
    _instance = None
    _connection = None

    # Acá obtenemos la carpeta en la que está este archivo, en nuestro caso es db/
    DB_PATH = Path(__file__).parent / "lura.db"
    # lo mismo con el schema.sql
    SCHEMA_PATH = Path(__file__).parent / "schema.sql"

    # Este es un método que implementa python antes del __init__, usualmente no se toca, pero acá sí lo hacemos para implementar un singleton.
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self):
        """ Abre la conexión e inicializa el schema si es necesario """
        if(self._connection is None):
            self._connection = sqlite3.connect(self.DB_PATH)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
            self._init_schema()

    def close(self):
        """ Esto solo se debe llamar cuando se cierra la app, pues cierra la conexión a la db si existe. """
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def get_connection(self):
        """Devuelve la conexión activa.

        Returns:
            Conexión activa a SQLite.

        Raises:
            RuntimeError: Si se llama antes de connect().
        """
        if self._connection is None:
            raise RuntimeError("No hay conexión activa. Llamá a connect() primero.")
        return self._connection

    def _init_schema(self):
        """Ejecuta el schema.sql si las tablas no existen todavía."""
        schema = self.SCHEMA_PATH.read_text(encoding="utf-8")
        self._connection.executescript(schema)
        self._connection.commit()
