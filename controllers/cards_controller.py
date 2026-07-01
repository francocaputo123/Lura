from db.connection import Database
from models.cards import Model

class CardController :

    def new_cards(self, deck_id) :
        if not deck_id :
            raise ValueError("No has pasado el id del mazo")

        model = Model()

        cards = model.new_cards(deck_id)

        if not cards :
            return []

        grouped_cards = {}

        """
        Como la bd puede traer filas repetidas (si hay imagen y audio)
        se agupan en un solo array para cada uno y extraerlo despues
        """
        for row in cards:

            card_id = row["id"]
            if card_id not in grouped_cards:
                grouped_cards[card_id] = {
                    "id": row["id"],
                    "deck_id": row["deck_id"],
                    "front": row["front"],
                    "back": row["back"],
                    "interval": row["interval"],
                    "repetitions": row["repetitions"],
                    "ease_factor": row["ease_factor"],
                    "next_review": row["next_review"],
                    "created_at": row["created_at"],
                    "images": [],
                    "audios": []
                }

            if row["filename"]:
                if row["media_type"] == "image":
                    grouped_cards[card_id]["images"].append({
                        "type": "image",
                        "file": row["filename"],
                        "id": deck_id
                    })
                elif row["media_type"] == "audio":
                    grouped_cards[card_id]["audios"].append({
                        "type": "audio",
                        "file": row["filename"],
                        "id": deck_id
                    })

        return list(grouped_cards.values())

    def update_next_review(self, card_id, deck_id, quality) :
        if not card_id and not deck_id and not quality:
            raise ValueError("Faltan parametros.")

        model = Model()

        response = model.update_next_review(card_id, deck_id, quality)

        if not response :
            return False

        return response
