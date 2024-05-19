from board import Board, Player
from pieces import piece_names

class Game:
    """
    handles the board and players
    """
    def __init__(self):
        self.game_board = Board()
        self.red_player = Player(1)
        self.black_player = Player(2)

    def start_game(self):
        print("Starting Board:")
        print("_"*40)
        self.game_board.print_board()
        print("_"*40)
        turn = 1 #Player 1's turn
        while(1):
            print(f"Player {turn}, which piece would you like to place? (Enter Number)")
            for n, p in enumerate(piece_names):
                print(f"{n+1}: {p}")
            piece = input()

            rotations = self.red_player.get_piece(piece) if turn == 1 else self.black_player.get_piece(piece)
            if len(rotations) > 1:
                print("Which rotation would you like to use? (Enter Number)")
                for m, r in enumerate(rotations):
                    print(f"{m+1}: {r}")
                rotation_choice = input()
                shape_selected = rotations[int(rotation_choice)-1]
            else:
                shape_selected = rotations[0]

            print("Possible Submatricies: ")
            potential_locations = self.game_board.find_potential_moves_for_given_shape(shape_selected, turn)

            print("Where would you like to place this piece?")
            for k, c in enumerate(potential_locations):
                print(f"{k+1}: {c}")
            user_input = input()
            location_selected = potential_locations[int(user_input)-1]

            self.game_board.update(location_selected, turn, piece)
            print("Updated Board:")
            self.game_board.print_board()
            
            if turn == 1: turn = 2
            else: turn = 1


G = Game()
G.start_game()
#G.game_board.print_board()
#manor_rotations = G.red_player.get_piece(5)
#manor = manor_rotations[0]
#target = [(0,1), (1,0), (1,1), (1,2)]
#G.game_board.update(manor, target, 1)
#print("After Placing Piece:")
#G.game_board.print_board()



        