from random import shuffle

from maumau import MauMau


def main():
    players = ["Jan", "Alpha", "Beta", "Gamma"]
    shuffle(players)
    maumau = MauMau(players)
    maumau.run("Jan")


if __name__ == '__main__':
    main()
