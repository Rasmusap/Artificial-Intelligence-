from src.agent.base import BaseAgent
from src.game.rules import calculate_winner, is_draw
from src.game.state import GameState


class MinimaxAgent(BaseAgent):
    def select_move(self, state: GameState) -> int:
        best_score = float("-inf")
        best_move = -1

        for move in self._available_moves(state.board):
            board = state.board.copy()
            board[move] = "O"
            score = self._minimax(board, is_maximizing=False)
            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def _minimax(self, board: list[str], is_maximizing: bool) -> int:
        winner = calculate_winner(board)
        if winner == "O":
            return 1
        if winner == "X":
            return -1
        if is_draw(board):
            return 0

        if is_maximizing:
            best = float("-inf")
            for move in self._available_moves(board):
                next_board = board.copy()
                next_board[move] = "O"
                best = max(best, self._minimax(next_board, False))
            return int(best)

        best = float("inf")
        for move in self._available_moves(board):
            next_board = board.copy()
            next_board[move] = "X"
            best = min(best, self._minimax(next_board, True))
        return int(best)

    @staticmethod
    def _available_moves(board: list[str]) -> list[int]:
        return [idx for idx, cell in enumerate(board) if cell == " "]
