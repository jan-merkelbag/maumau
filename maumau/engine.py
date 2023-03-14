import time
from random import shuffle
from typing import List, Dict, Callable

from cards import Deck, Hand, Card
from cards.card import IndexedSymbol
from .errors import CardNotAllowedError


class MauMau:
    DEBUG: bool = False

    deck: Deck
    table: Hand

    player_hands: Dict[str, Hand]
    finishers: List[str]

    cards_to_draw: int
    miss_turn: bool
    next_face: IndexedSymbol

    def __init__(self, player_names: List[str]):
        self.deck = Deck("./packs/french_32.json")
        self.table = Hand()
        self.player_hands = {}
        self.finishers = []

        self.deck.shuffle()

        for player_name in player_names:
            if player_name in self.player_hands:
                raise ValueError("Cannot have multiple players with identical names!")
            self.player_hands[player_name] = Hand()
            self.player_hands[player_name].draw_from(self.deck, 5)
            self.player_hands[player_name].sort()

        self.table.draw_from(self.deck, 1)
        self.next_face = self.table.cards[-1].face

    # noinspection PyUnusedLocal
    @staticmethod
    def prompt_card(player_hand: Hand,
                    current_card: Card,
                    current_face: IndexedSymbol,
                    cards_to_draw: int,
                    active_players_card_count: Dict[str, int],
                    ) -> int | str:
        prompt = "Your hand is:\n"
        prompt += "\n".join([f"{idx + 1}: {card}" for idx, card in enumerate(player_hand.cards)])
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

    def is_card_allowed(self, card: Card) -> bool:
        # Valid if any of the following is valid:
        # - matches current face
        # - matches previous card's rank
        # - is a Jake
        return card.face == self.next_face \
            or card.rank == self.table.cards[-1].rank \
            or card.rank.symbol == "J"

    # noinspection PyUnusedLocal
    def stupid_ai(self,
                  player_hand: Hand,
                  current_card: Card,
                  current_face: IndexedSymbol,
                  cards_to_draw: int,
                  active_players_card_count: Dict[str, int],
                  ) -> int | str:
        """
        Issue: Given a 7, AI will always try to match or draw otherwise.
        However, it should only do so if the 7 actually applies to them.
        -> More inputs:
          * player hand
          * current card on table
          * whether player is affected by it (in case of a 7 only)
          * active players count
          * hand size of each player
        """
        shuffle(player_hand.cards)
        a_jake: int | None = None
        for idx, card in enumerate(player_hand.cards):
            if card.rank.symbol == "J":
                a_jake = idx
                continue  # don't waste Jakes
            if self.is_card_allowed(card):
                if (current_card.rank.symbol == "7" and card.rank.symbol == "7") \
                        or current_card.rank.symbol != "7" or cards_to_draw < 2:
                    return idx
        if a_jake is not None and cards_to_draw < 2:
            return a_jake
        return "d"

    def pick_a_card(self,
                    choice_method: Callable[..., int | str],
                    player_hand: Hand,
                    current_card: Card,
                    current_face: IndexedSymbol,
                    cards_to_draw: int,
                    active_players_card_count: Dict[str, int],
                    ) -> int | str:
        while True:
            choice = choice_method(player_hand=player_hand,
                                   current_card=current_card,
                                   current_face=current_face,
                                   cards_to_draw=cards_to_draw,
                                   active_players_card_count=active_players_card_count)
            try:
                choice = int(choice)
                if choice > len(player_hand.cards) - 1 or choice < 0:
                    print("Invalid option!")
                    continue
                break
            except ValueError:
                if choice in ["d"]:
                    break
                elif choice == "!":
                    print(f"DEBUGGING:\n"
                          + "\n".join(['%s: %s' % (p, h) for p, h in self.player_hands.items()])
                          + f"\nTable: {self.table}")
                else:
                    print("Invalid option!")
                    continue

        return choice

    def print_scoreboard(self):
        for player_name in self.player_hands.keys():
            if player_name not in self.finishers:
                self.finishers.append(player_name)
                break
        print("Game over!\nScore board:")
        print("\n".join([f"{idx + 1}.: {pn}" for idx, pn in enumerate(self.finishers)]))

    def replenish_deck(self, min_cnt: int | None = None) -> None:
        """
        Replenish deck if it has less than min_cnt cards. If None is passed, the deck will be replenished regardless.
        :param min_cnt: (optional) The required amount of cards. If the deck contains more cards, do not replenish.
        :return: Nothing.
        """
        if min_cnt is None or len(self.deck.cards) < min_cnt:
            old_cards = self.table.cards[:-1]
            shuffle(old_cards)
            self.deck.cards = old_cards + self.deck.cards
            self.table.cards = self.table.cards[-1:]
            print("Deck was replenished")

    def get_draw_count(self):
        count = 0
        for card in reversed(self.table.cards):
            if card.rank.symbol == "7":
                count += 2
            else:
                break
        return count

    @staticmethod
    def prompt_face(player_hand: Hand,
                    current_face: IndexedSymbol,
                    available_faces: List[IndexedSymbol],
                    ) -> IndexedSymbol:
        prompt = "Your hand is:\n"
        prompt += "\n".join([f"{card}" for card in player_hand.cards])
        prompt += "\nAvailable faces:\n"
        prompt += "\n".join([f"{idx + 1}: {face.symbol}" for idx, face in enumerate(available_faces)])
        prompt += "\nd: draw"
        prompt += f"\n{current_face.symbol} is the current face."
        prompt += "\nWhich face do you choose? "
        choice = input(prompt)

        return available_faces[int(choice) - 1]

    # noinspection PyUnusedLocal
    @staticmethod
    def stupid_ai_face(player_hand: Hand,
                       current_face: IndexedSymbol,
                       available_faces: List[IndexedSymbol],
                       ) -> IndexedSymbol:
        face_counts: List[int] = [0] * len(available_faces)
        for card in player_hand.cards:
            face_counts[available_faces.index(card.face)] += 1
        return available_faces[max(range(len(face_counts)), key=lambda i: face_counts[i])]

    @staticmethod
    def pick_a_face(choice_method: Callable[..., IndexedSymbol],
                    player_hand: Hand,
                    current_face: IndexedSymbol,
                    available_faces: List[IndexedSymbol],
                    ) -> IndexedSymbol:
        while True:
            chosen_face = choice_method(player_hand=player_hand,
                                        current_face=current_face,
                                        available_faces=available_faces)
            try:
                available_faces.index(chosen_face)
                break

            except ValueError:
                print("Invalid option!")
                continue

        return chosen_face

    # noinspection PyUnusedLocal
    @staticmethod
    def prompt_to_play_drawn_card(player_hand: Hand, drawn_card: Card):
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

    # noinspection PyUnusedLocal
    @staticmethod
    def stupid_ai_choose_to_play_drawn_card(player_hand: Hand, drawn_card: Card) -> bool:
        return drawn_card.face.symbol not in ["J", "7"]  # do not waste "good" cards

    def choose_to_play_drawn_card(self, player_is_protagonist: bool, player_hand: Hand, drawn_card: Card) -> bool:
        choose_func = self.stupid_ai_choose_to_play_drawn_card  # AI move
        if player_is_protagonist:  # human move
            choose_func = self.prompt_to_play_drawn_card
        return choose_func(player_hand=player_hand, drawn_card=drawn_card)

    def draw_cards(self, player_is_protagonist: bool, player_name: str, player_hand: Hand):
        self.replenish_deck(self.cards_to_draw)
        if len(self.deck.cards) < self.cards_to_draw:
            self.cards_to_draw = len(self.deck.cards)
        if self.cards_to_draw > 0:
            drawn_cards = player_hand.draw_from(self.deck, self.cards_to_draw)
            if self.cards_to_draw == 1:
                print(f"{player_name} drew a card, and has {len(player_hand.cards)} cards left.")
                if self.is_card_allowed(drawn_cards[0]) \
                        and self.choose_to_play_drawn_card(player_is_protagonist, player_hand, drawn_cards[0]):
                    self.play_card(player_is_protagonist, player_name, player_hand, -1)
            else:
                print(f"{player_name} drew {self.cards_to_draw} cards, "
                      f"and has {len(player_hand.cards)} cards left.")
            player_hand.sort()
        self.cards_to_draw = 1

    def choose_action(self, player_is_protagonist: bool, player_hand: Hand) -> int | str:
        picker_func = self.stupid_ai  # AI move
        if player_is_protagonist:  # human move
            picker_func = self.prompt_card

        return self.pick_a_card(choice_method=picker_func,
                                player_hand=player_hand,
                                current_card=self.table.cards[-1],
                                current_face=self.next_face,
                                cards_to_draw=self.cards_to_draw,  # the only affection so far
                                active_players_card_count={pn: len(ph.cards) for pn, ph in
                                                           self.player_hands.items()})

    def enforce_chain(self, picked_card: Card) -> bool:
        """
        Check if the player needs to chain and chained properly.
        :return: Whether the player needed to and did chain.
        """
        if self.cards_to_draw > 1 and picked_card.rank.symbol != "7":
            print(f"You cannot play a {picked_card.rank.symbol} in response to a 7!")
            print(f"You have to either draw {self.cards_to_draw} cards or chain with another 7!")
            return False
        return True

    def play_card(self,
                  player_is_protagonist: bool,
                  player_name: str,
                  player_hand: Hand,
                  choice: int
                  ) -> None:
        if not self.is_card_allowed(player_hand.cards[choice]):
            raise CardNotAllowedError(player_hand.cards[choice], self.table.cards[-1], self.next_face)

        played_card = player_hand.cards.pop(choice)
        self.table.cards.append(played_card)
        print(f"{player_name} played {played_card}, and has {len(player_hand.cards)} cards left.")

        # Handle 7 - next player has to draw 2 cards or chain
        if played_card.rank.symbol == "7":
            if self.cards_to_draw < 2:
                self.cards_to_draw = 0
            self.cards_to_draw += 2

        # Handle 8 - next player misses their turn
        if played_card.rank.symbol == "8":
            self.miss_turn = True

        # Handle J - current player can change face to whatever they want
        if played_card.rank.symbol == "J":
            self.choose_face(player_is_protagonist, player_name, player_hand)
        else:
            self.next_face = played_card.face

    def choose_face(self, player_is_protagonist: bool, player_name: str, player_hand: Hand):
        face_picker_func = self.stupid_ai_face  # AI move
        if player_is_protagonist:  # human move
            face_picker_func = self.prompt_face
        self.next_face = self.pick_a_face(choice_method=face_picker_func,
                                          player_hand=player_hand,
                                          current_face=self.table.cards[-2].face,
                                          available_faces=self.deck.faces)
        print(f"{player_name} chose {self.next_face.symbol} as the next face.")

    def run(self, protagonist: str | None = None):
        print(f"Table: {self.table.cards[-1]}")
        # In case of a 7, records how many cards are to be drawn if 7 chain is not continued
        self.cards_to_draw = 1  # Start at 1, because it is also used for normal drawing
        self.miss_turn = False  # Record if an 8 is played
        turn = 0
        while True:
            turn += 1
            for player_name, player_hand in self.player_hands.items():

                if self.DEBUG:
                    print("============\n"
                          "DEBUGGING\n"
                          "------------\n"
                          f"Current turn: {turn}\n"
                          f"Table hand: {[str(card.face) + str(card.rank) for card in self.table.cards]}\n"
                          "%s\n"
                          f"Next face: {self.next_face}\n"
                          f"Miss turn: {self.miss_turn}\n"
                          f"Cards to draw: {self.cards_to_draw}\n"
                          "============\n" % ("\n".join([f"{pn}: {ph}" for pn, ph in self.player_hands.items()]),))

                if player_name in self.finishers:
                    continue

                player_is_protagonist = protagonist is not None and player_name == protagonist

                self.replenish_deck(1)

                if self.miss_turn:
                    self.miss_turn = False
                    print(f"{player_name} is skipped due to card, and has {len(player_hand.cards)} cards left")
                    continue

                def do_player_turn():
                    # Force to draw or chain in case of a 7
                    while True:
                        choice = self.choose_action(player_is_protagonist, player_hand)

                        if choice == "d":
                            self.draw_cards(player_is_protagonist, player_name, player_hand)
                        elif isinstance(choice, int):
                            if not self.enforce_chain(player_hand.cards[choice]):
                                continue

                            try:
                                self.play_card(player_is_protagonist, player_name, player_hand, choice)
                            except CardNotAllowedError as e:
                                print(e)
                                continue
                        else:
                            raise Exception("Unexpected choice")
                        break

                do_player_turn()
                sleep_time = 1
                if protagonist is None or protagonist in self.finishers:
                    sleep_time = .1
                time.sleep(sleep_time)

                if len(player_hand.cards) == 0:
                    self.finishers.append(player_name)
                    print(f"{player_name} finished!")
                    if len(self.player_hands) - len(self.finishers) < 2:
                        self.print_scoreboard()
                        return