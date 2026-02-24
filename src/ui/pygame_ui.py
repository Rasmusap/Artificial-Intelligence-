import pygame

from src.agent.base import BaseAgent
from src.game.engine import GameEngine


class PygameController:
    def __init__(self, engine: GameEngine, ai_agent: BaseAgent) -> None:
        self.engine = engine
        self.ai_agent = ai_agent

        self.window_width = 540
        self.window_height = 660
        self.board_size = 540
        self.cell_size = self.board_size // 3
        self.ai_delay_ms = 350
        self._ai_due_at = 0

    def run(self) -> None:
        pygame.init()
        screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Tic-Tac-Toe: Human vs Agent")

        clock = pygame.time.Clock()
        font = pygame.font.SysFont("consolas", 34)
        status_font = pygame.font.SysFont("consolas", 24)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_click(event.pos)

            self._maybe_play_ai_turn()
            self._draw(screen, font, status_font)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

    def _handle_click(self, pos: tuple[int, int]) -> None:
        x, y = pos

        if self.engine.is_over():
            if y > self.board_size:
                self.engine.reset()
            return

        if self.engine.state.current_player != "X":
            return

        if y >= self.board_size:
            return

        col = x // self.cell_size
        row = y // self.cell_size
        index = row * 3 + col
        self.engine.make_move(index)

    def _maybe_play_ai_turn(self) -> None:
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

    def _draw(self, screen: pygame.Surface, font: pygame.font.Font, status_font: pygame.font.Font) -> None:
        screen.fill((245, 247, 250))

        for i in range(1, 3):
            pygame.draw.line(
                screen,
                (40, 50, 60),
                (i * self.cell_size, 0),
                (i * self.cell_size, self.board_size),
                4,
            )
            pygame.draw.line(
                screen,
                (40, 50, 60),
                (0, i * self.cell_size),
                (self.board_size, i * self.cell_size),
                4,
            )

        for idx, mark in enumerate(self.engine.state.board):
            if mark == " ":
                continue

            row = idx // 3
            col = idx % 3
            text = font.render(mark, True, (25, 35, 45))
            text_rect = text.get_rect(
                center=(
                    col * self.cell_size + self.cell_size // 2,
                    row * self.cell_size + self.cell_size // 2,
                )
            )
            screen.blit(text, text_rect)

        status_rect = pygame.Rect(0, self.board_size, self.window_width, self.window_height - self.board_size)
        pygame.draw.rect(screen, (225, 230, 236), status_rect)

        status = self._status_text()
        status_surface = status_font.render(status, True, (20, 30, 40))
        screen.blit(status_surface, (16, self.board_size + 20))

        hint = "Click board to play."
        if self.engine.is_over():
            hint = "Game over: click lower panel to restart."
        hint_surface = status_font.render(hint, True, (20, 30, 40))
        screen.blit(hint_surface, (16, self.board_size + 60))

    def _status_text(self) -> str:
        if self.engine.state.winner is not None:
            return f"Winner: {self.engine.state.winner}"
        if self.engine.state.is_draw:
            return "Draw game"
        if self.engine.state.current_player == "X":
            return "Your turn (X)"
        return "Agent thinking (O)"
