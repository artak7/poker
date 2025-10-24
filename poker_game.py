import random
import time
import pygame
from typing import List, Tuple
from poker_gui import PokerGUI
# from poker_gui_old import PokerGUI


class Card:
    def __init__(self, suit: int = 0, rank: int = 0):
        self.suit = suit
        self.rank = rank


class Deck:
    def __init__(self):
        self.suits = ["♦", "♠", "♥", "♣"]
        self.ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        self.cards: List[Card] = []
        self.top = 0
        self.reset()

    def reset(self):
        self.cards = [Card(s, r) for s in range(4) for r in range(13)]
        self.top = 0

    def shuffle(self):
        random.shuffle(self.cards)
        self.top = 0

    def hitme(self) -> Card:
        if self.top >= len(self.cards):
            self.reset()
            random.shuffle(self.cards)
            self.top = 0
        c = self.cards[self.top]
        self.top += 1
        return c


class Player:
    def __init__(self, name: str = ""):
        self.name = name
        self.money = 0
        self.cards = [Card(), Card()]
        self.playing = True
        self.round = True
        self.is_ai = True
        self.goodToGo = False
        self.last_action = ""  # Track last action for display
        self.bet_this_round = 0  # Track how much bet in current betting round


class PokerGame:
    """A minimal, stable poker game loop integrated with the pygame GUI.

    Goals fulfilled:
    - community cards persist on the table until the end of the hand
    - human actions are driven by GUI buttons (non-blocking polling)
    - players with zero money are removed from play
    - simple betting model sufficient for UI testing
    """

    def __init__(self):
        self.players = [Player() for _ in range(6)]
        self.deck = Deck()
        self.tableCards = [Card() for _ in range(5)]
        for c in self.tableCards:
            c.rank = -1
        self.pot = 0
        self.gui = PokerGUI()
        self.current_player = 4  # default human seat
        self.human_index = 4
        self.betOn = 0  # Current bet amount that players need to match

    def card_to_tuple(self, card: Card) -> Tuple[str, str]:
        if card.rank < 0 or card.rank >= len(self.deck.ranks):
            return ("", "")
        if card.suit < 0 or card.suit >= len(self.deck.suits):
            return ("", "")
        return (self.deck.ranks[card.rank], self.deck.suits[card.suit])

    def get_game_state(self, showdown=False) -> dict:
        players_data = []
        for i, p in enumerate(self.players):
            # At showdown, show all cards of players still in the round
            show_cards = (i == self.human_index) and p.round
            if showdown and p.round:
                show_cards = True
            
            # Always show human player's cards, even if they folded
            show_human_cards = (i == self.human_index)
            if show_human_cards:
                show_cards = True
            
            # Show cards if: player is still in round OR is human player OR showdown for active players
            has_cards = p.round or (i == self.human_index)
            
            players_data.append({
                'name': p.name,
                'money': p.money,
                'cards': [self.card_to_tuple(c) for c in p.cards] if has_cards else [],
                'show_cards': show_cards,
                'round': p.round,
                'active': (i == self.current_player),
                'last_action': p.last_action if hasattr(p, 'last_action') else ""
            })
        community = []
        # always return exactly 5 slots; GUI will render backs for unknown cards
        for c in self.tableCards:
            if c.rank >= 0:
                community.append(self.card_to_tuple(c))
            else:
                community.append(None)
        return {
            'players': players_data,
            'community_cards': community,
            'pot': self.pot,
            'current_player': self.current_player,
            'human_index': self.human_index,
            'available_actions': []
        }

    def update_display(self, extra_actions: List[str] = None, action_text: str = "", showdown=False):
        state = self.get_game_state(showdown=showdown)
        if extra_actions:
            state['available_actions'] = extra_actions
        if action_text:
            # gui has a field current_action; set it directly for display
            self.gui.current_action = action_text
        self.gui.draw(state)

    def start(self, name: str):
        names = ["Alex", "Ivan", "Boris", "Lisa", name, "Katya"]
        for i, p in enumerate(self.players):
            p.name = names[i]
            p.money = 1000
            p.is_ai = (i != self.human_index)
            p.playing = True
            p.round = True

        self.run()

    def deal(self):
        self.deck.reset()
        self.deck.shuffle()
        for i in range(6):
            if self.players[i].playing:
                self.players[i].cards[0] = self.deck.hitme()
                self.players[i].cards[1] = self.deck.hitme()
        for c in self.tableCards:
            c.rank = -1

    def flop(self):
        for i in range(3):
            self.tableCards[i] = self.deck.hitme()

    def turn(self):
        self.tableCards[3] = self.deck.hitme()

    def river(self):
        self.tableCards[4] = self.deck.hitme()
    
    def get_hand_score(self, hand: List[Card]) -> tuple:
        """Calculate poker hand score as tuple for proper comparison with kickers.
        Returns: (hand_rank, primary_value, kicker1, kicker2, kicker3, ...)
        """
        hand_sorted = sorted(hand, key=lambda x: x.rank, reverse=True)
        
        # Count rank frequencies
        rank_counts = {}
        for card in hand_sorted:
            rank_counts[card.rank] = rank_counts.get(card.rank, 0) + 1
        
        # Sort by count, then by rank
        sorted_ranks = sorted(rank_counts.items(), key=lambda x: (x[1], x[0]), reverse=True)
        
        # Check for flush
        suits = [card.suit for card in hand]
        is_flush = len(set(suits)) == 1
        
        # Check for straight
        ranks = sorted([card.rank for card in hand])
        is_straight = all(ranks[i] == ranks[i-1] + 1 for i in range(1, 5))
        # Special case: A-2-3-4-5 (wheel)
        if ranks == [0, 1, 2, 3, 12]:
            is_straight = True
            ranks = [0, 1, 2, 3, 4]  # Treat ace as low
        
        # Get kickers (cards not part of the main combination)
        def get_kickers(exclude_ranks, count):
            kickers = []
            for card in hand_sorted:
                if card.rank not in exclude_ranks:
                    kickers.append(card.rank)
                if len(kickers) >= count:
                    break
            return tuple(kickers + [0] * (count - len(kickers)))
        
        # Straight Flush
        if is_straight and is_flush:
            return (8, max(ranks), 0, 0, 0)
        
        # Four of a Kind
        if sorted_ranks[0][1] == 4:
            quad_rank = sorted_ranks[0][0]
            kicker = get_kickers([quad_rank], 1)
            return (7, quad_rank, kicker[0], 0, 0)
        
        # Full House
        if sorted_ranks[0][1] == 3 and sorted_ranks[1][1] == 2:
            return (6, sorted_ranks[0][0], sorted_ranks[1][0], 0, 0)
        
        # Flush
        if is_flush:
            all_ranks = tuple(sorted([card.rank for card in hand_sorted], reverse=True))
            return (5,) + all_ranks
        
        # Straight
        if is_straight:
            return (4, max(ranks), 0, 0, 0)
        
        # Three of a Kind
        if sorted_ranks[0][1] == 3:
            trip_rank = sorted_ranks[0][0]
            kickers = get_kickers([trip_rank], 2)
            return (3, trip_rank, kickers[0], kickers[1], 0)
        
        # Two Pair
        if sorted_ranks[0][1] == 2 and sorted_ranks[1][1] == 2:
            high_pair = max(sorted_ranks[0][0], sorted_ranks[1][0])
            low_pair = min(sorted_ranks[0][0], sorted_ranks[1][0])
            kickers = get_kickers([high_pair, low_pair], 1)
            return (2, high_pair, low_pair, kickers[0], 0)
        
        # One Pair
        if sorted_ranks[0][1] == 2:
            pair_rank = sorted_ranks[0][0]
            kickers = get_kickers([pair_rank], 3)
            return (1, pair_rank, kickers[0], kickers[1], kickers[2])
        
        # High Card
        all_ranks = tuple(sorted([card.rank for card in hand_sorted], reverse=True))
        return (0,) + all_ranks
    
    def evaluate_best_hand(self, player_idx: int) -> tuple:
        """Find best 5-card combination from player's 2 cards + 5 community cards.
        Returns tuple for proper comparison with kickers.
        """
        if not self.players[player_idx].round:
            return (-1, 0, 0, 0, 0)
        
        best_score = (-1, 0, 0, 0, 0)
        # Try all combinations of 3 cards from table + 2 player cards
        for i in range(5):
            for j in range(i + 1, 5):
                for k in range(j + 1, 5):
                    hand = [
                        self.tableCards[i],
                        self.tableCards[j],
                        self.tableCards[k],
                        self.players[player_idx].cards[0],
                        self.players[player_idx].cards[1]
                    ]
                    score = self.get_hand_score(hand)
                    if score > best_score:
                        best_score = score
        
        return best_score
    
    def get_hand_name(self, score: tuple) -> str:
        """Convert hand score tuple to readable name."""
        hand_rank = score[0]
        hand_names = [
            "High Card",
            "Pair",
            "Two Pair",
            "Three of a Kind",
            "Straight",
            "Flush",
            "Full House",
            "Four of a Kind",
            "Straight Flush"
        ]
        if hand_rank >= 0 and hand_rank < len(hand_names):
            return hand_names[hand_rank]
        return "Unknown Hand"

    def simple_betting_round(self) -> bool:
        """Betting round with fold, call, raise, and all-in options.
        Human chooses using GUI buttons. This function polls GUI input (non-blocking) so the
        event loop continues and community cards stay visible.
        Returns False if the player requested quit.
        """
        bet_amount = 10
        
        # Reset goodToGo flags for this round
        for p in self.players:
            p.goodToGo = False
        
        # Continue betting until all active players have goodToGo flag set
        while True:
            # Check if all active players are goodToGo
            all_done = True
            for p in self.players:
                if p.round and p.playing and not p.goodToGo:
                    all_done = False
                    break
            if all_done:
                break
            
            for idx in range(6):
                if not self.players[idx].round or not self.players[idx].playing:
                    continue
                if self.players[idx].goodToGo:
                    continue
                # Skip players who are all-in (no money left)
                if self.players[idx].money <= 0:
                    self.players[idx].goodToGo = True
                    continue
                
                self.current_player = idx
                # show UI with available actions if this is human
                if not self.players[idx].is_ai:
                    # Determine available actions
                    can_call = self.players[idx].money >= self.betOn
                    can_raise = self.players[idx].money > self.betOn
                    
                    if self.betOn > 0:
                        if can_raise:
                            actions_for_human = ['Fold', 'Check/Call', 'Raise', 'All-In']
                        elif can_call:
                            actions_for_human = ['Fold', 'Check/Call', 'All-In']
                        else:
                            actions_for_human = ['Fold', 'All-In']
                    else:
                        actions_for_human = ['Fold', 'Check/Call', 'Raise', 'All-In']
                    
                    bet_info = f" (bet: ${self.betOn})" if self.betOn > 0 else ""
                    self.update_display(extra_actions=actions_for_human,
                                        action_text=f"Your turn, {self.players[idx].name}{bet_info}")
                    # poll until human chooses
                    while True:
                        ev = self.gui.handle_input()
                        if ev == 'QUIT':
                            return False
                        if ev in actions_for_human:
                            if ev == 'Fold':
                                self.players[idx].round = False
                                self.players[idx].last_action = "Fold"
                                self.update_display(action_text=f"{self.players[idx].name} folds")
                                pygame.time.wait(500)
                            elif ev == 'Check/Call':
                                if self.betOn > 0:
                                    # Call: pay the full betOn amount
                                    pay = min(self.betOn, self.players[idx].money)
                                    self.players[idx].money -= pay
                                    self.pot += pay
                                    self.players[idx].goodToGo = True
                                    self.players[idx].last_action = f"Call ${pay}"
                                    self.update_display(action_text=f"{self.players[idx].name} calls ${pay}")
                                else:
                                    self.players[idx].goodToGo = True
                                    self.players[idx].last_action = "Check"
                                    self.update_display(action_text=f"{self.players[idx].name} checks")
                                pygame.time.wait(500)
                            elif ev == 'Raise':
                                # Show raise dialog
                                self.gui.show_raise_dialog = True
                                # Min raise = current bet + minimum raise (at least double)
                                self.gui.min_raise = self.betOn + 10 if self.betOn > 0 else 10
                                # Max raise = player's money
                                self.gui.max_raise = self.players[idx].money
                                # Default raise amount
                                self.gui.raise_amount = min(self.gui.min_raise, self.gui.max_raise)
                                
                                # Initial draw with raise dialog
                                state = self.get_game_state()
                                state['available_actions'] = actions_for_human
                                self.gui.draw(state)
                                
                                while self.gui.show_raise_dialog:
                                    prev_amount = self.gui.raise_amount
                                    ev = self.gui.handle_input()
                                    if ev == 'QUIT':
                                        return False
                                    elif ev == 'RAISE_CONFIRM':
                                        raise_amount = self.gui.raise_amount
                                        # Calculate additional bet: difference from current bet
                                        additional_bet = raise_amount - self.betOn
                                        
                                        if additional_bet > self.players[idx].money:
                                            additional_bet = self.players[idx].money
                                            raise_amount = self.betOn + additional_bet
                                        
                                        self.pot += additional_bet
                                        self.players[idx].money -= additional_bet
                                        self.betOn = raise_amount
                                        
                                        self.players[idx].goodToGo = True
                                        self.players[idx].last_action = f"Raise ${self.betOn}"
                                        # Reset other players' goodToGo flags
                                        for i in range(6):
                                            if i != idx:
                                                self.players[i].goodToGo = False
                                        
                                        self.gui.show_raise_dialog = False
                                        self.update_display(action_text=f"{self.players[idx].name} raises to ${self.betOn}")
                                        pygame.time.wait(800)
                                        break
                                    elif ev == 'RAISE_CANCEL':
                                        self.gui.show_raise_dialog = False
                                        break
                                    
                                    # Redraw if amount changed (from +/- buttons)
                                    if self.gui.raise_amount != prev_amount:
                                        state = self.get_game_state()
                                        state['available_actions'] = actions_for_human
                                        self.gui.draw(state)
                                    
                                    time.sleep(0.05)
                                
                                self.gui.show_raise_dialog = False
                                if ev == 'RAISE_CANCEL':
                                    continue
                            elif ev == 'All-In':
                                pay = self.players[idx].money
                                self.pot += pay
                                self.players[idx].money = 0
                                self.players[idx].goodToGo = True
                                self.players[idx].last_action = f"All-in ${pay}"
                                
                                # If all-in is more than current bet, update betOn and reset other players
                                if pay > self.betOn:
                                    self.betOn = pay
                                    for i in range(6):
                                        if i != idx:
                                            self.players[i].goodToGo = False
                                
                                self.update_display(action_text=f"{self.players[idx].name} goes all-in ${pay}")
                                pygame.time.wait(800)
                            break
                        # redraw to keep screen responsive
                        self.update_display(extra_actions=actions_for_human)
                        time.sleep(0.05)
                else:
                    # AI action
                    self.update_display(action_text=f"{self.players[idx].name} is thinking...")
                    # Check for quit events during AI turn
                    for _ in range(10):
                        ev = self.gui.handle_input()
                        if ev == 'QUIT':
                            return False
                        time.sleep(0.05)
                    
                    # Simple AI logic
                    can_call = self.players[idx].money >= self.betOn
                    can_raise = self.players[idx].money > self.betOn
                    
                    # Calculate AI action based on hand strength
                    high_card = max(self.players[idx].cards[0].rank, self.players[idx].cards[1].rank)
                    pair = self.players[idx].cards[0].rank == self.players[idx].cards[1].rank
                    
                    action_choice = random.random()
                    
                    if high_card < 8 and not pair:
                        # Weak hand - mostly fold or check
                        if self.betOn > bet_amount:
                            self.players[idx].round = False
                            self.players[idx].last_action = "Fold"
                            action_msg = f"{self.players[idx].name} folds"
                        elif self.betOn > 0:
                            if action_choice < 0.3 and can_call:
                                pay = min(self.betOn, self.players[idx].money)
                                self.players[idx].money -= pay
                                self.pot += pay
                                self.players[idx].goodToGo = True
                                self.players[idx].last_action = f"Call ${pay}"
                                action_msg = f"{self.players[idx].name} calls ${pay}"
                            else:
                                self.players[idx].round = False
                                self.players[idx].last_action = "Fold"
                                action_msg = f"{self.players[idx].name} folds"
                        else:
                            self.players[idx].goodToGo = True
                            self.players[idx].last_action = "Check"
                            action_msg = f"{self.players[idx].name} checks"
                    elif high_card >= 10 or pair:
                        # Strong hand - call or raise
                        if self.betOn > 0:
                            if action_choice < 0.6 and can_call:
                                pay = min(self.betOn, self.players[idx].money)
                                self.players[idx].money -= pay
                                self.pot += pay
                                self.players[idx].goodToGo = True
                                self.players[idx].last_action = f"Call ${pay}"
                                action_msg = f"{self.players[idx].name} calls ${pay}"
                            elif can_raise and action_choice < 0.85:
                                # Raise
                                min_raise = self.betOn * 2
                                max_raise = min(self.players[idx].money, self.betOn * 3)
                                raise_to = random.randint(min_raise, max_raise) if max_raise > min_raise else min_raise
                                
                                # Calculate additional bet (difference from current bet)
                                additional_bet = raise_to - self.betOn
                                additional_bet = min(additional_bet, self.players[idx].money)
                                
                                self.pot += additional_bet
                                self.players[idx].money -= additional_bet
                                self.betOn = raise_to
                                self.players[idx].goodToGo = True
                                self.players[idx].last_action = f"Raise ${self.betOn}"
                                
                                # Reset other players
                                for i in range(6):
                                    if i != idx:
                                        self.players[i].goodToGo = False
                                
                                action_msg = f"{self.players[idx].name} raises to ${self.betOn}"
                            else:
                                pay = min(self.betOn, self.players[idx].money)
                                self.players[idx].money -= pay
                                self.pot += pay
                                self.players[idx].goodToGo = True
                                self.players[idx].last_action = f"Call ${pay}"
                                action_msg = f"{self.players[idx].name} calls ${pay}"
                        else:
                            # No bet yet - bet or check
                            if action_choice < 0.5:
                                bet = random.randint(bet_amount, bet_amount * 3)
                                bet = min(bet, self.players[idx].money)
                                self.pot += bet
                                self.players[idx].money -= bet
                                self.betOn = bet
                                self.players[idx].goodToGo = True
                                self.players[idx].last_action = f"Bet ${bet}"
                                
                                for i in range(6):
                                    if i != idx:
                                        self.players[i].goodToGo = False
                                
                                action_msg = f"{self.players[idx].name} bets ${bet}"
                            else:
                                self.players[idx].goodToGo = True
                                self.players[idx].last_action = "Check"
                                action_msg = f"{self.players[idx].name} checks"
                    else:
                        # Medium hand
                        if self.betOn > 0:
                            if action_choice < 0.7 and can_call:
                                pay = min(self.betOn, self.players[idx].money)
                                self.players[idx].money -= pay
                                self.pot += pay
                                self.players[idx].goodToGo = True
                                self.players[idx].last_action = f"Call ${pay}"
                                action_msg = f"{self.players[idx].name} calls ${pay}"
                            else:
                                self.players[idx].round = False
                                self.players[idx].last_action = "Fold"
                                action_msg = f"{self.players[idx].name} folds"
                        else:
                            self.players[idx].goodToGo = True
                            self.players[idx].last_action = "Check"
                            action_msg = f"{self.players[idx].name} checks"
                    
                    # Show action result
                    self.update_display(action_text=action_msg)
                    pygame.time.wait(800)  # Pause to show action
        return True

    def run(self):
        running = True
        self.gui.current_action = "Game started"
        self.update_display()
        time.sleep(0.5)

        while running and sum(1 for p in self.players if p.money > 0) > 1:
            # setup round
            for p in self.players:
                p.round = p.money > 0
                p.playing = p.money > 0
                p.last_action = ""  # Reset action display for new round
            self.pot = 0
            self.betOn = 0
            self.deal()
            self.update_display(action_text="Dealt")
            pygame.time.wait(1000)

            if not self.simple_betting_round():
                break

            self.flop()
            self.betOn = 0
            for p in self.players:
                p.goodToGo = False
            self.update_display(action_text="Flop")
            pygame.time.wait(1000)
            if not self.simple_betting_round():
                break

            self.turn()
            self.betOn = 0
            for p in self.players:
                p.goodToGo = False
            self.update_display(action_text="Turn")
            pygame.time.wait(1000)
            if not self.simple_betting_round():
                break

            self.river()
            self.betOn = 0
            for p in self.players:
                p.goodToGo = False
            self.update_display(action_text="River")
            pygame.time.wait(1000)
            if not self.simple_betting_round():
                break

            # Showdown - reveal all cards and determine winner
            active = [i for i, p in enumerate(self.players) if p.round]
            if active:
                # Show all remaining players' cards
                self.gui.current_action = "Showdown!"
                self.update_display(showdown=True)
                pygame.time.wait(2000)  # Pause to see all cards
                
                # Check for quit during showdown
                for _ in range(20):
                    ev = self.gui.handle_input()
                    if ev == 'QUIT':
                        running = False
                        break
                    time.sleep(0.05)
                
                if not running:
                    break
                
                # Evaluate hands and find winner
                best_score = (-1, 0, 0, 0, 0)
                winner = active[0]
                for player_idx in active:
                    score = self.evaluate_best_hand(player_idx)
                    if score > best_score:
                        best_score = score
                        winner = player_idx
                
                hand_name = self.get_hand_name(best_score)
                self.players[winner].money += self.pot
                self.gui.current_action = f"{self.players[winner].name} wins ${self.pot} with {hand_name}!"
                
                # Wait for user to click Continue button
                state = self.get_game_state(showdown=True)
                state['available_actions'] = ['Continue']
                self.gui.draw(state)
                
                waiting = True
                while waiting:
                    ev = self.gui.handle_input()
                    if ev == 'QUIT':
                        running = False
                        waiting = False
                    elif ev == 'Continue':
                        waiting = False
                    time.sleep(0.05)
                
                if not running:
                    break
                
                # Check if human player is out of money
                if self.players[self.human_index].money <= 0:
                    self.gui.current_action = "Game Over - You ran out of money!"
                    state = self.get_game_state(showdown=False)
                    state['available_actions'] = ['Continue']
                    self.gui.draw(state)
                    
                    # Wait for user acknowledgment
                    waiting = True
                    while waiting:
                        ev = self.gui.handle_input()
                        if ev == 'QUIT' or ev == 'Continue':
                            waiting = False
                        time.sleep(0.05)
                    break

        pygame.quit()


def show_welcome_screen(screen, fonts):
    """Show a simple welcome screen to enter the player's name."""
    running = True
    player_name = ""
    input_active = True

    while running:
        screen.fill((6, 100, 36))
        title = fonts['large'].render("TEXAS POKER", True, (255, 215, 0))
        title_rect = title.get_rect(center=(screen.get_width() // 2, screen.get_height() // 3))
        screen.blit(title, title_rect)

        prompt = fonts['medium'].render("Enter your name:", True, (255, 255, 255))
        prompt_rect = prompt.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(prompt, prompt_rect)

        name_surface = fonts['medium'].render(player_name + ("_" if input_active else ""), True, (255, 255, 255))
        name_rect = name_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50))
        screen.blit(name_surface, name_rect)

        if not player_name:
            instruction = fonts['small'].render("Type your name and press Enter to start", True, (200, 200, 200))
            instruction_rect = instruction.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 100))
            screen.blit(instruction, instruction_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and player_name:
                    return player_name
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    if len(player_name) < 15:
                        player_name += event.unicode

        pygame.time.wait(50)


def main():
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("Texas Poker")
    fonts = {
        'large': pygame.font.Font(None, 72),
        'medium': pygame.font.Font(None, 48),
        'small': pygame.font.Font(None, 24)
    }

    player_name = show_welcome_screen(screen, fonts)
    if not player_name:
        pygame.quit()
        return

    game = PokerGame()
    game.start(player_name)


if __name__ == '__main__':
    main()