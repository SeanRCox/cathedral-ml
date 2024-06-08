import math
import datetime
import json
import copy

from sim import sim_game, tree_expansion

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
        print(f"Simulating Game {i}...")
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
    f = open('results/sim_results.txt', "a")
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