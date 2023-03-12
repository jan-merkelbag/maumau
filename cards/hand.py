from functools import cmp_to_key

from .card import Card
from .deck import Deck


class Hand(Deck):
    def __init__(self):
        self.cards = []
        super(Deck, self).__init__()

    def sort(self) -> None:
        def compare(l: Card, r: Card):
            if l.face == r.face:
                return l.rank[0] - r.rank[0]
            return l.face[0] - r.face[0]

        self.cards.sort(key=cmp_to_key(compare))

    def draw_from(self, deck: Deck, count: int = 1) -> None:
        self.cards += deck.draw(count)

    def __str__(self) -> str:
        return f"{len(self.cards)} cards on hand: " + ", ".join([str(card) for card in self.cards])
