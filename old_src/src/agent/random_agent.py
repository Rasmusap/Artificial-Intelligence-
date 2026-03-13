import random
from src.agent.base import BaseAgent
from src.game.state import GameState


class RandomAgent(BaseAgent):
    def select_move(self, state: GameState) -> int:
        available = [idx for idx, cell in enumerate(state.board) if cell == " "]
        return random.choice(available)
