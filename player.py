#!/usr/bin/env python3

from pokerbot import Pokerbot

class Player:

    def __init__(self, ID, chips, auto, game):
        self.CPU = auto
        if auto:
            self.bot = Pokerbot(game, self)
        else:
            self.bot = None
        self.chips = chips
        self.ID = ID
        self.hand = list()
        self.current_bet = 0
        self.has_acted = False

    def print_hand(self):
        for card in self.hand:
            print(card.rank + card.suit, end=' ')
        print()

    def get_active(self):
        return len(self.hand)

    active = property(get_active)
