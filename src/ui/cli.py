from src.agent.base import BaseAgent
from src.game.engine import GameEngine
from src.ui.renderer import BoardRenderer


class CliController:
    def __init__(self, engine: GameEngine, ai_agent: BaseAgent) -> None:
        self.engine = engine
        self.ai_agent = ai_agent

    def run(self) -> None:
        print("You are X. Choose positions 1-9.")

        while not self.engine.is_over():
            state = self.engine.state
            print("\n" + BoardRenderer.render(state) + "\n")

            if state.current_player == "X":
                self._human_turn()
            else:
                move = self.ai_agent.select_move(state)
                self.engine.make_move(move)
                print(f"Agent played: {move + 1}")

        print("\nFinal board:\n")
        print(BoardRenderer.render(self.engine.state))

        if self.engine.state.winner:
            print(f"Winner: {self.engine.state.winner}")
        else:
            print("Game ended in a draw.")

    def _human_turn(self) -> None:
        while True:
            raw = input("Your move [1-9]: ").strip()
            if not raw.isdigit():
                print("Enter a number from 1 to 9.")
                continue

            move = int(raw) - 1
            if self.engine.make_move(move):
                return

            print("Invalid move. Try again.")
