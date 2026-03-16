import pygame
import sys
import threading
from enum import Enum
from game_engine import (
    GameState, P1, P2, P1_pits, P2_pits, P1_store, P2_store,
    actions, result, terminal_test, player, initial_state
)
from minmax_pruning import AlphaBetaPlayer
from evaluation import EVAL_FUNCTIONS

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
DARK_GREEN = (25, 100, 25)
BROWN = (139, 69, 19)
LIGHT_BROWN = (205, 133, 63)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
YELLOW = (255, 255, 0)

class GameMode(Enum):
    HOME = 1
    PLAYING = 2
    GAME_OVER = 3

class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hover = False

    def draw(self, surf, font):
        color = tuple(min(c + 30, 255) for c in self.color) if self.hover else self.color
        pygame.draw.rect(surf, color, self.rect)
        pygame.draw.rect(surf, WHITE, self.rect, 2)
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surf.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def update(self, pos):
        self.hover = self.rect.collidepoint(pos)

class KalahGUI:
    def __init__(self, width=1400, height=800):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Kalaha - Play Against AI")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
        self.state = initial_state()
        self.ai = AlphaBetaPlayer(P2, max_depth=8, eval_func="weighted")
        self.mode = GameMode.HOME
        self.selected_pit = None
        self.hovered_pit = None
        self.message = ""
        self.message_timer = 0
        self.ai_thinking = False
        self.ai_move = None
        
        # Board dimensions
        self.pit_radius = 40
        self.store_radius = 60
        self.pit_spacing_x = 160
        self.pit_spacing_y = 160
        
        # Calculate centered board position
        board_width = 6 * self.pit_spacing_x
        board_height = self.pit_spacing_y + 100
        self.board_offset_x = (self.width - board_width) // 2 + 30
        self.board_offset_y = (self.height - board_height) // 2 - 10
        
        self._legal_moves_cache = set()
        self._cached_state_id = None
        self.setup_buttons()
        self._precompute_positions()
        self._cache_static_surfaces()

    def _precompute_positions(self):
        self.p1_pit_positions = [
            (self.board_offset_x + self.pit_spacing_x * i,
             self.board_offset_y + self.pit_spacing_y)
            for i in range(len(P1_pits))
        ]
        self.p2_pit_positions = [
            (self.board_offset_x + self.pit_spacing_x * (5 - i),
             self.board_offset_y + 20)
            for i in range(len(P2_pits))
        ]
        self.p2_store_pos = (self.board_offset_x - 120, self.board_offset_y + 20)
        self.p1_store_pos = (self.board_offset_x + 5.5 * self.pit_spacing_x + 80,
                             self.board_offset_y + self.pit_spacing_y)
        board_left = self.board_offset_x - 80
        board_right = self.board_offset_x + 6 * self.pit_spacing_x + 80
        board_top = self.board_offset_y - 70
        board_bottom = self.board_offset_y + self.pit_spacing_y + 90
        self.board_rect = pygame.Rect(board_left, board_top,
                                      board_right - board_left, board_bottom - board_top)

    def _cache_static_surfaces(self):
        self.surf_ai_store_label = self.font_tiny.render("AI Store", True, WHITE)
        self.surf_p1_store_label = self.font_tiny.render("Your Store", True, WHITE)
        self.surf_p2_label = self.font_small.render("Player 2 (AI)", True, WHITE)
        self.surf_p1_label = self.font_small.render("Player 1 (You)", True, WHITE)
        self.surf_pit_numbers = [self.font_tiny.render(str(i + 1), True, WHITE)
                                 for i in range(6)]

    def _get_legal_moves(self):
        state_id = id(self.state)
        if state_id != self._cached_state_id:
            self._legal_moves_cache = set(actions(self.state))
            self._cached_state_id = state_id
        return self._legal_moves_cache

    def setup_buttons(self):
        button_width = 250
        button_height = 50
        center_x = self.width // 2
        
        self.btn_play = Button(center_x - button_width // 2, 250, button_width, button_height, 
                              "Play vs AI", GREEN, WHITE)
        self.btn_ai_easy = Button(center_x - button_width // 2, 320, button_width, button_height,
                                 "AI Easy (Depth 4)", BLUE, WHITE)
        self.btn_ai_medium = Button(center_x - button_width // 2, 390, button_width, button_height,
                                   "AI Medium (Depth 6)", BLUE, WHITE)
        self.btn_ai_hard = Button(center_x - button_width // 2, 460, button_width, button_height,
                                 "AI Hard (Depth 8)", BLUE, WHITE)
        self.btn_quit = Button(center_x - button_width // 2, 530, button_width, button_height,
                              "Quit", RED, WHITE)
        
        self.btn_back = Button(80, 20, 150, 40, "Menu", BLUE, WHITE)
        self.btn_restart = Button(self.width - 250, 20, 150, 40, "Restart", BLUE, WHITE)
        
        self.btn_play_again = Button(center_x - button_width // 2 - 110, self.height - 100, 
                                    button_width, button_height, "Play Again", GREEN, WHITE)
        self.btn_home = Button(center_x + 110, self.height - 100, button_width, button_height,
                              "Home", BLUE, WHITE)

    def draw_home_screen(self):
        self.screen.fill(DARK_GREEN)
        title = self.font_large.render("KALAHA", True, YELLOW)
        subtitle = self.font_medium.render("Play Against AI", True, WHITE)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 80))
        self.screen.blit(subtitle, (self.width // 2 - subtitle.get_width() // 2, 140))
        
        self.btn_ai_easy.draw(self.screen, self.font_medium)
        self.btn_ai_medium.draw(self.screen, self.font_medium)
        self.btn_ai_hard.draw(self.screen, self.font_medium)
        self.btn_quit.draw(self.screen, self.font_medium)
        
        instructions = [
            "Select AI difficulty to start playing",
            "",
            "Game Rules:",
            "• Click on pits on your side (bottom) to play",
            "• Stones are distributed counter-clockwise",
            "• Landing in your store gives you an extra turn",
            "• Landing in an empty pit captures opposite pit",
            "• Game ends when one side is empty"
        ]
        y = 500
        for instruction in instructions:
            if instruction:
                text = self.font_tiny.render(instruction, True, WHITE)
                self.screen.blit(text, (100, y))
            y += 25

    def draw_pit(self, x, y, pit_idx, legal_moves, is_hovered=False):
        stones = self.state.board[pit_idx]
        color = LIGHT_BROWN

        if pit_idx == self.selected_pit:
            color = YELLOW
        elif is_hovered and pit_idx in P1_pits:
            color = (255, 200, 100)
        elif pit_idx in legal_moves:
            color = (200, 220, 100)

        ix, iy, ir = int(x), int(y), int(self.pit_radius)
        pygame.draw.circle(self.screen, color, (ix, iy), ir)
        pygame.draw.circle(self.screen, BLACK, (ix, iy), ir, 3)

        text = self.font_medium.render(str(stones), True, BLACK)
        self.screen.blit(text, (ix - text.get_width() // 2, iy - text.get_height() // 2))

    def draw_board(self):
        self.screen.fill(GREEN)

        self.btn_back.draw(self.screen, self.font_small)
        self.btn_restart.draw(self.screen, self.font_small)

        current_player = player(self.state)
        player_text = "AI Thinking..." if self.ai_thinking else (
            "Your Turn (Player 1)" if current_player == P1 else "AI Thinking... (Player 2)"
        )
        status = self.font_medium.render(player_text, True, BLUE if current_player == P1 else RED)
        self.screen.blit(status, (self.width // 2 - status.get_width() // 2, 20))

        pygame.draw.rect(self.screen, DARK_GREEN, self.board_rect, 3)

        cx = self.width // 2
        self.screen.blit(self.surf_p2_label,
                         (cx - self.surf_p2_label.get_width() // 2, self.board_offset_y - 65))
        self.screen.blit(self.surf_p1_label,
                         (cx - self.surf_p1_label.get_width() // 2,
                          self.board_offset_y + self.pit_spacing_y + 60))

        p2x, p2y = int(self.p2_store_pos[0]), int(self.p2_store_pos[1])
        sr = int(self.store_radius)
        pygame.draw.circle(self.screen, BROWN, (p2x, p2y), sr)
        pygame.draw.circle(self.screen, BLACK, (p2x, p2y), sr, 3)
        p2_score = self.font_medium.render(str(self.state.board[P2_store]), True, YELLOW)
        self.screen.blit(p2_score, (p2x - p2_score.get_width() // 2, p2y - p2_score.get_height() // 2))
        self.screen.blit(self.surf_ai_store_label,
                         (p2x - self.surf_ai_store_label.get_width() // 2, p2y - 100))

        legal_moves = self._get_legal_moves()

        for i, pit_idx in enumerate(reversed(P2_pits)):
            x, y = self.p2_pit_positions[i]
            self.draw_pit(x, y, pit_idx, legal_moves, is_hovered=(pit_idx == self.hovered_pit))
            lbl = self.surf_pit_numbers[i]
            self.screen.blit(lbl, (x - lbl.get_width() // 2, y + 70))

        for i, pit_idx in enumerate(P1_pits):
            x, y = self.p1_pit_positions[i]
            self.draw_pit(x, y, pit_idx, legal_moves, is_hovered=(pit_idx == self.hovered_pit))
            lbl = self.surf_pit_numbers[i]
            self.screen.blit(lbl, (x - lbl.get_width() // 2, y + 70))

        p1x, p1y = int(self.p1_store_pos[0]), int(self.p1_store_pos[1])
        pygame.draw.circle(self.screen, BROWN, (p1x, p1y), sr)
        pygame.draw.circle(self.screen, BLACK, (p1x, p1y), sr, 3)
        p1_score = self.font_medium.render(str(self.state.board[P1_store]), True, YELLOW)
        self.screen.blit(p1_score, (p1x - p1_score.get_width() // 2, p1y - p1_score.get_height() // 2))
        self.screen.blit(self.surf_p1_store_label,
                         (p1x - self.surf_p1_store_label.get_width() // 2, p1y + 75))

        if self.message and self.message_timer > 0:
            msg = self.font_small.render(self.message, True, YELLOW)
            self.screen.blit(msg, (self.width // 2 - msg.get_width() // 2, self.height - 60))

    def draw_game_over_screen(self):
        self.screen.fill(DARK_GREEN)
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        p1_score = self.state.board[P1_store]
        p2_score = self.state.board[P2_store]
        title = self.font_large.render("GAME OVER", True, YELLOW)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 100))
        p1_text = self.font_medium.render(f"Your Score: {p1_score}", True, BLUE)
        p2_text = self.font_medium.render(f"AI Score: {p2_score}", True, RED)
        self.screen.blit(p1_text, (self.width // 2 - p1_text.get_width() // 2, 200))
        self.screen.blit(p2_text, (self.width // 2 - p2_text.get_width() // 2, 260))
        if p1_score > p2_score:
            result_text = "YOU WIN! 🎉"
            result_color = GREEN
        elif p2_score > p1_score:
            result_text = "AI WINS"
            result_color = RED
        else:
            result_text = "DRAW"
            result_color = YELLOW
        
        result = self.font_large.render(result_text, True, result_color)
        self.screen.blit(result, (self.width // 2 - result.get_width() // 2, 350))
        
        self.btn_play_again.draw(self.screen, self.font_medium)
        self.btn_home.draw(self.screen, self.font_medium)

    def get_pit_at_position(self, pos):
        mx, my = pos
        r2 = self.pit_radius ** 2
        for i, pit_idx in enumerate(P1_pits):
            x, y = self.p1_pit_positions[i]
            if (mx - x) ** 2 + (my - y) ** 2 < r2:
                return pit_idx
        for i, pit_idx in enumerate(reversed(P2_pits)):
            x, y = self.p2_pit_positions[i]
            if (mx - x) ** 2 + (my - y) ** 2 < r2:
                return pit_idx
        return None

    def handle_pit_click(self, pos):
        if self.ai_thinking or player(self.state) != P1:
            return None
        pit = self.get_pit_at_position(pos)
        if pit is not None and pit in self._get_legal_moves():
            return pit
        return None

    def ai_move_thread(self):
        self.ai_move = self.ai.choose_action(self.state)
        self.ai_thinking = False

    def update(self):
        self.message_timer -= 1

        if self.mode != GameMode.PLAYING:
            return

        if terminal_test(self.state):
            self.mode = GameMode.GAME_OVER
            return

        if player(self.state) == P2 and not self.ai_thinking:
            self.ai_thinking = True
            threading.Thread(target=self.ai_move_thread, daemon=True).start()

        if self.ai_move is not None:
            self.state = result(self.state, self.ai_move)
            self.ai_move = None
            self.selected_pit = None
            if terminal_test(self.state):
                self.mode = GameMode.GAME_OVER

    def handle_click(self, pos):
        if self.mode == GameMode.HOME:
            if self.btn_ai_easy.is_clicked(pos):
                self.start_game(4)
            elif self.btn_ai_medium.is_clicked(pos):
                self.start_game(6)
            elif self.btn_ai_hard.is_clicked(pos):
                self.start_game(8)
            elif self.btn_quit.is_clicked(pos):
                return False
        
        elif self.mode == GameMode.PLAYING:
            if self.btn_back.is_clicked(pos):
                self.mode = GameMode.HOME
                self.state = initial_state()
            elif self.btn_restart.is_clicked(pos):
                self.state = initial_state()
                self.ai_thinking = False
                self.ai_move = None
                self.selected_pit = None
            else:
                pit = self.handle_pit_click(pos)
                if pit is not None:
                    self.state = result(self.state, pit)
                    self.selected_pit = None
                    
                    if terminal_test(self.state):
                        self.mode = GameMode.GAME_OVER
        
        elif self.mode == GameMode.GAME_OVER:
            if self.btn_play_again.is_clicked(pos):
                self.state = initial_state()
                self.ai_thinking = False
                self.ai_move = None
                self.mode = GameMode.PLAYING
            elif self.btn_home.is_clicked(pos):
                self.mode = GameMode.HOME
                self.state = initial_state()
        
        return True

    def start_game(self, depth):
        self.state = initial_state()
        self.ai = AlphaBetaPlayer(P2, max_depth=depth, eval_func="weighted")
        self.mode = GameMode.PLAYING
        self.ai_thinking = False
        self.ai_move = None
        self.selected_pit = None
        self.message = ""

    def handle_motion(self, pos):
        self.btn_back.update(pos)
        self.btn_restart.update(pos)
        if self.mode == GameMode.HOME:
            self.btn_ai_easy.update(pos)
            self.btn_ai_medium.update(pos)
            self.btn_ai_hard.update(pos)
            self.btn_quit.update(pos)
        elif self.mode == GameMode.GAME_OVER:
            self.btn_play_again.update(pos)
            self.btn_home.update(pos)
        elif self.mode == GameMode.PLAYING:
            pit = self.get_pit_at_position(pos)
            if pit is not None and pit in P1_pits and player(self.state) == P1:
                self.hovered_pit = pit
            else:
                self.hovered_pit = None

    def draw(self):
        if self.mode == GameMode.HOME:
            self.draw_home_screen()
        elif self.mode == GameMode.PLAYING:
            self.draw_board()
        elif self.mode == GameMode.GAME_OVER:
            self.draw_game_over_screen()
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.handle_click(event.pos):
                        running = False
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_motion(event.pos)
            
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    gui = KalahGUI()
    gui.run()
