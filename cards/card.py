from typing import Tuple


class Card:
    face: Tuple[int, str]
    rank: Tuple[int, str]

    def __init__(self, face: Tuple[int, str], rank: Tuple[int, str]):
        self.face = face
        self.rank = rank

    def __str__(self):
        return f"{self.face[1]}{self.rank[1]}"
