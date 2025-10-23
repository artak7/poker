import pygame
import math
from typing import List, Tuple, Optional

class PokerGUI:
    def __init__(self):
        pygame.init()
        # Получаем информацию о разрешении экрана
        info = pygame.display.Info()
        self.screen_width = info.current_w
        self.screen_height = info.current_h
        
        # Устанавливаем размер окна как 80% от размера экрана
        self.width = int(self.screen_width * 0.8)
        self.height = int(self.screen_height * 0.8)
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Texas Hold'em Poker")
        
        # Цвета
        self.COLORS = {
            'table': (53, 101, 77),  # Зеленый цвет стола
            'felt': (34, 139, 34),   # Цвет сукна
            'white': (255, 255, 255),
            'gold': (255, 215, 0),
            'black': (0, 0, 0),
            'red': (255, 0, 0),
            'blue': (0, 70, 200),
            'gray': (128, 128, 128)
        }
        
        # Инициализация шрифтов
        self.update_fonts()
        
        # Размеры элементов
        self.update_dimensions()

    def update_dimensions(self):
        """Обновление размеров элементов при изменении размера окна"""
        self.card_width = int(self.width * 0.06)
        self.card_height = int(self.card_width * 1.4)
        self.chip_radius = int(self.width * 0.02)
        self.button_width = int(self.width * 0.12)
        self.button_height = int(self.height * 0.06)
        self.player_spot_radius = int(self.width * 0.08)

    def update_fonts(self):
        """Обновление шрифтов при изменении размера окна"""
        self.fonts = {
            'large': pygame.font.Font(None, int(self.height * 0.05)),
            'medium': pygame.font.Font(None, int(self.height * 0.04)),
            'small': pygame.font.Font(None, int(self.height * 0.03))
        }

    def draw_card(self, pos: Tuple[int, int], card: Tuple[str, str], face_up: bool = True):
        """Отрисовка карты с тенью и закруглёнными углами"""
        rank, suit = card
        
        # Создаем поверхность для карты с альфа-каналом
        card_surf = pygame.Surface((self.card_width, self.card_height), pygame.SRCALPHA)
        
        # Рисуем тень
        shadow_offset = 3
        shadow_surf = pygame.Surface((self.card_width, self.card_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 128), 
                        (shadow_offset, shadow_offset, self.card_width-shadow_offset, self.card_height-shadow_offset),
                        border_radius=10)
        
        if face_up:
            # Рисуем белую карту с закругленными углами
            pygame.draw.rect(card_surf, self.COLORS['white'], 
                           (0, 0, self.card_width, self.card_height),
                           border_radius=10)
            
            # Определяем цвет масти
            suit_color = self.COLORS['red'] if suit in ['♥', '♦'] else self.COLORS['black']
            
            # Отрисовка ранга и масти
            rank_text = self.fonts['medium'].render(rank, True, suit_color)
            suit_text = self.fonts['medium'].render(suit, True, suit_color)
            
            # Размещаем ранг и масть в углах
            margin = 5
            card_surf.blit(rank_text, (margin, margin))
            card_surf.blit(suit_text, (margin, margin + rank_text.get_height()))
            
            # Большая масть в центре
            big_suit = self.fonts['large'].render(suit, True, suit_color)
            suit_rect = big_suit.get_rect(center=(self.card_width/2, self.card_height/2))
            card_surf.blit(big_suit, suit_rect)
        else:
            # Рубашка карты
            pygame.draw.rect(card_surf, self.COLORS['blue'], 
                           (0, 0, self.card_width, self.card_height),
                           border_radius=10)
            
            # Узор на рубашке
            pattern_color = self.COLORS['gold']
            margin = 10
            for i in range(margin, self.card_width-margin, 8):
                for j in range(margin, self.card_height-margin, 8):
                    pygame.draw.circle(card_surf, pattern_color, (i, j), 1)
        
        # Добавляем тень и карту на экран
        self.screen.blit(shadow_surf, pos)
        self.screen.blit(card_surf, pos)

    def draw_player_spot(self, pos: Tuple[int, int], player_data: dict):
        """Отрисовка места игрока с подсветкой для активного игрока"""
        x, y = pos
        
        # Рисуем подсветку для активного игрока
        if player_data['active']:
            glow_radius = self.player_spot_radius + 5
            pygame.draw.circle(self.screen, self.COLORS['gold'], pos, glow_radius)
        
        # Рисуем место игрока
        pygame.draw.circle(self.screen, self.COLORS['gray'], pos, self.player_spot_radius)
        pygame.draw.circle(self.screen, self.COLORS['felt'], pos, self.player_spot_radius - 2)
        
        # Имя игрока
        name_text = self.fonts['medium'].render(player_data['name'], True, self.COLORS['white'])
        name_rect = name_text.get_rect(center=(x, y - 15))
        self.screen.blit(name_text, name_rect)
        
        # Количество фишек
        money_text = self.fonts['small'].render(f"${player_data['money']}", True, self.COLORS['gold'])
        money_rect = money_text.get_rect(center=(x, y + 15))
        self.screen.blit(money_text, money_rect)
        
        # Отрисовка карт игрока
        if player_data['cards']:
            card_x = x - self.card_width - 5
            card_y = y - self.card_height/2
            for i, card in enumerate(player_data['cards']):
                self.draw_card((int(card_x + i*(self.card_width + 10)), int(card_y)),
                             card, face_up=player_data['show_cards'])

    def draw_community_cards(self, cards: List[Tuple[str, str]]):
        """Отрисовка общих карт"""
        if not cards:
            return
            
        # Расчет начальной позиции для общих карт
        total_width = len(cards) * self.card_width + (len(cards) - 1) * 10
        start_x = self.width/2 - total_width/2
        y = self.height/2 - self.card_height/2
        
        # Отрисовка карт с эффектом появления
        for i, card in enumerate(cards):
            x = start_x + i * (self.card_width + 10)
            self.draw_card((int(x), int(y)), card)

    def draw_pot(self, amount: int):
        """Отрисовка банка с фишками"""
        # Текст банка
        pot_text = self.fonts['large'].render(f"Pot: ${amount}", True, self.COLORS['gold'])
        text_rect = pot_text.get_rect(center=(self.width/2, self.height/2 + self.card_height))
        self.screen.blit(pot_text, text_rect)
        
        # Отрисовка стопок фишек разного номинала
        if amount > 0:
            chip_values = [100, 25, 5, 1]
            remaining = amount
            x_offset = -len(chip_values) * self.chip_radius
            for value in chip_values:
                num_chips = remaining // value
                if num_chips > 0:
                    self.draw_chip_stack(
                        (self.width/2 + x_offset, self.height/2 + self.card_height/2),
                        value, min(num_chips, 5)
                    )
                    remaining %= value
                x_offset += self.chip_radius * 2

    def draw_chip_stack(self, pos: Tuple[int, int], value: int, count: int):
        """Отрисовка стопки фишек"""
        x, y = pos
        colors = {
            1: self.COLORS['white'],
            5: self.COLORS['red'],
            25: self.COLORS['blue'],
            100: self.COLORS['black']
        }
        
        for i in range(count):
            y_offset = -i * 2  # Сдвиг каждой фишки вверх
            pygame.draw.circle(self.screen, colors[value], (x, y + y_offset), self.chip_radius)
            pygame.draw.circle(self.screen, self.COLORS['gold'], (x, y + y_offset), self.chip_radius - 2, 2)
            
            # Номинал фишки
            value_text = self.fonts['small'].render(str(value), True, self.COLORS['gold'])
            text_rect = value_text.get_rect(center=(x, y + y_offset))
            self.screen.blit(value_text, text_rect)

    def draw_table(self):
        """Отрисовка покерного стола с градиентом и бортиком"""
        # Внешний овал (бортик)
        pygame.draw.ellipse(self.screen, self.COLORS['black'],
                          (self.width*0.1, self.height*0.1,
                           self.width*0.8, self.height*0.8))
        
        # Внутренний овал (сукно)
        pygame.draw.ellipse(self.screen, self.COLORS['felt'],
                          (self.width*0.1 + 2, self.height*0.1 + 2,
                           self.width*0.8 - 4, self.height*0.8 - 4))

    def draw_buttons(self, enabled_actions: List[str]):
        """Отрисовка кнопок действий"""
        buttons = ['Fold', 'Check/Call', 'Raise', 'All-In']
        total_width = len(buttons) * self.button_width + (len(buttons) - 1) * 10
        start_x = self.width/2 - total_width/2
        y = self.height - self.button_height - 20
        
        for i, text in enumerate(buttons):
            enabled = text in enabled_actions
            color = self.COLORS['white'] if enabled else self.COLORS['gray']
            
            button_rect = pygame.Rect(start_x + i * (self.button_width + 10),
                                    y, self.button_width, self.button_height)
            
            # Рисуем тень для кнопки
            shadow_rect = button_rect.copy()
            shadow_rect.move_ip(2, 2)
            pygame.draw.rect(self.screen, (0, 0, 0, 128), shadow_rect, border_radius=5)
            
            # Рисуем кнопку
            pygame.draw.rect(self.screen, color, button_rect, border_radius=5)
            pygame.draw.rect(self.screen, self.COLORS['black'], button_rect, 2, border_radius=5)
            
            text_surface = self.fonts['small'].render(text, True, 
                                                    self.COLORS['black'] if enabled 
                                                    else self.COLORS['black'])
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)

    def draw(self, game_state: dict):
        """Основной метод отрисовки игры"""
        # Очищаем экран
        self.screen.fill(self.COLORS['black'])
        
        # Рисуем стол
        self.draw_table()
        
        # Расставляем игроков по кругу
        num_players = len(game_state['players'])
        radius = min(self.width, self.height) * 0.35
        center_x = self.width / 2
        center_y = self.height / 2
        
        # Отрисовка игроков
        for i, player in enumerate(game_state['players']):
            angle = (2 * math.pi * i / num_players) - math.pi/2
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.draw_player_spot((int(x), int(y)), player)
        
        # Отрисовка общих карт
        if game_state['community_cards']:
            self.draw_community_cards(game_state['community_cards'])
        
        # Отрисовка банка
        self.draw_pot(game_state['pot'])
        
        # Отрисовка кнопок для текущего игрока
        if game_state['current_player'] == 0:  # Если ход человека
            self.draw_buttons(game_state['available_actions'])
        
        # Обновляем экран
        pygame.display.flip()

    def handle_resize(self, event):
        """Обработка изменения размера окна"""
        self.width = event.w
        self.height = event.h
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.update_fonts()
        self.update_dimensions()

    def handle_input(self) -> Optional[str]:
        """Обработка пользовательского ввода"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'QUIT'
            elif event.type == pygame.VIDEORESIZE:
                self.handle_resize(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Проверяем клики по кнопкам
                mouse_pos = pygame.mouse.get_pos()
                return self.check_button_click(mouse_pos)
        return None

    def check_button_click(self, pos: Tuple[int, int]) -> Optional[str]:
        """Проверка клика по кнопкам"""
        buttons = ['Fold', 'Check/Call', 'Raise', 'All-In']
        total_width = len(buttons) * self.button_width + (len(buttons) - 1) * 10
        start_x = self.width/2 - total_width/2
        y = self.height - self.button_height - 20
        
        for i, text in enumerate(buttons):
            button_rect = pygame.Rect(start_x + i * (self.button_width + 10),
                                    y, self.button_width, self.button_height)
            if button_rect.collidepoint(pos):
                return text
        return None