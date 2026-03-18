from game_engine import (
    GameState, P1, P2, P1_pits, P2_pits, P1_store, P2_store,
    actions, result, terminal_test, utility, score, player,
    opposite_pit
)

from evaluation import (
    evaluate_score_difference, eval_weighted, EVAL_FUNCTIONS, eval_positional
)

import math


# orders moves so the search tries the most promising ones first
def order_moves(state, legal_moves):
    current_player = state.current_player
    board = state.board
    own_store = P1_store if current_player == P1 else P2_store
    own_pits = P1_pits if current_player == P1 else P2_pits

    extra_turn_moves = []
    capture_moves = []
    other_moves = []

    for move in legal_moves:
        stones = board[move]
        last_pos = (move + stones) % 14

        if last_pos == own_store:
            extra_turn_moves.append(move)
        elif last_pos in own_pits and board[last_pos] == 0 and board[opposite_pit(last_pos)] > 0:
            capture_moves.append(move)
        else:
            other_moves.append(move)

    return extra_turn_moves + capture_moves + other_moves


class AlphaBetaPlayer:
    def __init__(self, player_id, max_depth=8, eval_func="weighted"):
        self.player_id = player_id
        self.max_depth = max_depth
        self.eval_fn = EVAL_FUNCTIONS[eval_func]
        self.eval_func_name = eval_func
        self.nodes_explored = 0

    def choose_action(self, state):
        self.nodes_explored = 0

        best_action = None
        best_value = -math.inf

        legal_moves = actions(state)
        legal_moves = order_moves(state, legal_moves)

        alpha = -math.inf
        beta = math.inf

        for action in legal_moves:
            child = result(state, action)
            value = self._min_max(child, self.max_depth - 1, alpha, beta)

            if value > best_value:
                best_value = value
                best_action = action

            alpha = max(alpha, value)

        return best_action

    def _min_max(self, state, depth, alpha, beta):
        self.nodes_explored += 1

        if terminal_test(state):
            u = utility(state, self.player_id)
            return u * 10000

        if depth <= 0:
            return self.eval_fn(state, self.player_id)

        legal_moves = actions(state)
        legal_moves = order_moves(state, legal_moves)
        is_maximizing = (player(state) == self.player_id)

        if is_maximizing:
            value = -math.inf
            for action in legal_moves:
                child = result(state, action)
                value = max(value, self._min_max(child, depth - 1, alpha, beta))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = math.inf
            for action in legal_moves:
                child = result(state, action)
                value = min(value, self._min_max(child, depth - 1, alpha, beta))
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value