from functools import cmp_to_key
from typing import List

from .card import Card
from .deck import Deck


class Hand(Deck):
    def __init__(self):
        self.cards = []
        super(Deck, self).__init__()

    def sort(self) -> None:
        def compare(l: Card, r: Card):
            if l.face == r.face:
                return l.rank.index - r.rank.index
            return l.face.index - r.face.index

        self.cards.sort(key=cmp_to_key(compare))

    def draw_from(self, deck: Deck, count: int = 1) -> List[Card]:
        drawn_cards = deck.draw(count)
        self.cards += drawn_cards
        return drawn_cards

    def __str__(self) -> str:
        return f"{len(self.cards)} cards on hand: " + ", ".join([str(card) for card in self.cards])
