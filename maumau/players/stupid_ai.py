from random import shuffle
from typing import List, Callable

from cards import Card, IndexedSymbol
from .base import BasePlayer


class StupidAI(BasePlayer):
    def __init__(self, name: str):
        super().__init__(name=name)

    def choose_card(
            self,
            is_card_allowed: Callable[[Card], bool],
            current_card: Card,
            current_face: IndexedSymbol,
            cards_to_draw: int,
            active_players_card_count: List[int],
    ) -> int | str:
        shuffle(self.hand.cards)
        a_jake: int | None = None
        for idx, card in enumerate(self.hand.cards):
            if card.rank.symbol == "J":
                a_jake = idx
                continue  # don't waste Jakes
            if is_card_allowed(card):
                if (current_card.rank.symbol == "7" and card.rank.symbol == "7") \
                        or current_card.rank.symbol != "7" or cards_to_draw < 2:
                    return idx
        if a_jake is not None and cards_to_draw < 2:
            return a_jake
        return "d"

    def choose_face(
            self,
            current_face: IndexedSymbol,
            available_faces: List[IndexedSymbol],
    ) -> IndexedSymbol:
        face_counts: List[int] = [0] * len(available_faces)
        for card in self.hand.cards:
            face_counts[available_faces.index(card.face)] += 1
        return available_faces[max(range(len(face_counts)), key=lambda i: face_counts[i])]

    def choose_play_immediately(
            self,
            drawn_card: Card
    ) -> bool:
        return drawn_card.face.symbol not in ["J", "7"]  # do not waste "good" cards
