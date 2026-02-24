from dataclasses import dataclass, field
from typing import List, Optional


Board = List[str]


@dataclass
class GameState:
    board: Board = field(default_factory=lambda: [" "] * 9)
    current_player: str = "X"
    winner: Optional[str] = None
    is_draw: bool = False

    def copy(self) -> "GameState":
        return GameState(
            board=self.board.copy(),
            current_player=self.current_player,
            winner=self.winner,
            is_draw=self.is_draw,
        )
