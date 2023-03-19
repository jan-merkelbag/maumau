import time
from random import shuffle
from typing import List, Dict, Callable

from cards import Deck, Hand, Card
from cards.card import IndexedSymbol
from .errors import CardNotAllowedError
from .players import BasePlayer, HumanPlayer


class MauMau:
    DEBUG: bool = False

    deck: Deck
    table: Hand

    players: List[BasePlayer]
    finishers: List[BasePlayer]

    cards_to_draw: int
    miss_turn: bool
    next_face: IndexedSymbol

    def __init__(self, players: List[BasePlayer]):
        self.deck = Deck("./packs/french_32.json")
        self.table = Hand()
        self.players = []
        self.finishers = []

        self.deck.shuffle()

        for player in players:
            if player in self.players:
                raise ValueError("Cannot have multiple players with identical names!")
            player.hand = Hand()
            player.hand.draw_from(self.deck, 5)
            player.hand.sort()
            self.players.append(player)

        self.table.draw_from(self.deck, 1)
        self.next_face = self.table.cards[-1].face

    def is_card_allowed(self, card: Card) -> bool:
        # Valid if any of the following is valid:
        # - matches current face
        # - matches previous card's rank
        # - is a Jake
        return card.face == self.next_face \
            or card.rank == self.table.cards[-1].rank \
            or card.rank.symbol == "J"

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
                          + "\n".join(['%s: %s' % (player.name, player.hand) for player in self.players])
                          + f"\nTable: {self.table}")
                else:
                    print("Invalid option!")
                    continue

        return choice

    def print_scoreboard(self):
        for player in self.players:
            if player not in self.finishers:
                self.finishers.append(player)
                break
        print("Game over!\nScore board:")
        print("\n".join([f"{idx + 1}.: {player.name}" for idx, player in enumerate(self.finishers)]))

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

    def draw_cards(self, player: BasePlayer):
        self.replenish_deck(self.cards_to_draw)
        if len(self.deck.cards) < self.cards_to_draw:
            self.cards_to_draw = len(self.deck.cards)
        if self.cards_to_draw > 0:
            drawn_cards = player.hand.draw_from(self.deck, self.cards_to_draw)
            if self.cards_to_draw == 1:
                print(f"{player.name} drew a card, and has {len(player.hand.cards)} cards left.")
                if self.is_card_allowed(drawn_cards[0]) \
                        and player.choose_play_immediately(drawn_card=drawn_cards[0]):
                    self.play_card(player, -1)
            else:
                print(f"{player.name} drew {self.cards_to_draw} cards, "
                      f"and has {len(player.hand.cards)} cards left.")
            player.hand.sort()
        self.cards_to_draw = 1

    def choose_action(self, player: BasePlayer) -> int | str:
        return player.choose_card(is_card_allowed=self.is_card_allowed,
                                  current_card=self.table.cards[-1],
                                  current_face=self.next_face,
                                  cards_to_draw=self.cards_to_draw,  # the only affection so far
                                  active_players_card_count=[len(player.hand.cards) for player in
                                                             self.players])

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
                  player: BasePlayer,
                  choice: int
                  ) -> None:
        if not self.is_card_allowed(player.hand.cards[choice]):
            raise CardNotAllowedError(player.hand.cards[choice], self.table.cards[-1], self.next_face)

        played_card = player.hand.cards.pop(choice)
        self.table.cards.append(played_card)
        print(f"{player.name} played {played_card}, and has {len(player.hand.cards)} cards left.")

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
            self.next_face = player.choose_face(current_face=self.table.cards[-2].face,
                                                available_faces=self.deck.faces)
            print(f"{player.name} chose {self.next_face.symbol} as the next face.")
        else:
            self.next_face = played_card.face

    def step_turn(self, turn_no: int = 0):
        for player in self.players:
            self.step_player_turn(player=player, turn_no=turn_no)

    def step_player_turn(self, player: BasePlayer, turn_no: int = 0):
        if self.DEBUG:
            print("============\n"
                  "DEBUGGING\n"
                  "------------\n"
                  f"Current turn: {turn_no}\n"
                  f"Table hand: {[str(card.face) + str(card.rank) for card in self.table.cards]}\n"
                  "%s\n"
                  f"Next face: {self.next_face}\n"
                  f"Miss turn: {self.miss_turn}\n"
                  f"Cards to draw: {self.cards_to_draw}\n"
                  "============\n" % ("\n".join([f"{player.name}: {player.hand}" for player in self.players]),))

        if player in self.finishers:
            return

        self.replenish_deck(1)

        if self.miss_turn:
            self.miss_turn = False
            print(f"{player.name} is skipped due to card, and has {len(player.hand.cards)} cards left")
            return

        def do_player_turn():
            # Force to draw or chain in case of a 7
            while True:
                choice = self.choose_action(player)

                if choice == "d":
                    self.draw_cards(player)
                elif isinstance(choice, int):
                    if not self.enforce_chain(player.hand.cards[choice]):
                        continue

                    try:
                        self.play_card(player, choice)
                    except CardNotAllowedError as e:
                        print(e)
                        continue
                else:
                    raise Exception("Unexpected choice")
                break

        do_player_turn()
        sleep_time = 1
        human_players_left = False
        for p in self.players:
            if isinstance(p, HumanPlayer):
                human_players_left = True
                break
        if not human_players_left:
            sleep_time = .1
        time.sleep(sleep_time)

        if len(player.hand.cards) == 0:
            self.finishers.append(player)
            print(f"{player.name} finished!")
            if len(self.players) - len(self.finishers) < 2:
                self.print_scoreboard()
                return

    def init(self):
        # In case of a 7, records how many cards are to be drawn if 7 chain is not continued
        self.cards_to_draw = 1  # Start at 1, because it is also used for normal drawing
        self.miss_turn = False  # Record if an 8 is played

    def run(self):
        print(f"Table: {self.table.cards[-1]}")
        self.init()
        turn = 0

        while True:
            turn += 1
            self.step_turn()
