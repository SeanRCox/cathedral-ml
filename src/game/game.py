from board import Board, Player
import random

class Game:
    """
    Handles the game board and the two players
    """

    def __init__(self, modified_rules=None):
        """
        Initializes the game
        """

        self.game_board = Board()
        self.red_player = Player(1, modified_rules)
        self.black_player = Player(2, modified_rules)
        self.winner = None
                
    def game_over(self):
        """
        Determines whether the game is ended or not and returns a winner

        returns : winner if there is a winner, otherwise False
        """

        # Check if either player has legal moves
        red_has_moves = self.game_board.check_if_any_legal_moves(1, self.red_player.get_piece_counts(), self.red_player.can_place_cathedral()) 
        black_has_moves = self.game_board.check_if_any_legal_moves(2, self.black_player.get_piece_counts(), self.black_player.can_place_cathedral())
        #print(f"Legal Moves: {self.game_board.find_all_legal_moves(1, self.red_player.get_piece_counts(), self.red_player.can_place_cathedral)}")

        # If both players have no legal moves, game is over
        if not red_has_moves and not black_has_moves:
            if self.red_player.score < self.black_player.score:
                self.winner = 1
            elif self.red_player.score > self.black_player.score:
                self.winner = -1
            else:  
                self.winner = 0
            
            #print("Game is Over")
            return True

        # Check if either player has 0 score (played all their pieces)
        if self.red_player.score == 0:
            self.winner = 1
            return True
        elif self.black_player.score == 0:
            self.winner = -1
            return True
        
        return False

    def get_potential_moves(self, player, cathedral_turn=None):
        """
        find all potential moves for a player
        """
        return self.game_board.find_all_legal_moves(player.player_num, player.get_piece_counts(), player.can_place_cathedral(), cathedral_turn)

    def has_potential_moves(self, player):
        """
        find if any potential moves for a player
        """
        return self.game_board.check_if_any_legal_moves(player.player_num, player.get_piece_counts(), player.can_place_cathedral())
    
    def use_piece(self, player, piece_selected):
        """
        use a piece for a player
        """
        if player == 1:
            self.red_player.use_piece(piece_selected)
        else: 
            self.black_player.use_piece(piece_selected)

    def return_piece(self, player, returned_piece):
        if player == 1: 
            self.black_player.return_pieces(returned_piece)
        else: 
            self.red_player.return_pieces(returned_piece)


        