import time
from random import shuffle
from typing import List, Dict, Callable, Tuple

from cards import Deck, Hand, Card


class MauMau:
    deck: Deck
    table: Hand

    player_hands: Dict[str, Hand]
    finishers: List[str]

    cards_to_draw: int
    miss_turn: bool
    next_face: Tuple[int, str]

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

    @staticmethod
    def prompt_card(player_hand: Hand,
                    current_card: Card,
                    current_face: Tuple[int, str],
                    cards_to_draw: int,
                    active_players_card_count: Dict[str, int],
                    ) -> int | str:
        prompt = "Your hand is:\n"
        prompt += "\n".join([f"{idx + 1}: {card}" for idx, card in enumerate(player_hand.cards)])
        prompt += "\nd: draw"
        prompt += f"\n{current_card} lies on top of the table."
        if current_face != current_card.face:
            prompt += f" The current face is {current_face[1]}."
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
            or card.rank[1] == "J"

    def stupid_ai(self,
                  player_hand: Hand,
                  current_card: Card,
                  current_face: Tuple[int, str],
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
            if card.rank[1] == "J":
                a_jake = idx
                continue  # don't waste Jakes
            if self.is_card_allowed(card):
                if (current_card.rank[1] == 7 and card.rank[1] == 7) \
                        or current_card.rank[1] != 7 or cards_to_draw < 2:
                    return idx
        if a_jake is not None:
            return a_jake
        return "d"

    def pick_a_card(self,
                    choice_method: Callable[..., int | str],
                    player_hand: Hand,
                    current_card: Card,
                    current_face: Tuple[int, str],
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
                picked_card = player_hand.cards[choice]

                if not self.is_card_allowed(picked_card):
                    print("Bad choice!")
                else:
                    break
            except ValueError as e:
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
            if card.rank[1] == 7:
                count += 2
            else:
                break
        return count

    @staticmethod
    def prompt_face(player_hand: Hand,
                    current_face: Tuple[int, str],
                    available_faces: List[Tuple[int, str]],
                    ) -> Tuple[int, str]:
        prompt = "Your hand is:\n"
        prompt += "\n".join([f"{card}" for card in player_hand.cards])
        prompt += "\nAvailable faces:\n"
        prompt += "\n".join([f"{idx + 1}: {face[1]}" for idx, face in enumerate(available_faces)])
        prompt += "\nd: draw"
        prompt += f"\n{current_face[1]} is the current face."
        prompt += "\nWhich face do you choose? "
        choice = input(prompt)

        return available_faces[int(choice) - 1]

    @staticmethod
    def stupid_ai_face(player_hand: Hand,
                       current_face: Tuple[int, str],
                       available_faces: List[Tuple[int, str]],
                       ) -> Tuple[int, str]:
        face_counts: List[int] = [0] * len(available_faces)
        for card in player_hand.cards:
            face_counts[available_faces.index(card.face)] += 1
        return available_faces[max(range(len(face_counts)), key=lambda i: face_counts[i])]

    @staticmethod
    def pick_a_face(choice_method: Callable[..., Tuple[int, str]],
                    player_hand: Hand,
                    current_face: Tuple[int, str],
                    available_faces: List[Tuple[int, str]],
                    ) -> Tuple[int, str]:
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

    def draw_cards(self, player_name: str, player_hand: Hand):
        self.replenish_deck(self.cards_to_draw)
        if len(self.deck.cards) < self.cards_to_draw:
            self.cards_to_draw = len(self.deck.cards)
        if self.cards_to_draw > 0:
            player_hand.draw_from(self.deck, self.cards_to_draw)
            player_hand.sort()
        if self.cards_to_draw == 1:
            print(f"{player_name} drew a card, and has {len(player_hand.cards)} cards left.")
        else:
            print(f"{player_name} drew {self.cards_to_draw} cards, "
                  f"and has {len(player_hand.cards)} cards left.")
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

    def player_chains(self, player_hand: Hand, choice: int) -> bool:
        """
        Check if the player chained properly, and tell them otherwise.
        :param player_hand:
        :param choice:
        :return: Whether the player chained.
        """
        if self.cards_to_draw > 1 and player_hand.cards[choice].rank[1] != 7:
            print(f"You cannot play a {player_hand.cards[choice].rank[1]} in response to a 7!")
            print(f"You have to either draw {self.cards_to_draw} cards or chain with another 7!")
            return False
        return True

    def play_card(self,
                  player_is_protagonist: bool,
                  player_name: str,
                  player_hand: Hand,
                  choice: int
                  ) -> None:
        played_card = player_hand.cards.pop(choice)
        self.table.cards.append(played_card)
        print(f"{player_name} played {played_card}, and has {len(player_hand.cards)} cards left.")

        # Handle 7 - next player has to draw 2 cards or chain
        if played_card.rank[1] == 7:
            if self.cards_to_draw < 2:
                self.cards_to_draw = 0
            self.cards_to_draw += 2

        # Handle 8 - next player misses their turn
        if played_card.rank[1] == 8:
            self.miss_turn = True

        # Handle J - current player can change face to whatever they want
        if played_card.rank[1] == "J":
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
        print(f"{player_name} chose {self.next_face[1]} as the next face.")

    def run(self, protagonist: str | None = None):
        print(f"Table: {self.table.cards[-1]}")
        # In case of a 7, records how many cards are to be drawn if 7 chain is not continued
        self.cards_to_draw = 1  # Start at 1, because it is also used for normal drawing
        self.miss_turn = False  # Record if an 8 is played
        while True:
            for player_name, player_hand in self.player_hands.items():
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
                            self.draw_cards(player_name, player_hand)
                        elif isinstance(choice, int):
                            if not self.player_chains(player_hand, choice):
                                continue

                            self.play_card(player_is_protagonist, player_name, player_hand, choice)
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
