import random
import time
import os
from typing import List, Tuple, Optional

class Card:
    def __init__(self, suit: int = 0, rank: int = 0):
        self.suit = suit
        self.rank = rank

class Deck:
    def __init__(self):
        self.suits = ["D", "S", "H", "C"]
        self.ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        self.cards = []
        self.top = 0
        self.reset()
    
    def reset(self):
        self.cards = []
        for i in range(4):
            for j in range(13):
                self.cards.append(Card(i, j))
    
    def print_deck(self):
        print("Printing the deck...")
        input()
        for card in self.cards:
            print(f"{self.ranks[card.rank]}{self.suits[card.suit]}")
        print()
    
    def shuffle(self):
        self.top = 0
        self.reset()
        print("Shuffling the cards and dealing..." + os.linesep)
        random.shuffle(self.cards)
    
    def hitme(self) -> Card:
        if self.top >= len(self.cards):
            self.shuffle()
        card = self.cards[self.top]
        self.top += 1
        return card

class Player:
    def __init__(self):
        self.name = ""
        self.money = 0
        self.cards = [Card(), Card()]
        self.playing = False
        self.round = False
        self.goodToGo = False

class PokerGame:
    def __init__(self):
        self.players = [Player() for _ in range(6)]
        self.deck1 = Deck()
        self.bind = 0
        self.tableCards = [Card() for _ in range(5)]
        for i in range(5):
            self.tableCards[i].rank = -1
        self.pot = 0
        self.potBet = 0
        self.action = 0
        self.bet = 0
        self.rational = 0
        self.betOn = 0
        self.winner = 0
        self.maxPoints = 0
        self.roundWinner = 0
        self.handPoints = [0] * 6
        self.bestHand = [[-1, -1, -1] for _ in range(6)]
    
    def start(self, name: str):
        total_money = 0
        for i in range(6):
            self.players[i].money = 1000
            self.players[i].playing = True
            total_money += self.players[i].money
        
        print(f"Total money in game: {total_money}")
        
        self.players[0].name = "Alex"
        self.players[1].name = "Ivan"
        self.players[2].name = "Boris"
        self.players[3].name = "Lisa"
        self.players[4].name = name
        self.players[5].name = "Katya"
        
        self.startGame()
    
    def deal(self):
        for i in range(6):
            for j in range(2):
                if self.players[i].playing:
                    self.players[i].cards[j] = self.deck1.hitme()
        
        for i in range(5):
            self.tableCards[i].rank = -1
    
    def flop(self):
        for i in range(3):
            self.tableCards[i] = self.deck1.hitme()
    
    def turn(self):
        self.tableCards[3] = self.deck1.hitme()
    
    def river(self):
        self.tableCards[4] = self.deck1.hitme()
    
    def printTable(self):
        print(f"  {'flops' if not self.players[0].round else '      '}       {'flops' if not self.players[1].round else '      '}         {'flops' if not self.players[2].round else '      '}")
        print(f"  {self.players[0].name if self.players[0].playing else '    '}         {self.players[1].name if self.players[1].playing else '    '}           {self.players[2].name if self.players[2].playing else '     '}")
        print(f"  ${self.players[0].money:4}        ${self.players[1].money:4}          ${self.players[2].money:4}")
        print("     _____________________________")
        print(f"    / {'@' if self.bind == 0 else ' '}            {'@' if self.bind == 1 else ' '}            {'@' if self.bind == 2 else ' '} \\")
        print("   /  ___   ___   ___   ___   ___  \\")
        
        table_ranks = []
        table_suits = []
        for i in range(5):
            if self.tableCards[i].rank >= 0:
                table_ranks.append(self.deck1.ranks[self.tableCards[i].rank])
                table_suits.append(self.deck1.suits[self.tableCards[i].suit])
            else:
                table_ranks.append(" ")
                table_suits.append(" ")
        
        print(f"   | | {table_ranks[0]} | | {table_ranks[1]} | | {table_ranks[2]} | | {table_ranks[3]} | | {table_ranks[4]} | |")
        print(f"   | | {table_suits[0]} | | {table_suits[1]} | | {table_suits[2]} | | {table_suits[3]} | | {table_suits[4]} | |")
        print("   | |___| |___| |___| |___| |___| |")
        print("   |                               |")
        print(f"   |          Pot = ${self.pot:4}          |")
        print("   \\                               /")
        print(f"    \\_{'@' if self.bind == 5 else '_'}_____________{'@' if self.bind == 4 else '_'}___________{'@' if self.bind == 3 else '_'}_/")
        print()
        
        print(f"  {self.players[5].name if self.players[5].playing else '     '}          {self.players[4].name if self.players[4].playing else '      '}         {self.players[3].name if self.players[3].playing else '    '}")
        print(f"  ${self.players[5].money:4}          ${self.players[4].money:4}         ${self.players[3].money:4}")
        print(f"  {'flops' if not self.players[5].round else '      '}         {'flops' if not self.players[4].round else '      '}        {'flops' if not self.players[3].round else '      '}")
        print()
        
        if self.players[4].round:
            print("   Your hand:")
            print("    ___    ___")
            print(f"   | {self.deck1.ranks[self.players[4].cards[0].rank]} |  | {self.deck1.ranks[self.players[4].cards[1].rank]} |")
            print(f"   | {self.deck1.suits[self.players[4].cards[0].suit]} |  | {self.deck1.suits[self.players[4].cards[1].suit]} |")
            print("   |___|  |___|" + os.linesep)
        
        input()
    
    def playersLeft(self) -> int:
        count = 0
        for i in range(6):
            if self.players[i].money > 0:
                count += 1
        return count
    
    def computerAction(self, playerNum: int) -> int:
        if (self.players[playerNum].cards[0].rank < 8 and 
            self.players[playerNum].cards[1].rank < 8):
            if self.players[playerNum].cards[0].rank != self.players[playerNum].cards[1].rank:
                return 0
            else:
                return 1
        elif (self.players[playerNum].cards[0].rank < 10 and 
              self.players[playerNum].cards[1].rank < 10):
            if self.players[playerNum].cards[0].rank != self.players[playerNum].cards[1].rank:
                return 1
            else:
                return 2
        else:
            return 2
    
    def playersToBet(self) -> bool:
        for i in range(6):
            if self.players[i].round and not self.players[i].goodToGo:
                return True
        return False
    
    def takeBets(self):
        for k in range(6):
            self.players[k].goodToGo = False
        
        if not self.potBet:
            self.betOn = 0
        else:
            self.players[self.bind].goodToGo = True
        
        for k in range(self.bind + 1, self.bind + 7):
            player_index = k % 6
            
            # Human player actions
            if player_index == 4 and self.players[4].round and self.players[4].money > 0:
                can_call = self.players[4].money >= self.betOn
                can_raise = self.players[4].money > self.betOn
                
                if self.betOn > 0:
                    if can_call and can_raise:
                        print("Your action: (1) FLOP (2) CALL (3) RAISE ")
                        valid_actions = [1, 2, 3]
                    elif can_call:
                        print("Your action: (1) FLOP (2) CALL ")
                        valid_actions = [1, 2]
                    else:
                        print("Your action: (1) FLOP (2) ALL-IN ")
                        valid_actions = [1, 2]
                    
                    try:
                        self.action = int(input())
                    except ValueError:
                        self.action = 0
                    while self.action not in valid_actions:
                        print("Invalid number pressed.")
                        if can_call and can_raise:
                            print("Your action: (1) FLOP (2) CALL (3) RAISE ")
                            valid_actions = [1, 2, 3]
                        elif can_call:
                            print("Your action: (1) FLOP (2) CALL ")
                            valid_actions = [1, 2]
                        else:
                            print("Your action: (1) FLOP (2) ALL-IN ")
                            valid_actions = [1, 2]
                        try:
                            self.action = int(input())
                        except ValueError:
                            self.action = 0
                else:
                    print("Your action: (1) FLOP (2) CHECK (3) BET ")
                    try:
                        self.action = int(input())
                    except ValueError:
                        self.action = 0
                    while self.action not in [1, 2, 3]:
                        print("Invalid number pressed.")
                        print("Your action: (1) FLOP (2) CHECK (3) BET ")
                        try:
                            self.action = int(input())
                        except ValueError:
                            self.action = 0
                
                print()
                if self.action == 1:
                    self.players[4].round = False
                    print("You fold." + os.linesep)
                elif self.action == 2:
                    if self.betOn > 0:
                        # CALL or ALL-IN
                        bet_amount = min(self.players[4].money, self.betOn)
                        self.pot += bet_amount
                        self.players[4].money -= bet_amount
                        self.players[4].goodToGo = True
                        if bet_amount == self.betOn:
                            print(f"You call ${bet_amount}" + os.linesep)
                        else:
                            print(f"You go all-in with ${bet_amount}" + os.linesep)
                    else:
                        # CHECK
                        print("You check." + os.linesep)
                        continue
                else:
                    # BET or RAISE
                    if self.betOn > 0:
                        # RAISE
                        if not can_raise:
                            print("You don't have enough money to raise.")
                            continue
                            
                        print(f"Current bet is ${self.betOn}. How much do you want to raise to: ")
                        try:
                            new_bet = int(input())
                        except ValueError:
                            new_bet = 0
                        
                        while (new_bet <= self.betOn or new_bet > self.players[4].money or new_bet < self.betOn + 1):
                            if new_bet <= self.betOn:
                                print(f"Raise must be higher than current bet (${self.betOn})")
                            elif new_bet > self.players[4].money:
                                print(f"You don't have enough money. Maximum raise: ${self.players[4].money}")
                            else:
                                print("Invalid bet amount")
                            
                            print(f"How much do you want to raise to: ")
                            try:
                                new_bet = int(input())
                            except ValueError:
                                new_bet = 0
                        
                        # Вычисляем сколько нужно добавить к ставке
                        additional_bet = new_bet - self.betOn
                        self.pot += additional_bet
                        self.players[4].money -= additional_bet
                        self.betOn = new_bet
                        self.players[4].goodToGo = True
                        
                        # Сбрасываем флаги goodToGo у других игроков, так как ставка повышена
                        for i in range(6):
                            if i != 4:
                                self.players[i].goodToGo = False
                        
                        print(f"You raise to ${new_bet}" + os.linesep)
                    else:
                        # BET
                        print("How much do you want to bet: ")
                        try:
                            self.bet = int(input())
                        except ValueError:
                            self.bet = 0
                        while self.bet > self.players[4].money or self.bet < 1:
                            if self.bet > self.players[4].money:
                                print(f"You don't have enough money. Maximum bet: ${self.players[4].money}")
                            else:
                                print("Invalid bet amount")
                            print("How much do you want to bet: ")
                            try:
                                self.bet = int(input())
                            except ValueError:
                                self.bet = 0
                            print(os.linesep * 2)
                        
                        self.pot += self.bet
                        self.players[4].money -= self.bet
                        self.betOn = self.bet
                        self.players[4].goodToGo = True
                        
                        # Сбрасываем флаги goodToGo у других игроков
                        for i in range(6):
                            if i != 4:
                                self.players[i].goodToGo = False
                        
                        print(f"You bet ${self.bet}" + os.linesep)
            
            # Computer actions
            else:
                if not self.players[player_index].round:
                    continue
                
                self.rational = random.randint(0, 1)
                if self.rational:
                    computer_action = self.computerAction(player_index)
                else:
                    computer_action = random.randint(0, 3)  # 0-фолд, 1-чек/колл, 2-ставка, 3-рейз
                
                can_call = self.players[player_index].money >= self.betOn
                can_raise = self.players[player_index].money > self.betOn
                
                if computer_action == 0:
                    self.players[player_index].round = False
                    print(f"{self.players[player_index].name} folds..." + os.linesep)
                elif computer_action == 1:
                    if self.betOn > 0:
                        # CALL or ALL-IN
                        if can_call:
                            bet_amount = min(self.players[player_index].money, self.betOn)
                            self.pot += bet_amount
                            self.players[player_index].money -= bet_amount
                            print(f"{self.players[player_index].name} calls ${bet_amount}!" + os.linesep)
                            self.players[player_index].goodToGo = True
                        else:
                            # Олл-ин
                            bet_amount = self.players[player_index].money
                            self.pot += bet_amount
                            self.players[player_index].money = 0
                            print(f"{self.players[player_index].name} goes all-in with ${bet_amount}!" + os.linesep)
                            self.players[player_index].goodToGo = True
                    else:
                        # CHECK
                        print(f"{self.players[player_index].name} checks." + os.linesep)
                        continue
                elif computer_action == 2:
                    # BET (если нет текущей ставки) или RAISE (если есть)
                    if self.betOn > 0:
                        # RAISE - компьютер повышает ставку
                        if can_raise:
                            # Компьютер рейзит на случайную сумму (от 1.5x до 2x текущей ставки)
                            min_raise = self.betOn * 2
                            max_raise = min(self.players[player_index].money, self.betOn * 3)
                            
                            if max_raise > min_raise:
                                raise_to = random.randint(min_raise, max_raise)
                            else:
                                raise_to = min_raise
                            
                            if raise_to > self.players[player_index].money:
                                raise_to = self.players[player_index].money
                            
                            additional_bet = raise_to - self.betOn
                            self.pot += additional_bet
                            self.players[player_index].money -= additional_bet
                            self.betOn = raise_to
                            self.players[player_index].goodToGo = True
                            
                            # Сбрасываем флаги goodToGo у других игроков
                            for i in range(6):
                                if i != player_index:
                                    self.players[i].goodToGo = False
                            
                            print('\a')
                            print(f"{self.players[player_index].name} raises to ${raise_to}!" + os.linesep)
                        else:
                            # Не может рейзить - просто коллирует
                            bet_amount = min(self.players[player_index].money, self.betOn)
                            self.pot += bet_amount
                            self.players[player_index].money -= bet_amount
                            print(f"{self.players[player_index].name} calls ${bet_amount}!" + os.linesep)
                            self.players[player_index].goodToGo = True
                    else:
                        # BET - первая ставка
                        if self.players[player_index].money > 0:
                            max_bet = self.players[player_index].money // 3 + 1
                            self.bet = random.randint(10, max_bet + 10)
                            if self.bet > self.players[player_index].money:
                                self.bet = self.players[player_index].money
                            self.pot += self.bet
                            self.players[player_index].money -= self.bet
                            self.betOn = self.bet
                            self.players[player_index].goodToGo = True
                            
                            # Сбрасываем флаги goodToGo у других игроков
                            for i in range(6):
                                if i != player_index:
                                    self.players[i].goodToGo = False
                            
                            print('\a')
                            print(f"{self.players[player_index].name} bets ${self.bet}!" + os.linesep)
                        else:
                            print(f"{self.players[player_index].name} checks." + os.linesep)
                            continue
                else:
                    # ACTION 3 - более агрессивный рейз
                    if self.betOn > 0 and can_raise:
                        min_raise = self.betOn * 2
                        max_raise = min(self.players[player_index].money, self.betOn * 4)
                        if max_raise > min_raise:
                            raise_to = random.randint(min_raise, max_raise)
                        else:
                            raise_to = min_raise
                        additional_bet = raise_to - self.betOn
                        
                        self.pot += additional_bet
                        self.players[player_index].money -= additional_bet
                        self.betOn = raise_to
                        self.players[player_index].goodToGo = True
                        
                        # Сбрасываем флаги goodToGo у других игроков
                        for i in range(6):
                            if i != player_index:
                                self.players[i].goodToGo = False
                        
                        print('\a')
                        print(f"{self.players[player_index].name} raises big to ${raise_to}!" + os.linesep)
                    else:
                        # Не может рейзить - используем обычную логику
                        if self.betOn > 0:
                            bet_amount = min(self.players[player_index].money, self.betOn)
                            self.pot += bet_amount
                            self.players[player_index].money -= bet_amount
                            print(f"{self.players[player_index].name} calls ${bet_amount}!" + os.linesep)
                            self.players[player_index].goodToGo = True
                        else:
                            print(f"{self.players[player_index].name} checks." + os.linesep)
                            continue
                
                input()
        
        # Второй круг ставок - для тех, кто еще не уравнял ставку после рейза
        if self.betOn and self.playersToBet():
            for k in range(self.bind + 1, self.bind + 7):
                player_index = k % 6
                
                if player_index == 4:
                    if self.players[4].round and not self.players[4].goodToGo:
                        can_call = self.players[4].money >= self.betOn
                        
                        if can_call:
                            print("Your action: (1) FLOP (2) CALL ")
                            valid_actions = [1, 2]
                        else:
                            print("Your action: (1) FLOP (2) ALL-IN ")
                            valid_actions = [1, 2]
                            
                        try:
                            self.action = int(input())
                        except ValueError:
                            self.action = 0
                        while self.action not in valid_actions:
                            print("Invalid number pressed.")
                            if can_call:
                                print("Your action: (1) FLOP (2) CALL ")
                                valid_actions = [1, 2]
                            else:
                                print("Your action: (1) FLOP (2) ALL-IN ")
                                valid_actions = [1, 2]
                            try:
                                self.action = int(input())
                            except ValueError:
                                self.action = 0
                            print(os.linesep * 2)
                        
                        if self.action == 1:
                            self.players[4].round = False
                            print("You fold." + os.linesep)
                        else:
                            bet_amount = min(self.players[4].money, self.betOn)
                            self.pot += bet_amount
                            self.players[4].money -= bet_amount
                            self.players[4].goodToGo = True
                            if bet_amount == self.betOn:
                                print(f"You call ${bet_amount}" + os.linesep)
                            else:
                                print(f"You go all-in with ${bet_amount}" + os.linesep)
                
                else:
                    if not self.players[player_index].round or self.players[player_index].goodToGo:
                        continue
                    
                    self.action = random.randint(0, 1)
                    if self.action == 0:
                        self.players[player_index].round = False
                        print(f"{self.players[player_index].name} folds..." + os.linesep)
                    else:
                        if self.players[player_index].money >= self.betOn:
                            self.pot += self.betOn
                            self.players[player_index].money -= self.betOn
                        else:
                            # Олл-ин
                            bet_amount = self.players[player_index].money
                            self.pot += bet_amount
                            self.players[player_index].money = 0
                        print(f"{self.players[player_index].name} calls!" + os.linesep)
                        self.players[player_index].goodToGo = True
    
    def oneLeft(self) -> bool:
        count = 0
        for k in range(6):
            if self.players[k].round:
                count += 1
        return count == 1
    
    def getWinner(self) -> int:
        for k in range(6):
            if self.players[k].round:
                return k
        return 0
    
    def getScore(self, hand: List[Card]) -> int:
        hand_sorted = sorted(hand, key=lambda x: x.rank)
        straight = flush = three = four = full = pairs = high = 0
        k = 0
        
        # Check for flush
        while k < 4 and hand_sorted[k].suit == hand_sorted[k + 1].suit:
            k += 1
        if k == 4:
            flush = 1
        
        # Check for straight
        k = 0
        while k < 4 and hand_sorted[k].rank == hand_sorted[k + 1].rank - 1:
            k += 1
        if k == 4:
            straight = 1
        
        # Check for four of a kind
        for i in range(2):
            k = i
            while k < i + 3 and hand_sorted[k].rank == hand_sorted[k + 1].rank:
                k += 1
            if k == i + 3:
                four = 1
                high = hand_sorted[i].rank
        
        # Check for three of a kind and full house
        if not four:
            for i in range(3):
                k = i
                while k < i + 2 and hand_sorted[k].rank == hand_sorted[k + 1].rank:
                    k += 1
                if k == i + 2:
                    three = 1
                    high = hand_sorted[i].rank
                    if i == 0:
                        if hand_sorted[3].rank == hand_sorted[4].rank:
                            full = 1
                    elif i == 1:
                        if hand_sorted[0].rank == hand_sorted[4].rank:
                            full = 1
                    else:
                        if hand_sorted[0].rank == hand_sorted[1].rank:
                            full = 1
        
        if straight and flush:
            return 170 + hand_sorted[4].rank
        elif four:
            return 150 + high
        elif full:
            return 130 + high
        elif flush:
            return 110
        elif straight:
            return 90 + hand_sorted[4].rank
        elif three:
            return 70 + high
        
        # Check for pairs
        for k in range(4):
            if hand_sorted[k].rank == hand_sorted[k + 1].rank:
                pairs += 1
                if hand_sorted[k].rank > high:
                    high = hand_sorted[k].rank
        
        if pairs == 2:
            return 50 + high
        elif pairs:
            return 30 + high
        else:
            return hand_sorted[4].rank
    
    def tryHand(self, array: List[int], player: int) -> int:
        hand = [Card() for _ in range(5)]
        
        # Get cards from table and player
        for i in range(1, 4):
            hand[i - 1] = self.tableCards[array[i]]
        
        for i in range(2):
            hand[i + 3] = self.players[player].cards[i]
        
        return self.getScore(hand)
    
    def evaluateHands(self):
        for q in range(6):
            if self.players[q].round:
                self.handPoints[q] = -1
                # Простая реализация - проверяем все комбинации из 3 карт со стола
                for i in range(5):
                    for j in range(i + 1, 5):
                        for k in range(j + 1, 5):
                            currentPoints = self.getScore([
                                self.tableCards[i],
                                self.tableCards[j], 
                                self.tableCards[k],
                                self.players[q].cards[0],
                                self.players[q].cards[1]
                            ])
                            if currentPoints > self.handPoints[q]:
                                self.handPoints[q] = currentPoints
                                self.bestHand[q] = [i, j, k]
    
    def printWinningHand(self, winner: int):
        winningHand = [Card() for _ in range(5)]
        # Берем лучшие 3 карты со стола и 2 карты игрока
        winningHand[0] = self.tableCards[self.bestHand[winner][0]]
        winningHand[1] = self.tableCards[self.bestHand[winner][1]]
        winningHand[2] = self.tableCards[self.bestHand[winner][2]]
        winningHand[3] = self.players[winner].cards[0]
        winningHand[4] = self.players[winner].cards[1]
        
        winningHand_sorted = sorted(winningHand, key=lambda x: x.rank)
        
        print("   The winning hand:")
        print("   ___   ___   ___   ___   ___")
        print(f"  | {self.deck1.ranks[winningHand_sorted[0].rank]} | | {self.deck1.ranks[winningHand_sorted[1].rank]} | | {self.deck1.ranks[winningHand_sorted[2].rank]} | | {self.deck1.ranks[winningHand_sorted[3].rank]} | | {self.deck1.ranks[winningHand_sorted[4].rank]} |")
        print(f"  | {self.deck1.suits[winningHand_sorted[0].suit]} | | {self.deck1.suits[winningHand_sorted[1].suit]} | | {self.deck1.suits[winningHand_sorted[2].suit]} | | {self.deck1.suits[winningHand_sorted[3].suit]} | | {self.deck1.suits[winningHand_sorted[4].suit]} |")
        print("  |___| |___| |___| |___| |___|")
        print(os.linesep * 2)
        input()
    
    def startGame(self):
        i = 0
        
        while self.playersLeft() > 1:
            # Starting default values
            for z in range(6):
                if self.players[z].money < 1:
                    self.players[z].playing = False
                    self.players[z].round = False
                else:
                    self.players[z].round = True
                self.handPoints[z] = -1
            
            for x in range(6):
                for y in range(3):
                    self.bestHand[x][y] = -1
            
            # Check for game over
            if not self.players[4].playing:
                print("You are out of money, sorry.")
                print("Game over.")
                break
            
            self.bind = i % 6
            
            # Pay blind - только если у игрока есть деньги
            self.pot = 0
            self.potBet = 0
            self.betOn = 0
            
            if self.players[self.bind].playing and self.players[self.bind].money >= 20:
                blind_amount = min(20, self.players[self.bind].money)
                self.pot += blind_amount
                self.players[self.bind].money -= blind_amount
                self.potBet = 1
                self.betOn = blind_amount
                print(f"{self.players[self.bind].name} posts blind ${blind_amount}")
            
            print(f"Get ready for round {i + 1}...")
            input()
            self.deck1.shuffle()
            
            # Pre-flop
            self.deal()
            self.printTable()
            self.takeBets()
            
            if self.oneLeft():
                self.winner = self.getWinner()
                print(f"{self.players[self.winner].name} wins ${self.pot}" + os.linesep)
                self.players[self.winner].money += self.pot
                self.pot = 0
                i += 1
                continue
            
            # Flop
            self.potBet = 0
            self.betOn = 0
            for z in range(6):
                self.players[z].goodToGo = False
            self.flop()
            print()
            self.printTable()
            self.takeBets()
            
            if self.oneLeft():
                self.winner = self.getWinner()
                print(f"{self.players[self.winner].name} wins ${self.pot}" + os.linesep)
                self.players[self.winner].money += self.pot
                self.pot = 0
                i += 1
                continue
            
            # Turn
            self.turn()
            print()
            self.printTable()
            self.takeBets()
            
            if self.oneLeft():
                self.winner = self.getWinner()
                print(f"{self.players[self.winner].name} wins ${self.pot}" + os.linesep)
                self.players[self.winner].money += self.pot
                self.pot = 0
                i += 1
                continue
            
            # River
            self.river()
            print()
            self.printTable()
            self.takeBets()
            
            self.evaluateHands()
            
            # Find and declare round winner
            self.maxPoints = 0
            round_winners = []
            for q in range(6):
                if self.players[q].round:
                    if self.handPoints[q] > self.maxPoints:
                        self.maxPoints = self.handPoints[q]
                        round_winners = [q]
                    elif self.handPoints[q] == self.maxPoints:
                        round_winners.append(q)
            
            print()
            if len(round_winners) == 1:
                self.roundWinner = round_winners[0]
                print(f"{self.players[self.roundWinner].name} wins ${self.pot} with ", end="")
                
                if self.maxPoints < 30:
                    print("HIGH CARD")
                elif self.maxPoints < 50:
                    print("SINGLE PAIR")
                elif self.maxPoints < 70:
                    print("TWO PAIRS")
                elif self.maxPoints < 90:
                    print("THREE OF A KIND")
                elif self.maxPoints < 110:
                    print("STRAIGHT")
                elif self.maxPoints < 130:
                    print("FLUSH")
                elif self.maxPoints < 150:
                    print("FULL HOUSE")
                elif self.maxPoints < 170:
                    print("FOUR OF A KIND")
                else:
                    print("STRAIGHT FLUSH")
                
                print(os.linesep)
                self.printWinningHand(self.roundWinner)
                self.players[self.roundWinner].money += self.pot
                self.pot = 0
            else:
                # Разделение банка между несколькими победителями
                split_pot = self.pot // len(round_winners)
                print(f"Split pot! ${split_pot} each to: ", end="")
                for winner in round_winners:
                    print(f"{self.players[winner].name} ", end="")
                    self.players[winner].money += split_pot
                print()
                self.pot = 0
            
            # Проверяем общую сумму денег (для отладки)
            total_money = sum(player.money for player in self.players) + self.pot
            print(f"Total money in game: {total_money}")
            
            i += 1

def main():
    random.seed(int(time.time()))
    os.system("color 65")
    
    print("Welcome to..." + os.linesep)
    input()
    
    print("#######                        ###### ")
    print("   #    ###### #    # #####    #     #  ####  #    # ###### #####")
    print("   #    #       #  #    #      #     # #    # #   #  #      #    #")
    print("   #    #####    ##     #      ######  #    # ####   #####  #    #")
    print("   #    #        ##     #      #       #    # #  #   #      #####")
    print("   #    #       #  #    #      #       #    # #   #  #      #   #")
    print("   #    ###### #    #   #      #        ####  #    # ###### #    #" + os.linesep)
    
    print("Please type your name: ")
    name = input()
    
    print(f"OK {name} let's play some poker!" + os.linesep)
    input()
    
    game = PokerGame()
    game.start(name)

if __name__ == "__main__":
    main()