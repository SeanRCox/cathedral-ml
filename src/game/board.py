"""
Handles the game board, players and piece objects
"""

import copy
import numpy as np


class Board: 
    """
    Manages the Board - places pieces, refreshes the board state, etc
    
    Board:
    0 - empty square
    positive # - player 1 piece (red)
    negative # - player 2 piece (black)
    r - player 1 control (red)
    b - player 2 control (black)
    c - cathedral (special square)
    """
    def __init__(self):
        """
        Initializes the board

        _board_dimensions : the dimensions of the board, in this case 10x10
        _total_squares : the total number of squares on the board
        _board : the board
        """

        self._board_dimensions = 10
        self._total_squares = self._board_dimensions * self._board_dimensions
        self._board = np.zeros([self._board_dimensions, self._board_dimensions], dtype=object)

    def _refresh_board_state(self, placed_piece, player_sign):
        """
        Used after every player turn to update the board state
        
        param placed_piece : the most recent placed piece
        param player_sign : positive/negative numbers associated with each players pieces (1 for p1 or -1 for p2)

        return : any pieces that were captured
        """

        for sq in placed_piece:  # Check around every newly placed square to see if control needs to be updated
            checked = []  # Keep track of checked squares so as not to check twice
            
            nx, ny = sq[0], sq[1]  # Get coordinates of the given square
            for adj_sq in self._get_adjacent_squares(nx, ny): # Find all adjacent squares to given square
                
                if adj_sq in checked:
                    continue  # Skip checking squares that have already been checked
                
                else:
                    checked.append(adj_sq)
                    adj_x, adj_y = adj_sq[0], adj_sq[1]  # Get coordinates of the adjacent square to be checked
                    
                    if (self._board[adj_x, adj_y] == 'c') or (self._board[adj_x, adj_y] == 'b') or (self._board[adj_x, adj_y] == 'r'): 
                        # If a square is either the cathedral or already controlled by a player we don't need to check in that direction
                        continue
                    
                    elif (int(self._board[adj_x, adj_y]) * player_sign > 0):
                        # If a square is controlled by the player who just placed a piece we dont need to check in that direction
                        continue
                    
                    else:
                        captured_squares = self._check_if_surrounded(player_sign*-1, adj_x, adj_y)  # Check if the square is surrounded by the opposing player
                        if captured_squares:  # If the square is surrounded by the opposing player
                            captured_pieces = []

                            controlled_by = 'r' if player_sign == 1 else 'b'  # Determine which symbol to place based on which player will now control the squares
                            for c_sq in captured_squares:
                                c_x, c_y = c_sq[0], c_sq[1]

                                if self._board[c_x, c_y] != 0 and self._board[c_x, c_y] not in captured_pieces:
                                    captured_pieces.append(self._board[c_x, c_y])  # Check if any pieces are captured (Should only be 1 max)

                                self._board[c_x, c_y] = controlled_by  # Update the captured squares to represent control by a player
                        
                            return captured_pieces
        
        return False  # Returns False if no pieces are captured 
        
    def _get_adjacent_squares(self, x, y):
        """
        Gets all adjacent squares

        x : x coordinate to be checked around
        y : y coordinate to be checked around

        return -> all adjacent squares in every direction (including diagonals)
        """

        adj_squares = []

        for dx in range(-1 if (x > 0) else 0, 2 if (x < self._board_dimensions-1) else 1):  # Determine which x squares to check based on board dimensions
            for dy in range( -1 if (y > 0) else 0, 2 if (y < self._board_dimensions-1) else 1):  # Determine which y squares to check based on board dimensions
                if (dx != 0 or dy != 0):
                    adj_squares.append((x+dx, y+dy))

        return adj_squares
    
    def _check_if_surrounded(self, player_sign, x, y):
        """
        Checks if a given square is surronded by the opposing player

        player_sign : positive/negative numbers associated with each players pieces (1 for p1 or -1 for p2)
        x : x coordinate to be checked
        y : y coordinate to be checked

        return -> either False (not surrounded) or a list of the surrounded squares
        """

        piece_type_seen = []  # Record each type of piece seen (More then 1 cannot be captured)
        visited = []  # Record which squares we've visited
        queue = [(x,y)]  # Intialize the queue

        while queue:
            
            x, y = queue.pop(0)
            if (x, y) in visited:
                continue  # skip squares that we've already seen
            visited.append((x, y))

            if len(piece_type_seen) > 1:
                return False  # Only 1 piece can be surrounded and captured. If there is more then 1 type of piece in an area, the area is uncapturable.
            
            for sq in self._get_adjacent_squares(x,y): # Check every adjacent square to the given square
                nx, ny = sq[0], sq[1]
                
                controlled_squares = 'r' if player_sign == 1 else 'b'
                if (self._board[nx, ny] == controlled_squares): 
                    queue.append((nx, ny))

                elif (self._board[nx, ny] == 'c'): 
                    # Special case where the cathedral is seen: This can be captured
                    queue.append((nx, ny))
                    if 'c' not in piece_type_seen:
                        piece_type_seen.append('c')
                
                elif (int(self._board[nx, ny]) * player_sign > 0):
                    # Given square has a player piece on it, so we check around this aswell
                    queue.append((nx, ny))
                    if (self._board[nx, ny]) not in piece_type_seen:
                        piece_type_seen.append(self._board[nx, ny])

                elif (int(self._board[nx, ny]) == 0):
                    # Given square has nothing on it, so we check this
                    queue.append((nx, ny))

        return visited
    
    def _check_if_legal_move(self, target_squares, player):
        """
        Checks if a proposed move is legal

        target_squares : squares to updated
        player : the player number (1 or 2)

        return -> True if legal, otherwise False
        """

        valid_squares = 'r' if player == 1 else 'b'
        for target in target_squares:
            if self._board[target[0], target[1]] != 0 and self._board[target[0], target[1]] != valid_squares:
                return False
        return True

    def update(self, target_squares, player, piece_num):
        """
        Used to place pieces on the board, subsequently updates the board state

        target_squares : squares to updated
        player : the player number (1 or 2)
        piece_num : the piece number (1-10)

        return -> any pieces that have been captured
        """
        self.total_placed_pieces += 1
        player_sign = 1 if player == 1 else -1
        if self._check_if_legal_move(target_squares, player):
            for target in target_squares:
                if piece_num == 'c' : 
                    self._board[target[0], target[1]] = 'c'
                else:
                    self._board[target[0], target[1]] = int(piece_num) * player_sign  # Update the target squares with the proper piece number
            if self.total_placed_pieces <= 3:  # Squares can only be captured after each players first turn
                return False
            return self._refresh_board_state(target_squares, player_sign)  # If any pieces are captured, return them to the player
    
    def print_board(self):
        """
        Prints the board in a pretty way
        """

        for row in self._board:
        # Create a formatted string for each row where each element is formatted to be 3 characters wide
            formatted_row = ' '.join(f'{str(item):>3}' for item in row)
            print(formatted_row)

    def check_if_any_legal_moves(self, player, piece_counts, has_cathedral):
        """
        Finds if there are any legal moves for the given player

        player : the player number (1 or 2)
        piece_counts :
        has_cathedral :
        
        return -> True if a legal move is found, otherwise False
        """

        legal_moves = []
        for piece_number in range(1, 12):
            if has_cathedral: # If the player has the cathedral, they can re-place it down (this will almost never happen)
                legal_moves.append(self.find_potential_moves_for_given_piece('c', player))
            if piece_counts[piece_number-1] > 0:  # Check to see if the player has one of those pieces to place
                legal_move = self.find_potential_moves_for_given_piece(piece_number, player)
                if legal_move: return True
        return False
    
    def find_all_legal_moves(self, player, piece_counts, has_cathedral, cathedral_turn=None):
        """
        Creates a list of all legal moves for the given player

        player : the player number (1 or 2)
        piece_counts : list of piece counts for that player (needs to be atleast 1 to be able to place the piece)
        has_cathedral : boolean, true if player has cathedral, otherwise false
        cathedral_turn : boolean, true if it is the cathedral turn (special turn) otherwise false
        
        return -> a list of all legal moves for each piece for the given player
        """

        legal_moves = []
        if cathedral_turn:
            legal_move = self.find_potential_moves_for_given_piece('c', player)
            for move in legal_move:
                legal_moves.append(('c', move))
        else:
            for piece_number in range(1, 12):
                if has_cathedral: # If the player has the cathedral, they can re-place it down (this will almost never happen)
                    legal_move = self.find_potential_moves_for_given_piece('c', player)
                    for move in legal_move:
                        legal_moves.append(('c', move))
                if piece_counts[piece_number-1] > 0:  # Check to see if the player has one of those pieces to place
                    legal_move = self.find_potential_moves_for_given_piece(piece_number, player)
                    for move in legal_move:
                        legal_moves.append((piece_number, move))

        return legal_moves

    def find_potential_moves_for_given_piece(self, piece_number, player):
        """
        Creates a list of all potential moves for each piece (considering all shapes)

        player : the player number (1 or 2)
        piece_number : the piece number (1-11)
        
        return -> all potential moves for a given piece
        """

        pieces = get_pieces(1) if player == 1 else get_pieces(2)
        if piece_number == 'c':
            rotations = get_pieces('c')[2]
        else:
            rotations = pieces[int(piece_number)-1][2] # Get all possible rotations of the given piece
        
        potential_moves = [] # Intialize the potential moves list
        
        for potential_shape in rotations:
            for move in self.find_potential_moves_for_given_shape(potential_shape, player):
                # For each shape, get all of the potential moves and add it to the list
                potential_moves.append(move)

        return potential_moves
            
    def find_potential_moves_for_given_shape(self, piece_shape, player):
        """
        Scans the board to final all potential moves for a given piece shape

        piece_shape : the shape to checked for
        player : the player number (1 or 2)

        return -> a list of all valid placements of that shape
        """

        potential_placements = []  # All potential spots on the board that fit the given shape
        valid_placements = []  # All valid spots on the board that fit the given shape
        
        n, m = piece_shape.shape
        for i in range(self._board_dimensions - n + 1):
            for j in range(self._board_dimensions - m + 1):
                # Find all submatricies of size n x m and add them to potential placements
                coords = [(x, y) for x in range(i, i + n) for y in range(j, j + m)]
                potential_placements.append(coords) 

        piece_values = piece_shape.flatten().tolist()  # Flatten the list, we only care about its values now

        valid_player_squares = 'r' if player == 1 else 'b'
        for shape in potential_placements:
            coordinates_to_update = []  # Track which coordiantes within the shape need to be updated (0's dont need to be updated)
            valid = True
            for n, coords in enumerate(shape):
                if piece_values[n] != 0 and piece_values[n] != '0': # If a part of the piece needs to be placed
                    if self._board[coords[0]][coords[1]] != 0 and self._board[coords[0]][coords[1]] != valid_player_squares:
                        valid = False # If a part of the piece needs to be placed but theres another piece or other player control, its not a valid placement
                    else:
                        coordinates_to_update.append((coords[0], coords[1]))  # Its a valid placement at that coordinate, add it to the list of coordinates
            if valid: valid_placements.append(coordinates_to_update)  # If all of the squares are valid, add it to the list of valid placements

        return valid_placements
    
    def board_to_array(self):
        return self._board.flatten().tolist()


class Player:
    """
    Handles each player (red/black)
    """

    def __init__(self, player_num, modified_rules=None):
        """
        player_num : 1 for red, 2 for black
        modified_rules : optional arg to specify if tree should be using modified ruleset
        
        pieces : gets all player pieces
        score : the player score (lower score is better)
        has_cathedral : boolean, if player has cathedral or not
        """

        self.player_num = player_num
        self.pieces = copy.deepcopy(get_pieces(1))if player_num == 1 else copy.deepcopy(get_pieces(2))
        self.score = 47  # Starting score is sum of all pieces, goal is to place all pieces or get lowest score before game ends
        if modified_rules and player_num == 2:
            self.has_cathedral = True
        elif not modified_rules and player_num == 1:
            self.has_cathedral = True
        else:
            self.has_cathedral = False
    
    def use_piece(self, piece):
        """
        Remove a piece from a players piece count, update their score

        piece : piece to remove

        return -> True if piece is used
        """

        # If piece is the cathedral, set cathedral boolean to false
        if piece == 'c':
            self.has_cathedral = False
            return True
        
        # If player cannot use piece, return false
        if self.pieces[int(piece)-1][1] < 1: return False  

        # Decrement and update piece count and score
        self.pieces[int(piece)-1][1] -= 1
        self.score -= self.pieces[int(piece)-1][0]
        
        return True
    
    def get_piece_counts(self):
        """
        Returns a list of the current players piece count

        return -> list of the current players piece count
        """

        counts = []
        for piece in self.pieces:
            counts.append(piece[1])
        
        return counts
    
    def return_pieces(self, piece):
        """
        Increments a players piece count if a piece is captured by the other player

        piece : the piece to be returned

        return -> None
        """

        if piece == 'c':
            self.has_cathedral = True
        else:
            piece = abs(piece)
            self.pieces[int(piece)-1][1] += 1

    def can_place_cathedral(self):
        """
        Returns whether or not the current player can place the cathedral

        return -> boolean
        """

        return self.has_cathedral
    

class Piece:
    """
    Creates the board pieces
    """

    def __init__(self, p_num, p_value, p_count, p_shape, player):
        """
        p_value : value of the piece
        p_num : number (1-9) that identifies the piece on the board
        p_count : amount of that piece the player starts with
        p_shape : 2d array of the pieces base shape
        player :  player number (1/-1)
        rotations: all of the possible rotations for that piece (between 1 and 4)
        """
        
        self._point_value = p_value
        self._piece_shape = np.where(p_shape == 1, p_num*player, p_shape)
        self._initial_count = p_count
        self._rotations = []
        self._rotations.append(self._piece_shape)

        # Get all potential rotations
        _potential_rotations = []
        _potential_rotations.append(self._rotate_clockwise())
        _potential_rotations.append(self._rotate_180())
        _potential_rotations.append(self._rotate_counterclockwise())
        
        # Remove any duplicate rotations
        seen = set()
        unique_rotations = []
        for rotation in _potential_rotations:
            # Use a tuple representation to hash the array for checking duplicates
            rotation_tuple = tuple(map(tuple, rotation))
            if rotation_tuple not in seen:
                seen.add(rotation_tuple)
                unique_rotations.append(rotation)

        # Add all unique shapes to the rotations list
        for shape in unique_rotations:
            if not np.array_equal(shape, self._piece_shape):
                self._rotations.append(shape)

    def _rotate_clockwise(self):
        """ 
        Rotate the matrix clockwise 90 degrees. 

        return -> rotated matrix
        """

        return np.array([list(reversed(col)) for col in zip(*self._piece_shape)])
    
    def _rotate_180(self):
        """ 
        Rotate the matrix 180 degrees. 

        return -> rotated matrix
        """

        return np.array([list(reversed(row)) for row in reversed(self._piece_shape)])

    def _rotate_counterclockwise(self):
        """ 
        Rotate the matrix counterclockwise 90 degrees. 

        return -> rotated matrix
        """

        return np.array([list(col) for col in reversed(list(zip(*self._piece_shape)))])
    
    def get_piece(self):
        """
        Returns the specified piece's values

        return -> point value, count, all rotations
        """
        return [self._point_value, self._initial_count, self._rotations]


def get_pieces(type):
    """
    Returns the appropriate piece objects

    type : 1 for red, 2 for black, c for cathedral
    
    return -> red pieces/black pieces, or cathedral
    """
    # Piece Information

    # Default piece shapes
    tavern_shape = np.array([[1]])

    stable_shape = np.array([[1, 1]])

    inn_shape = np.array([[1, 1],
                        [1, 0]])
    
    bridge_shape = np.array([[1, 1, 1]])
    manor_shape = np.array([[1, 1, 1],
                        [0, 1, 0]])
    
    square_shape = np.array([[1, 1],
                            [1, 1]])
    
    abbey_shape = np.array([[1, 1, 0],
                        [0, 1, 1]])
    
    infirmary_shape = np.array([[0, 1, 0],
                            [1, 1, 1],
                            [0, 1, 0]])
    
    castle_shape = np.array([[1, 1],
                    [1, 0],
                    [1, 1]])
    
    tower_shape = np.array([[0, 0, 1],
                        [0, 1, 1],
                        [1, 1, 0]])
    
    academy_shape = np.array([[0, 1, 0],
                            [0, 1, 1],
                            [1, 1, 0]])
    
    cathedral_shape = np.array([[0, 1, 0],
                            [1, 1, 1],
                            [0, 1, 0],
                            [0, 1, 0]])

    piece_shapes = [tavern_shape, stable_shape, inn_shape, bridge_shape, manor_shape, square_shape, 
                abbey_shape, infirmary_shape, castle_shape, tower_shape, academy_shape]

    # Piece number, piece value, inital piece count
    piece_values = [(1, 1, 2), (2, 2, 2), (3, 3, 2), (4, 3, 1), (5, 4, 1), (6, 4, 1),
                (7, 4, 1), (8, 5, 1), (9, 5, 1), (10, 5, 1), (11, 5, 1)] 

    # Return requested piece set
    if type == 1: 
        # Red Pieces
        return [(Piece(piece_values[i][0], piece_values[i][1], piece_values[i][2], shape, 1).get_piece()) for i, shape in enumerate(piece_shapes)]
    elif type == 2:
        # Red Pieces
        return [(Piece(piece_values[i][0], piece_values[i][1], piece_values[i][2], shape, -1).get_piece()) for i, shape in enumerate(piece_shapes)]
    elif type == 'c':
        # Cathedral
        return (Piece('c', 0, 1, cathedral_shape, 1).get_piece())


