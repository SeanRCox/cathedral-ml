import numpy as np

class Piece:
    def __init__(self, p_num, p_value, p_count, p_shape, player):
        """
        p_value: value of the piece
        p_num: number (1-9) that identifies the piece on the board
        p_count: amount of that piece the player starts with
        p_shape: 2d array of the pieces base shape
        player = player number (1/-1)
        """
        self.point_value = p_value
        self.piece_shape = np.where(p_shape == 1, p_num*player, p_shape)
        self.initial_count = p_count
        self.rotations = []
        self.rotations.append(self.piece_shape)

        potential_rotations = []
        potential_rotations.append(rotate_180(self.piece_shape))
        potential_rotations.append(rotate_clockwise(self.piece_shape))
        potential_rotations.append(rotate_counterclockwise(self.piece_shape))
        
        seen = set()
        unique_rotations = []
        for rotation in potential_rotations:
            # Use a tuple representation to hash the array for checking duplicates
            rotation_tuple = tuple(map(tuple, rotation))
            if rotation_tuple not in seen:
                seen.add(rotation_tuple)
                unique_rotations.append(rotation)

        for shape in unique_rotations:
            if not np.array_equal(shape, self.piece_shape):
                self.rotations.append(shape)

def get_piece(piece):
    return[piece.point_value, piece.initial_count, piece.rotations]

def rotate_180(piece):
    """ Rotate the matrix 180 degrees. """
    return np.array([list(reversed(row)) for row in reversed(piece)])

def rotate_clockwise(piece):
    """ Rotate the matrix clockwise 90 degrees. """
    return np.array([list(reversed(col)) for col in zip(*piece)])

def rotate_counterclockwise(piece):
    """ Rotate the matrix counterclockwise 90 degrees. """
    return rotate_clockwise(rotate_clockwise(rotate_clockwise(piece)))

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

piece_names = ["Tavern", "Stable", "Inn", "Bridge", "Manor", "Square", "Abbey", "Infirmary", "Castle", "Tower", "Academy"]

piece_shapes = [tavern_shape, stable_shape, inn_shape, bridge_shape, manor_shape, square_shape, 
                abbey_shape, infirmary_shape, castle_shape, tower_shape, academy_shape]

piece_values = [(1, 1, 2), (2, 2, 2), (3, 3, 2), (4, 3, 1), (5, 4, 1), (6, 4, 1), #piece number, piece value, inital piece count
                (7, 4, 1), (8, 5, 1), (9, 5, 1), (10, 5, 1), (11, 5, 1)] 

red_pieces = [get_piece(Piece(piece_values[i][0], piece_values[i][1], piece_values[i][2], shape, 1)) for i, shape in enumerate(piece_shapes)]
black_pieces = [get_piece(Piece(piece_values[i][0], piece_values[i][1], piece_values[i][2], shape, -1)) for i, shape in enumerate(piece_shapes)]



