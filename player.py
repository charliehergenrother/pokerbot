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
        self.max_win_per_player = dict()
        self.game = game

    def print_hand(self):
        for card in self.hand:
            print(card.rank + card.suit, end=' ')
        print()

    def get_active(self):
        return len(self.hand)

    def get_max_bet(self):
        max_bet = 0
        for player in self.game.players:
            if player.ID == self.ID:
                continue
            if not player.active:
                continue
            if max_bet < player.chips + player.current_bet:
                max_bet = player.chips + player.current_bet
        return min([max_bet, self.chips + self.current_bet])

    active = property(get_active)
    current_max_bet = property(get_max_bet)





