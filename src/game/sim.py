import random
from game import Game
from mcts import MCTS_Node

results_file = 'results/sim_results.txt'

def tree_expansion(num_games, C):
    """
    Build a MCT with a certain number of simulated games from the root
    """

    # Intialize the blank node and game
    cathedral = Game()
    root = MCTS_Node(cathedral, 1, 0) 

    root.best_action(num_games, C)

    return root

def create_trees():
    Trees = [

        # High Exploitation, Low Exploration
        tree_expansion(num_games=100, C=0.2),
        tree_expansion(num_games=1000, C=0.2),
        tree_expansion(num_games=2000, C=0.2),
        #tree_expansion(num_games=100000, C=0.2),

        # Equal Exploitation, Exploration
        #tree_expansion(num_games=100, C=0.5),
        #tree_expansion(num_games=1000, C=0.5),
        #tree_expansion(num_games=10000, C=0.5),
        #tree_expansion(num_games=100000, C=0.5),

        # High Exploration, Low Exploitation
        #tree_expansion(num_games=100, C=0.8),
        #tree_expansion(num_games=1000, C=0.8),
        #tree_expansion(num_games=10000, C=0.8),
        #tree_expansion(num_games=100000, C=0.8)
    ]

    return Trees

def sim_game(tree, sim_num, C):
    """
    Simulate a game between a tree and a player who plays random moves
    """
    sim = Game()

    turn = 1
    first_turn = True


    while not sim.game_over():
         
        if turn == 1: 
            potential_moves = sim.game_board.find_all_legal_moves(1, sim.red_player.get_piece_counts(), sim.red_player.can_place_cathedral()) 

            if potential_moves:
                best_action = tree.best_action(sim_num, C)._game

                if best_action is not None:
                    sim = best_action
                
                    next_node = tree.find_node(sim)
                    if next_node:
                        tree = next_node
                    else: 
                        tree = tree.expand_specific_node(sim)

        elif turn == 2:
            potential_moves = sim.game_board.find_all_legal_moves(2, sim.black_player.get_piece_counts(), False)   # Add a new function to game so I dont have to put in all this

            if potential_moves:
                move_selected = random.choice(potential_moves)
                
                piece_selected = move_selected[0] 
                sim.black_player.use_piece(piece_selected)

                returned_pieces = sim.game_board.update(move_selected[1], turn, move_selected[0])
                if returned_pieces:
                    sim.red_player.return_pieces(returned_pieces[0])

                next_node = tree.find_node(sim)
                if next_node:
                    tree = next_node
                else: 
                    tree = tree.expand_specific_node(sim)

        turn = 1 if turn == 2 or first_turn else 2 
        if first_turn: first_turn = False
        
    return sim.winner

def simulate_trees(trees, C):
    for n, tree in enumerate(trees):
        results = {}  # Results dictionary
        results[1] = 0  # Red Wins
        results[-1] = 0  # Black Wins
        results[0] = 0  # Ties

        for i in range(1,100):
            print(f"Tree {n}: Simulating Game {i}...")
            winner = sim_game(tree, 100, C)
            results[winner]+=1

        f = open(results_file, "a")
        f.write(f"Results for Tree {n}, C = {C}")
        f.write(results)

trees = create_trees()
trees_1 = trees[0:3]
trees_2 = trees[3:6]
trees_3 = trees[6:9]

simulate_trees(trees_1, 0.2)
#simulate_trees(trees_2, 0.5)
#simulate_trees(trees_3, 0.8)






