from typing import List, Callable

from cards import Card, IndexedSymbol
from .base import BasePlayer


class HumanPlayer(BasePlayer):
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
        prompt = "Your hand is:\n"
        prompt += "\n".join([f"{idx + 1}: {card}" for idx, card in enumerate(self.hand.cards)])
        prompt += "\nd: draw"
        prompt += f"\n{current_card} lies on top of the table."
        if current_face != current_card.face:
            prompt += f" The current face is {current_face.symbol}."
        if current_card.rank.symbol in ["7", "8"]:
            if cards_to_draw > 1:
                prompt += f" If you chose to draw, you will have to draw {cards_to_draw} cards."
            else:
                prompt += " You are not affected by it."
        prompt += "\nWhich card do you want to play? "
        choice = input(prompt)

        try:
            return int(choice) - 1
        except ValueError:
            pass

        return choice

    def choose_face(
            self,
            current_face: IndexedSymbol,
            available_faces: List[IndexedSymbol],
    ) -> IndexedSymbol:
        prompt = "Your hand is:\n"
        prompt += "\n".join([f"{card}" for card in self.hand.cards])
        prompt += "\nAvailable faces:\n"
        prompt += "\n".join([f"{idx + 1}: {face.symbol}" for idx, face in enumerate(available_faces)])
        prompt += "\nd: draw"
        prompt += f"\n{current_face.symbol} is the current face."
        prompt += "\nWhich face do you choose? "
        choice = input(prompt)

        return available_faces[int(choice) - 1]

    def choose_play_immediately(
            self,
            drawn_card: Card
    ):
        while True:
            prompt = f"You drew {drawn_card}.\n"
            prompt += "y - play it\n"
            prompt += "n - keep it\n"
            prompt += "What do you want to do? "
            choice = input(prompt)
            if choice.lower() == "y":
                return True
            if choice.lower() == "n":
                return False
