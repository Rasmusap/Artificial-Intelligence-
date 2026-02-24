import math

import pygame

from src.agent.base import BaseAgent
from src.agent.minimax_agent import MinimaxAgent
from src.agent.random_agent import RandomAgent
from src.game.engine import GameEngine
from src.game.rules import WIN_LINES


class PygameController:
    def __init__(self, engine: GameEngine, ai_agent: BaseAgent | None = None) -> None:
        self.engine = engine
        self.ai_agent = ai_agent
        self.agent_label = "None"
        self.view_state = "menu"

        self.min_window_w = 640
        self.min_window_h = 720
        self.windowed_size = (960, 900)
        self.is_minimized = False

        self.ai_delay_ms = 350
        self._ai_due_at = 0

        self.colors = {
            "bg_top": (15, 26, 48),
            "bg_bottom": (34, 95, 145),
            "panel": (235, 241, 248),
            "panel_border": (163, 177, 196),
            "grid": (231, 236, 244),
            "x": (255, 117, 56),
            "o": (45, 212, 191),
            "text_dark": (18, 30, 46),
            "text_muted": (60, 82, 107),
            "cell_hover": (255, 255, 255),
            "win": (255, 215, 87),
            "button": (23, 78, 130),
            "button_hover": (30, 95, 156),
            "button_text": (245, 250, 255),
            "board_bg": (246, 250, 255),
            "board_border": (191, 205, 222),
            "board_shadow": (6, 12, 21),
        }

        self.board_rect = pygame.Rect(0, 0, 0, 0)
        self.cell_size = 0
        self.panel_rect = pygame.Rect(0, 0, 0, 0)
        self.restart_button = pygame.Rect(0, 0, 0, 0)
        self.random_button = pygame.Rect(0, 0, 0, 0)
        self.minimax_button = pygame.Rect(0, 0, 0, 0)

    def run(self) -> None:
        pygame.init()
        screen = self._create_windowed_mode(self.windowed_size)
        pygame.display.set_caption("Tic-Tac-Toe: Human vs Agent")

        clock = pygame.time.Clock()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    w = max(self.min_window_w, event.w)
                    h = max(self.min_window_h, event.h)
                    self.windowed_size = (w, h)
                    screen = self._create_windowed_mode(self.windowed_size)
                elif event.type == pygame.WINDOWMINIMIZED:
                    # Skip expensive redraws while iconified.
                    self.is_minimized = True
                elif event.type == pygame.WINDOWRESTORED:
                    self.is_minimized = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.view_state == "menu":
                        self._handle_menu_click(event.pos)
                    else:
                        self._handle_click(event.pos)

            self._maybe_play_ai_turn()

            if self.is_minimized:
                clock.tick(20)
                continue

            current_size = screen.get_size()
            if current_size[0] > 1 and current_size[1] > 1:
                layout = self._compute_layout(current_size)
                self._draw(screen, layout)
                pygame.display.flip()

            clock.tick(60)

        pygame.quit()

    def _create_windowed_mode(self, size: tuple[int, int]) -> pygame.Surface:
        return pygame.display.set_mode(size, pygame.RESIZABLE)

    def _compute_layout(self, size: tuple[int, int]) -> dict[str, int | pygame.Rect]:
        width, height = size
        margin = max(12, int(min(width, height) * 0.02))
        title_h = max(46, int(height * 0.08))
        gap = max(10, int(min(width, height) * 0.012))

        available_h = height - title_h - margin * 3
        board_size = int(min(width - margin * 2, available_h * 0.74))
        board_size = max(300, board_size)
        board_size -= board_size % 3

        board_x = (width - board_size) // 2
        board_y = title_h + margin

        panel_y = board_y + board_size + gap
        panel_h = max(130, height - panel_y - margin)
        panel_rect = pygame.Rect(margin, panel_y, width - margin * 2, panel_h)

        cell_size = board_size // 3
        board_rect = pygame.Rect(board_x, board_y, board_size, board_size)

        button_h = max(42, int(panel_h * 0.36))
        button_w = max(150, int(panel_rect.width * 0.22))
        button_y = panel_rect.bottom - margin - button_h
        button_x = panel_rect.right - margin - button_w
        restart_button = pygame.Rect(button_x, button_y, button_w, button_h)

        text_block_x = panel_rect.x + margin
        text_block_y = panel_rect.y + margin
        text_block_w = max(120, restart_button.x - text_block_x - margin)

        self.board_rect = board_rect
        self.cell_size = cell_size
        self.panel_rect = panel_rect
        self.restart_button = restart_button

        menu_card_w = int(min(width * 0.82, 680))
        menu_card_h = int(min(height * 0.52, 420))
        menu_card = pygame.Rect((width - menu_card_w) // 2, (height - menu_card_h) // 2, menu_card_w, menu_card_h)
        menu_button_w = int(menu_card.width * 0.72)
        menu_button_h = max(56, int(menu_card.height * 0.16))
        menu_button_x = menu_card.centerx - menu_button_w // 2
        random_button_y = menu_card.y + int(menu_card.height * 0.48)
        minimax_button_y = random_button_y + menu_button_h + max(14, int(height * 0.018))
        self.random_button = pygame.Rect(menu_button_x, random_button_y, menu_button_w, menu_button_h)
        self.minimax_button = pygame.Rect(menu_button_x, minimax_button_y, menu_button_w, menu_button_h)

        return {
            "width": width,
            "height": height,
            "margin": margin,
            "title_h": title_h,
            "board_rect": board_rect,
            "panel_rect": panel_rect,
            "cell_size": cell_size,
            "text_block_x": text_block_x,
            "text_block_y": text_block_y,
            "text_block_w": text_block_w,
            "menu_card": menu_card,
        }

    def _handle_menu_click(self, pos: tuple[int, int]) -> None:
        if self.random_button.collidepoint(pos):
            self._start_game(RandomAgent(), "Random Agent")
            return
        if self.minimax_button.collidepoint(pos):
            self._start_game(MinimaxAgent(), "Minimax Agent")

    def _start_game(self, agent: BaseAgent, label: str) -> None:
        self.ai_agent = agent
        self.agent_label = label
        self.view_state = "game"
        self.engine.reset()
        self._ai_due_at = 0

    def _handle_click(self, pos: tuple[int, int]) -> None:
        if self.restart_button.collidepoint(pos):
            self.engine.reset()
            self._ai_due_at = 0
            return

        if self.engine.is_over() or self.engine.state.current_player != "X":
            return

        if not self.board_rect.collidepoint(pos):
            return

        x = pos[0] - self.board_rect.x
        y = pos[1] - self.board_rect.y
        col = x // self.cell_size
        row = y // self.cell_size
        index = row * 3 + col
        self.engine.make_move(index)

    def _maybe_play_ai_turn(self) -> None:
        if self.view_state != "game" or self.ai_agent is None:
            return
        if self.engine.is_over() or self.engine.state.current_player != "O":
            return

        now = pygame.time.get_ticks()
        if self._ai_due_at == 0:
            self._ai_due_at = now + self.ai_delay_ms
            return

        if now >= self._ai_due_at:
            move = self.ai_agent.select_move(self.engine.state.copy())
            self.engine.make_move(move)
            self._ai_due_at = 0

    def _draw(self, screen: pygame.Surface, layout: dict[str, int | pygame.Rect]) -> None:
        self._draw_gradient_background(screen, int(layout["width"]), int(layout["height"]))
        if self.view_state == "menu":
            self._draw_startup_menu(screen, layout)
            return
        self._draw_title(screen, layout)
        self._draw_board_surface(screen)
        self._draw_hover_cell(screen)
        self._draw_marks(screen)
        self._draw_win_line(screen)
        self._draw_status_panel(screen, layout)

    def _draw_startup_menu(self, screen: pygame.Surface, layout: dict[str, int | pygame.Rect]) -> None:
        width = int(layout["width"])
        height = int(layout["height"])
        menu_card = layout["menu_card"]
        assert isinstance(menu_card, pygame.Rect)

        title_font = self._fit_font("Tic-Tac-Toe Arena", int(width * 0.7), 64, 28, True)
        subtitle_font = self._fit_font("Choose the agent to play against", int(menu_card.width * 0.86), 32, 16, False)
        button_font = self._fit_font("Minimax Agent", int(self.minimax_button.width * 0.8), 32, 16, True)

        title = title_font.render("Tic-Tac-Toe Arena", True, (244, 248, 255))
        title_rect = title.get_rect(center=(width // 2, int(height * 0.18)))
        screen.blit(title, title_rect)

        shadow = menu_card.move(0, max(6, int(height * 0.01)))
        pygame.draw.rect(screen, self.colors["board_shadow"], shadow, border_radius=18)
        pygame.draw.rect(screen, self.colors["panel"], menu_card, border_radius=18)
        pygame.draw.rect(screen, self.colors["panel_border"], menu_card, 2, border_radius=18)

        subtitle = subtitle_font.render("Choose the agent to play against", True, self.colors["text_dark"])
        subtitle_rect = subtitle.get_rect(center=(menu_card.centerx, menu_card.y + int(menu_card.height * 0.28)))
        screen.blit(subtitle, subtitle_rect)

        self._draw_menu_button(screen, self.random_button, "Random Agent", button_font)
        self._draw_menu_button(screen, self.minimax_button, "Minimax Agent", button_font)

    def _draw_menu_button(self, screen: pygame.Surface, rect: pygame.Rect, label: str, font: pygame.font.Font) -> None:
        mouse_pos = pygame.mouse.get_pos()
        button_color = self.colors["button_hover"] if rect.collidepoint(mouse_pos) else self.colors["button"]
        pygame.draw.rect(screen, button_color, rect, border_radius=max(10, rect.height // 4))
        pygame.draw.rect(screen, (13, 38, 63), rect, 2, border_radius=max(10, rect.height // 4))
        text = font.render(label, True, self.colors["button_text"])
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

    def _draw_gradient_background(self, screen: pygame.Surface, width: int, height: int) -> None:
        for y in range(height):
            blend = y / max(1, height - 1)
            color = (
                int(self.colors["bg_top"][0] * (1 - blend) + self.colors["bg_bottom"][0] * blend),
                int(self.colors["bg_top"][1] * (1 - blend) + self.colors["bg_bottom"][1] * blend),
                int(self.colors["bg_top"][2] * (1 - blend) + self.colors["bg_bottom"][2] * blend),
            )
            pygame.draw.line(screen, color, (0, y), (width, y))

    def _draw_title(self, screen: pygame.Surface, layout: dict[str, int | pygame.Rect]) -> None:
        height = int(layout["height"])
        font_size = max(28, min(54, int(height * 0.045)))
        font = pygame.font.SysFont("segoeui", font_size, bold=True)
        title = "Tic-Tac-Toe Arena"
        surface = font.render(title, True, (244, 248, 255))
        shadow = font.render(title, True, (0, 0, 0))
        center_x = int(layout["width"]) // 2
        y = int(layout["margin"]) + 4
        rect = surface.get_rect(midtop=(center_x, y))
        shadow_rect = shadow.get_rect(midtop=(center_x + 2, y + 2))
        screen.blit(shadow, shadow_rect)
        screen.blit(surface, rect)

    def _draw_board_surface(self, screen: pygame.Surface) -> None:
        board_shadow = self.board_rect.move(0, max(4, self.cell_size // 16))
        radius = max(12, self.cell_size // 8)

        pygame.draw.rect(screen, self.colors["board_shadow"], board_shadow, border_radius=radius)
        pygame.draw.rect(screen, self.colors["board_bg"], self.board_rect, border_radius=radius)
        pygame.draw.rect(screen, self.colors["board_border"], self.board_rect, 3, border_radius=radius)

        inset = max(8, self.cell_size // 14)
        grid_width = max(4, self.cell_size // 18)

        for i in range(1, 3):
            x = self.board_rect.x + i * self.cell_size
            y = self.board_rect.y + i * self.cell_size
            pygame.draw.line(
                screen,
                self.colors["grid"],
                (x, self.board_rect.y + inset),
                (x, self.board_rect.bottom - inset),
                grid_width,
            )
            pygame.draw.line(
                screen,
                self.colors["grid"],
                (self.board_rect.x + inset, y),
                (self.board_rect.right - inset, y),
                grid_width,
            )

    def _draw_hover_cell(self, screen: pygame.Surface) -> None:
        if self.engine.is_over() or self.engine.state.current_player != "X":
            return

        mx, my = pygame.mouse.get_pos()
        if not self.board_rect.collidepoint((mx, my)):
            return

        col = (mx - self.board_rect.x) // self.cell_size
        row = (my - self.board_rect.y) // self.cell_size
        idx = row * 3 + col
        if self.engine.state.board[idx] != " ":
            return

        pulse = int((math.sin(pygame.time.get_ticks() * 0.01) + 1) * 24)
        alpha = 28 + pulse

        pad = max(5, self.cell_size // 30)
        hover_rect = pygame.Rect(
            self.board_rect.x + col * self.cell_size + pad,
            self.board_rect.y + row * self.cell_size + pad,
            self.cell_size - pad * 2,
            self.cell_size - pad * 2,
        )
        overlay = pygame.Surface((hover_rect.width, hover_rect.height), pygame.SRCALPHA)
        overlay.fill((*self.colors["cell_hover"], alpha))
        screen.blit(overlay, hover_rect.topleft)

    def _draw_marks(self, screen: pygame.Surface) -> None:
        for idx, mark in enumerate(self.engine.state.board):
            if mark == " ":
                continue

            cx, cy = self._cell_center(idx)
            if mark == "X":
                self._draw_x(screen, cx, cy)
            else:
                self._draw_o(screen, cx, cy)

    def _draw_x(self, screen: pygame.Surface, cx: int, cy: int) -> None:
        size = int(self.cell_size * 0.28)
        thickness = max(6, int(self.cell_size * 0.06))
        pygame.draw.line(screen, self.colors["x"], (cx - size, cy - size), (cx + size, cy + size), thickness)
        pygame.draw.line(screen, self.colors["x"], (cx + size, cy - size), (cx - size, cy + size), thickness)

    def _draw_o(self, screen: pygame.Surface, cx: int, cy: int) -> None:
        radius = int(self.cell_size * 0.29)
        thickness = max(6, int(self.cell_size * 0.06))
        pygame.draw.circle(screen, self.colors["o"], (cx, cy), radius, thickness)

    def _draw_win_line(self, screen: pygame.Surface) -> None:
        if self.engine.state.winner is None:
            return

        board = self.engine.state.board
        winning_line = None
        for a, b, c in WIN_LINES:
            if board[a] != " " and board[a] == board[b] == board[c]:
                winning_line = (a, c)
                break

        if winning_line is None:
            return

        sx, sy = self._cell_center(winning_line[0])
        ex, ey = self._cell_center(winning_line[1])

        outer = max(8, int(self.cell_size * 0.08))
        inner = max(4, int(self.cell_size * 0.045))
        pygame.draw.line(screen, (0, 0, 0), (sx, sy), (ex, ey), outer)
        pygame.draw.line(screen, self.colors["win"], (sx, sy), (ex, ey), inner)

    def _draw_status_panel(self, screen: pygame.Surface, layout: dict[str, int | pygame.Rect]) -> None:
        radius = max(10, self.cell_size // 10)
        pygame.draw.rect(screen, self.colors["panel"], self.panel_rect, border_radius=radius)
        pygame.draw.rect(screen, self.colors["panel_border"], self.panel_rect, 2, border_radius=radius)

        left_x = int(layout["text_block_x"])
        top_y = int(layout["text_block_y"])
        max_w = int(layout["text_block_w"])

        status_text = self._status_text()
        hint_text = self._hint_text()

        status_font = self._fit_font(status_text, max_w, 34, 18, True)
        hint_font = self._fit_font(hint_text, max_w, 24, 14, False)
        button_font = self._fit_font("New Match", self.restart_button.width - 20, 26, 14, True)

        status_surface = status_font.render(status_text, True, self.colors["text_dark"])
        hint_surface = hint_font.render(hint_text, True, self.colors["text_muted"])

        screen.blit(status_surface, (left_x, top_y))
        screen.blit(hint_surface, (left_x, top_y + status_surface.get_height() + max(6, self.cell_size // 20)))

        mouse_pos = pygame.mouse.get_pos()
        button_color = self.colors["button_hover"] if self.restart_button.collidepoint(mouse_pos) else self.colors["button"]
        pygame.draw.rect(screen, button_color, self.restart_button, border_radius=max(8, self.cell_size // 12))
        pygame.draw.rect(screen, (13, 38, 63), self.restart_button, 2, border_radius=max(8, self.cell_size // 12))

        text = button_font.render("New Match", True, self.colors["button_text"])
        text_rect = text.get_rect(center=self.restart_button.center)
        screen.blit(text, text_rect)

    def _fit_font(self, text: str, max_width: int, max_size: int, min_size: int, bold: bool) -> pygame.font.Font:
        for size in range(max_size, min_size - 1, -1):
            font = pygame.font.SysFont("segoeui", size, bold=bold)
            if font.size(text)[0] <= max_width:
                return font
        return pygame.font.SysFont("segoeui", min_size, bold=bold)

    def _cell_center(self, index: int) -> tuple[int, int]:
        row = index // 3
        col = index % 3
        cx = self.board_rect.x + col * self.cell_size + self.cell_size // 2
        cy = self.board_rect.y + row * self.cell_size + self.cell_size // 2
        return cx, cy

    def _status_text(self) -> str:
        if self.agent_label != "None" and self.engine.state.winner is None and not self.engine.state.is_draw:
            if self.engine.state.current_player == "X":
                return f"Your turn (X) vs {self.agent_label}"
            return f"Agent is thinking (O) - {self.agent_label}"
        if self.engine.state.winner == "X":
            return "You won this round"
        if self.engine.state.winner == "O":
            return "Agent wins this round"
        if self.engine.state.is_draw:
            return "Draw game"
        return "Your turn (X)"

    def _hint_text(self) -> str:
        if self.engine.is_over():
            return "Press New Match to play again."
        return "Click an empty tile to place your move."
