from src.game.engine import GameEngine


def test_valid_move_updates_board() -> None:
    engine = GameEngine()
    ok = engine.make_move(0)

    assert ok
    assert engine.state.board[0] == "X"
    assert engine.state.current_player == "O"
