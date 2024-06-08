import random
import json
import datetime
import copy
import math

from game import Game
from mcts import MCTS_Node

class Tree:
    def __init__(self, num_games, C, n_expansion_per_turn, modified_rules=None):
        self.root = tree_expansion(num_games, C, modified_rules=modified_rules)
        self.tree = self.root
        self.C = C
        self.elo = 1000
        self.sims_per_turn = n_expansion_per_turn
        self.modified_rules = modified_rules

class Random_Player:
    def __init__(self):
        self.root = None
        self.tree = None
        self.elo = 1000

def simulate_games(games_to_sim, p1, p2, modified_rules=None):
    """
    Simulate n games for all input trees using given C
    writes all results to a file 

    trees : a list of all trees
    C : hyperparameter for explotation vs exploration
    num_games : number of games to simulate
    """
    results = {}
    results[1] = 0
    results[-1] = 0
    results[0] = 0
    
    # simulate n games, update results dict
    for i in range(games_to_sim):
        print(f"Simulating Game {i+1}...")
        winner = sim_game(p1, p2, modified_rules=modified_rules)
        results[winner]+=1
        print(f"Winner: {winner}")

        # Reset trees to root
        p1.tree = p1.root
        p2.tree = p2.root

        p1.elo, p2.elo = elo(p1.elo, p2.elo, 20, winner)
        print(f"P1: {p1.elo}")
        print(f"P2: {p2.elo}")

    # save results to a file
    f = open('sim_results.txt', "a")
    now = datetime.datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    f.write(f"Results: {dt_string}")
    f.write(f"\n")
    f.write(json.dumps(results))
    f.write(f"\n"*2)
    f.close()

def elo_calulation(elo_a, elo_b):
     
    return 1.0 * 1.0 / (1 + 1.0 * math.pow(10, 1.0 * (elo_a - elo_b) / 400))
 
def elo(elo_1, elo_2, k, winner):
 
    # Probability of Player 1 winning
    prob_1 = elo_calulation(elo_2, elo_1)

    # Probability of Player 2 winning
    prob_2 = elo_calulation(elo_1, elo_2)
 
    if winner == 1:
        elo_1 = elo_1 + k * (1 - prob_1)
        elo_2 = elo_2 + k * (0 - prob_2)
    elif winner == -1:
        elo_1 = elo_1 + k * (0 - prob_1)
        elo_2 = elo_2 + k * (1 - prob_2)
    # Tie
    else:
        elo_1 = elo_1 + k * (0.5 - prob_1)
        elo_2 = elo_2 + k * (0.5 - prob_2)

    return elo_1, elo_2

def tree_expansion(num_games, C, modified_rules=None):
    """
    Build a MCT with a certain number of simulated games from the root
    saves the tree to a file for later use

    num_games : the number of games the tree should be pre-computed with
    C : hyperparameter for exploitation vs exploration
    """

    # Intialize the blank node and game
    cathedral = Game(modified_rules=modified_rules)
    root = MCTS_Node(cathedral, 1, 0, modified_rules=modified_rules) 

    root.best_action(num_games, C)

    return root

def sim_game(p1, p2, modified_rules=None):
    sim = Game()
    p1_type = 'Tree' if isinstance(p1.tree, MCTS_Node) else 'Random'
    p2_type = 'Tree' if isinstance(p2.tree, MCTS_Node) else 'Random'

    turn = 1
    level = 0

    while not sim.game_over(): 
        # While the game is not over
        current_player = sim.red_player if turn == 1 else sim.black_player

        # Get potential moves for the current player
        cathedral_turn = True if (modified_rules and level == 1) or (not modified_rules and level == 0) else None
        potential_moves = sim.get_potential_moves(current_player, cathedral_turn=cathedral_turn)

        # If the current player can make a move, if not flip to the other player/end the game
        if potential_moves: 
            if turn == 1:
                if p1_type == 'Tree':
                    sim = copy.deepcopy(p1.tree.best_action(p1.sims_per_turn, p1.C)._game)

                elif p1_type == 'Random':
                    move_selected = random.choice(potential_moves)  # choice a random move to make
                    piece_selected = move_selected[0] 
                    sim.use_piece(turn, piece_selected) 

                    # Update the board
                    returned_pieces = sim.game_board.update(move_selected[1], turn, move_selected[0])
                    if returned_pieces:
                        sim.return_piece(turn, returned_pieces[0])

            elif turn == 2:
                if p2_type == 'Tree':
                    sim = copy.deepcopy(p2.tree.best_action(p2.sims_per_turn, p2.C)._game)

                elif p2_type == 'Random':
                    move_selected = random.choice(potential_moves)  # choice a random move to make
                    piece_selected = move_selected[0] 
                    sim.use_piece(turn, piece_selected) 

                    # Update the board
                    returned_pieces = sim.game_board.update(move_selected[1], turn, move_selected[0])
                    if returned_pieces:
                       sim.return_piece(turn, returned_pieces[0])

        if p1_type == 'Tree':
            next_node = p1.tree.find_node(sim)
            if next_node:
                p1.tree = next_node
            else:
                p1.tree = p1.tree.expand_specific_node(copy.deepcopy(sim), modified_rules=modified_rules)

        if p2_type == 'Tree':
            next_node = p2.tree.find_node(sim)
            if next_node:
                p2.tree = next_node
            else: 
                p2.tree = p2.tree.expand_specific_node(copy.deepcopy(sim), modified_rules=modified_rules)

        # Go to the next 'level' (next order of potential moves)
        level+=1

        if modified_rules and level == 2:
            turn = 2
        # Under normal rules, red places first cathedral then first piece
        elif not modified_rules and level == 1:
            turn = 1
        else:
            turn = 1 if turn == 2 else 2

    return sim.winner  # Once a winner is found, end simulation

def main(): 
    # Low -> C = 0.7
    # Medium -> C = sqrt(2) (Theoretical ideal value)
    # High -> C = 2.1 

    random_player_red = Random_Player()
    random_player_black = Random_Player()

    # Trees with normal Rules
    tree_low_normal = Tree(num_games=2500, C=0.7, n_expansion_per_turn=25)
    tree_medium_normal = Tree(num_games=2500, C=math.sqrt(2), n_expansion_per_turn=25)
    tree_high_normal = Tree(num_games=2500, C=2.1, n_expansion_per_turn=25)

    # Trees with modified rules
    tree_low_modified = Tree(num_games=2500, C=0.7, n_expansion_per_turn=25, modified_rules=True)
    tree_medium_modified = Tree(num_games=2500, C=math.sqrt(2), n_expansion_per_turn=25, modified_rules=True)
    tree_high_modified = Tree(num_games=2500, C=2.1, n_expansion_per_turn=25, modified_rules=True)

    # Control Group 
    simulate_games(100, random_player_red, random_player_black)  # Sim 1
    simulate_games(100, random_player_red, random_player_black, modified_rules=True)  # Sim 2

    simulate_games(50, tree_low_normal, random_player_black)
    simulate_games(50, random_player_red, tree_low_normal)

    simulate_games(50, tree_medium_normal, random_player_black)
    simulate_games(50, random_player_red, tree_medium_normal)

    simulate_games(50, tree_high_normal, random_player_black)
    simulate_games(50, random_player_red, tree_high_normal)

    simulate_games(50, tree_low_modified, random_player_black, modified_rules=True)
    simulate_games(50, random_player_red, tree_low_modified, modified_rules=True)

    simulate_games(50, tree_medium_modified, random_player_black, modified_rules=True)
    simulate_games(50, random_player_red, tree_medium_modified, modified_rules=True)

    simulate_games(50, tree_high_modified, random_player_black, modified_rules=True)
    simulate_games(50, random_player_red, tree_high_modified, modified_rules=True)


if __name__=="__main__": 
    main() 