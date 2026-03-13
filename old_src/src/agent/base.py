from abc import ABC, abstractmethod
from src.game.state import GameState


class BaseAgent(ABC):
    @abstractmethod
    def select_move(self, state: GameState) -> int:
        raise NotImplementedError
