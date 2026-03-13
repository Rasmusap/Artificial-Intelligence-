from src.game.engine import GameEngine
from src.ui.pygame_ui import PygameController


def main() -> None:
    engine = GameEngine()
    controller = PygameController(engine=engine)
    controller.run()


if __name__ == "__main__":
    main()
