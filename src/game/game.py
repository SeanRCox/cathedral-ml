"""
Manages the game state: the board and the two players
"""

from board import Board, Player


class Game:
    """
    Handles the game board and the two players
    """

    def __init__(self, modified_rules=None):
        """
        Initializes the game

        modified_rules : optional arg to specify if tree should be using modified ruleset
        """

        self.game_board = Board()
        self.red_player = Player(1, modified_rules)
        self.black_player = Player(2, modified_rules)
        self.winner = None
                
    def game_over(self):
        """
        Determines whether the game is ended or not and returns a winner

        return -> winner if there is a winner, otherwise False
        """

        # Check if either player has legal moves
        red_has_moves = self.game_board.check_if_any_legal_moves(1, self.red_player.get_piece_counts(), self.red_player.can_place_cathedral()) 
        black_has_moves = self.game_board.check_if_any_legal_moves(2, self.black_player.get_piece_counts(), self.black_player.can_place_cathedral())

        # If both players have no legal moves, game is over
        if not red_has_moves and not black_has_moves:
            if self.red_player.score < self.black_player.score:
                self.winner = 1
            elif self.red_player.score > self.black_player.score:
                self.winner = -1
            else:  
                self.winner = 0
            
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
        Find all potential moves for a player

        player : the player to get the moves of
        cathedral_turn : boolean, is it the turn to place the cathedral

        return -> list of all potential moves
        """

        return self.game_board.find_all_legal_moves(player.player_num, player.get_piece_counts(), player.can_place_cathedral(), cathedral_turn=cathedral_turn)

    def has_potential_moves(self, player):
        """
        Find if any potential moves for a player

        player : the player to get the moves of

        return -> boolean, if any potential moves
        """

        return self.game_board.check_if_any_legal_moves(player.player_num, player.get_piece_counts(), player.can_place_cathedral())
    
    def use_piece(self, player, piece_selected):
        """
        Use a piece for a player

        player : the player to use the piece
        piece_selected : the piece to use

        return -> None
        """

        if player == 1:
            self.red_player.use_piece(piece_selected)
        else: 
            self.black_player.use_piece(piece_selected)

    def return_piece(self, player, returned_piece):
        """
        return a piece back to the opposing player

        player : returning the piece to opposite player
        returned_piece : the piece to return

        return -> None
        """

        if player == 1: 
            self.black_player.return_pieces(returned_piece)
        else: 
            self.red_player.return_pieces(returned_piece)


        