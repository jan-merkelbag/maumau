from random import shuffle

from maumau import MauMau
from maumau import HumanPlayer, StupidAI


def main():
    players = [
        HumanPlayer("Jan"),
        StupidAI("Alpha"),
        StupidAI("Beta"),
        StupidAI("Gamma"),
    ]
    shuffle(players)
    maumau = MauMau(players)
    maumau.run()


if __name__ == '__main__':
    main()
