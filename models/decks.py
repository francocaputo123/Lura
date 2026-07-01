import sqlite3
from db.connection import Database

class Model :

    '''
    Creacion del mazo
    '''
    def create_deck(self, name, category, description="") :
        db = Database()
        conn = db.get_connection()

        cursor = conn.cursor()

        query = "INSERT INTO decks (name, description, category) VALUES (?,?,?)"
        try :
            #importante verificar primero si el mazo ya existe
            cursor.execute("SELECT * FROM decks WHERE name = ?", (name,))

            deck = cursor.fetchone()

            if deck :
                return False

            cursor.execute(
                query, (name, description, category)
            )
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ocurrio un error en la base de datos: {e}")
            conn.rollback()
        finally :
            cursor.close()


    def insert_card(self, deck_id, front, back) :
        db = Database()
        conn = db.get_connection()

        cursor = conn.cursor()

        query = "INSERT INTO cards (deck_id, front, back) VALUES (?,?,?)"

        try :
            cursor.execute(
                query, (deck_id, front, back)
            )
            conn.commit()
            return True
        except sqlite3.Error as e :
            print(f"Ocurrio un error en la base de datos: {e}")
            conn.commit()
        finally :
            cursor.close()


    '''
    Obtener los mazos
    '''
    def get_decks(self) :
        db = Database()
        conn = db.get_connection()
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        query = "SELECT id, name FROM decks"
        try :
            cursor.execute(
                query
            )

            rows = cursor.fetchall()

            if not rows :
                return []

            decks = [{"id": row["id"], "name": row["name"]} for row in rows]
            conn.commit()
            return decks
        except sqlite3.Error as e :
            print(f"Ocurrio un error en la base de datos: {e}")
            conn.rollback()
        finally :
            cursor.close()

    def delete_deck(self, deck_id) :
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()

        query = """
        DELETE from decks
        WHERE id = ?
        """

        try :
            cursor.execute(query,
            (deck_id,)
            )
            conn.commit()
            return True
        except sqlite3.Error as e :
            print(f"Ocurrio un error en la base de datos: {e}")
            conn.rollback()
            return False
        finally :
            cursor.close()

