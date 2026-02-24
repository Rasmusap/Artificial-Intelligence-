from src.game.engine import GameEngine
from src.agent.random_agent import RandomAgent
from src.agent.minimax_agent import MinimaxAgent
from src.ui.pygame_ui import PygameController


def main() -> None:
    print("Select mode:")
    print("1) Human vs Random Agent")
    print("2) Human vs Minimax Agent")
    choice = input("Enter choice [1-2]: ").strip()

    agent = MinimaxAgent() if choice == "2" else RandomAgent()
    engine = GameEngine()
    controller = PygameController(engine=engine, ai_agent=agent)
    controller.run()


if __name__ == "__main__":
    main()
