import abc
from typing import List, Callable

from cards import Hand, Card, IndexedSymbol


class BasePlayer(abc.ABC):
    name: str
    """ The player's name. """

    hand: Hand
    """ The hand of the player. """

    def __init__(self, name: str):
        """ Create a player with a name. """
        self.name = name
        self.hand = Hand()

    def choose_card(
            self,
            is_card_allowed: Callable[[Card], bool],
            current_card: Card,
            current_face: IndexedSymbol,
            cards_to_draw: int,
            active_players_card_count: List[int],
    ) -> int | str:
        """
        Choose card to play.
        :return: Index of the card in hand to play, or other actions.
        """
        raise NotImplementedError()

    def choose_face(
            self,
            current_face: IndexedSymbol,
            available_faces: List[IndexedSymbol],
    ) -> IndexedSymbol:
        """
        Choose the face the next player has to play.
        :return: The face chosen.
        """
        raise NotImplementedError()

    def choose_play_immediately(
            self,
            drawn_card: Card
    ) -> bool:
        """
        Choose whether to play the card just drawn immediately or keep it.
        :return: Whether card should be played.
        """
        raise NotImplementedError()

    def __str__(self) -> str:
        return self.name
