from game_engine import (
    GameState, P1, P2, P1_pits, P2_pits, P1_store, P2_store,
    actions, result, terminal_test, utility, score, player,
    opposite_pit
)
# There are different ways to evaluate who is in the better position (who is winning).
# We implement three evaluation functions and compare them through benchmarking:
#
# 1.
#    Just the difference in store counts. Direct and fast, 
#    but blind to board opportunities.
#
# 2.
#    Combines four factors: store difference, 
#    side stone difference, capture potential, and extra turn potential.
#    Each factor is multiplied by a weight reflecting its importance.
#    This is our strongest evaluation function.
#
# 3.
#    Values stones more if they are closer to the player's store, 
#    since closer stones give better tactical control (easier extra turns, 
#    faster scoring). Also detects endgame positions where only 
#    store counts matter.


#1: comparing score difference
def evaluate_score_difference(state, max_player):
    min_player = 1 - max_player
    return score(state, max_player) - score(state, min_player)


#2: 
def eval_weighted(state, max_player):
    min_player = 1 - max_player
    board = state.board

    # determine which pits and store belong to the max player and which belong to the min player
    if max_player == P1:
        my_pits, opp_pits = P1_pits, P2_pits
        my_store, opp_store = P1_store, P2_store
    else:
        my_pits, opp_pits = P2_pits, P1_pits
        my_store, opp_store = P2_store, P1_store

    # calculate the score difference
    score_diff= evaluate_score_difference(state, max_player)
    
    # calculate the number of stones in the player's pits and the opponent's pits (not including the stores)
    # evaluting how many stones there are left in the pits tells us how many stones they can potentially capture
    my_side = sum(board[i] for i in my_pits)
    opp_side = sum(board[i] for i in opp_pits)
    stone_diff = my_side - opp_side
    
    # calculate the potential captures for the player (if they land in an empty pit on their side, they can capture the opposite pit)
    capture_potential = 0
    for pit in my_pits:
        if board[pit] == 0:
            opp = opposite_pit(pit)
            capture_potential += board[opp]
    
    
    # Extra Turn Potential
    extra_turn_potential = 0
    for pit in my_pits:
        if board[pit] > 0:
            distance_to_store = (my_store - pit) % 14
            if board[pit] == distance_to_store:
                extra_turn_potential += 1
    
    # how much weight we want to put on each of these factors in our evaluation function.
    w1 = 5.0
    w2 = 2.0
    w3 = 2.0
    w4 = 3.0

    return (w1 * score_diff + w2 * stone_diff + w3 * capture_potential + w4 * extra_turn_potential)


def eval_positional(state, max_player):
    min_player = 1 - max_player
    board = state.board

    # determine which pits and store belong to the max player and which belong to the min player
    if max_player == P1:
        my_pits, opp_pits = P1_pits, P2_pits
        my_store, opp_store = P1_store, P2_store
    else:
        my_pits, opp_pits = P2_pits, P1_pits
        my_store, opp_store = P2_store, P1_store

    # calculate the score difference
    score_diff= evaluate_score_difference(state, max_player)
    
    # if the game is in the late stages (most stones are in the stores), then the score difference becomes more important, so we can give it more weight in our evaluation function.
    total_stones = sum(board)
    stones_in_stores = board[P1_store] + board[P2_store]
    if stones_in_stores > total_stones * 0.7:
        return score_diff * 10 # give more weight to the score difference in the late game
    
    # if stones are close to the store, they are more likely to be captured, so we can give them more weight in our evaluation function. not always the case, but in general. it does have some limitation of positional heuristics. explained in the report.
    positional_score = 0
    for idx, pit in enumerate(my_pits):
        weight = 1.0 + idx * 0.3
        positional_score += board[pit] * weight
        
    opp_positional = 0
    for idx, pit in enumerate(opp_pits):
        weight = 1.0 + idx * 0.3
        opp_positional += board[pit] * weight
    
    positional_diff = positional_score - opp_positional
    
    # calculate the potential captures for the player (if they land in an empty pit on their side, they can capture the opposite pit)
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











