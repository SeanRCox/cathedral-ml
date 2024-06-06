import numpy as np
import pieces as p

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

        _p1_controlled : number of squares controlled by player 1
        _p2_controlled : number of squares controlled by player 2
        """

        self._board_dimensions = 10
        self._total_squares = self._board_dimensions * self._board_dimensions
        self._board = np.zeros([self._board_dimensions, self._board_dimensions], dtype=object)
        
        self._p1_controlled = 0
        self._p2_controlled = 0 

        self.total_placed_pieces = 0

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
                            
                            if player_sign == 1: self._p1_controlled += len(captured_squares)  # Update the amount of captured squares, used to check if squares are surrounded
                            else: self._p2_controlled += len(captured_squares) 

                            controlled_by = 'r' if player_sign == 1 else 'b'  # Determine which symbol to place based on which player will now control the squares
                            for c_sq in captured_squares:
                                c_x, c_y = c_sq[0], c_sq[1]

                                if self._board[c_x, c_y] != 0 and self._board[c_x, c_y] not in captured_pieces:
                                    captured_pieces.append(self._board[c_x, c_y])  # Check if any pieces are captured (Should only be 1 max)

                                self._board[c_x, c_y] = controlled_by  # Update the captured squares to represent control by a player
                        
                            return captured_pieces
        
        return False  # Returns False if no pieces are captured 
        
    def _get_adjacent_squares(self, x,y):
        """
        Gets all adjacent squares

        param x : x coordinate to be checked around
        param y : y coordinate to be checked around

        return : all adjacent squares in every direction (including diagonals)
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

        param player_sign : positive/negative numbers associated with each players pieces (1 for p1 or -1 for p2)
        param x : x coordinate to be checked
        param y : y coordinate to be checked

        return : either False (not surrounded) or a list of the surrounded squares
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

            """
            opponent_control_count = self._p2_controlled if player_sign == 1 else self._p1_controlled  # number of squares controlled by opponent (unreachable)
            if len(visited) > self._total_squares/2 - opponent_control_count: 
                # If an area is able to be reached by half the reachable board, it cannot be captured
                # This logic ensures only small areas can be captured
                return False
            """
            
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

    def update(self, target_squares, player, piece_num):
        """
        Used to place pieces on the board, subsequently updates the board state

        param target_squares : squares to updated
        param player : the player number (1 or 2)
        param piece_num : the piece number (1-10)

        return : any pieces that have been captured
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

    def _check_if_legal_move(self, target_squares, player):
        """
        Checks if a proposed move is legal

        param target_squares : squares to updated
        param player : the player number (1 or 2)

        return : True if legal, otherwise False
        """

        valid_squares = 'r' if player == 1 else 'b'
        for target in target_squares:
            if self._board[target[0], target[1]] != 0 and self._board[target[0], target[1]] != valid_squares:
                return False
        return True
    
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

        param player : the player number (1 or 2)
        
        return : True if a legal move is found, otherwise False
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

        param player : the player number (1 or 2)
        param piece_counts : list of piece counts for that player (needs to be atleast 1 to be able to place the piece)
        
        return : a list of all legal moves for each piece for the given player
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

        param player : the player number (1 or 2)
        param piece_number : the piece number (1-11)
        
        return : all potential moves for a given piece
        """

        pieces = p.red_pieces if player == 1 else p.black_pieces
        if piece_number == 'c':
            rotations = p.cathedral[2]
        else:
            rotations = pieces[int(piece_number)-1][2] # Get all possible rotations of the given piece
        
        potential_moves = [] # Intialize the potential moves list
        
        for potential_shape in rotations:
            for move in self.find_potential_moves_for_given_shape(potential_shape, player):
                # For each shape, get all of the potential moves and add it to the list
                potential_moves.append(move)

        #print("Potential Moves for piece #:" + str(piece_number) + str(potential_moves))
        return potential_moves
            
    def find_potential_moves_for_given_shape(self, piece_shape, player):
        """
        Scans the board to final all potential moves for a given piece shape

        param piece_shape : the shape to checked for
        param player : the player number (1 or 2)

        return : a list of all valid placements of that shape
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
        player_num :
        pieces : gets all player pieces
        score : the player score (lower score is better)
        has_cathedral : T/F, if player has cathedral or not
        """

        self.player_num = player_num
        self.pieces = p.red_pieces if player_num == 1 else p.black_pieces
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
        """

        counts = []
        for piece in self.pieces:
            counts.append(piece[1])
        
        return counts
    
    def return_pieces(self, piece):
        """
        Increments a players piece count if a piece is captured by the other player

        piece : the piece to be returned
        """

        if piece == 'c':
            self.has_cathedral = True
        else:
            piece = abs(piece)
            self.pieces[int(piece)-1][1] += 1

    def can_place_cathedral(self):
        """
        Returns whether or not the current player can place the cathedral
        """

        return self.has_cathedral

    


