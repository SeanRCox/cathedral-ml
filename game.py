from board import Board, Player
from pieces import piece_names
import random

class Game:
    """
    Handles the game board and the two players
    """

    def __init__(self):
        """
        Initializes the game
        """

        self.game_board = Board()
        self.red_player = Player(1)
        self.black_player = Player(2)

    def simulate_game(self):
        """
        Simulated version of the game with random moves
        """

        turn = 1  # Start with player 1's turn
        potential_locations = self.game_board.find_potential_moves_for_given_piece('c', turn)  # Player 1 places the cathedral
        self.game_board.update(random.choice(potential_locations), turn, 'c')  #Put the cathedral on the board 
        
        piece_count = self.red_player.get_piece_counts()  # We need to know the piece count to know if moves are valid, start with p1's count
        while not self.game_over():
            if self.game_board.check_if_any_legal_moves(turn, piece_count):  # Check if there are any legal moves for the current player
                potential_pieces = []
                for n in range(0, 10): # 11 possible pieces
                    if piece_count[n] > 0:  # If player has that piece
                        if len(self.game_board.find_potential_moves_for_given_piece(n+1, turn)) > 0:  # If theres a valid spot for that piece
                            potential_pieces.append(n+1)
                
                random_piece_picked = random.choice(potential_pieces)  # Pick random piece from possible choices
                if turn == 1:
                    self.red_player.use_piece(random_piece_picked)
                else: 
                    self.black_player.use_piece(random_piece_picked)

                # Get a list of all potential locations for the selected piece
                potential_locations = self.game_board.find_potential_moves_for_given_piece(random_piece_picked, turn)
                # Place the piece on the board
                returned_pieces = self.game_board.update(random.choice(potential_locations), turn, random_piece_picked)
                if returned_pieces:  # If any pieces were captured, return them to the opposing player
                    if turn == 1: self.black_player.return_pieces(returned_pieces[0])
                    else: self.red_player.return_pieces(returned_pieces[0])
                
                #print("_"*40)
                #self.game_board.print_board()

            if turn == 1: 
                piece_count = self.black_player.get_piece_counts()
                turn = 2
            else: 
                piece_count = self.red_player.get_piece_counts()
                turn = 1
                
    def game_over(self):
        """
        Determines whether the game is ended or not and returns a winner

        returns : winner if there is a winner, otherwise False
        """

        # Check if either player has legal moves
        red_has_moves = self.game_board.check_if_any_legal_moves(1, self.red_player.get_piece_counts()) 
        #print("Red Possible Moves:" + str(len(self.game_board.find_all_legal_moves(1, self.red_player.get_piece_counts()))))
        #print((self.game_board.find_all_legal_moves(1, self.red_player.get_piece_counts())))
        black_has_moves = self.game_board.check_if_any_legal_moves(2, self.black_player.get_piece_counts())
        #print("Black Possible Moves:" + str(len(self.game_board.find_all_legal_moves(1, self.black_player.get_piece_counts()))))
        #print((self.game_board.find_all_legal_moves(1, self.black_player.get_piece_counts())))
        # If both players have no legal moves, game is over
        if not red_has_moves and not black_has_moves:
            #print(f"Red Score: {self.red_player.score}, Black Score: {self.black_player.score}")
            if self.red_player.score < self.black_player.score:
                print("Red Wins")
                return True
            elif self.red_player.score > self.black_player.score:
                print("Black Wins")
                return True
            else:  
                print("Tie")
                return True

        # Check if either player has 0 score (played all their pieces)
        if self.red_player.score == 0:
            print("Red Wins")
            return True
        if self.black_player.score == 0:
            print("Black Wins")
            return True
        
        return False

G = Game()
G.simulate_game()



        