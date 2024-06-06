import random
import pickle
import os
import json
import datetime
import copy

from game import Game
from mcts import MCTS_Node

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

    rules = "modified" if modified_rules else "standard"
    filename = f"trees/tree_{num_games}_{C}_{rules}"
    with open(filename, 'wb') as f:
            pickle.dump(root, f)

    return root

def create_trees():
    trees = [

        # High Exploitation, Low Exploration
        tree_expansion(num_games=100, C=0.2),
        #tree_expansion(num_games=1000, C=0.2),
        #tree_expansion(num_games=10000, C=0.2),

        # Equal Exploitation, Exploration
        tree_expansion(num_games=100, C=0.5),
        #tree_expansion(num_games=1000, C=0.5),
        #tree_expansion(num_games=10000, C=0.5),

        # High Exploration, Low Exploitation
        tree_expansion(num_games=100, C=0.8),
        #tree_expansion(num_games=1000, C=0.8),
        #tree_expansion(num_games=10000, C=0.8),
    ]

    return True

def sim_game(p1, p2, p1_C=None, p2_C=None, p1_sims=None, p2_sims=None, modified_rules=None):
    sim = Game()
    p1_type = 'Tree' if isinstance(p1, MCTS_Node) else 'Random'
    p2_type = 'Tree' if isinstance(p2, MCTS_Node) else 'Random'

    turn = 1
    level = 0

    while not sim.game_over(): 
        # While the game is not over
        sim.game_board.print_board()
        print("_"*40)

        current_player = sim.red_player if turn == 1 else sim.black_player

        # Get potential moves for the current player
        cathedral_turn = True if (modified_rules and level == 1) or (not modified_rules and level == 0) else None
        potential_moves = sim.get_potential_moves(current_player, cathedral_turn=cathedral_turn)

        # If the current player can make a move, if not flip to the other player/end the game
        if potential_moves: 
            if turn == 1:
                if p1_type == 'Tree':
                    sim = copy.deepcopy(p1.best_action(p1_sims, p1_C)._game)

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
                    sim = copy.deepcopy(p2.best_action(p2_sims, p2_C)._game)

                elif p2_type == 'Random':
                    move_selected = random.choice(potential_moves)  # choice a random move to make
                    piece_selected = move_selected[0] 
                    sim.use_piece(turn, piece_selected) 

                    # Update the board
                    returned_pieces = sim.game_board.update(move_selected[1], turn, move_selected[0])
                    if returned_pieces:
                       sim.return_piece(turn, returned_pieces[0])

        if p1_type == 'Tree':
            next_node = p1.find_node(sim)
            if next_node:
                p1 = next_node
            else:
                p1 = p1.expand_specific_node(copy.deepcopy(sim), modified_rules=modified_rules)

        if p2_type == 'Tree':
            next_node = p2.find_node(sim)
            if next_node:
                p2 = next_node
            else: 
                p2 = p2.expand_specific_node(copy.deepcopy(sim), modified_rules=modified_rules)

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


def simulate_games(num_games, p1, p2, p1_C=None, p2_C=None, p1_sims=None, p2_sims=None, modified_rules=None):
    """
    Simulate n games for all input trees using given C
    writes all results to a file 

    trees : a list of all trees
    C : hyperparameter for explotation vs exploration
    num_games : number of games to simulate
    """
    
    for n, tree in enumerate(trees):
        results = {}  # Results dictionary
        results[1] = 0  # Red Wins
        results[-1] = 0  # Black Wins
        results[0] = 0  # Ties

        # simulate n games, update results dict
        for i in range(1, num_games+1):
            print(f"Tree {n}: Simulating Game {i}...")
            winner = sim_game(p1, p2, p1_C=p1_C, p1_sims=p1_sims, p2_C=p2_C, p2_sims=p2_sims, modified_rules=modified_rules)
            print(winner)
            results[winner]+=1

        
        # save results to a file
        f = open('results/sim_results.txt', "a")
        now = datetime.datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        f.write(f"Results for sim {n}, {dt_string}")
        f.write(f"\n")
        f.write(json.dumps(results))
        f.write(f"\n"*2)
        f.close()

def get_trees():
    """
    Load trees from the trees file
    """

    trees = []
    folder_path = 'trees/'

    # For each file in the trees/ folder, load the file into the trees list
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                trees.append(pickle.load(f))

    return trees

trees = []
trees.append(tree_expansion(num_games=1, C=0.5))
#trees.append(tree_expansion(num_games=1000, C=0.5, modified_rules=True))

simulate_games(100, trees[0], trees[0], p1_C=0.5, p1_sims=10, p2_C=0.5, p2_sims=10)

