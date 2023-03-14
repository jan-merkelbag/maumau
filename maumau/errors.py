from cards import Card, IndexedSymbol


class CardNotAllowedError(RuntimeError):
    def __init__(self,
                 card_to_play: Card,
                 last_played_card: Card,
                 next_face: IndexedSymbol
                 ):
        message = f"You are not allowed to play {card_to_play}!"
        if next_face != last_played_card.face and next_face != card_to_play.face:
            message = f"You are not allowed to play {card_to_play} because face {next_face} is expected!"
        elif last_played_card.rank != card_to_play.rank and last_played_card.face != card_to_play.face:
            message = f"You are not allowed to play {card_to_play} " \
                      f"because it matches neither last card {last_played_card}'s face nor rank!"
        super(RuntimeError, self).__init__(message)
