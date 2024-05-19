import numpy as np
import pieces as p

class Board: 
    """
    manages the board
    """
    def __init__(self):
        """
        board:
        0 - empty square
        positive # - player 1 piece (red)
        negative # - player 2 piece (black)
        r - player 1 control (red)
        b - player 2 control (black)
        c - cathedral (special square)
        """
        self._board_dimensions = 10 #10x10 board
        self._total_squares = self._board_dimensions * self._board_dimensions
        self._board = np.zeros([self._board_dimensions, self._board_dimensions], dtype=object)
        
        # number of squares controlled by each player
        self._p1_controlled = 0
        self._p2_controlled = 0 

    def _refresh_board_state(self, placed_piece, p_num):
        """
        Used after every player turn to update the board state
        returns any pieces that have been removed
        """
        for sq in placed_piece: # check all newly placed square
            #print("Checking Around Square:" + str(sq))
            checked = []
            nx, ny = sq[0], sq[1]
            #self._board[nx, ny] = p_num
            for adj_sq in self._get_adjacent_squares(nx, ny): # find all adjacent squares
                if adj_sq in checked:
                    continue # dont check squares that have already been checked
                else:
                    checked.append(adj_sq)
                    adj_x, adj_y = adj_sq[0], adj_sq[1]
                    if (self._board[adj_x, adj_y] == 'c') or (self._board[adj_x, adj_y] == 'b') or (self._board[adj_x, adj_y] == 'r'): 
                        continue
                    elif (int(self._board[adj_x, adj_y]) * p_num > 0):
                        continue
                    else:
                        captured_squares = self._check_if_surrounded(p_num*-1, adj_x, adj_y)
                        #print("Captured Squares:" + str(captured_squares))
                        if captured_squares:
                            #return all pieces
                            controlled_by = 'r' if p_num == 1 else 'b'
                            if p_num == 1:
                                self._p1_controlled += len(captured_squares) 
                            else: self._p2_controlled += len(captured_squares)
                            for c_sq in captured_squares:
                                c_x, c_y = c_sq[0], c_sq[1]
                                self._board[c_x, c_y] = controlled_by
        
    def _get_adjacent_squares(self, x,y):
            adj_squares = []

            for dx in range(-1 if (x > 0) else 0, 2 if (x < self._board_dimensions-1) else 1):
                for dy in range( -1 if (y > 0) else 0, 2 if (y < self._board_dimensions-1) else 1):
                    if (dx != 0 or dy != 0):
                        adj_squares.append((x+dx, y+dy))

            return adj_squares
    
    def _check_if_surrounded(self, p_num, x, y):
        piece_type_seen = []
        visited = [] # record which squares we've visited
        queue = [(x,y)]

        while queue:
            x, y = queue.pop(0)
            if (x, y) in visited:
                continue
            visited.append((x, y))

            if len(piece_type_seen) > 1:
                return False # cannot surround more then 1 piece

            opponent_control_count = self._p2_controlled if p_num == 1 else self._p1_controlled # number of squares controlled by opponent (unreachable)
            if len(visited) > self._total_squares/2 - opponent_control_count:
                return False
            
            for sq in self._get_adjacent_squares(x,y):
                nx, ny = sq[0], sq[1]
                if (self._board[nx, ny] == 'b') or (self._board[nx, ny] == 'r'):
                    continue 
                if (self._board[nx, ny] == 'c'): 
                    queue.append((nx, ny))
                    if 'c' not in piece_type_seen:
                        piece_type_seen.append('c')
                elif (int(self._board[nx, ny]) * p_num > 0):
                    queue.append((nx, ny))
                    if (self._board[nx, ny]) not in piece_type_seen:
                        piece_type_seen.append('c')
                elif (int(self._board[nx, ny]) == 0):
                    queue.append((nx, ny))

        return visited

    def update(self, target_squares, player, piece_num):
        """
        used to place pieces
        """
        sign = 1 if player == 1 else -1
        if self._check_if_legal_move(target_squares, player):
            for target in target_squares:
                self._board[target[0], target[1]] = int(piece_num) * sign
            self._refresh_board_state(target_squares, sign)
    
    def _check_if_legal_move(self, target_squares, player):
        valid_squares = 'r' if player == 1 else 'b'
        for target in target_squares:
            if self._board[target[0], target[1]] != 0 and self._board[target[0], target[1]] != valid_squares:
                return False
        return True
    
    def print_board(self):
        for row in self._board:
        # Create a formatted string for each row where each element is formatted to be 3 characters wide
            formatted_row = ' '.join(f'{str(item):>3}' for item in row)
            print(formatted_row)

    def check_if_any_legal_moves(self, all_potential_shapes):
        """
        Quicker version of find_all_legal_moves to be used to determine if game should end
        """
    
    def find_all_legal_moves(self, shape_list):
        pass
            
    def find_potential_moves_for_given_piece(self, all_potential_shapes, player, piece_number):
        potential_moves = [piece_number]
        
        for potential_shape in all_potential_shapes:
            potential_moves.append(self.find_potential_moves_for_given_shape(potential_shape, player))

        return potential_moves
            
    def find_potential_moves_for_given_shape(self, piece_shape, player):
        valid_player_squares = 'r' if player == 1 else 'b'
        submatricies = [] # All potential spots on the board that fit the given shape
        coordinates_to_potentially_update = []
        
        n, m = piece_shape.shape
        for i in range(self._board_dimensions - n + 1):
            for j in range(self._board_dimensions - m + 1):
                coords = [(x, y) for x in range(i, i + n) for y in range(j, j + m)]
                submatricies.append(coords)

        piece_values = piece_shape.flatten().tolist()

        for matrix in submatricies:
            coordinates_to_update = []
            valid = True
            for n, coords in enumerate(matrix):
                if piece_values[n] != 0:
                    if self._board[coords[0]][coords[1]] != 0 and self._board[coords[0]][coords[1]] != valid_player_squares:
                        valid = False
                    else:
                        coordinates_to_update.append((coords[0], coords[1]))
            if valid: coordinates_to_potentially_update.append(coordinates_to_update)

        return coordinates_to_potentially_update

class Player:
    def __init__(self, player_num):
        self.pieces = p.red_pieces if player_num == 1 else p.black_pieces
        self.score = 47 # starting score is sum of all pieces, goal is to get the lowest score
    
    def get_piece(self, piece):
        #if self.pieces[int(piece)-1][1] < 1: return False
        self.pieces[int(piece)-1][1] -= 1
        self.score -= self.pieces[int(piece)-1][1]
        return self.pieces[int(piece)-1][2]



    


