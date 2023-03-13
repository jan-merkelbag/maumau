import time
from random import shuffle
from typing import List, Dict, Callable

from cards import Deck, Hand, Card


class MauMau:
    deck: Deck
    table: Hand

    player_hands: Dict[str, Hand]
    finishers: List[str]

    cards_to_draw: int
    miss_turn: bool

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

    @staticmethod
    def prompt_card(player_hand: Hand,
                    current_card: Card,
                    cards_to_draw: int,
                    active_players_card_count: Dict[str, int],
                    ) -> int | str:
        prompt = "Your hand is:\n"
        prompt += "\n".join([f"{idx + 1}: {card}" for idx, card in enumerate(player_hand.cards)])
        prompt += "\nd: draw"
        prompt += f"\n{current_card} lies on top of the table."
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
        # Identical face OR rank
        return card.face == self.table.cards[-1].face \
            or card.rank == self.table.cards[-1].rank

    def stupid_ai(self,
                  player_hand: Hand,
                  current_card: Card,
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
        for idx, card in enumerate(player_hand.cards):
            if self.is_card_allowed(card):
                if (current_card.rank[1] == 7 and card.rank[1] == 7) \
                        or current_card.rank[1] != 7 or cards_to_draw < 2:
                    return idx
        return "d"

    def pick_a_card(self,
                    choice_method: Callable,
                    player_hand: Hand,
                    current_card: Card,
                    cards_to_draw: int,
                    active_players_card_count: Dict[str, int],
                    ):
        while True:
            choice = choice_method(player_hand=player_hand,
                                   current_card=current_card,
                                   cards_to_draw=cards_to_draw,
                                   active_players_card_count=active_players_card_count, )
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

        return choice

    def print_scoreboard(self):
        for player_name in self.player_hands.keys():
            if player_name not in self.finishers:
                self.finishers.append(player_name)
                break
        print("Game over!\nScore board:")
        print("\n".join([f"{idx + 1}.: {pn}" for idx, pn in enumerate(self.finishers)]))

    def replenish_deck(self):
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

    def run(self, protagonist: str | None = None):
        print(f"Table: {self.table.cards[-1]}")
        # In case of a 7, records how many cards are to be drawn if 7 chain is not continued
        self.cards_to_draw = 1  # Start at 1, because it is also used for normal drawing
        self.miss_turn = False  # Record if an 8 is played
        while True:
            for player_name, player_hand in self.player_hands.items():
                if player_name in self.finishers:
                    continue

                if len(self.deck.cards) < 1:
                    self.replenish_deck()

                if self.miss_turn:
                    self.miss_turn = False
                    print(f"{player_name} is skipped due to card, and has {len(player_hand.cards)} cards left")
                    continue

                def do_player_turn():
                    # Force to draw or chain in case of a 7
                    while True:
                        picker_func = self.stupid_ai  # AI move
                        if protagonist is not None and player_name == protagonist:  # human move
                            picker_func = self.prompt_card

                        choice = self.pick_a_card(choice_method=picker_func,
                                                  player_hand=player_hand,
                                                  current_card=self.table.cards[-1],
                                                  cards_to_draw=self.cards_to_draw,  # the only affection so far
                                                  active_players_card_count={pn: len(ph.cards) for pn, ph in
                                                                             self.player_hands.items()})
                        if choice == "d":
                            if len(self.deck.cards) < self.cards_to_draw:
                                self.replenish_deck()
                                if len(self.deck.cards) < self.cards_to_draw:
                                    self.cards_to_draw = len(self.deck.cards)
                            if self.cards_to_draw > 0:
                                player_hand.draw_from(self.deck, self.cards_to_draw)
                                player_hand.sort()
                            if self.cards_to_draw == 1:
                                print(f"{player_name} drew a card, and has {len(player_hand.cards)} cards left")
                            else:
                                print(f"{player_name} drew {self.cards_to_draw} cards, "
                                      f"and has {len(player_hand.cards)} cards left")
                            self.cards_to_draw = 1
                        else:
                            if self.cards_to_draw > 1 and player_hand.cards[choice].rank[1] != 7:
                                print(f"You cannot play a {player_hand.cards[choice].rank[1]} in response to a 7!")
                                print(f"You have to either draw {self.cards_to_draw} cards or chain with another 7!")
                                continue
                            played_card = player_hand.cards.pop(choice)
                            self.table.cards.append(played_card)
                            if played_card.rank[1] == 7:
                                if self.cards_to_draw < 2:
                                    self.cards_to_draw = 0
                                self.cards_to_draw += 2
                            elif played_card.rank[1] == 8:
                                self.miss_turn = True
                            print(f"{player_name} played {played_card}, and has {len(player_hand.cards)} cards left")
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
