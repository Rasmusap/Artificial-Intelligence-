from game_engine import (
    GameState, P1, P2, P1_pits, P2_pits, P1_store, P2_store,
    actions, result, terminal_test, utility, score, player,
    opposite_pit
)

# three evaluation functions, compared in benchmarking


#1: comparing score difference
def evaluate_score_difference(state, max_player):
    min_player = 1 - max_player
    return score(state, max_player) - score(state, min_player)


#2: weighted combination of store diff, side stones, capture potential, extra turn potential
def eval_weighted(state, max_player):
    min_player = 1 - max_player
    board = state.board

    if max_player == P1:
        my_pits, opp_pits = P1_pits, P2_pits
        my_store, opp_store = P1_store, P2_store
    else:
        my_pits, opp_pits = P2_pits, P1_pits
        my_store, opp_store = P2_store, P1_store

    score_diff= evaluate_score_difference(state, max_player)

    my_side = sum(board[i] for i in my_pits)
    opp_side = sum(board[i] for i in opp_pits)
    stone_diff = my_side - opp_side

    # empty pits where the opposite side has stones = capture opportunity
    capture_potential = 0
    for pit in my_pits:
        if board[pit] == 0:
            opp = opposite_pit(pit)
            capture_potential += board[opp]

    # count pits that would land exactly in the store
    extra_turn_potential = 0
    for pit in my_pits:
        if board[pit] > 0:
            distance_to_store = (my_store - pit) % 14
            if board[pit] == distance_to_store:
                extra_turn_potential += 1

    w1 = 5.0
    w2 = 2.0
    w3 = 2.0
    w4 = 3.0

    return (w1 * score_diff + w2 * stone_diff + w3 * capture_potential + w4 * extra_turn_potential)


#3: positional - weights stones higher the closer they are to the store
def eval_positional(state, max_player):
    min_player = 1 - max_player
    board = state.board

    if max_player == P1:
        my_pits, opp_pits = P1_pits, P2_pits
        my_store, opp_store = P1_store, P2_store
    else:
        my_pits, opp_pits = P2_pits, P1_pits
        my_store, opp_store = P2_store, P1_store

    score_diff= evaluate_score_difference(state, max_player)

    # late game: most stones are in stores, just use score diff
    total_stones = sum(board)
    stones_in_stores = board[P1_store] + board[P2_store]
    if stones_in_stores > total_stones * 0.7:
        return score_diff * 10

    # stones closer to the store get a higher weight. not perfect but works reasonably well, explained in report
    positional_score = 0
    for idx, pit in enumerate(my_pits):
        weight = 1.0 + idx * 0.3
        positional_score += board[pit] * weight

    opp_positional = 0
    for idx, pit in enumerate(opp_pits):
        weight = 1.0 + idx * 0.3
        opp_positional += board[pit] * weight

    positional_diff = positional_score - opp_positional

    capture_potential = 0
    for pit in my_pits:
        if board[pit] == 0:
            opp = opposite_pit(pit)
            capture_potential += board[opp]

    return (5.0 * score_diff + 1.5 * positional_diff + 2.0 * capture_potential)


EVAL_FUNCTIONS = {
    "simple": evaluate_score_difference,
    "weighted": eval_weighted,
    "positional": eval_positional,
}
