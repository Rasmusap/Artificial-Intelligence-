from game_engine import (
    GameState, P1, P2, P1_pits, P2_pits, P1_store, P2_store,
    actions, result, terminal_test, player, initial_state
)
from minmax_pruning import AlphaBetaPlayer
from evaluation import EVAL_FUNCTIONS

def display(state):
    b = state.board
    print("=" * 40)
    print("        Player 2 (top)")
    print()
    p2_str = "   ".join(f"{b[i]:2d}" for i in reversed(P2_pits))
    print(f"     [{p2_str}]")
    print(f"[{b[P2_store]:2d}]" + " " * 28 + f"[{b[P1_store]:2d}]")
    p1_str = "   ".join(f"{b[i]:2d}" for i in P1_pits)
    print(f"     [{p1_str}]")
    print()
    print("        Player 1 (bottom)")
    print("=" * 40)
    turn = "Player 1" if state.current_player == P1 else "Player 2"
    print(f"  Current turn: {turn}")


def get_human_action(state):
    legal = actions(state)
    cp = player(state)

    if cp == P1:
        pit_labels = {i: i + 1 for i in P1_pits}
    else:
        pit_labels = {i: i - 6 for i in P2_pits}

    legal_labels = [pit_labels[m] for m in legal]
    label_to_pit = {pit_labels[m]: m for m in legal}

    while True:
        try:
            choice = int(input(f"  Your move (choose pit {legal_labels}): "))
            if choice in label_to_pit:
                return label_to_pit[choice]
            else:
                print(f"  Invalid choice. Legal moves: {legal_labels}")
        except ValueError:
            print("  Please enter a number.")


def play_game(mode="human_vs_ai", ai_depth=8, ai_eval="weighted"):
    state = initial_state()
    move_count = 0

    if mode == "human_vs_ai":
        ai = AlphaBetaPlayer(P2, max_depth=ai_depth, eval_func=ai_eval)
        print(f"\n  You are Player 1 (bottom). AI is Player 2 (top).")
        print(f"  AI depth: {ai_depth}, eval: {ai_eval}\n")
    elif mode == "ai_vs_ai":
        ai1 = AlphaBetaPlayer(P1, max_depth=ai_depth, eval_func=ai_eval)
        ai2 = AlphaBetaPlayer(P2, max_depth=ai_depth, eval_func=ai_eval)
        print(f"\n  AI vs AI — depth: {ai_depth}, eval: {ai_eval}\n")

    while not terminal_test(state):
        display(state)
        print()

        cp = player(state)

        if mode == "human_vs_human":
            action = get_human_action(state)
        elif mode == "human_vs_ai":
            if cp == P1:
                action = get_human_action(state)
            else:
                print("  AI is thinking...")
                action = ai.choose_action(state)
                pit_label = action - 6
                print(f"  AI plays pit {pit_label}")
        elif mode == "ai_vs_ai":
            if cp == P1:
                action = ai1.choose_action(state)
                print(f"  Player 1 (AI) plays pit {action + 1}")
            else:
                action = ai2.choose_action(state)
                print(f"  Player 2 (AI) plays pit {action - 6}")

        state = result(state, action)
        move_count += 1

    # Game over
    display(state)
    p1 = state.board[P1_store]
    p2 = state.board[P2_store]
    print(f"\n  Final Score: Player 1 = {p1}, Player 2 = {p2}")
    if p1 > p2:
        print("  >>> Player 1 WINS! <<<")
    elif p2 > p1:
        print("  >>> Player 2 WINS! <<<")
    else:
        print("  >>> DRAW! <<<")
    print(f"  Total moves: {move_count}")


if __name__ == "__main__":
    print("\n" + "=" * 40)
    print("       K A L A H A")
    print("     with AI opponent")
    print("=" * 40)

    play_game(mode="human_vs_ai", ai_depth=8, ai_eval="weighted")