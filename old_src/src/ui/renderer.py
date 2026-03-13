from src.game.state import GameState


class BoardRenderer:
    @staticmethod
    def render(state: GameState) -> str:
        b = state.board
        rows = [
            f" {b[0]} | {b[1]} | {b[2]} ",
            f" {b[3]} | {b[4]} | {b[5]} ",
            f" {b[6]} | {b[7]} | {b[8]} ",
        ]
        return "\n---+---+---\n".join(rows)
