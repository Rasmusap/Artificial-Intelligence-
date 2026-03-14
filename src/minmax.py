# without pruning
from game_engine import (
    GameState, P1, P2, P1_pits, P2_pits, P1_store, P2_store,
    actions, result, terminal_test, utility, score, player,
    opposite_pit
)
from evaluation import (
    evaluate_score_difference, eval_weighted, EVAL_FUNCTIONS, eval_positional
)
import math

def minimax(self, state, depth):
    # Base case: terminal state
    if terminal_test(state):
        return utility(state, self.player_id) * 10000

    # Base case 2: depth limit reached
    if depth <= 0:
        return self.eval_fn(state, self.player_id)

    legal_moves = actions(state)
    is_maximizing = (player(state) == self.player_id)

    if is_maximizing:
        value = -math.inf
        for action in legal_moves:
            child = result(state, action)
            value = max(value, self.minimax(child, depth - 1))
        return value
    else:
        value = math.inf
        for action in legal_moves:
            child = result(state, action)
            value = min(value, self.minimax(child, depth - 1))
        return value