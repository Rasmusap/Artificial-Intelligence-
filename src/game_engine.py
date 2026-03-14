from dataclasses import dataclass, field
# Players
P1 = 0
P2 = 1

# about the board
P1_pits  = [0, 1, 2, 3, 4, 5]
P1_store = 6
P2_pits  = [7, 8, 9, 10, 11, 12]
P2_store = 13
Board_size = 14

# to find the oppoite pit.
# hvis i ikke forstår opposite, så prøv at lave nogle eksempler så giver det mening. at man får præcis den modsatte pit
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
        board = [4,4,4,4,4,4, 0, 4,4,4,4,4,4, 0], # every pit start with 4 stones, and the stores start with 0
        current_player = 0  # Player 1 goes first
    )

# whose turn it is
def player(state):
    return state.current_player


def actions(state):
    if state.current_player == P1:
        pits = P1_pits
    else:
        pits = P2_pits
    
    return [i for i in pits if state.board[i] > 0] # player can only choose pits that have more than 0 stones

def result(state, action):
    # make a copy of the state, so we don't modify the original state
    new_state= state.copy()
    board= new_state.board
    current_player = new_state.current_player
    
    
    #We check who the current player is, and then we set the opponent's store, own store and own pits accordingly    
    opponent_store = P2_store if current_player == P1 else P1_store
    own_store = P1_store if current_player == P1 else P2_store
    own_pits = P1_pits if current_player == P1 else P2_pits
    
    stones=board[action] # number of stones in the chosen pit
    board[action] = 0 # we take all the stones from the chosen pit
    
    index=action
    while stones >0:
        index = (index + 1) % Board_size # move to the next pit, wrap around using modulo
        if index == opponent_store: # skip the opponent's store
            continue
        board[index] += 1 # drop a stone in the current pit
        stones -= 1 # decrease the number of stones left to drop
    
    # Check if the last stone landed in the player's own store, if so, they get another turn
    extra_turn = (index == own_store)
    
    if not extra_turn and index in own_pits and board[index] == 1: # if the last stone landed in an empty pit on the player's own side
        opp = opposite_pit(index) # find the opposite pit
        if board[opp] > 0: # if the opposite pit has stones, capture them
            board[own_store] += board[opp] + 1 # move the captured stones and the last stone to the player's store
            board[index] = 0 # empty the pit where the last stone landed
            board[opp] = 0 # empty the opposite pit
    
    
    # check if the game is over (one side has no stones in their pits)
    p1_empty = all(board[i] == 0 for i in P1_pits)
    p2_empty = all(board[i] == 0 for i in P2_pits)
    
    if p1_empty or p2_empty:
        # if the game is over, move all remaining stones to the respective stores
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
    # the game is terminal if one player's pits are all empty
    P1_empty = all(state.board[i] == 0 for i in P1_pits)
    P2_empty = all(state.board[i] == 0 for i in P2_pits)
    return P1_empty or P2_empty

def utility(state, player_id):
    # count the stones in each player's store to determine the winner
    P1_score = state.board[P1_store]
    P2_score = state.board[P2_store]
    
    
    if player_id==P1:
        if P1_score > P2_score:
            return 1 # Player 1 wins
        elif P1_score < P2_score:
            return -1 # Player 1 loses
        else:
            return 0 # Draw
    else:
        if P2_score > P1_score:
            return 1
        elif P2_score < P1_score:
            return -1
        else:
            return 0
        
def score(state, player_id):
    # return the score for the given player
    if player_id == P1:
        return state.board[P1_store]
    else:
        return state.board[P2_store]
        
        
