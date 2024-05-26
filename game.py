#!/usr/bin/env python3

from deck import Deck
from player import Player
import random

ALL_RANKS = ["A", "K", "Q", "J", "10", "9", "8", "7", "6", "5", "4", "3", "2"]
ALL_SUITS = ["C", "S", "H", "D"]
ALL_HAND_RANKS = ["royal flush", "straight flush", "four of a kind", "full house", \
        "flush", "straight", "three of a kind", "two pair", "one pair", "high card"]
PHASES = ["predeal", "preflop", "flop", "turn", "river"]

PLAYERS = {
    2: "Connor",
    3: "Brandon",
    4: "Pete",
    5: "David",
    6: "Nick",
    7: "Matt",
    8: "Michael",
    9: "Carson"
}

class Game:

    def __init__(self, players, chips, big_blind, double_hands, automated, verbose):
        self.players = list()
        for i in range(1, players + 1):
            if i != 1 or automated:
                self.players.append(Player(PLAYERS[i], chips, True, self))
            else:
                self.players.append(Player("Charlie", chips, False, self))
        for player in self.players:
            player.max_win_per_player = dict()
            for opponent in self.players:
                player.max_win_per_player[opponent] = chips

        random.shuffle(self.players)
        
        self.deck = Deck()
        
        self.big_blind = big_blind
        self.dealer = 0

        self.double_hands = double_hands
        self.hands_until_double = double_hands

        self.phase = 0

        self.pot = dict()
        for player in self.players:
            self.pot[player] = 0
        
        self.community = list()
        self.verbose = verbose

    def winner(self):
        chip_holders = False
        for player in self.players:
            if player.chips > 0:
                if chip_holders:
                    return False
                chip_holders = True
        return player

    def deal(self):
        self.deck = Deck()
        self.deck.shuffle()
        for _ in range(2):
            for player in self.players:
                if player.chips > 0:
                    player.hand.append(self.deck.cards.pop(0))

        self.phase += 1

    def find_blind(self, position):
        blind_player = -1
        while blind_player == -1:
            if position >= len(self.players):
                position = 0
            if self.players[position].chips > 0:
                blind_player = position
            position += 1
        return blind_player

    def take_one_blind(self, player, blind):
        if player.chips >= blind:
            player.chips -= blind
            player.current_bet += blind
        #TODO: what if the player can't cover the blind?

    def take_blinds(self):
        small_blind_player = self.find_blind(self.dealer + 1)
        big_blind_player = self.find_blind(small_blind_player + 1)
        small_blind = self.big_blind // 2
        self.take_one_blind(self.players[small_blind_player], small_blind)
        self.take_one_blind(self.players[big_blind_player], self.big_blind)
        self.action = (big_blind_player + 1) % len(self.players)

    def start_phase(self):
        self.action = (self.dealer + 1) % len(self.players)

    def complete_phase(self):
        for player in self.players:
            self.pot[player] += player.current_bet
            player.current_bet = 0
            player.has_acted = False
        self.phase += 1

    def do_community(self):
        if PHASES[self.phase] == "flop":
            self.do_flop()
        else:
            self.do_turn_river(PHASES[self.phase])
        self.start_phase()

    def do_flop(self):
        print()
        print("FLOP:", end='')
        for _ in range(3):
            card = self.deck.cards.pop()
            self.community.append(card)
            print(card.rank + card.suit + ' ', end='')
        print()

    def do_turn_river(self, phase):
        print()
        print(phase + ":", end='')
        self.community.append(self.deck.cards.pop())
        for card in self.community:
            print(card.rank + card.suit + ' ', end='')
        print()

    def get_hand_rank(self, player):
        ranks = [card.rank for card in player.hand + self.community]
        suits = [card.suit for card in player.hand + self.community]
        cards = [card.rank + card.suit for card in player.hand + self.community]

        #straight flush
        for suit in ALL_SUITS:
            if suits.count(suit) >= 5:
                for index, rank in enumerate((ALL_RANKS + ['A'])[:-4]):
                    found = True
                    for rank in (ALL_RANKS + ['A'])[index:index+5]:
                        if rank + suit not in cards:
                            found = False
                            break
                    if found:
                        if self.verbose:
                            print('straight flush!')
                        if rank == "A":
                            return "royal flush", [rank]
                        return "straight flush", [rank]
        if self.verbose:
            print('no straight flush')
        
        #four of a kind
        for rank in ALL_RANKS:
            if ranks.count(rank) == 4:
                if self.verbose:
                    print('four of a kind!')
                for tiebreaker_rank in ALL_RANKS:
                    if tiebreaker_rank != rank and tiebreaker_rank in ranks:
                        return "four of a kind", [rank, tiebreaker_rank]
        if self.verbose:
            print('no four of a kind')
    
        #full house
        for trips_rank in ALL_RANKS:
            if ranks.count(trips_rank) == 3:
                for pair_rank in ALL_RANKS:
                    if pair_rank != trips_rank and ranks.count(pair_rank) == 2:
                        if self.verbose:
                            print('full house!')
                        return "full house", [trips_rank, pair_rank]
        if self.verbose:
            print('no full house')

        #flush
        for suit in ALL_SUITS:
            if suits.count(suit) >= 5:
                if self.verbose:
                    print('flush!')
                tiebreakers = list()
                for rank in ALL_RANKS:
                    if rank + suit in cards:
                        tiebreakers.append(rank)
                    if len(tiebreakers) == 5:
                        return "flush", tiebreakers
        if self.verbose:
            print('no flush')

        #straight
        for index, rank in enumerate((ALL_RANKS + ['A'])[:-4]):
            found = True
            for rank in (ALL_RANKS + ['A'])[index:index+5]:
                if rank not in ranks:
                    found = False
                    break
            if found:
                if self.verbose:
                    print('straight!')
                return "straight", [rank]
        if self.verbose:
            print('no straight')

        #three of a kind
        for rank in ALL_RANKS:
            if ranks.count(rank) == 3:
                if self.verbose:
                    print('three of a kind!')
                tiebreakers = [rank]
                for tiebreaker_rank in ALL_RANKS:
                    if tiebreaker_rank != rank and tiebreaker_rank in ranks:
                        tiebreakers.append(tiebreaker_rank)
                    if len(tiebreakers) == 3:
                        return "three of a kind", tiebreakers
        if self.verbose:
            print('no three of a kind')

        #two pair
        for high_rank in ALL_RANKS:
            if ranks.count(high_rank) == 2:
                for low_rank in ALL_RANKS:
                    if low_rank != high_rank and ranks.count(low_rank) == 2:
                        if self.verbose:
                            print('two pair!')
                        for tiebreaker_rank in ALL_RANKS:
                            if tiebreaker_rank != high_rank and tiebreaker_rank != low_rank and \
                                    tiebreaker_rank in ranks:
                                return "two pair", [high_rank, low_rank, tiebreaker_rank]
        if self.verbose:
            print('no two pair')

        #one pair
        for pair_rank in ALL_RANKS:
            if ranks.count(pair_rank) == 2:
                if self.verbose:
                    print('pair!')
                tiebreakers = [pair_rank]
                for tiebreaker_rank in ALL_RANKS:
                    if tiebreaker_rank != pair_rank and tiebreaker_rank in ranks:
                        tiebreakers.append(tiebreaker_rank)
                    if len(tiebreakers) == 4:
                        return "one pair", tiebreakers
        if self.verbose:
            print('no pair')

        #high card
        tiebreakers = []
        for rank in ALL_RANKS:
            if rank in ranks:
                tiebreakers.append(rank)
            if len(tiebreakers) == 5:
                return "high card", tiebreakers

    def do_showdown(self):
        hand_ranks = list()
        for player in self.players:
            if player.active:
                found_winnable_chips = False
                if self.verbose:
                    print("POT: ", end='')
                    for opponent in self.players:
                        print(opponent.ID + ":", self.pot[opponent], end=', ')
                    print()
                    print("MAX WIN PER PLAYER FOR", player.ID + ': ', end='')
                    for opponent in self.players:
                        print(opponent.ID + ":", player.max_win_per_player[opponent], end=', ')
                    print()
                for opponent in self.players:
                    if self.pot[opponent] > 0 and player.max_win_per_player[opponent] > 0:
                        found_winnable_chips = True
                        break
                if not found_winnable_chips:
                    if self.verbose:
                        print(player.ID, "has no winnable chips")
                    player.hand = list()
                    player.rank = "fold"
                    player.tiebreakers = []
                    continue
                if self.verbose:
                    print(player.ID)
                player.rank, player.tiebreakers = self.get_hand_rank(player)
                hand_ranks.append(player.rank)
            else:
                player.rank = "fold"
                player.tiebreakers = []
        if self.verbose:
            print(hand_ranks)
        for hand_rank in ALL_HAND_RANKS:
            if hand_rank in hand_ranks:
                print('With a', hand_rank + "...")
                if hand_ranks.count(hand_rank) == 1:
                    for player in self.players:
                        if player.rank == hand_rank:
                            return player
                tied_players = list()
                for player in self.players:
                    if player.rank == hand_rank:
                        tied_players.append(player)
                tiebreaker_index = 0
                while len(tied_players) > 1 and tiebreaker_index < len(tied_players[0].tiebreakers):
                    for rank in ALL_RANKS:
                        winner = list()
                        for player in tied_players:
                            if player.tiebreakers[tiebreaker_index] == rank:
                                winner.append(player)
                        if len(winner) >= 1:
                            tied_players = winner
                            tiebreaker_index += 1
                            break
                return winner


    def status(self):
        print()
        print()
        print("CURRENT STATUS")
        print("Big blind: " + str(self.big_blind))
        print("Hands until double: " + str(self.hands_until_double))
        print("Phase: " + PHASES[self.phase])
        print("Community: ", end='')
        for card in self.community:
            print(card.rank + card.suit, end=' ')
        print()
        print("Pot:", sum([self.pot[player] for player in self.players]))
        print()
        print()
        for index, player in enumerate(self.players):
            print(player.ID, str(player.chips) + " chips ", end='')
            if self.phase > 0 and player.active:
                print(player.hand[0].rank + player.hand[0].suit + ' ' + \
                        player.hand[1].rank + player.hand[1].suit, end='')
            if index == self.dealer:
                print(' D', end='')
            if index == self.action:
                print(' <---')
            else:
                print()
            if player.active:
                if player.current_bet:
                    print("Current bet: " + str(player.current_bet))
            print()
        print("Action: " + self.players[self.action].ID)
        if self.bet_to_call:
            if self.bet_to_call == self.players[self.action].current_bet:
                print("Check, Raise, or Fold")
            else:
                print("Call " + str(self.bet_to_call) + ", Raise, or Fold")
        else:
            print("Check, Bet, or Fold")

    


    def get_bet_to_call(self):
        return max([player.current_bet for player in self.players])

    def get_all_players_acted(self):
        for player in self.players:
            if player.active and not player.has_acted:
                return False
        return True

    def get_all_bets_even(self):
        max_bet = self.bet_to_call
        for player in self.players:
            if player.active and player.current_bet != max_bet and player.chips != 0:
                return False
            #TODO: fix split pots
        return True

    def get_hand_winner(self):
        has_cards = False
        for player in self.players:
            if player.active:
                if has_cards:
                    return False
                has_cards = player
        return has_cards

    def get_pot_total(self):
        return sum([self.pot[player] for player in self.players])

    bet_to_call = property(get_bet_to_call)
    all_players_acted = property(get_all_players_acted)
    all_bets_even = property(get_all_bets_even)
    hand_winner = property(get_hand_winner)
    pot_total = property(get_pot_total)



