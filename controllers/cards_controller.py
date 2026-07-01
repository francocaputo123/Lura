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

        return cards

    def update_next_review(self, card_id, deck_id, quality) :
        if not card_id and not deck_id and not quality:
            raise ValueError("Faltan parametros.")

        model = Model()

        response = model.update_next_review(card_id, deck_id, quality)


        if not response :
            return False

        return response
