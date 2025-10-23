import pygame
import math
import os
from typing import List, Tuple, Optional

# Инициализация pygame
pygame.init()

class Card:
    def __init__(self, suit: int = 0, rank: int = 0):
        self.suit = suit
        self.rank = rank

class Deck:
    def __init__(self):
        self.suits = ["D", "S", "H", "C"]  # Вернем буквы для простоты
        self.ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        self.cards = []
        self.top = 0
        self.reset()
    
    def reset(self):
        self.cards = []
        for i in range(4):
            for j in range(13):
                self.cards.append(Card(i, j))
    
    def shuffle(self):
        self.top = 0
        self.reset()
        print("Shuffling the cards and dealing...\n")
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
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
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
        self.clear_screen()
        
        # Заголовок
        print("═" * 80)
        print("🎰 TEXAS HOLD'EM POKER".center(80))
        print("═" * 80)
        print()
        
        # Верхний ряд игроков (0, 1, 2)
        print(" " * 15, end="")
        for i in range(3):
            player = self.players[i]
            status = "💤" if not player.round else "🎯"
            if i == self.bind:
                status = "💰"
            print(f"{status} {player.name:8} ${player.money:4}", end="    ")
        print("\n")
        
        # Карты верхних игроков (скрытые)
        print(" " * 18, end="")
        for i in range(3):
            if self.players[i].playing and self.players[i].round:
                print("┌───┐ ┌───┐", end="     ")
            else:
                print(" " * 11, end="     ")
        print("\n")
        
        print(" " * 18, end="")
        for i in range(3):
            if self.players[i].playing and self.players[i].round:
                print("│ ▒ │ │ ▒ │", end="     ")
            else:
                print(" " * 11, end="     ")
        print("\n")
        
        print(" " * 18, end="")
        for i in range(3):
            if self.players[i].playing and self.players[i].round:
                print("└───┘ └───┘", end="     ")
            else:
                print(" " * 11, end="     ")
        print("\n")
        
        # Стол
        print(" " * 25 + "┌" + "─" * 35 + "┐")
        
        # Карты на столе
        table_display = []
        for i in range(5):
            if self.tableCards[i].rank >= 0:
                rank = self.deck1.ranks[self.tableCards[i].rank]
                suit = self.deck1.suits[self.tableCards[i].suit]
                table_display.append(f"{rank}{suit}")
            else:
                table_display.append("  ")
        
        print(" " * 25 + "│ ", end="")
        for card in table_display:
            print(f"{card:^5}", end=" ")
        print(" │")
        
        print(" " * 25 + "│" + f"💰 BANK: ${self.pot:6}".center(35) + "│")
        print(" " * 25 + "└" + "─" * 35 + "┘")
        print()
        
        # Нижний ряд игроков (5, 4, 3)
        print(" " * 18, end="")
        for i in [5, 4, 3]:
            if self.players[i].playing and self.players[i].round:
                if i == 4:  # Игрок видит свои карты
                    card1 = self.players[i].cards[0]
                    card2 = self.players[i].cards[1]
                    rank1 = self.deck1.ranks[card1.rank]
                    suit1 = self.deck1.suits[card1.suit]
                    rank2 = self.deck1.ranks[card2.rank]
                    suit2 = self.deck1.suits[card2.suit]
                    print(f"┌───┐ ┌───┐", end="     ")
                else:
                    print(f"┌───┐ ┌───┐", end="     ")
            else:
                print(" " * 11, end="     ")
        print("\n")
        
        print(" " * 18, end="")
        for i in [5, 4, 3]:
            if self.players[i].playing and self.players[i].round:
                if i == 4:
                    card1 = self.players[i].cards[0]
                    card2 = self.players[i].cards[1]
                    rank1 = self.deck1.ranks[card1.rank]
                    suit1 = self.deck1.suits[card1.suit]
                    rank2 = self.deck1.ranks[card2.rank]
                    suit2 = self.deck1.suits[card2.suit]
                    print(f"│{rank1:>2}{suit1}│ │{rank2:>2}{suit2}│", end="     ")
                else:
                    print(f"│ ▒ │ │ ▒ │", end="     ")
            else:
                print(" " * 11, end="     ")
        print("\n")
        
        print(" " * 18, end="")
        for i in [5, 4, 3]:
            if self.players[i].playing and self.players[i].round:
                print(f"└───┘ └───┘", end="     ")
            else:
                print(" " * 11, end="     ")
        print("\n")
        
        # Информация о нижних игроках
        print(" " * 15, end="")
        for i in [5, 4, 3]:
            player = self.players[i]
            status = "💤" if not player.round else "🎯"
            if i == self.bind:
                status = "💰"
            if i == 4:
                print(f"🎮 {player.name:8} ${player.money:4}", end="    ")
            else:
                print(f"{status} {player.name:8} ${player.money:4}", end="    ")
        print("\n")
        
        # Рука игрока
        if self.players[4].round:
            print("─" * 50)
            print("🎮 YOUR HAND".center(50))
            card1 = self.players[4].cards[0]
            card2 = self.players[4].cards[1]
            rank1 = self.deck1.ranks[card1.rank]
            suit1 = self.deck1.suits[card1.suit]
            rank2 = self.deck1.ranks[card2.rank]
            suit2 = self.deck1.suits[card2.suit]
            
            print(" " * 15 + "┌───┐ ┌───┐")
            print(" " * 15 + f"│{rank1:>2}{suit1}│ │{rank2:>2}{suit2}│")
            print(" " * 15 + "└───┘ └───┘")
            print(" " * 18 + f"{rank1}{suit1}   {rank2}{suit2}")
            print("─" * 50)
        
        print("\n" + "═" * 80)
    
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
            
            if player_index == 4 and self.players[4].round and self.players[4].money > 0:
                can_call = self.players[4].money >= self.betOn
                can_raise = self.players[4].money > self.betOn
                
                self.printTable()
                print(f"\nCurrent bet: ${self.betOn} | Your money: ${self.players[4].money}")
                print("Your turn! Choose action:")
                
                if self.betOn > 0:
                    if can_call and can_raise:
                        print("1. Fold")
                        print("2. Call")
                        print("3. Raise")
                        valid_actions = [1, 2, 3]
                    elif can_call:
                        print("1. Fold") 
                        print("2. Call")
                        valid_actions = [1, 2]
                    else:
                        print("1. Fold")
                        print("2. All-In")
                        valid_actions = [1, 2]
                    
                    try:
                        self.action = int(input("\nEnter your choice: "))
                    except ValueError:
                        self.action = 0
                    while self.action not in valid_actions:
                        print("Invalid choice!")
                        try:
                            self.action = int(input("Enter your choice: "))
                        except ValueError:
                            self.action = 0
                else:
                    print("1. Fold")
                    print("2. Check") 
                    print("3. Bet")
                    try:
                        self.action = int(input("\nEnter your choice: "))
                    except ValueError:
                        self.action = 0
                    while self.action not in [1, 2, 3]:
                        print("Invalid choice!")
                        try:
                            self.action = int(input("Enter your choice: "))
                        except ValueError:
                            self.action = 0
                
                print()
                if self.action == 1:
                    self.players[4].round = False
                    print("You fold.")
                elif self.action == 2:
                    if self.betOn > 0:
                        bet_amount = min(self.players[4].money, self.betOn)
                        self.pot += bet_amount
                        self.players[4].money -= bet_amount
                        self.players[4].goodToGo = True
                        if bet_amount == self.betOn:
                            print(f"You call ${bet_amount}")
                        else:
                            print(f"You go all-in with ${bet_amount}")
                    else:
                        print("You check.")
                        continue
                else:
                    if self.betOn > 0:
                        if not can_raise:
                            print("You don't have enough money to raise.")
                            continue
                            
                        print(f"Current bet: ${self.betOn}")
                        print(f"Your money: ${self.players[4].money}")
                        try:
                            new_bet = int(input("How much do you want to raise to: $"))
                        except ValueError:
                            new_bet = 0
                        
                        while (new_bet <= self.betOn or new_bet > self.players[4].money or new_bet < self.betOn + 1):
                            if new_bet <= self.betOn:
                                print(f"Raise must be higher than current bet (${self.betOn})")
                            elif new_bet > self.players[4].money:
                                print(f"You don't have enough money. Maximum: ${self.players[4].money}")
                            else:
                                print("Invalid amount")
                            
                            try:
                                new_bet = int(input("How much do you want to raise to: $"))
                            except ValueError:
                                new_bet = 0
                        
                        additional_bet = new_bet - self.betOn
                        self.pot += additional_bet
                        self.players[4].money -= additional_bet
                        self.betOn = new_bet
                        self.players[4].goodToGo = True
                        
                        for i in range(6):
                            if i != 4:
                                self.players[i].goodToGo = False
                        
                        print(f"You raise to ${new_bet}")
                    else:
                        print(f"Your money: ${self.players[4].money}")
                        try:
                            self.bet = int(input("How much do you want to bet: $"))
                        except ValueError:
                            self.bet = 0
                        while self.bet > self.players[4].money or self.bet < 1:
                            if self.bet > self.players[4].money:
                                print(f"You don't have enough money. Maximum: ${self.players[4].money}")
                            else:
                                print("Invalid bet amount")
                            try:
                                self.bet = int(input("How much do you want to bet: $"))
                            except ValueError:
                                self.bet = 0
                        
                        self.pot += self.bet
                        self.players[4].money -= self.bet
                        self.betOn = self.bet
                        self.players[4].goodToGo = True
                        
                        for i in range(6):
                            if i != 4:
                                self.players[i].goodToGo = False
                        
                        print(f"You bet ${self.bet}")
                
                input("\nPress Enter to continue...")
            
            else:
                if not self.players[player_index].round:
                    continue
                
                self.rational = random.randint(0, 1)
                if self.rational:
                    computer_action = self.computerAction(player_index)
                else:
                    computer_action = random.randint(0, 3)
                
                can_call = self.players[player_index].money >= self.betOn
                can_raise = self.players[player_index].money > self.betOn
                
                if computer_action == 0:
                    self.players[player_index].round = False
                    print(f"{self.players[player_index].name} folds...")
                elif computer_action == 1:
                    if self.betOn > 0:
                        if can_call:
                            bet_amount = min(self.players[player_index].money, self.betOn)
                            self.pot += bet_amount
                            self.players[player_index].money -= bet_amount
                            print(f"{self.players[player_index].name} calls ${bet_amount}!")
                            self.players[player_index].goodToGo = True
                        else:
                            bet_amount = self.players[player_index].money
                            self.pot += bet_amount
                            self.players[player_index].money = 0
                            print(f"{self.players[player_index].name} goes all-in with ${bet_amount}!")
                            self.players[player_index].goodToGo = True
                    else:
                        print(f"{self.players[player_index].name} checks.")
                        continue
                elif computer_action == 2:
                    if self.betOn > 0:
                        if can_raise:
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
                            
                            for i in range(6):
                                if i != player_index:
                                    self.players[i].goodToGo = False
                            
                            print(f"{self.players[player_index].name} raises to ${raise_to}!")
                        else:
                            bet_amount = min(self.players[player_index].money, self.betOn)
                            self.pot += bet_amount
                            self.players[player_index].money -= bet_amount
                            print(f"{self.players[player_index].name} calls ${bet_amount}!")
                            self.players[player_index].goodToGo = True
                    else:
                        if self.players[player_index].money > 0:
                            max_bet = self.players[player_index].money // 3 + 1
                            self.bet = random.randint(10, max_bet + 10)
                            if self.bet > self.players[player_index].money:
                                self.bet = self.players[player_index].money
                            self.pot += self.bet
                            self.players[player_index].money -= self.bet
                            self.betOn = self.bet
                            self.players[player_index].goodToGo = True
                            
                            for i in range(6):
                                if i != player_index:
                                    self.players[i].goodToGo = False
                            
                            print(f"{self.players[player_index].name} bets ${self.bet}!")
                        else:
                            print(f"{self.players[player_index].name} checks.")
                            continue
                else:
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
                        
                        for i in range(6):
                            if i != player_index:
                                self.players[i].goodToGo = False
                        
                        print(f"{self.players[player_index].name} raises big to ${raise_to}!")
                    else:
                        if self.betOn > 0:
                            bet_amount = min(self.players[player_index].money, self.betOn)
                            self.pot += bet_amount
                            self.players[player_index].money -= bet_amount
                            print(f"{self.players[player_index].name} calls ${bet_amount}!")
                            self.players[player_index].goodToGo = True
                        else:
                            print(f"{self.players[player_index].name} checks.")
                            continue
                
                time.sleep(1)
        
        if self.betOn and self.playersToBet():
            for k in range(self.bind + 1, self.bind + 7):
                player_index = k % 6
                
                if player_index == 4:
                    if self.players[4].round and not self.players[4].goodToGo:
                        can_call = self.players[4].money >= self.betOn
                        
                        self.printTable()
                        if can_call:
                            print("1. Fold")
                            print("2. Call")
                            valid_actions = [1, 2]
                        else:
                            print("1. Fold")
                            print("2. All-In")
                            valid_actions = [1, 2]
                            
                        try:
                            self.action = int(input("\nEnter your choice: "))
                        except ValueError:
                            self.action = 0
                        while self.action not in valid_actions:
                            print("Invalid choice!")
                            try:
                                self.action = int(input("Enter your choice: "))
                            except ValueError:
                                self.action = 0
                        
                        if self.action == 1:
                            self.players[4].round = False
                            print("You fold.")
                        else:
                            bet_amount = min(self.players[4].money, self.betOn)
                            self.pot += bet_amount
                            self.players[4].money -= bet_amount
                            self.players[4].goodToGo = True
                            if bet_amount == self.betOn:
                                print(f"You call ${bet_amount}")
                            else:
                                print(f"You go all-in with ${bet_amount}")
                
                else:
                    if not self.players[player_index].round or self.players[player_index].goodToGo:
                        continue
                    
                    self.action = random.randint(0, 1)
                    if self.action == 0:
                        self.players[player_index].round = False
                        print(f"{self.players[player_index].name} folds...")
                    else:
                        if self.players[player_index].money >= self.betOn:
                            self.pot += self.betOn
                            self.players[player_index].money -= self.betOn
                        else:
                            bet_amount = self.players[player_index].money
                            self.pot += bet_amount
                            self.players[player_index].money = 0
                        print(f"{self.players[player_index].name} calls!")
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
        # Упрощенная версия для демонстрации
        return sum(card.rank for card in hand)
    
    def evaluateHands(self):
        for q in range(6):
            if self.players[q].round:
                # Простая оценка - сумма рангов
                self.handPoints[q] = self.players[q].cards[0].rank + self.players[q].cards[1].rank
    
    def startGame(self):
        i = 0
        
        while self.playersLeft() > 1:
            # Reset for new round
            for z in range(6):
                if self.players[z].money < 1:
                    self.players[z].playing = False
                    self.players[z].round = False
                else:
                    self.players[z].round = True
            
            if not self.players[4].playing:
                print("You are out of money, sorry.")
                print("Game over.")
                break
            
            self.bind = i % 6
            
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
                print(f"{self.players[self.winner].name} wins ${self.pot}!")
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
            self.printTable()
            self.takeBets()
            
            if self.oneLeft():
                self.winner = self.getWinner()
                print(f"{self.players[self.winner].name} wins ${self.pot}!")
                self.players[self.winner].money += self.pot
                self.pot = 0
                i += 1
                continue
            
            # Turn
            self.turn()
            self.printTable()
            self.takeBets()
            
            if self.oneLeft():
                self.winner = self.getWinner()
                print(f"{self.players[self.winner].name} wins ${self.pot}!")
                self.players[self.winner].money += self.pot
                self.pot = 0
                i += 1
                continue
            
            # River
            self.river()
            self.printTable()
            self.takeBets()
            
            self.evaluateHands()
            
            # Find winner
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
                print(f"{self.players[self.roundWinner].name} wins ${self.pot}!")
                self.players[self.roundWinner].money += self.pot
            else:
                split_pot = self.pot // len(round_winners)
                print(f"Split pot! ${split_pot} each to: ", end="")
                for winner in round_winners:
                    print(f"{self.players[winner].name} ", end="")
                    self.players[winner].money += split_pot
                print()
            
            self.pot = 0
            
            total_money = sum(player.money for player in self.players) + self.pot
            print(f"Total money in game: {total_money}")
            
            input("\nPress Enter to continue to next round...")
            i += 1

def main():
    random.seed(int(time.time()))
    
    print("Welcome to Texas Hold'em Poker!\n")
    name = input("Enter your name: ")
    print(f"OK {name} let's play some poker!\n")
    input("Press Enter to start the game...")
    
    game = PokerGame()
    game.start(name)

if __name__ == "__main__":
    main()