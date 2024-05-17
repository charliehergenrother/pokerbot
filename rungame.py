#!/usr/bin/env python3

import sys
from game import Game
import time

def process_args():
    argcounter = 1
    players = 2
    chips = 1000
    big_blind = 10
    double_hands = -1
    automated = False
    verbose = False
    while argcounter < len(sys.argv):
        if sys.argv[argcounter] == '-h':
            print('Welcome to Pokerbot!')
            print('I play poker like nobody\'s business.')
            print()
            print('Usage: ./rungame.py [-p <players>] [-c <chips>] [-b <big blind>] [-d <blind length>] [-h]')
            print('     -p: start a game with <players> players. Default: 2')
            print('     -c: use this value as the starting chip amount for each player. Default: 1000')
            print('     -b: use this value as the starting big blind. Default: 10')
            print('     -d: wait this many hands before doubling the blinds. Default: 10*<players>')
            print('     -a: automate game. Default: one human player')
            print('     -v: verbose mode')
            print('     -h: print this help message.')
            sys.exit()
        elif sys.argv[argcounter] == '-p':
            players = int(sys.argv[argcounter + 1])
        elif sys.argv[argcounter] == '-c':
            chips = int(sys.argv[argcounter + 1])
        elif sys.argv[argcounter] == '-b':
            big_blind = int(sys.argv[argcounter + 1])
        elif sys.argv[argcounter] == '-d':
            double_hands = int(sys.argv[argcounter + 1])
        elif sys.argv[argcounter] == '-a':
            automated = True
        elif sys.argv[argcounter] == '-v':
            verbose = True
        else:
            print("unrecognized argument", sys.argv[argcounter])
            sys.exit()
        argcounter += 2
    if double_hands == -1:
        double_hands = 10*players
    return players, chips, big_blind, double_hands, automated, verbose

def run_one_betting_round(game):
    while not (game.all_bets_even and game.all_players_acted) and not game.hand_winner:
        player = game.players[game.action]
        if not player.active:
            game.action = (game.action + 1) % len(game.players)
            continue
        game.status()
        if player.CPU:
            decision = player.bot.make_decision()
            time.sleep(1)
        else:
            decision = input("What would you like to do? ").lower()
        if decision == "check":
            if game.bet_to_call > 0 and player.current_bet != game.bet_to_call:
                print("You can't check, silly, there's a bet to call.")
                continue
            player.has_acted = True
        elif decision == "fold":
            player.hand = list()
            game.pot += player.current_bet 
            player.current_bet = 0
            player.has_acted = True
        elif decision == "call":
            player.chips -= game.bet_to_call - player.current_bet
            player.current_bet = game.bet_to_call
            #TODO: going all in & split pots
            player.has_acted = True
        elif (decision.split(" ")[0] in ["raise", "bet"]) and int(decision.split(" ")[1]) > 0:
            amount = int(decision.split(" ")[1])
            if amount < game.bet_to_call:
                print("Raise must be higher than the current bet of", game.bet_to_call)
                continue
            if player.chips == 0:
                print("you cannot make a bet when you don't have any chips.")
                continue
            player.chips -= min([player.chips + player.current_bet, amount - player.current_bet])
            player.current_bet = amount
            player.has_acted = True
        else:
            print("Unrecognized decision. Type 'check', 'call', 'fold', 'raise <x>', or 'bet <x>'.")
            continue
        game.action = (game.action + 1) % len(game.players)
    print('Continuing game! Woohoo!')
    game.complete_phase()

def run_one_hand(game):
    game.deal()
    game.take_blinds()
    winner = False
    for i in range(4):
        run_one_betting_round(game)
        if game.hand_winner:
            break
        if i < 3:
            game.do_community()
        else:
            winner = game.do_showdown()
    if not winner:
        winner = game.hand_winner
    if type(winner) == list:
        for player in winner:
            #TODO: extra chips?
            print("Winner:", player.ID, game.pot // len(winner), "chips")
            player.chips += game.pot // len(winner)
    else:
        winner.chips += game.pot
        print("Winner:", winner.ID, game.pot, "chips")
    game.pot = 0
    game.phase = 0
    game.community = list()
    for player in game.players:
        player.hand = list()
        player.current_bet = 0
        player.has_acted = 0
    game.dealer = (game.dealer + 1) % len(game.players)
    game.hands_until_double -= 1
    if game.hands_until_double == 0:
        game.big_blind *= 2
        game.hands_until_double = len(game.players)*10

if __name__ == "__main__":
    players, chips, big_blind, double_hands, automated, verbose = process_args()
    game = Game(players, chips, big_blind, double_hands, automated, verbose)
    
    while not game.winner():
        run_one_hand(game)





