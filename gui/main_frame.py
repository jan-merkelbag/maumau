import sys
from random import shuffle
from threading import Thread
from typing import List

from maumau import BasePlayer, HumanPlayer, StupidAI, MauMau
from .generated.noname import MainFrame


class MyMainFrame(MainFrame):
    players: List[BasePlayer]
    engine: MauMau
    engine_worker: Thread | None

    def __init__(self, parent):
        super().__init__(parent)
        self.engine_worker = Thread(target=self.engine_worker_func)

    def __del__(self):
        if self.engine_worker is not None \
                and self.engine_worker.is_alive():
            self.engine_worker.join()
        super().__del__()

    def new_game(self, event):
        self.players = [
            HumanPlayer("Jan"),
            StupidAI("Alpha"),
            StupidAI("Beta"),
            StupidAI("Gamma"),
        ]
        shuffle(self.players)

        for player in self.players:
            self.m_listBox_playerList.Append(item=str(player))

        self.engine = MauMau(self.players)
        self.engine.init()
        #self.engine_worker.run()
        self.engine_worker_func()

    def close(self, event):
        sys.exit()

    def set_active_player(self, idx: int):
        self.m_listBox_playerList.Select(idx)

    def engine_worker_func(self):
        for idx, player in enumerate(self.players):
            self.set_active_player(idx)
            self.engine.step_player_turn(player, 0)
