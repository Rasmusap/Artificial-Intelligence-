from dataclasses import dataclass, field

P1 = 0
P2 = 1

P1_pits  = [0, 1, 2, 3, 4, 5]
P1_store = 6
P2_pits  = [7, 8, 9, 10, 11, 12]
P2_store = 13
Board_size = 14

# to find the oppoite pit.
def opposite_pit(i: int) -> int:
    return 12 - i

@dataclass
class GameState:
    board: list
    current_player: int

    def copy(self):
        return GameState(board=self.board[:], current_player=self.current_player)

def initial_state():
    return GameState(
        board = [4,4,4,4,4,4, 0, 4,4,4,4,4,4, 0],
        current_player = 0
    )

def player(state):
    return state.current_player


def actions(state):
    if state.current_player == P1:
        pits = P1_pits
    else:
        pits = P2_pits

    return [i for i in pits if state.board[i] > 0]

def result(state, action):
    new_state= state.copy()
    board= new_state.board
    current_player = new_state.current_player

    opponent_store = P2_store if current_player == P1 else P1_store
    own_store = P1_store if current_player == P1 else P2_store
    own_pits = P1_pits if current_player == P1 else P2_pits

    stones=board[action]
    board[action] = 0

    index=action
    while stones >0:
        index = (index + 1) % Board_size
        if index == opponent_store:
            continue
        board[index] += 1
        stones -= 1

    # if the last stone lands in own store, player gets another turn
    extra_turn = (index == own_store)

    if not extra_turn and index in own_pits and board[index] == 1:
        opp = opposite_pit(index)
        if board[opp] > 0:
            board[own_store] += board[opp] + 1
            board[index] = 0
            board[opp] = 0

    p1_empty = all(board[i] == 0 for i in P1_pits)
    p2_empty = all(board[i] == 0 for i in P2_pits)

    if p1_empty or p2_empty:
        for i in P1_pits:
            board[P1_store] += board[i]
            board[i] = 0
        for i in P2_pits:
            board[P2_store] += board[i]
            board[i] = 0
    else:
        if not extra_turn:
            new_state.current_player = 1 - current_player

    return new_state

def terminal_test(state):
    P1_empty = all(state.board[i] == 0 for i in P1_pits)
    P2_empty = all(state.board[i] == 0 for i in P2_pits)
    return P1_empty or P2_empty

def utility(state, player_id):
    P1_score = state.board[P1_store]
    P2_score = state.board[P2_store]


    if player_id==P1:
        if P1_score > P2_score:
            return 1
        elif P1_score < P2_score:
            return -1
        else:
            return 0
    else:
        if P2_score > P1_score:
            return 1
        elif P2_score < P1_score:
            return -1
        else:
            return 0

def score(state, player_id):
    if player_id == P1:
        return state.board[P1_store]
    else:
        return state.board[P2_store]
