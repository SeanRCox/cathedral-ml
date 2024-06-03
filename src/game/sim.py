import random
import pickle
import os
import json

from game import Game
from mcts import MCTS_Node

def tree_expansion(num_games, C):
    """
    Build a MCT with a certain number of simulated games from the root
    saves the tree to a file for later use

    num_games : the number of games the tree should be pre-computed with
    C : hyperparameter for exploitation vs exploration
    """

    # Intialize the blank node and game
    cathedral = Game()
    root = MCTS_Node(cathedral, 1, 0) 

    root.best_action(num_games, C)

    filename = f"trees/tree_{num_games}_{C}"
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

def sim_game(tree, sim_num, C):
    """
    Simulate a game between a tree and a player who plays random moves

    tree : the tree being used
    sim_num : number of future moves the tree can simulate per move 
    C : hyperparamter for exploitation vs exploration
    """

    sim = Game()  # Create a game to simulate

    turn = 1
    first_turn = True

    while not sim.game_over():
        sim.game_board.print_board()
        print("_"*40)


        if turn == 1: 
            potential_moves = sim.get_potential_moves(sim.red_player)  # If red has potential moves
            if potential_moves: 
                
                best_action = tree.best_action(sim_num, C)._game  # Find best action for red, able to serach sim_num number of games
                sim = best_action
            
                next_node = tree.find_node(sim)  # Search for the next node 
                # If the next node is found already in the tree (it should be), set the tree to that new node
                # Otherwise expand to that node specifically
                if next_node:
                    tree = next_node
                else: 
                    tree = tree.expand_specific_node(sim)

        elif turn == 2:
            potential_moves = sim.get_potential_moves(sim.black_player) # If black has potential moves
            if potential_moves:
                
                move_selected = random.choice(potential_moves)  # choice a random move to make
                piece_selected = move_selected[0] 
                sim.black_player.use_piece(piece_selected)  # Remove piece from piece count for black

                # Update the game board, return any pieces
                returned_pieces = sim.game_board.update(move_selected[1], turn, move_selected[0])
                if returned_pieces:
                    sim.red_player.return_pieces(returned_pieces[0])

                # If the next node is found already in the tree (it probably isnt), set the tree to that new node
                # Otherwise expand to that node specifically
                next_node = tree.find_node(sim)
                if next_node:
                    tree = next_node
                else: 
                    tree = tree.expand_specific_node(sim)

        # Flip turns, first player goes twice to start
        turn = 1 if turn == 2 or first_turn else 2 
        if first_turn: first_turn = False
        
    return sim.winner

def simulate_trees(trees, C, num_games):
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
            winner = sim_game(tree, 20, C)
            results[winner]+=1

        
        # save results to a file
        f = open('results/sim_results.txt', "a")
        f.write(f"Results for Tree {n}, C = {C}")
        f.write(json.dumps(results))
        print()

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

#create_trees()
trees = get_trees()

simulate_trees(trees, 0.5, 1)






