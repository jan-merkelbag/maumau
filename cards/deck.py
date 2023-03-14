import json
from random import shuffle
from typing import List, Tuple

from .card import Card, IndexedSymbol


class Deck:
    cards: List[Card]
    faces: List[IndexedSymbol]
    """ Faces available in the pack. """
    ranks: List[IndexedSymbol]
    """ Ranks available in the pack. """

    def __init__(self, deck_data: any = None):
        self.cards = []
        if isinstance(deck_data, str):
            self.load_deck_file(deck_data)
        else:
            raise ValueError("Unknown deck data type!")

    @staticmethod
    def verify_deck_obj(obj: object) -> bool:
        if "faces" in obj and "ranks" in obj:
            return True
        return False

    def load_deck_file(self, deck_file: str) -> None:
        self.cards = []
        self.faces = []
        self.ranks = []

        with open(deck_file, "r") as fp:
            deck_obj = json.load(fp)
            if not self.verify_deck_obj(deck_obj):
                raise ValueError("Bad deck file!")

        for f_idx, face in enumerate(deck_obj["faces"]):
            face_obj = IndexedSymbol(f_idx, face)
            self.faces.append(face_obj)
            for r_idx, rank in enumerate(deck_obj["ranks"]):
                rank_obj = IndexedSymbol(r_idx, rank)
                self.ranks.append(face_obj)
                self.cards.append(Card(face_obj, rank_obj))

    def shuffle(self) -> None:
        shuffle(self.cards)

    def draw(self, count: int = 1) -> List[Card]:
        cards: List[Card] = []
        if count < 1:
            raise ValueError("It does not make sense to draw less than one card!")
        elif count > len(self.cards):
            raise RuntimeError(f"Cannot draw {count} cards when only {len(self.cards)} are left!")
        for i in range(count):
            cards.append(self.cards.pop())
        return cards

    def put_under(self, card: Card):
        self.cards.insert(0, card)

    def __str__(self) -> str:
        return f"{len(self.cards)} cards in deck: " + ", ".join([str(card) for card in self.cards])
