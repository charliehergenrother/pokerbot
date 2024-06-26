#!/usr/bin/env python3

import sys
from game import Game
import time

def process_args():
    argcounter = 1
    players = 2
    chips = 1000
    big_blind = 10
    double_hands = 20
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
            argcounter -= 1
        else:
            print("unrecognized argument", sys.argv[argcounter])
            sys.exit()
        argcounter += 2
    return players, chips, big_blind, double_hands, automated, verbose

def run_one_betting_round(game):
    while not (game.all_bets_even and game.all_players_acted) and not game.hand_winner:
        player = game.players[game.action]
        if not player.active:
            game.action = (game.action + 1) % len(game.players)
            continue
        game.status()
        if player.CPU:
            if player.chips:
                decision = player.bot.make_decision()
                print(decision)
            else:
                decision = "check"
            time.sleep(1)
        else:
            decision = input("What would you like to do? ").lower()
        if decision == "check":
            if game.bet_to_call > 0 and player.current_bet != game.bet_to_call and player.chips:
                print("You can't check, silly, there's a bet to call.")
                continue
            player.has_acted = True
        elif decision == "fold":
            player.hand = list()
            game.pot[player] += player.current_bet 
            player.current_bet = 0
            player.has_acted = True
        elif decision == "call":
            amount_called = min([game.bet_to_call, player.chips + player.current_bet])
            player.chips -= amount_called - player.current_bet
            player.current_bet = amount_called
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

def find_win_amounts(winner, player, game):
    player_amount_won = 0
    for opponent in game.players:
        print("From", opponent.ID + ": ", end='')
        check_mins = [player.max_win_per_player[opponent]]
        if game.pot[opponent] >= len(winner):
            check_mins.append(game.pot[opponent] // len(winner))
        elif game.pot[opponent] > 0:
            check_mins.append(1)
        else:
            check_mins.append(0)
        print(check_mins)
        opponent_amount_won = min(check_mins)
        player.chips += opponent_amount_won
        player_amount_won += opponent_amount_won
        game.pot[opponent] -= opponent_amount_won
        player.max_win_per_player[opponent] -= opponent_amount_won
    print("Winner:", player.ID, player_amount_won, "chips")

#TODO: when a player makes a bet that ends up being too big, he needs the difference back
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
    while game.pot_total:
        if game.verbose:
            for player in game.pot:
                print(player.ID, game.pot[player], end=', ')
            print()
        winner = game.hand_winner
        if not winner:
            winner = game.do_showdown()
        if game.verbose:
            if type(winner) != list:
                print("Big ol winner:", winner.ID)
        if type(winner) == list:
            for player in winner:
                find_win_amounts(winner, player, game)
        else:
            find_win_amounts([winner], winner, game)
    time.sleep(5)

def reset_for_new_hand():
    game.phase = 0
    game.community = list()
    for player in game.players:
        player.hand = list()
        player.current_bet = 0
        player.has_acted = 0
        for opponent in game.players:
            player.max_win_per_player[opponent] = player.chips
        game.pot[player] = 0
        if not player.chips and player not in game.eliminated_players:
            game.eliminated_players.append(player)
    game.dealer = (game.dealer + 1) % len(game.players)
    while not game.players[game.dealer].chips:
        game.dealer = (game.dealer + 1) % len(game.players)
    game.hands_until_double -= 1
    if game.hands_until_double == 0:
        game.big_blind *= 2
        total_chips = sum([player.chips for player in game.players])
        if game.big_blind > total_chips * 0.05:
            game.big_blind = round(total_chips * 0.05)
            if game.big_blind % 2:
                game.big_blind += 1
        game.hands_until_double = 20

if __name__ == "__main__":
    players, chips, big_blind, double_hands, automated, verbose = process_args()
    game = Game(players, chips, big_blind, double_hands, automated, verbose)
    
    while not game.winner():
        run_one_hand(game)
        reset_for_new_hand()

    num_players = int(players)
    for player in game.eliminated_players:
        print(num_players, end='')
        if num_players > 3:
            print('th: ', end='')
        elif num_players == 3:
            print('rd: ', end='')
        elif num_players == 2:
            print('nd: ', end='')
        print(player.ID)

    print("Winner:", game.winner().ID + "! Congratulations!")
    

