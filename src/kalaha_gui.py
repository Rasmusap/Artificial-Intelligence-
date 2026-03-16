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
        
        self.setup_buttons()

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

    def draw_pit(self, x, y, pit_idx, radius=None, is_hovered=False):
        if radius is None:
            radius = self.pit_radius
        
        stones = self.state.board[pit_idx]
        color = LIGHT_BROWN

        if pit_idx == self.selected_pit:
            color = YELLOW
        # Highlight hovered pit (only for player's pits)
        elif is_hovered and pit_idx in P1_pits:
            color = (255, 200, 100)
        elif pit_idx in actions(self.state):
            color = (200, 220, 100)
        
        pygame.draw.circle(self.screen, color, (int(x), int(y)), int(radius))
        pygame.draw.circle(self.screen, BLACK, (int(x), int(y)), int(radius), 3)
        
        # Draw stones count
        text = self.font_medium.render(str(stones), True, BLACK)
        self.screen.blit(text, (int(x - text.get_width() // 2), int(y - text.get_height() // 2)))

    def draw_board(self):
        self.screen.fill(GREEN)
        
        # Header
        self.btn_back.draw(self.screen, self.font_small)
        self.btn_restart.draw(self.screen, self.font_small)
        
        current_player = player(self.state)
        player_text = "Your Turn (Player 1)" if current_player == P1 else "AI Thinking... (Player 2)"
        if self.ai_thinking:
            player_text = "AI Thinking..."
        color = BLUE if current_player == P1 else RED
        
        status = self.font_medium.render(player_text, True, color)
        self.screen.blit(status, (self.width // 2 - status.get_width() // 2, 20))
        
        # Calculate board boundaries for centered layout
        board_left = self.board_offset_x - 80
        board_right = self.board_offset_x + 6 * self.pit_spacing_x + 80
        board_top = self.board_offset_y - 70
        board_bottom = self.board_offset_y + self.pit_spacing_y + 90
        board_width = board_right - board_left
        board_height = board_bottom - board_top
        
        # Draw board background
        pygame.draw.rect(self.screen, DARK_GREEN, (board_left, board_top, board_width, board_height), 3)
        
        # Player 2 label (top - opponent)
        p2_label = self.font_small.render("Player 2 (AI)", True, WHITE)
        self.screen.blit(p2_label, (self.width // 2 - p2_label.get_width() // 2, self.board_offset_y - 65))
        
        # Player 1 label (bottom - human)
        p1_label = self.font_small.render("Player 1 (You)", True, WHITE)
        self.screen.blit(p1_label, (self.width // 2 - p1_label.get_width() // 2, self.board_offset_y + self.pit_spacing_y + 60))
        
        # Draw P2 store (left side, top)
        p2_store_x = self.board_offset_x - 120
        p2_store_y = self.board_offset_y + 20
        pygame.draw.circle(self.screen, BROWN, (int(p2_store_x), int(p2_store_y)), int(self.store_radius))
        pygame.draw.circle(self.screen, BLACK, (int(p2_store_x), int(p2_store_y)), int(self.store_radius), 3)
        p2_score = self.font_medium.render(str(self.state.board[P2_store]), True, YELLOW)
        self.screen.blit(p2_score, (int(p2_store_x - p2_score.get_width() // 2), 
                                     int(p2_store_y - p2_score.get_height() // 2)))
        store_label = self.font_tiny.render("AI Store", True, WHITE)
        self.screen.blit(store_label, (int(p2_store_x - store_label.get_width() // 2), int(p2_store_y - 100)))
        
        # Draw P2 pits (top, reversed order)
        for i, pit_idx in enumerate(reversed(P2_pits)):
            x = self.board_offset_x + self.pit_spacing_x * (5 - i)
            y = self.board_offset_y + 20
            is_hovered = pit_idx == self.hovered_pit
            self.draw_pit(x, y, pit_idx, is_hovered=is_hovered)
            label = self.font_tiny.render(str(i + 1), True, WHITE)
            self.screen.blit(label, (x - label.get_width() // 2, y + 70))
        
        # Draw P1 pits (bottom, normal order)
        for i, pit_idx in enumerate(P1_pits):
            x = self.board_offset_x + self.pit_spacing_x * i
            y = self.board_offset_y + self.pit_spacing_y
            is_hovered = pit_idx == self.hovered_pit
            self.draw_pit(x, y, pit_idx, is_hovered=is_hovered)
            label = self.font_tiny.render(str(i + 1), True, WHITE)
            self.screen.blit(label, (x - label.get_width() // 2, y + 70))
        
        # Draw P1 store (right side, bottom)
        p1_store_x = self.board_offset_x + 5.5 * self.pit_spacing_x + 80
        p1_store_y = self.board_offset_y + self.pit_spacing_y
        pygame.draw.circle(self.screen, BROWN, (int(p1_store_x), int(p1_store_y)), int(self.store_radius))
        pygame.draw.circle(self.screen, BLACK, (int(p1_store_x), int(p1_store_y)), int(self.store_radius), 3)
        p1_score = self.font_medium.render(str(self.state.board[P1_store]), True, YELLOW)
        self.screen.blit(p1_score, (int(p1_store_x - p1_score.get_width() // 2),
                                     int(p1_store_y - p1_score.get_height() // 2)))
        store_label = self.font_tiny.render("Your Store", True, WHITE)
        self.screen.blit(store_label, (int(p1_store_x - store_label.get_width() // 2), int(p1_store_y + 75)))
        
        # Draw message
        if self.message and self.message_timer > 0:
            msg = self.font_small.render(self.message, True, YELLOW)
            self.screen.blit(msg, (self.width // 2 - msg.get_width() // 2, self.height - 60))

    def draw_game_over_screen(self):
        self.screen.fill(DARK_GREEN)
        
        # Overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Final scores
        p1_score = self.state.board[P1_store]
        p2_score = self.state.board[P2_store]
        
        title = self.font_large.render("GAME OVER", True, YELLOW)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 100))
        
        # Scores
        p1_text = self.font_medium.render(f"Your Score: {p1_score}", True, BLUE)
        p2_text = self.font_medium.render(f"AI Score: {p2_score}", True, RED)
        self.screen.blit(p1_text, (self.width // 2 - p1_text.get_width() // 2, 200))
        self.screen.blit(p2_text, (self.width // 2 - p2_text.get_width() // 2, 260))
        
        # Result
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
        
        # Buttons
        self.btn_play_again.draw(self.screen, self.font_medium)
        self.btn_home.draw(self.screen, self.font_medium)

    def get_pit_at_position(self, pos):
        """Get pit index at mouse position, or None if no pit"""
        # Check P1 pits (bottom row)
        for i, pit_idx in enumerate(P1_pits):
            x = self.board_offset_x + self.pit_spacing_x * i
            y = self.board_offset_y + self.pit_spacing_y
            distance = ((pos[0] - x) ** 2 + (pos[1] - y) ** 2) ** 0.5
            if distance < self.pit_radius:
                return pit_idx
        
        # Check P2 pits (top row)
        for i, pit_idx in enumerate(reversed(P2_pits)):
            x = self.board_offset_x + self.pit_spacing_x * (5 - i)
            y = self.board_offset_y + 20
            distance = ((pos[0] - x) ** 2 + (pos[1] - y) ** 2) ** 0.5
            if distance < self.pit_radius:
                return pit_idx
        
        return None

    def handle_pit_click(self, pos):
        """Check if a pit was clicked and return the pit index if valid"""
        if self.ai_thinking or player(self.state) != P1:
            return None
        
        legal_moves = actions(self.state)
        pit = self.get_pit_at_position(pos)
        
        if pit is not None and pit in legal_moves:
            return pit
        
        return None

    def ai_move_thread(self):
        """Run AI move in background thread"""
        self.ai_move = self.ai.choose_action(self.state)
        self.ai_thinking = False

    def update(self):
        """Update game state"""
        self.message_timer -= 1
        
        if self.mode == GameMode.PLAYING and not terminal_test(self.state):
            if player(self.state) == P2 and not self.ai_thinking:
                # AI's turn
                self.ai_thinking = True
                thread = threading.Thread(target=self.ai_move_thread, daemon=True)
                thread.start()
            
            # Apply AI move if ready
            if self.ai_move is not None:
                self.state = result(self.state, self.ai_move)
                self.ai_move = None
                self.selected_pit = None
                
                if terminal_test(self.state):
                    self.mode = GameMode.GAME_OVER
        
        if self.mode == GameMode.PLAYING and terminal_test(self.state):
            self.mode = GameMode.GAME_OVER

    def handle_click(self, pos):
        """Handle mouse click events"""
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
        """Start a new game with specified AI depth"""
        self.state = initial_state()
        self.ai = AlphaBetaPlayer(P2, max_depth=depth, eval_func="weighted")
        self.mode = GameMode.PLAYING
        self.ai_thinking = False
        self.ai_move = None
        self.selected_pit = None
        self.message = ""

    def handle_motion(self, pos):
        """Handle mouse motion for button hover effects and pit highlighting"""
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
            # Update pit hover detection (only for player's pits)
            pit = self.get_pit_at_position(pos)
            # Only highlight player's pits (P1)
            if pit is not None and pit in P1_pits and player(self.state) == P1:
                self.hovered_pit = pit
            else:
                self.hovered_pit = None

    def draw(self):
        """Draw the current screen"""
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
