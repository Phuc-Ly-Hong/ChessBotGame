class MoveGenerator:
    def __init__(self, board):
        self.board = board
        self.is_white_turn = True  # Default value, updated by ChessBot
        self.castling_rights = ''
        self.last_move = None
        # Initialize any move generation data (e.g., bitboards or lookup tables)
        self.move_data = {}  # Placeholder for move generation data

    def init_move_generation(self):
        """Initialize move generation state."""
        # Use self.is_white_turn instead of self.board.is_white_turn
        self.is_white_to_move = self.is_white_turn
        # Additional initialization (e.g., update bitboards or move tables)
        # For now, we assume this is minimal since we're using a 2D list
        self.move_data.clear()  # Reset any cached move data

    def generate_moves(self):
        """Generate all valid moves for the current player."""
        self.init_move_generation()
        moves = []
        color = 'w' if self.is_white_to_move else 'b'
        
        # Iterate over the 8x8 board
        for rank in range(8):
            for file in range(8):
                piece = self.board[rank][file]
                if piece and piece[0] == color:
                    piece_moves = self.get_piece_moves(file, rank, piece)
                    for move in piece_moves:
                        start_square = rank * 8 + file
                        end_square = move[1] * 8 + move[0]
                        moves.append((start_square, end_square))
        
        return moves

    def get_piece_moves(self, file, rank, piece):
        """Generate moves for a specific piece at (file, rank)."""
        moves = []
        piece_type = piece[1]
        color = piece[0]
        
        if piece_type == 'P':  # Pawn
            moves.extend(self.get_pawn_moves(file, rank, color))
        elif piece_type == 'N':  # Knight
            moves.extend(self.get_knight_moves(file, rank))
        elif piece_type == 'B':  # Bishop
            moves.extend(self.get_bishop_moves(file, rank))
        elif piece_type == 'R':  # Rook
            moves.extend(self.get_rook_moves(file, rank))
        elif piece_type == 'Q':  # Queen
            moves.extend(self.get_queen_moves(file, rank))
        elif piece_type == 'K':  # King
            moves.extend(self.get_king_moves(file, rank))
        
        return moves

    def get_pawn_moves(self, file, rank, color):
        moves = []
        direction = -1 if color == 'w' else 1
        start_rank = 6 if color == 'w' else 1
        
        # Move one square forward
        new_rank = rank + direction
        if 0 <= new_rank < 8 and self.board[new_rank][file] == '':
            moves.append((file, new_rank))
            
            # Move two squares from starting rank
            if rank == start_rank:
                new_rank2 = rank + 2 * direction
                if self.board[new_rank2][file] == '' and self.board[new_rank][file] == '':
                    moves.append((file, new_rank2))
        
        # Capture diagonally
        for df in [-1, 1]:
            new_file = file + df
            if 0 <= new_file < 8 and 0 <= new_rank < 8:
                target = self.board[new_rank][new_file]
                if target and target[0] != color:
                    moves.append((new_file, new_rank))
        
        # En passant
        if self.last_move and len(self.last_move) == 2:
            (start_file, start_rank), (end_file, end_rank) = self.last_move
            if abs(start_rank - end_rank) == 2 and self.board[end_rank][end_file][1] == 'P':
                ep_rank = rank
                ep_file = end_file
                if abs(file - ep_file) == 1 and (rank == 3 and color == 'w' or rank == 4 and color == 'b'):
                    moves.append((ep_file, rank + direction))
        
        return moves

    def get_knight_moves(self, file, rank):
        moves = []
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for df, dr in knight_moves:
            new_file, new_rank = file + df, rank + dr
            if 0 <= new_file < 8 and 0 <= new_rank < 8:
                target = self.board[new_rank][new_file]
                if not target or target[0] != self.board[rank][file][0]:
                    moves.append((new_file, new_rank))
        return moves

    def get_bishop_moves(self, file, rank):
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for df, dr in directions:
            for i in range(1, 8):
                new_file, new_rank = file + i * df, rank + i * dr
                if not (0 <= new_file < 8 and 0 <= new_rank < 8):
                    break
                target = self.board[new_rank][new_file]
                if not target:
                    moves.append((new_file, new_rank))
                elif target[0] != self.board[rank][file][0]:
                    moves.append((new_file, new_rank))
                    break
                else:
                    break
        return moves

    def get_rook_moves(self, file, rank):
        moves = []
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for df, dr in directions:
            for i in range(1, 8):
                new_file, new_rank = file + i * df, rank + i * dr
                if not (0 <= new_file < 8 and 0 <= new_rank < 8):
                    break
                target = self.board[new_rank][new_file]
                if not target:
                    moves.append((new_file, new_rank))
                elif target[0] != self.board[rank][file][0]:
                    moves.append((new_file, new_rank))
                    break
                else:
                    break
        return moves

    def get_queen_moves(self, file, rank):
        moves = []
        moves.extend(self.get_bishop_moves(file, rank))
        moves.extend(self.get_rook_moves(file, rank))
        return moves

    def get_king_moves(self, file, rank):
        moves = []
        king_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for df, dr in king_moves:
            new_file, new_rank = file + df, rank + dr
            if 0 <= new_file < 8 and 0 <= new_rank < 8:
                target = self.board[new_rank][new_file]
                if not target or target[0] != self.board[rank][file][0]:
                    moves.append((new_file, new_rank))
        
        # Castling
        if self.board[rank][file][1] == 'K':
            if self.is_white_to_move and 'K' in self.castling_rights and self.board[7][5] == '' and self.board[7][6] == '':
                moves.append((6, 7))  # Kingside castling (white)
            if self.is_white_to_move and 'Q' in self.castling_rights and self.board[7][3] == '' and self.board[7][2] == '' and self.board[7][1] == '':
                moves.append((2, 7))  # Queenside castling (white)
            if not self.is_white_to_move and 'k' in self.castling_rights and self.board[0][5] == '' and self.board[0][6] == '':
                moves.append((6, 0))  # Kingside castling (black)
            if not self.is_white_to_move and 'q' in self.castling_rights and self.board[0][3] == '' and self.board[0][2] == '' and self.board[0][1] == '':
                moves.append((2, 0))  # Queenside castling (black)
        
        return moves