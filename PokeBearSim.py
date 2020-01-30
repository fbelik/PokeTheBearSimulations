import sys
import time
import pickle
class Card:
    names = ['2','3','4','5','6','7','8','9','10','J','Q','K','A','JK']
    suits = ['C','S','D','H']
    def __init__(self,num,suit):
        self.num = num
        self.suit = suit
        self.color = 'black'
        if self.suit in ['H','D']:
            self.color = 'red'
    def __repr__(self):
        return self.name()
    def value(self):
        try:
            n = int(self.num)
        except ValueError:
            if (self.num == 'J'):
                n = 11
            elif self.num == 'Q':
                n = 12
            elif self.num == 'K':
                n = 13
            elif self.num == 'A':
                n = 15
            elif self.num == 'JK':
                n = 14
            else:
                print("ERROR, UNKNOWN CARD")
                return -1
        return n
    def name(self):
        return "{} of {}".format(self.num, self.suit)
    def beats(self, card, trump):
        if self.suit == card.suit:
            return self.value() > card.value()
        elif card.suit == trump:
            return False
        else:
            return True

import random

class Deck:
    def __init__(self):
        self.cards = []
        self.discard = []
        nums = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
        suits = ['C','S','D','H']
        for suit in suits:
            for num in nums:
                self.cards.append(Card(num,suit))
        # Insert 2 jokers
        self.cards.append(Card('JK','1'))
        self.cards.append(Card('JK','2'))
    def shuffle_discard(self):
        all_cards = self.cards + self.discard
        self.cards = random.sample(all_cards, len(all_cards))
        self.discard = []
    def deal(self, num):
        ret = []
        # Remove last card from deck and return
        for i in range(num):
            if (len(self.cards) == 0):
                # Reshuffle cards if empty
                self.shuffle_discard()
            ret.append(self.cards.pop())
        return ret
    def copy(self):
        new = Deck()
        new.cards = []
        for card in self.cards:
            new.cards.append(card)
        for card in self.discard:
            new.discard.append(card)
        return new


class Player:
    def __init__(self,name):
        self.name = name
        self.hand = []
        self.spot = 0
        self.max_spot = 0
    def can_play(self, opp_card):
        poss = []
        for card in self.hand:
            if card.suit == opp_card.suit:
                poss.append(card)
        if len(poss) == 0:
            for card in self.hand:
                if card.num != 'JK':
                    poss.append(card)
        return poss
    def effect_cards(self):
        return [card for card in self.hand if card.num in ['2','J','Q','K']]
    def random_card2(self, card):
        cards = self.can_play(card)
        if len(cards) == 0:
            return self.random_card()
        else:
            selection = cards[random.randrange(len(cards))]
            self.hand.remove(selection)
            return selection
    def random_card(self):
        random.shuffle(self.hand)
        return self.hand.pop()
    def move_suit(self,suit):
        if suit == 'C':
            offset = 0
        elif suit == 'H':
            offset = 1
        elif suit == 'S':
            offset = 2
        elif suit == 'D':
            offset = 3
        else:
            self.move_suit(self.current_suit())
            return
        self.spot += 1
        while ((self.spot-offset) % 4 != 0):
            self.spot += 1
        if self.spot > self.max_spot:
            self.max_spot = self.spot
    def current_suit(self):
        offset = self.spot % 4
        if offset == 0:
            return 'C'
        elif offset == 1:
            return 'H'
        elif offset == 2:
            return 'S'
        else:
            return 'D'
    def on_color(self):
        if (self.spot % 4 == 0 or (self.spot-2) % 4 == 0):
            return 'black'
        else:
            return 'red'
    def on_suit(self, suit):
        if suit == 'C':
            offset = 0
        elif suit == 'H':
            offset = 1
        elif suit == 'S':
            offset = 2
        elif suit == 'D':
            offset = 3
        return (self.spot - offset) % 4 == 0
    def get_trump(self):
        mod = self.spot % 4
        if mod == 0:
            return 'C'
        elif mod == 1:
            return 'H'
        elif mod == 2:
            return 'S'
        elif mod == 3:
            return 'D'
    def has_suit(self, suit):
        for card in self.hand:
            if card.suit == suit:
                return True
        return False
    def copy(self):
        new = Player(self.name)
        for card in self.hand:
            new.hand.append(card)
        new.spot = self.spot
        new.max_spot = self.max_spot
        return new 

def mean(lst): 
    return sum(lst) / len(lst) 
from statistics import stdev
from statistics import median

class Endgame:
    def __init__(self, nplayers):
        self.finishes = 0
        self.num_players = nplayers
        self.players = []
        for i in range(nplayers):
            self.players.append(Player(i))
        self.deck = Deck()

    def sim_endings_with_effects(self, num):
        result = [[[],[]] for i in range(self.num_players)]
        for i in range(num):
            tmp = self.play_ending_with_effects()
            if (len(self.deck.cards) + len(self.deck.discard) > 54):
                print ("Too many cards in deck {},{}".format(len(self.deck.cards), len(self.deck.discard)))
                return
            for j in range(self.num_players):
                result[j][0].append(tmp[j][0])
                result[j][1].append(tmp[j][1])
            print("Finished trial {}/{}".format(i+1, num), end='\r')
        print("")
        print("Results over {} simulations".format(num))
        for i in range(self.num_players):
            print("for player {}:".format(i))
            print("mean end movement was {}, std deviation was {}".format(mean(result[i][0]), stdev(result[i][0])))
            print("mean max movement was {}, std deviation was {}".format(mean(result[i][1]), stdev(result[i][1])))
        return result

    def sim_endings_no_effects(self, num):
        result = [[[],[]] for i in range(self.num_players)]
        for i in range(num):
            tmp = self.play_ending_no_effects()
            for j in range(self.num_players):
                result[j][0].append(tmp[j][0])
                result[j][1].append(tmp[j][1])
            print("Finished trial {}/{}".format(i+1, num), end='\r')
        print("")
        print("Results over {} simulations".format(num))
        return result

    # Typical ending played out as if last player has just frozen,
    # second to last player is last to play
    def play_ending_with_effects(self):
        # Reshuffle deck
        for player in self.players:
            player.spot = 0
            player.max_spot = 0
            self.deck.cards.extend(player.hand)
            player.hand = []
        self.deck.shuffle_discard()
        # Deal 7 cards to each player
        for player in self.players:
            player.hand.extend(self.deck.deal(7))
        # Loop thru players for first round
        for idx in range(len(self.players)):
            current = self.players[idx]
            # Decide whether or not to play effect
            effects = current.effect_cards()
            opp_on_red = 0
            opp_on_black = 0
            max_red_ahead = 0
            max_black_ahead = 0
            furthest_red = -1
            furthest_black = -1
            for opp in range(len(self.players)):
                if opp != idx:
                    if self.players[opp].on_color() == 'black':
                        opp_on_black += 1
                        dist = self.players[opp].spot - current.spot
                        if dist > max_black_ahead:
                            max_black_ahead = dist
                            furthest_black = opp
                    else:
                        opp_on_red += 1
                        dist = self.players[opp].spot - current.spot
                        if dist > max_red_ahead:
                            max_red_ahead = dist
                            furthest_red = opp
            played_effect = False
            # Check for Jacks
            for card in effects:
                if card.num == 'J' and card.color == 'red' and max_red_ahead > 0:
                    # Play jack on furthest ahead player
                    aced = False
                    for card2 in self.players[furthest_red].hand:
                        if card2.num == 'A':
                            self.players[furthest_red].hand.remove(card2)
                            self.deck.discard.append(card2)
                            aced = True
                            break
                    if not aced:
                        tmp = current.spot
                        current.spot = self.players[furthest_red].spot
                        if (current.spot > current.max_spot):
                            current.max_spot = current.spot
                        self.players[furthest_red].spot = tmp
                    current.hand.remove(card)
                    self.deck.discard.append(card)
                    played_effect = True
                    break
                elif card.num == 'J' and card.color == 'black' and max_black_ahead > 0:
                    # Play jack on furthest ahead player
                    aced = False
                    for card2 in self.players[furthest_black].hand:
                        if card2.num == 'A':
                            self.players[furthest_black].hand.remove(card2)
                            self.deck.discard.append(card2)
                            aced = True
                            break
                    if not aced:
                        tmp = current.spot
                        current.spot = self.players[furthest_black].spot
                        if (current.spot > current.max_spot):
                            current.max_spot = current.spot
                        self.players[furthest_black].spot = tmp
                    current.hand.remove(card)
                    self.deck.discard.append(card)
                    played_effect = True 
                    break
            # Check for K/Q
            if not played_effect:
                for card in effects:
                    if card.num == 'K' and current.on_color() == card.color:
                        for player in self.players:
                            if player.on_color() == card.color:
                                player.spot += 4
                                if player.spot > player.max_spot:
                                    player.max_spot = player.spot
                        current.hand.remove(card)
                        self.deck.discard.append(card)
                        played_effect = True
                        break
                    elif card.num == 'Q' and current.on_color() != card.color:
                        for player in self.players:
                            if player.on_color() == card.color:
                                player.spot -= 4
                        current.hand.remove(card)
                        self.deck.discard.append(card)
                        played_effect = True
                        break
            if not played_effect:
                for card in effects:
                    if card.num == '2':
                        current.hand.remove(card)
                        self.deck.discard.append(current.hand.pop())
                        self.deck.discard.append(card)
                        current.hand.extend(self.deck.deal(2))
                        played_effect = True
                        break

            # Play out trick
            trump = current.get_trump()
            cards_played = [None for i in range(self.num_players)]
            init_card = current.random_card()
            cards_played[idx] = init_card 
            winning_card = init_card
            winning = idx
            for idx2 in range(idx+1, len(self.players)):
                card = self.players[idx2].random_card2(init_card)
                cards_played[idx2] = card
                if (not winning_card.beats(card, trump)):
                    winning_card = card
                    winning = idx2
            for idx2 in range(0, idx):
                card = self.players[idx2].random_card2(init_card)
                cards_played[idx2] = card
                if (not winning_card.beats(card, trump)):
                    winning_card = card
                    winning = idx2
            self.players[winning].move_suit(winning_card.suit)
            for card in cards_played:
                self.deck.discard.append(card)
            for player in self.players:
                n = 7 - len(player.hand)
                player.hand.extend(self.deck.deal(n))
        # Loop thru players for second round
        for idx in range(len(self.players)-1):
            current = self.players[idx]
            trump = current.get_trump()
            # Decide whether or not to play effect
            effects = current.effect_cards()
            opp_on_red = 0
            opp_on_black = 0
            max_red_ahead = 0
            max_black_ahead = 0
            furthest_red = -1
            furthest_black = -1
            for opp in range(len(self.players)):
                if opp != idx:
                    if self.players[opp].on_color() == 'black':
                        opp_on_black += 1
                        dist = self.players[opp].spot - current.spot
                        if dist > max_black_ahead:
                            max_black_ahead = dist
                            furthest_black = opp
                    else:
                        opp_on_red += 1
                        dist = self.players[opp].spot - current.spot
                        if dist > max_red_ahead:
                            max_red_ahead = dist
                            furthest_red = opp
            played_effect = False
            # Check for Jacks
            for card in effects:
                if card.num == 'J' and card.color == 'red' and max_red_ahead > 0:
                    # Play jack on furthest ahead player
                    aced = False
                    for card2 in self.players[furthest_red].hand:
                        if card2.num == 'A':
                            self.players[furthest_red].hand.remove(card2)
                            self.deck.discard.append(card2)
                            aced = True
                            break
                    if not aced:
                        tmp = current.spot
                        current.spot = self.players[furthest_red].spot
                        if (current.spot > current.max_spot):
                            current.max_spot = current.spot
                        self.players[furthest_red].spot = tmp
                    current.hand.remove(card)
                    self.deck.discard.append(card)
                    played_effect = True
                    break
                elif card.num == 'J' and card.color == 'black' and max_black_ahead > 0:
                    # Play jack on furthest ahead player
                    aced = False
                    for card2 in self.players[furthest_black].hand:
                        if card2.num == 'A':
                            self.players[furthest_black].hand.remove(card2)
                            self.deck.discard.append(card2)
                            aced = True
                            break
                    if not aced:
                        tmp = current.spot
                        current.spot = self.players[furthest_black].spot
                        if (current.spot > current.max_spot):
                            current.max_spot = current.spot
                        self.players[furthest_black].spot = tmp
                    current.hand.remove(card)
                    self.deck.discard.append(card)
                    played_effect = True 
                    break
            # Check for K/Q
            if not played_effect:
                for card in effects:
                    if card.num == 'K' and current.on_color() == card.color:
                        for player in self.players:
                            if player.on_color() == card.color:
                                player.spot += 4
                                if player.spot > player.max_spot:
                                    player.max_spot = player.spot
                        current.hand.remove(card)
                        self.deck.discard.append(card)
                        played_effect = True
                        break
                    elif card.num == 'Q' and current.on_color() != card.color:
                        for player in self.players:
                            if player.on_color() == card.color:
                                player.spot -= 4
                        current.hand.remove(card)
                        self.deck.discard.append(card)
                        played_effect = True
                        break
            if not played_effect:
                for card in effects:
                    if card.num == '2':
                        current.hand.remove(card)
                        self.deck.discard.append(current.hand.pop())
                        self.deck.discard.append(card)
                        current.hand.extend(self.deck.deal(2))
                        played_effect = True
                        break
            # Play out trick
            cards_played = [None for i in range(self.num_players)]
            init_card = current.random_card()
            cards_played[idx] = init_card 
            winning_card = init_card
            winning = idx
            for idx2 in range(idx+1, len(self.players)):
                card = self.players[idx2].random_card2(init_card)
                cards_played[idx2] = card
                if (not winning_card.beats(card, trump)):
                    winning_card = card
                    winning = idx2
            for idx2 in range(0, idx):
                card = self.players[idx2].random_card2(init_card)
                cards_played[idx2] = card
                if (not winning_card.beats(card, trump)):
                    winning_card = card
                    winning = idx2
            self.players[winning].move_suit(winning_card.suit)
            for card in cards_played:
                self.deck.discard.append(card)
            for player in self.players:
                n = 7 - len(player.hand)
                player.hand.extend(self.deck.deal(n))
        return [[p.spot, p.max_spot] for p in self.players]

    # Typical ending played out as if last player has just frozen,
    # second to last player is last to play
    def play_ending_no_effects(self):
        # Reshuffle deck
        for player in self.players:
            player.spot = 0
            player.max_spot = 0
            self.deck.cards.extend(player.hand)
            player.hand = []
        self.deck.shuffle_discard()
        # Deal 7 cards to each player
        for player in self.players:
            player.hand.extend(self.deck.deal(7))
        # Loop thru players for first round
        for idx in range(len(self.players)):
            current = self.players[idx]
            trump = current.get_trump()
            cards_played = [None for i in range(self.num_players)]
            init_card = current.random_card()
            cards_played[idx] = init_card 
            winning_card = init_card
            winning = idx
            for idx2 in range(idx+1, len(self.players)):
                card = self.players[idx2].random_card2(init_card)
                cards_played[idx2] = card
                if (not winning_card.beats(card, trump)):
                    winning_card = card
                    winning = idx2
            for idx2 in range(0, idx):
                card = self.players[idx2].random_card2(init_card)
                cards_played[idx2] = card
                if (not winning_card.beats(card, trump)):
                    winning_card = card
                    winning = idx2
            self.players[winning].move_suit(winning_card.suit)
            for card in cards_played:
                self.deck.discard.append(card)
            for player in self.players:
                n = 7 - len(player.hand)
                player.hand.extend(self.deck.deal(n))
        # Loop thru players for second round
        for idx in range(len(self.players)-1):
            current = self.players[idx]
            trump = current.get_trump()
            cards_played = [None for i in range(self.num_players)]
            init_card = current.random_card()
            cards_played[idx] = init_card 
            winning_card = init_card
            winning = idx
            for idx2 in range(idx+1, len(self.players)):
                card = self.players[idx2].random_card2(init_card)
                cards_played[idx2] = card
                if (not winning_card.beats(card, trump)):
                    winning_card = card
                    winning = idx2
            for idx2 in range(0, idx):
                card = self.players[idx2].random_card2(init_card)
                cards_played[idx2] = card
                if (not winning_card.beats(card, trump)):
                    winning_card = card
                    winning = idx2
            self.players[winning].move_suit(winning_card.suit)
            for card in cards_played:
                self.deck.discard.append(card)
            for player in self.players:
                n = 7 - len(player.hand)
                player.hand.extend(self.deck.deal(n))
        return [[p.spot, p.max_spot] for p in self.players]

import sys
import matplotlib.pyplot as plt
if (len(sys.argv) < 3):
    print("Must enter a number of players, then trials")
    sys.exit(0)
players = 0
try:
    players = int(sys.argv[1])
except ValueError:
    print("First argument must be number of players")
    sys.exit(0)
sims = 0
try:
    sims = int(sys.argv[2])
except ValueError:
    print("Second argument must be an integer number of simulations")
    sys.exit(0)

g = Endgame(players)
result = g.sim_endings_with_effects(sims)

data1 = [i[0] for i in result]
data2 = [i[1] for i in result]
mid1 = [median(i) for i in data1]
mid2 = [median(i) for i in data2]

fig, ax = plt.subplots()
ax.set_ylabel('Spots Moved')
ax.set_title('Ending distances for the players')
bp1 = ax.boxplot(data1)
print("Data for Ending Distances:")
for i in range(players):
    w1 = bp1['whiskers'][2*i].get_data()[1]
    w2 = bp1['whiskers'][2*i+1].get_data()[1]
    d = bp1['boxes'][i].get_data()[1]
    print("For player {}, ranges were {},{},{},{},{}".format(i,w1[1],w1[0],mid1[i],w2[0],w2[1]))

plt.figure(1)
fig, ax = plt.subplots()
ax.set_ylabel('Spots Moved')
ax.set_title('Maximum distances for the players')
bp2= ax.boxplot(data2)
print("Data for Maximum Distances:")
for i in range(players):
    w1 = bp2['whiskers'][2*i].get_data()[1]
    w2 = bp2['whiskers'][2*i+1].get_data()[1]
    d = bp2['boxes'][i].get_data()[1]
    print("For player {}, ranges were {},{},{},{},{}".format(i,w1[1],w1[0],mid1[i],w2[0],w2[1]))
plt.show()
