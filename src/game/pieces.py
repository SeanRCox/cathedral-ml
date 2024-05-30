import numpy as np

class Piece:
    """
    Creates the board pieces
    """
    def __init__(self, p_num, p_value, p_count, p_shape, player):
        """
        param p_value: value of the piece
        param p_num: number (1-9) that identifies the piece on the board
        param p_count: amount of that piece the player starts with
        param p_shape: 2d array of the pieces base shape
        param player = player number (1/-1)

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
        """

        return np.array([list(reversed(col)) for col in zip(*self._piece_shape)])
    
    def _rotate_180(self):
        """ 
        Rotate the matrix 180 degrees. 
        """

        return np.array([list(reversed(row)) for row in reversed(self._piece_shape)])

    def _rotate_counterclockwise(self):
        """ 
        Rotate the matrix counterclockwise 90 degrees. 
        """

        return np.array([list(col) for col in reversed(list(zip(*self._piece_shape)))])
    
    def get_piece(self):
        return[self._point_value, self._initial_count, self._rotations]
    
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

# Create Pieces for each player and the cathedral
red_pieces = [(Piece(piece_values[i][0], piece_values[i][1], piece_values[i][2], shape, 1).get_piece()) for i, shape in enumerate(piece_shapes)]
black_pieces = [(Piece(piece_values[i][0], piece_values[i][1], piece_values[i][2], shape, -1).get_piece()) for i, shape in enumerate(piece_shapes)]
cathedral = (Piece('c', 0, 1, cathedral_shape, 1).get_piece())



