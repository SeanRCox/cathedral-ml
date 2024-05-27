import random
import copy
import numpy as np
from game import Game

class MCTS_Node:
    def __init__(self, game, turn, first_move=None, parent=None, parent_move=None):
        """
        Initializes a node for the Monte Carlo Tree
        
        game_board : the current state of the game board (10x10 np array)
        parent : the parent node to the current node (None for the root)
        parent_move : the move that parent took to reach this node (none for the root)
        children : all children of the current node
        num_visits : the number of times this node has been visited
        """

        self.game = game  # Use this to access game board, players and turn
        self.turn = turn # 1 for red 2 for black
        self.next_turn = 1 if self.turn == 2 or first_move == True else 2
        self.first_move = first_move  # Player 1 goes twice to start, need a way to track if its the first move 
        self.current_player = game.red_player if self.turn == 1 else game.black_player
        self.opposing_player = game.red_player if self.turn == 2 else game.black_player

        self.parent = parent
        self.parent_move = parent_move
        self.children = []
        self.num_visits = 0

        self.results = {}
        self.results[1] = 0  # Wins
        self.results[-1] = 0  # Losses
        self.results[0] = 0  # Ties

        if self.parent == None:
            self._untried_moves = self.game.game_board.find_all_legal_moves \
                               (1, self.current_player.get_piece_counts(), self.current_player.can_place_cathedral(), True)
            self.game.red_player.use_piece('c')
        else:
            self._untried_moves = self.game.game_board.find_all_legal_moves \
                               (self.next_turn, self.opposing_player.get_piece_counts(), self.opposing_player.can_place_cathedral())
        

    def expand(self):
        """
        Expand the tree from the current node
        """
        print(f"Untried Moves: {len(self._untried_moves)}")
        move = self._untried_moves.pop()
        
        updated_game = copy.deepcopy(self.game)
        updated_game.game_board.update(move[1], self.turn, move[0])

        child_node = MCTS_Node(updated_game, self.next_turn, parent=self, parent_move=move)
        self.children.append(child_node)
        #print(child_node.game.game_board.print_board())
        #print("_"*40)
        return child_node
    
    def rollout(self, from_root=None):
        """
        Simulate the rest of the game from the current position
        """
        simulated_game = copy.deepcopy(self.game)
        current_turn = self.turn

        """
        if node_level == 0:
            potential_moves = simulated_game.game_board.find_potential_moves_for_given_piece('c', 1)  # Player 1 places the cathedral
            move_selected = self.rollout_policy(potential_moves)
            simulated_game.red_player.use_piece('c')
            simulated_game.game_board.update(move_selected, 1, 'c')  #Put the cathedral on the board 
            print(move_selected)
        """
        
        while not simulated_game.game_over():

            current_turn = 1 if current_turn == 2 else 2
            if from_root:
                current_turn = 1
                from_root = False

            current_player = simulated_game.red_player if current_turn == 1 else simulated_game.black_player
            #print(f"Current Player: {current_turn}, can play cathedral?: {current_player.can_place_cathedral()}")

            potential_moves = simulated_game.game_board.find_all_legal_moves \
                                (current_turn, current_player.get_piece_counts(), current_player.can_place_cathedral())


            if potential_moves: 
                move_selected = self.rollout_policy(potential_moves)

                piece_selected = move_selected[0]
                if current_turn == 1:
                    simulated_game.red_player.use_piece(piece_selected)
                else: 
                    simulated_game.black_player.use_piece(piece_selected)

                returned_pieces = simulated_game.game_board.update(move_selected[1], current_turn, move_selected[0])
                if returned_pieces:  # If any pieces were captured, return them to the opposing player
                    if current_turn == 1: simulated_game.black_player.return_pieces(returned_pieces[0])
                    else: simulated_game.red_player.return_pieces(returned_pieces[0])
            
        return simulated_game.winner

    def rollout_policy(self, potential_moves):
        """
        The policy for selecting which moves to simulate. For now it is just random
        """
        return random.choice(potential_moves)

    def backpropagate(self, result):
        self.num_visits += 1
        self.results[result] += 1
        if self.parent:
            self.parent.backpropagate(result)

    def is_fully_expanded(self):
        return len(self._untried_moves) == 0

    def best_child(self, c_param=0.1):
        choices_weights = [(c.q() / c.n()) + c_param * np.sqrt((2 * np.log(self.n()) / c.n())) for c in self.children]
        return self.children[np.argmax(choices_weights)]

    def _tree_policy(self):
        current_node = self
        while not current_node.is_terminal_node():
    
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child()
        
        return current_node

    def is_terminal_node(self):
        return self.game.game_over()

    def best_action(self, from_root=None):
        simulation_no = 100
        
        for _ in range(simulation_no):
            v = self._tree_policy()
            reward = v.rollout(from_root)
            v.backpropagate(reward)
        
        return self.best_child(c_param=0.1)
    
    def q(self):
        wins = self.results[1]
        loses = self.results[-1]
        return wins - loses
    
    def n(self):
        return self.num_visits

cathedral = Game()
root = MCTS_Node(cathedral, 1, first_move=True)
selected_node = root.best_action(from_root=True)
next_node = selected_node.best_action()
for child in selected_node.children:
    child.game.game_board.print_board()
    print("_"*40)
print(selected_node.results)
print("Best Move:")
next_node.game.game_board.print_board()