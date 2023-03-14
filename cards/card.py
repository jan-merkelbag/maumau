from typing import Tuple


class IndexedSymbol:
    index: int
    symbol: str

    def __init__(self, index: int, symbol: str):
        self.index = int(index)
        self.symbol = str(symbol)

    def __str__(self) -> str:
        return self.symbol

    def __eq__(self, other: "IndexedSymbol") -> bool:
        return self.index == other.index and self.symbol == other.symbol


class Card:
    face: IndexedSymbol
    rank: IndexedSymbol

    def __init__(self, face: IndexedSymbol, rank: IndexedSymbol):
        self.face = face
        self.rank = rank

    def __str__(self):
        return f"{self.face}{self.rank}"
