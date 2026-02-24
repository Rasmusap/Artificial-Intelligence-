from src.agent.minimax_agent import MinimaxAgent
from src.game.state import GameState


def test_minimax_takes_winning_move() -> None:
    state = GameState(
        board=["O", "O", " ", "X", "X", " ", " ", " ", " "],
        current_player="O",
    )
    agent = MinimaxAgent()

    assert agent.select_move(state) == 2
