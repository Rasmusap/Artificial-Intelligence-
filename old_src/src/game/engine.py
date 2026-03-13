from src.game.state import GameState
from src.game.rules import calculate_winner, is_draw


class GameEngine:
    def __init__(self) -> None:
        self.state = GameState()

    def available_moves(self) -> list[int]:
        return [idx for idx, cell in enumerate(self.state.board) if cell == " "]

    def make_move(self, index: int) -> bool:
        if index not in range(9) or self.state.board[index] != " ":
            return False

        self.state.board[index] = self.state.current_player
        self.state.winner = calculate_winner(self.state.board)
        self.state.is_draw = is_draw(self.state.board)

        if not self.state.winner and not self.state.is_draw:
            self.state.current_player = "O" if self.state.current_player == "X" else "X"

        return True

    def is_over(self) -> bool:
        return self.state.winner is not None or self.state.is_draw

    def reset(self) -> None:
        self.state = GameState()
