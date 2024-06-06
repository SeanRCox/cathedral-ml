import random
import copy
import numpy as np

results_file = 'results/sim_results.txt'

class MCTS_Node:
    def __init__(self, game, turn, level, parent=None, modified_rules=None):
        """
        Initializes a node for the Monte Carlo Tree
        
        _game : game class, manages game board and players
        _turn : tracks the current turn, 1 for red, 2 for black
        _next_turn : opposite of turn
        _first_move : optional arg used to track if this node corresponds to the first move,
        this is necessary to becuase red goes twice to start

        _parent : the parent node, none for root
        _children : list of all child nodes
        _num_visits : the amount of times this node was visited

        results: track the wins for this node (1 for red, -1 for black, 0 for tie)
        """

        self._game = game # Use this to access game board, players
        self._red = game.red_player
        self._black = game.black_player
        self._turn = turn # 1 for red 2 for black
        self._level = level
        self._modified_rules = modified_rules

        # Under modified rules, black player places cathedral and their first move together
        if self._level == 0:
            self._next_turn = 1
        elif self._modified_rules and (self._level == 2):
            self._next_turn = 2
        elif not self._modified_rules and (self._level == 1):
            self._next_turn = 1
        else:
            self._next_turn = 1 if self._turn == 2 else 2

        # If a player does not have a move, skip their turn and go to the other player
        if not self._game.has_potential_moves(self._red):
            self._next_turn = 2
        if not self._game.has_potential_moves(self._black):
            self._next_turn = 1

        self._parent = parent  # Parent node
        self._children = []  # List of child nodes
        self._num_visits = 0  # number of times this node has been visited

        self._results = {}  # Results dictionary
        self._results[1] = 0  # Red Wins
        self._results[-1] = 0  # Black Wins
        self._results[0] = 0  # Ties

        # Special checks to account for cathedral placement
        if modified_rules and self._level == 1:
            self._untried_moves = self._game.get_potential_moves(self._black, True)
        elif not modified_rules and self._level == 0:
            self._untried_moves = self._game.get_potential_moves(self._red, True)
        else:
            if self._next_turn == 2:
                self._untried_moves = self._game.get_potential_moves(self._black)
            
            if self._next_turn == 1:
                self._untried_moves = self._game.get_potential_moves(self._red)
                
        self._untried_moves = self._randomize_potential_moves(self._untried_moves)  # Randomize the potential moves 
        
    def _expand(self):
        """
        Expand the tree from the current node

        return : a new child node with the updated board/player state after playing an untried move
        """

        #print(f"Potential Moves to Explore: {len(self._untried_moves)}")
        move = self._untried_moves.pop()  # Pop an untried move
        
        updated_game = copy.deepcopy(self._game)  # Make a deepcopy of the current game, this is the game for the new node

        piece_selected = move[0] 
        updated_game.use_piece(self._next_turn, piece_selected)
        
        returned_pieces = updated_game.game_board.update(move[1], self._next_turn, move[0])  # Update the new game, this is the initial game for the new node
        if returned_pieces: 
            updated_game.return_piece(self._next_turn, returned_pieces[0])

        # Create a new child node with the updated board/player states
        child_node = MCTS_Node(updated_game, self._next_turn, self._level+1, parent=self, modified_rules=self._modified_rules)
        self._children.append(child_node)
        
        return child_node
    
    def _rollout(self):
        """
        Simulate the rest of the game from the current position
        """

        simulated_game = copy.deepcopy(self._game)  # Make a deepycopy of the current game state to simulate from
        current_turn = self._turn
        current_level = self._level
        
        while not simulated_game.game_over(): 
            # While the game is not over

            if self._modified_rules and (current_level == 2):
                current_turn = 2
            # Under normal rules, red places first cathedral then first piece
            elif not self._modified_rules and (current_level == 1):
                current_turn = 1
            else:
                current_turn = 1 if current_turn == 2 else 2

            current_player = simulated_game.red_player if current_turn == 1 else simulated_game.black_player

            # Get potential moves for the current player
            cathedral_turn = True if (self._modified_rules and current_level == 1) else None
            potential_moves = simulated_game.get_potential_moves(current_player, cathedral_turn)

            # If the current player can make a move, if not flip to the other player/end the game
            if potential_moves: 
                move_selected = self._rollout_policy(potential_moves)  # Select a move based on rollout policy (right now just pick a random move)

                # Remove the piece from the players piece count
                piece_selected = move_selected[0] 
                simulated_game.use_piece(current_turn, piece_selected)

                # Update the board
                returned_pieces = simulated_game.game_board.update(move_selected[1], current_turn, move_selected[0])
                if returned_pieces:  # If any pieces were captured, return them to the opposing player
                    simulated_game.return_piece(current_turn, returned_pieces[0])
        
            # Go to the next 'level' (next order of potential moves)
            current_level+=1

        return simulated_game.winner  # Once a winner is found, end simulation

    def _rollout_policy(self, potential_moves):
        """
        The policy for selecting which moves to simulate 
        for now it is just picking a random move

        potential_moves : list of potential moves to pick from
        """

        return random.choice(potential_moves)

    def _backpropagate(self, result):
        """
        Backpropgate the result up the tree

        result : the result of the simulated node (1 for red win, -1 for black win, 0 for tie)
        """

        self._num_visits += 1
        self._results[result] += 1
        if self._parent:
            self._parent._backpropagate(result)  # Backprop

    def _is_fully_expanded(self):
        """
        Determines if the tree is fully expanded (no potential moves from current node)
        """

        return len(self._untried_moves) == 0

    def best_child(self, C):
        """
        Use Upper Confidence Bound formula for selecting the most optimal node

        C : the 'c' hyperparamter, set to bias exploration vs exploitation,
        or going to new nodes vs going to nodes already known to be strong
        """

        choices_weights = [(child._get_num_wins() / child._get_num_visits()) + C * \
                           np.sqrt((2 * np.log(self._get_num_visits()) / child._get_num_visits())) for child in self._children]
        return self._children[np.argmax(choices_weights)]  # Return the strongest node

    def _tree_policy(self, C):
        """
        Determines the policy for expanding the tree
        If the current node is not an end node, and the tree is not fully expanded
        from the current node, expand the tree from the current node. Otherwise just
        return the best child node
        """

        current_node = self
        while not current_node._is_terminal_node():
    
            if not current_node._is_fully_expanded():
                return current_node._expand()
            else:
                current_node = current_node.best_child(C)
        
        return current_node

    def _is_terminal_node(self):
        """
        Check if the game is over
        """
        return self._game.game_over()

    def _get_num_wins(self):
        """
        Determine the win-loss ratio of simulated games from current node and all child nodes
        Different for each player
        """

        red_wins = self._results[1]
        black_wins = self._results[-1]
        if self._turn == 1: 
            return red_wins-black_wins 
        elif self._turn == 2:
            return black_wins-red_wins
    
    def _get_num_visits(self):
        """
        returns the number of times the current node has been visited
        """

        return self._num_visits

    def _randomize_potential_moves(self, potential_moves):
        """
        helper function to randomize the list of potential moves
        this is useful when there are too many potential moves,
        but you want a more representaive sample of the possible
        moves rather then just the potential moves of a few pieces
        """

        random.shuffle(potential_moves)
        return potential_moves
    
    def best_action(self, num_games, C):
        """
        Find the best action from the current node
        """

        num_of_expansions = num_games  # Amount of nodes to expand/sim

        for i in range(num_of_expansions):
            #print(f"Simulation #: {i}")
            node = self._tree_policy(C)  # Either a new node or the best child
            reward = node._rollout()  # Simulate a game from this node
            node._backpropagate(reward)  # Backprop results of sim

        return self.best_child(C)   
    
    def find_node(self, game_state):
        if self.check_equivelence(game_state):
            return self
        for child in self._children:
            if child.check_equivelence(game_state):
                return child
        return False
    
    def expand_specific_node(self, game_state, modified_rules=None):
        """
        Used when a game is being played and the tree does
        not contain a child node for the opponents selected move
        """
        new_node = MCTS_Node(game_state, self._next_turn, self._level+1, parent=self, modified_rules=modified_rules)
        self._children.append(new_node)
        return new_node
    
    def check_equivelence(self, game_state):
        #print(self._game.game_board.board_to_array(), game_state.game_board.board_to_array())
        if (self._game.game_board.board_to_array() == game_state.game_board.board_to_array()):
            return True
        else:
            return False
    
