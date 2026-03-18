import argparse
import time
import sys
import random
from typing import Tuple

from game_engine import (
    GameState, initial_state, player, actions, result,
    terminal_test, score, P1, P2, P1_store, P2_store
)
from minmax_pruning import AlphaBetaPlayer


class RandomPlayer:
    def __init__(self, player_id):
        self.player_id = player_id

    def choose_action(self, state):
        return random.choice(actions(state))


class GreedyPlayer:
    def __init__(self, player_id):
        self.player_id = player_id

    def choose_action(self, state):
        best_action = None
        best_score = -1
        for action in actions(state):
            s = result(state, action)
            sc = score(s, self.player_id)
            if sc > best_score:
                best_score = sc
                best_action = action
        return best_action


def play_game(ai1, ai2) -> Tuple[int, int, int]:
    state = initial_state()
    moves = 0
    while not terminal_test(state):
        cp = player(state)
        if cp == P1:
            action = ai1.choose_action(state)
        else:
            action = ai2.choose_action(state)
        state = result(state, action)
        moves += 1
    return state.board[P1_store], state.board[P2_store], moves


def run_matchup(ai1_factory, ai2_factory, num_games: int, label: str = "") -> dict:
    print(f"\n  {label}")
    print(f"  {'-' * len(label)}")

    ai1_wins = 0
    ai2_wins = 0
    draws = 0
    total_moves = 0
    results_list = []
    start = time.time()

    for i in range(num_games):
        ai1 = ai1_factory(P1)
        ai2 = ai2_factory(P2)
        s1, s2, moves = play_game(ai1, ai2)
        total_moves += moves

        if s1 > s2:
            ai1_wins += 1
        elif s2 > s1:
            ai2_wins += 1
        else:
            draws += 1
        results_list.append((s1, s2))

        # swap sides to reduce first-player bias
        ai1 = ai1_factory(P2)
        ai2 = ai2_factory(P1)
        s1, s2, moves = play_game(ai2, ai1)
        total_moves += moves

        if s2 > s1:
            ai1_wins += 1
        elif s1 > s2:
            ai2_wins += 1
        else:
            draws += 1
        results_list.append((s2, s1))

        sys.stdout.write(f"\r  Games played: {(i+1)*2}/{num_games*2}")
        sys.stdout.flush()

    elapsed = time.time() - start
    total_games = num_games * 2
    avg_s1 = sum(r[0] for r in results_list) / len(results_list)
    avg_s2 = sum(r[1] for r in results_list) / len(results_list)

    stats = {
        "total_games": total_games,
        "ai1_wins": ai1_wins,
        "ai2_wins": ai2_wins,
        "draws": draws,
        "ai1_win_rate": ai1_wins / total_games * 100,
        "ai2_win_rate": ai2_wins / total_games * 100,
        "draw_rate": draws / total_games * 100,
        "avg_score_ai1": avg_s1,
        "avg_score_ai2": avg_s2,
        "avg_moves": total_moves / total_games,
        "total_time": elapsed,
    }

    print(f"\n  AI1 wins: {ai1_wins}/{total_games} ({stats['ai1_win_rate']:.1f}%)")
    print(f"  AI2 wins: {ai2_wins}/{total_games} ({stats['ai2_win_rate']:.1f}%)")
    print(f"  Draws:    {draws}/{total_games} ({stats['draw_rate']:.1f}%)")
    print(f"  Avg score: AI1={avg_s1:.1f}  AI2={avg_s2:.1f}")
    print(f"  Avg moves/game: {stats['avg_moves']:.1f}")
    print(f"  Time: {elapsed:.1f}s")

    return stats


def benchmark_eval_functions(num_games: int = 25):
    print("\n" + "=" * 55)
    print("  Evaluation Function Comparison (depth 6)")
    print("=" * 55)

    depth = 6
    evals = ["simple", "weighted", "positional"]

    for i, ev1 in enumerate(evals):
        for ev2 in evals[i+1:]:
            f1 = lambda pid, e=ev1: AlphaBetaPlayer(pid, max_depth=depth, eval_func=e)
            f2 = lambda pid, e=ev2: AlphaBetaPlayer(pid, max_depth=depth, eval_func=e)
            run_matchup(f1, f2, num_games, f"{ev1} vs {ev2}")


def benchmark_search_depths(num_games: int = 25):
    print("\n" + "=" * 55)
    print("  Search Depth Comparison (weighted eval)")
    print("=" * 55)

    depths = [2, 4, 6, 8]

    for i, d1 in enumerate(depths):
        for d2 in depths[i+1:]:
            f1 = lambda pid, d=d1: AlphaBetaPlayer(pid, max_depth=d, eval_func="weighted")
            f2 = lambda pid, d=d2: AlphaBetaPlayer(pid, max_depth=d, eval_func="weighted")
            run_matchup(f1, f2, num_games, f"Depth {d1} vs Depth {d2}")


def benchmark_against_baselines(num_games: int = 25):
    print("\n" + "=" * 55)
    print("  AI vs Baselines")
    print("=" * 55)

    ai = lambda pid: AlphaBetaPlayer(pid, max_depth=6, eval_func="weighted")
    rnd = lambda pid: RandomPlayer(pid)
    greedy = lambda pid: GreedyPlayer(pid)

    run_matchup(ai, rnd, num_games, "AlphaBeta(d=6, weighted) vs Random")
    run_matchup(ai, greedy, num_games, "AlphaBeta(d=6, weighted) vs Greedy")
    run_matchup(greedy, rnd, num_games, "Greedy vs Random")


def main():
    parser = argparse.ArgumentParser(description="Kalaha benchmark")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--eval-compare", action="store_true")
    parser.add_argument("--depth-compare", action="store_true")
    parser.add_argument("--baselines", action="store_true")
    parser.add_argument("--num-games", type=int, default=25)

    args = parser.parse_args()
    num_games = 10 if args.quick else args.num_games

    run_specific = args.eval_compare or args.depth_compare or args.baselines

    print("\n" + "=" * 55)
    print("         KALAHA BENCHMARK")
    print("=" * 55)

    if not run_specific or args.baselines:
        benchmark_against_baselines(num_games)

    if not run_specific or args.eval_compare:
        benchmark_eval_functions(num_games)

    if not run_specific or args.depth_compare:
        benchmark_search_depths(num_games)

    print("\n" + "=" * 55)
    print("  Done.")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()
