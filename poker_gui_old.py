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
        
        # Устанавливаем минимальный размер окна и начальный размер
        self.min_width = 1024
        self.min_height = 768
        self.width = max(int(self.screen_width * 0.8), self.min_width)
        self.height = max(int(self.screen_height * 0.8), self.min_height)
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Texas Hold'em Poker")
        
        # Текущее действие для отображения
        self.current_action = ""
        
        # Raise dialog state
        self.show_raise_dialog = False
        self.raise_amount = 0
        self.min_raise = 0
        self.max_raise = 0
        
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
        
        # Инициализируем размеры элементов и шрифты
        self.update_dimensions()
        self.update_fonts()

    def update_dimensions(self):
        """Обновление размеров элементов при изменении размера окна"""
        # Используем минимальные размеры для расчета пропорций
        base_width = min(self.width, max(1024, self.width))
        base_height = min(self.height, max(768, self.height))
        
        self.card_width = int(base_width * 0.055)  # Уменьшили размер карт
        self.card_height = int(self.card_width * 1.4)
        self.chip_radius = int(base_width * 0.02)
        self.button_width = int(base_width * 0.15)
        self.button_height = int(base_height * 0.08)
        self.player_spot_radius = int(base_width * 0.08)  # Уменьшили размер места игрока
        
        # Обновляем шрифты при изменении размеров
        self.update_fonts()

    def update_fonts(self):
        """Обновление шрифтов при изменении размера окна"""
        base_height = min(self.height, max(768, self.height))
        self.fonts = {
            'large': pygame.font.Font(None, int(base_height * 0.08)),  # Увеличили с 0.05 до 0.08
            'medium': pygame.font.Font(None, int(base_height * 0.06)),  # Увеличили с 0.04 до 0.06
            'small': pygame.font.Font(None, int(base_height * 0.045))  # Увеличили с 0.03 до 0.045
        }

    def draw_card(self, pos: Tuple[int, int], card, face_up: bool = True):
        """Отрисовка карты с тенью и закруглёнными углами.

        card может быть None — в этом случае рисуется рубашка.
        Также допускаются пустые кортежи/строки для рубашки.
        """
        # Защитимся от None или некорректных значений
        if not card or not isinstance(card, (list, tuple)) or len(card) != 2:
            face_up = False
            rank, suit = "", ""
        else:
            rank, suit = card
            # If either is empty, treat as face-down
            if not rank or not suit:
                face_up = False
        
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
        
        # Создаем поверхность для места игрока
        spot_width = self.player_spot_radius * 2.5
        spot_height = self.player_spot_radius * 3
        spot_surface = pygame.Surface((spot_width, spot_height), pygame.SRCALPHA)
        
        # Рисуем подсветку для активного игрока
        if player_data['active']:
            glow_radius = self.player_spot_radius + 5
            pygame.draw.circle(spot_surface, (255, 215, 0, 100), 
                             (spot_width/2, spot_height/2), glow_radius)
        
        # Рисуем фон места игрока
        background_color = (200, 0, 0, 200) if not player_data.get('round', True) else (50, 50, 50, 200)
        pygame.draw.circle(spot_surface, background_color, 
                         (spot_width/2, spot_height/2), self.player_spot_radius)
        
        # Рисуем окантовку
        border_color = (255, 215, 0) if player_data['active'] else (200, 200, 200)
        pygame.draw.circle(spot_surface, border_color, 
                         (spot_width/2, spot_height/2), self.player_spot_radius, 2)
        
        # Имя игрока
        name_height = self.player_spot_radius * 0.4
        name_y = spot_height/2 - self.player_spot_radius - name_height
        
        name_bg = pygame.Surface((spot_width, name_height), pygame.SRCALPHA)
        name_bg.fill((0, 0, 0, 180))
        spot_surface.blit(name_bg, (0, name_y))
        
        name_text = self.fonts['small'].render(player_data['name'], True, self.COLORS['white'])
        name_rect = name_text.get_rect(center=(spot_width/2, name_y + name_height/2))
        spot_surface.blit(name_text, name_rect)
        
        # Количество фишек
        money_height = self.player_spot_radius * 0.4
        money_y = spot_height/2 + self.player_spot_radius
        
        money_bg = pygame.Surface((spot_width, money_height), pygame.SRCALPHA)
        money_bg.fill((0, 0, 0, 180))
        spot_surface.blit(money_bg, (0, money_y))
        
        money_text = self.fonts['small'].render(f"${player_data['money']}", True, self.COLORS['gold'])
        money_rect = money_text.get_rect(center=(spot_width/2, money_y + money_height/2))
        spot_surface.blit(money_text, money_rect)
        
        # Если игрок сбросил карты
        if not player_data.get('round', True):
            fold_text = self.fonts['small'].render("FOLD", True, self.COLORS['red'])
            fold_rect = fold_text.get_rect(center=(spot_width/2, spot_height/2))
            spot_surface.blit(fold_text, fold_rect)
        
        # Отображаем карты игрока
        if player_data.get('cards'):
            card_y = spot_height/2 - self.card_height/2
            card_spacing = 5
            total_cards_width = len(player_data['cards']) * self.card_width + (len(player_data['cards'])-1) * card_spacing
            card_start_x = (spot_width - total_cards_width) / 2
            
            for i, card in enumerate(player_data['cards']):
                card_x = card_start_x + i * (self.card_width + card_spacing)
                self.draw_card((int(x - spot_width/2 + card_x), int(y - self.card_height/2)),
                             card, face_up=player_data['show_cards'])
        
        # Отображаем всё на экране
        final_rect = spot_surface.get_rect(center=(x, y))
        self.screen.blit(spot_surface, final_rect)

    def draw_community_cards(self, cards: List[Tuple[str, str]]):
        """Отрисовка общих карт"""
        # Всегда рисуем 5 слотов для общих карт (даже если некоторые еще не выложены)
        slots = 5
        spacing = max(10, int(self.card_width * 0.2))
        total_width = slots * self.card_width + (slots - 1) * spacing
        start_x = self.width / 2 - total_width / 2
        y = int(self.height / 2 - self.card_height / 2)

        for i in range(slots):
            x = start_x + i * (self.card_width + spacing)
            # Защищаемся от None: если в списке слотов None — рисуем рубашку
            if i < len(cards) and cards[i]:
                self.draw_card((int(x), int(y)), cards[i], face_up=True)
            else:
                # Показываем рубашку (пустой слот)
                self.draw_card((int(x), int(y)), ("", ""), face_up=False)

    def draw_pot(self, amount: int):
        """Отрисовка банка с фишками и игровой информации"""
        # Текст банка
        pot_text = self.fonts['large'].render(f"Pot: ${amount}", True, self.COLORS['gold'])
        text_rect = pot_text.get_rect(center=(self.width/2, self.height/2 + self.card_height))
        self.screen.blit(pot_text, text_rect)
        
        # Отображение текущего действия (если есть)
        if hasattr(self, 'current_action'):
            action_text = self.fonts['medium'].render(self.current_action, True, self.COLORS['white'])
            action_rect = action_text.get_rect(center=(self.width/2, 50))
            self.screen.blit(action_text, action_rect)
        
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
        table_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Размеры стола
        table_width = self.width * 0.8
        table_height = self.height * 0.8
        x = self.width * 0.1
        y = self.height * 0.1
        
        # Тень стола
        shadow_offset = 20
        shadow = pygame.Surface((table_width + shadow_offset*2, table_height + shadow_offset*2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 100), shadow.get_rect())
        self.screen.blit(shadow, (x - shadow_offset, y - shadow_offset))
        
        # Внешний бортик (темное дерево)
        border_width = 20
        pygame.draw.ellipse(self.screen, (80, 40, 0), (x, y, table_width, table_height))
        
        # Внутренний бортик (светлое дерево)
        pygame.draw.ellipse(self.screen, (120, 60, 0), 
                          (x + border_width/2, y + border_width/2,
                           table_width - border_width, table_height - border_width))
        
        # Основное сукно
        felt_color = (0, 100, 0)  # Темно-зеленый
        pygame.draw.ellipse(self.screen, felt_color,
                          (x + border_width, y + border_width,
                           table_width - border_width*2, table_height - border_width*2))
        
        # Градиент на сукне для создания эффекта освещения
        gradient_surface = pygame.Surface((table_width, table_height), pygame.SRCALPHA)
        for i in range(int(table_height/2)):
            alpha = int(100 * (1 - i/(table_height/2)))
            pygame.draw.ellipse(gradient_surface, (255, 255, 255, alpha),
                              (i, i, table_width-i*2, table_height-i*2), 1)
        
        self.screen.blit(gradient_surface, (x, y))
        
        # Декоративная строчка на бортике
        stitch_color = (150, 75, 0)
        pygame.draw.ellipse(self.screen, stitch_color,
                          (x + border_width - 2, y + border_width - 2,
                           table_width - (border_width-2)*2, table_height - (border_width-2)*2), 2)

    def draw_buttons(self, enabled_actions: List[str]):
        """Отрисовка кнопок действий"""
        if not enabled_actions:  # Если нет доступных действий, не рисуем кнопки
            return
        
        # Определяем активные кнопки и их тексты
        button_data = [
            ('Fold', 'FOLD', (200, 50, 50)),
            ('Check/Call', 'CHECK/CALL', (50, 150, 50)),
            ('Raise', 'RAISE', (50, 50, 200)),
            ('All-In', 'ALL-IN', (200, 150, 50))
        ]
        
        # Фильтруем только доступные действия
        active_buttons = [b for b in button_data if b[0] in enabled_actions]
        
        # Настройка размещения кнопок
        padding = 20
        total_width = len(active_buttons) * self.button_width + (len(active_buttons) - 1) * padding
        start_x = self.width/2 - total_width/2
        y = self.height - self.button_height - 30  # Отступ снизу
        
        # Рисуем фон для кнопок
        bg_height = self.button_height + 20
        bg_surface = pygame.Surface((self.width, bg_height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 180))
        self.screen.blit(bg_surface, (0, y - 10))
        
        # Рисуем кнопки
        for i, (action, text, color) in enumerate(active_buttons):
            button_x = start_x + i * (self.button_width + padding)
            button_rect = pygame.Rect(button_x, y, self.button_width, self.button_height)
            
            # Тень кнопки
            shadow_rect = button_rect.copy()
            shadow_rect.move_ip(2, 2)
            pygame.draw.rect(self.screen, (0, 0, 0, 128), shadow_rect, border_radius=10)
            
            # Фон кнопки
            pygame.draw.rect(self.screen, color, button_rect, border_radius=10)
            pygame.draw.rect(self.screen, (255, 255, 255), button_rect, 2, border_radius=10)
            
            # Текст кнопки
            text_surface = self.fonts['medium'].render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.screen.blit(text_surface, text_rect)

    def draw_raise_dialog(self):
        """Отрисовка диалога для ввода суммы рейза"""
        # Затемнение фона
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Размеры диалога
        dialog_width = 400
        dialog_height = 250
        dialog_x = self.width // 2 - dialog_width // 2
        dialog_y = self.height // 2 - dialog_height // 2
        
        # Фон диалога
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(self.screen, (50, 50, 50), dialog_rect, border_radius=15)
        pygame.draw.rect(self.screen, self.COLORS['gold'], dialog_rect, 3, border_radius=15)
        
        # Заголовок
        title_text = self.fonts['large'].render("Raise", True, self.COLORS['gold'])
        title_rect = title_text.get_rect(center=(self.width // 2, dialog_y + 40))
        self.screen.blit(title_text, title_rect)
        
        # Текущая сумма
        amount_text = self.fonts['large'].render(f"${self.raise_amount}", True, self.COLORS['white'])
        amount_rect = amount_text.get_rect(center=(self.width // 2, dialog_y + 100))
        self.screen.blit(amount_text, amount_rect)
        
        # Подсказка
        hint_text = self.fonts['small'].render(f"Range: ${self.min_raise} - ${self.max_raise}", True, self.COLORS['gray'])
        hint_rect = hint_text.get_rect(center=(self.width // 2, dialog_y + 140))
        self.screen.blit(hint_text, hint_rect)
        
        # Кнопки +/- для изменения суммы
        button_size = 50
        minus_rect = pygame.Rect(dialog_x + 50, dialog_y + 90, button_size, button_size)
        plus_rect = pygame.Rect(dialog_x + dialog_width - 100, dialog_y + 90, button_size, button_size)
        
        pygame.draw.rect(self.screen, (100, 50, 50), minus_rect, border_radius=10)
        pygame.draw.rect(self.screen, (50, 100, 50), plus_rect, border_radius=10)
        
        minus_text = self.fonts['large'].render("-", True, self.COLORS['white'])
        plus_text = self.fonts['large'].render("+", True, self.COLORS['white'])
        self.screen.blit(minus_text, minus_text.get_rect(center=minus_rect.center))
        self.screen.blit(plus_text, plus_text.get_rect(center=plus_rect.center))
        
        # Кнопки подтверждения
        btn_width = 120
        btn_height = 40
        confirm_rect = pygame.Rect(dialog_x + 50, dialog_y + dialog_height - 60, btn_width, btn_height)
        cancel_rect = pygame.Rect(dialog_x + dialog_width - 170, dialog_y + dialog_height - 60, btn_width, btn_height)
        
        pygame.draw.rect(self.screen, (50, 150, 50), confirm_rect, border_radius=10)
        pygame.draw.rect(self.screen, (150, 50, 50), cancel_rect, border_radius=10)
        
        confirm_text = self.fonts['medium'].render("Confirm", True, self.COLORS['white'])
        cancel_text = self.fonts['medium'].render("Cancel", True, self.COLORS['white'])
        self.screen.blit(confirm_text, confirm_text.get_rect(center=confirm_rect.center))
        self.screen.blit(cancel_text, cancel_text.get_rect(center=cancel_rect.center))
        
        pygame.display.flip()
    
    def draw(self, game_state: dict):
        """Основной метод отрисовки игры"""
        # Сохраняем последнее состояние игры для перерисовки при ресайзе
        self._last_game_state = game_state
        
        # Очищаем экран
        self.screen.fill((40, 40, 40))  # Темно-серый фон
        
        # Рисуем стол
        self.draw_table()
        
        # Рисуем информацию о текущем действии в нижней части экрана
        if hasattr(self, 'current_action') and self.current_action:
            # Создаем градиентный фон для текста
            gradient_height = 60
            gradient_surface = pygame.Surface((self.width, gradient_height), pygame.SRCALPHA)
            for i in range(gradient_height):
                alpha = int(255 * (i / gradient_height))
                pygame.draw.line(gradient_surface, (0, 0, 0, alpha), 
                               (0, i), (self.width, i))
            
            # Размещаем градиент над кнопками
            gradient_y = self.height - self.button_height - gradient_height - 60
            self.screen.blit(gradient_surface, (0, gradient_y))
            
            # Рисуем текст
            action_text = self.fonts['large'].render(self.current_action, True, self.COLORS['gold'])
            text_rect = action_text.get_rect(center=(self.width/2, gradient_y + gradient_height/2))
            self.screen.blit(action_text, text_rect)
        
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
        
        # Отрисовка кнопок для текущего игрока (показываем кнопки, если ход человека)
        human_index = game_state.get('human_index', 4)
        if game_state.get('current_player') == human_index:
            # available_actions may be present in game_state
            self.draw_buttons(game_state.get('available_actions', []))
        
        # Обновляем экран
        pygame.display.flip()
        
        # Если показываем диалог рейза, рисуем его поверх всего
        if self.show_raise_dialog:
            self.draw_raise_dialog()

    def handle_resize(self, event):
        """Обработка изменения размера окна"""
        # Устанавливаем минимальные размеры окна
        self.width = max(event.w, self.min_width)
        self.height = max(event.h, self.min_height)
        
        # Обновляем размер окна с учетом минимальных значений
        self.screen = pygame.display.set_mode(
            (self.width, self.height),
            pygame.RESIZABLE
        )
        
        # Обновляем размеры элементов и шрифты
        self.update_dimensions()
        
        # Принудительно перерисовываем экран
        if hasattr(self, '_last_game_state'):
            self.draw(self._last_game_state)

    def handle_input(self) -> Optional[str]:
        """Обработка пользовательского ввода"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'QUIT'
            elif event.type == pygame.VIDEORESIZE:
                self.handle_resize(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Если показан диалог рейза, обрабатываем клики по нему
                if self.show_raise_dialog:
                    return self.check_raise_dialog_click(mouse_pos)
                else:
                    # Проверяем клики по кнопкам
                    return self.check_button_click(mouse_pos)
            elif event.type == pygame.KEYDOWN and self.show_raise_dialog:
                # Поддержка клавиатуры для диалога рейза
                if event.key == pygame.K_UP or event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    self.raise_amount = min(self.raise_amount + 10, self.max_raise)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_MINUS:
                    self.raise_amount = max(self.raise_amount - 10, self.min_raise)
                elif event.key == pygame.K_RETURN:
                    return 'RAISE_CONFIRM'
                elif event.key == pygame.K_ESCAPE:
                    return 'RAISE_CANCEL'
        return None

    def check_raise_dialog_click(self, pos: Tuple[int, int]) -> Optional[str]:
        """Проверка клика по элементам диалога рейза"""
        dialog_width = 400
        dialog_height = 250
        dialog_x = self.width // 2 - dialog_width // 2
        dialog_y = self.height // 2 - dialog_height // 2
        
        # Кнопки +/-
        button_size = 50
        minus_rect = pygame.Rect(dialog_x + 50, dialog_y + 90, button_size, button_size)
        plus_rect = pygame.Rect(dialog_x + dialog_width - 100, dialog_y + 90, button_size, button_size)
        
        if minus_rect.collidepoint(pos):
            self.raise_amount = max(self.raise_amount - 10, self.min_raise)
            return None
        elif plus_rect.collidepoint(pos):
            self.raise_amount = min(self.raise_amount + 10, self.max_raise)
            return None
        
        # Кнопки подтверждения
        btn_width = 120
        btn_height = 40
        confirm_rect = pygame.Rect(dialog_x + 50, dialog_y + dialog_height - 60, btn_width, btn_height)
        cancel_rect = pygame.Rect(dialog_x + dialog_width - 170, dialog_y + dialog_height - 60, btn_width, btn_height)
        
        if confirm_rect.collidepoint(pos):
            return 'RAISE_CONFIRM'
        elif cancel_rect.collidepoint(pos):
            return 'RAISE_CANCEL'
        
        return None
    
    def check_button_click(self, pos: Tuple[int, int]) -> Optional[str]:
        """Проверка клика по кнопкам"""
        if not hasattr(self, '_last_game_state') or 'available_actions' not in self._last_game_state:
            return None
            
        button_data = [
            ('Fold', 'FOLD', (200, 50, 50)),
            ('Check/Call', 'CHECK/CALL', (50, 150, 50)),
            ('Raise', 'RAISE', (50, 50, 200)),
            ('All-In', 'ALL-IN', (200, 150, 50))
        ]
        
        # Фильтруем только доступные действия
        active_buttons = [b for b in button_data if b[0] in self._last_game_state['available_actions']]
        
        padding = 20
        total_width = len(active_buttons) * self.button_width + (len(active_buttons) - 1) * padding
        start_x = self.width/2 - total_width/2
        y = self.height - self.button_height - 30
        
        for i, (action, _, _) in enumerate(active_buttons):
            button_rect = pygame.Rect(start_x + i * (self.button_width + padding),
                                    y, self.button_width, self.button_height)
            if button_rect.collidepoint(pos):
                return action
        return None
