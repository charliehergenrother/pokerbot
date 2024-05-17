#!/usr/bin/env python3

import random

class Pokerbot:

    def __init__(self, game, player):
        self.game = game
        self.player = player

    def make_decision(self):
        if self.game.bet_to_call:
            if self.game.bet_to_call == self.player.current_bet:
                choices = ["check", "raise"]
            else:
                choices = ["call", "raise", "fold"]
        else:
            choices = ["check", "bet"]

        decision = random.choice(choices)
        if decision == "bet":
            return "bet " + str(min([random.choice(range(self.game.pot // 2, self.game.pot + 1)), self.player.chips]))
        elif decision == "raise":
            return "raise " + str(min([self.game.bet_to_call*2, self.player.chips + self.player.current_bet]))
        else:
            return decision
