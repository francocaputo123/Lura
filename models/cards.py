import sqlite3
from db.connection import Database
from tools.algorithm import sm2

class Model :
    '''
        Encargado de todo lo referente a las cartas.
    '''

    '''
    Para las nuevas cartas se tomaran un total de 20 cada dia.
    Para establecer que una carta es "nueva" se ve si created_at = next_review.
    '''
    def new_cards(self, deck_id) :

        """
            Las nuevas cartas se componen de: created igual a next_review y también cartas que sean <= a la fecha de hoy.
            Todo se registra en cards_today que son todas las cartas que el usuario debe repasar hoy.

        """
        db = Database()
        conn = db.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        check_query = """
        SELECT COUNT(*) as total, SUM(reviewed) as reviewed FROM cards_today
        WHERE date_fetched = DATE('now') AND deck_id = ?;
        """

        try :
            """
                Si el usuario ya observo todas las cartas, el total y la suma de reviews bloquea el acceso a seguir en el dia.
            """
            cursor.execute(check_query, (deck_id,))
            current_sesion = cursor.fetchone()

            total = current_sesion["total"]

            reviewed = current_sesion["reviewed"] or 0

            current_sesion = total > 0

            if current_sesion and reviewed == total:
                return []

            if not current_sesion :
                cursor.execute("DELETE FROM cards_today WHERE date_fetched < DATE('now');")

                search_query = """
                SELECT id FROM cards
                WHERE deck_id = ?
                AND DATE(created_at) = next_review
                ORDER BY RANDOM()
                LIMIT 20;
                """
                cursor.execute(search_query, (deck_id,))
                rows = cursor.fetchall()

                if not rows:
                    return None

                insert_query = """
                INSERT INTO cards_today (card_id, deck_id) VALUES (?, ?);
                """
                for row in rows:
                    cursor.execute(insert_query, (row["id"], deck_id))

                self.get_reviews(deck_id)

                conn.commit()

            fetch_query = """
            SELECT
                c.id,
                c.deck_id,
                c.front,
                c.back,
                c.interval,
                c.repetitions,
                c.ease_factor,
                c.next_review,
                DATE(c.created_at) as created_at
            FROM
                cards c
            JOIN
                cards_today ct ON c.id = ct.card_id
            WHERE
                ct.date_fetched = DATE('now')
                AND ct.reviewed = 0
                AND ct.deck_id = ?;
            """
            cursor.execute(fetch_query, (deck_id,))
            rows = cursor.fetchall()

            if not rows :
                return None

            self.get_reviews(deck_id)

            return [
                {
                    "id": row["id"],
                    "deck_id": row["deck_id"],
                    "front": row["front"],
                    "back": row["back"],
                    "interval": row["interval"],
                    "repetitions": row["repetitions"],
                    "ease_factor": row["ease_factor"],
                    "next_review": row["next_review"],
                    "created_at": row["created_at"],
                }
                for row in rows
            ]

        except sqlite3.Error as e:
            print(f"Ocurrio un error en la base de datos: {e}")
            return []
        finally :
            cursor.close()

    def update_next_review(self, card_id, deck_id, quality ) :
        """
            Actualizacion de la carta segun la dificultad. EL algoritmo sm2 calcula en base a la dificultad que ingreso el usuario
            y los campos de la carta. Esto ajusta el intervalo para saber cuando se deberá mostrar en la siguiente ocasión.
        """
        db = Database()
        conn = db.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try :
            #primero, obtener los valores de la carta actual
            query_card = """
                SELECT
                    interval,
                    repetitions,
                    ease_factor
                FROM
                    cards
                WHERE id = ?
            """
            cursor.execute(query_card, (card_id,))
            card = cursor.fetchone()

            #obtener el resultado con el algoritmo
            result_sm = sm2(
                quality=quality,
                interval=card["interval"],
                repetitions=card["repetitions"],
                ease_factor=card["ease_factor"]
            )

            #si es menor a 1, necesitan revision hoy
            if result_sm["interval"] < 1 :
                query_card = """
                UPDATE cards
                SET interval = ?, repetitions = ?, ease_factor = ?,
                    next_review = datetime('now', '+15 minutes'),
                    updated_at = datetime('now')
                WHERE id = ?;
                """
                cursor.execute(query_card,(
                    result_sm["interval"],
                    result_sm["repetitions"],
                    result_sm["ease_factor"],
                    card_id
                ))

            else :
                query_card = """
                UPDATE cards
                SET interval = ?, repetitions = ?, ease_factor = ?,
                    next_review = date('now', '+' || CAST(? AS TEXT) || ' days'),
                    updated_at = datetime('now')
                WHERE id = ?;
                """

                cursor.execute(query_card,(
                    result_sm["interval"],
                    result_sm["repetitions"],
                    result_sm["ease_factor"],
                    int(result_sm["interval"]),
                    card_id
                ))

                #actulizamos las cartas de hoy asi no se vuelven a mostrar
                cursor.execute("""
                    UPDATE cards_today
                    SET
                        reviewed = 1
                    WHERE card_id = ?;
                """, (card_id,))

            query_review = """
            INSERT INTO reviews (card_id, quality) VALUES (?, ?);
            """
            cursor.execute(query_review, (card_id, quality))

            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ocurrio un error en la base de datos: {e}")
            conn.rollback()
        finally :
            cursor.close()

    def get_reviews(self, deck_id) :
        db = Database()
        conn = db.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try :
            query = """
            SELECT
                id,
                deck_id,
                front,
                back,
                interval,
                repetitions,
                ease_factor,
                next_review,
                created_at
            FROM
                cards
            WHERE id in(
                    SELECT
                        id
                    FROM
                        cards
                    WHERE deck_id = ?
                    AND next_review <= DATE('now')
                    AND DATE(created_at) != next_review
                    ORDER BY
                    RANDOM()
                    LIMIT 20
                );
            """
            cursor.execute(query, (deck_id,))
            rows = cursor.fetchall()

            if not rows :
                return None

            insert_query = """
                INSERT INTO cards_today (card_id, deck_id) VALUES(?,?)
            """

            for row in rows :
                cursor.execute(insert_query, (row["id"], row["deck_id"]))

            return True
        except sqlite3.Error as e:
            print(f"Ocurrio un error en la base de datos: {e}")
            return None
        finally :
            cursor.close()
