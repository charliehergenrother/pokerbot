#!/usr/bin/env python3

import random

class Pokerbot:

    def __init__(self, game, player):
        self.game = game
        self.player = player

    def make_decision(self):
        if self.game.bet_to_call:
            choices = list()
            if self.game.bet_to_call < self.player.current_bet + self.player.chips:
                choices.append("raise")
            if self.game.bet_to_call == self.player.current_bet:
                choices.append("check")
            else:
                choices += ["call", "fold"]
        elif self.player.current_max_bet > 0:
            choices = ["check", "bet"]
        else:
            return "check"

        decision = random.choice(choices)
        if decision == "bet":
            return "bet " + str(min([random.choice(range(self.game.pot_total // 2, self.game.pot_total + 1)), self.player.chips, self.player.current_max_bet]))
        elif decision == "raise":
            return "raise " + str(min([self.game.bet_to_call*2, self.player.chips + self.player.current_bet, self.player.current_max_bet]))
        else:
            return decision
