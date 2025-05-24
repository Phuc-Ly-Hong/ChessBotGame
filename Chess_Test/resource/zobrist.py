import random

class ZobristHasher:
    def __init__(self):
        self.piece_keys = {}
        self.castling_keys = {}
        self.en_passant_keys = [random.getrandbits(64) for _ in range(8)]
        self.side_key = random.getrandbits(64)
        self.init_random_keys()

    def init_random_keys(self):
        pieces = ['P', 'N', 'B', 'R', 'Q', 'K']
        colors = ['w', 'b']
        for color in colors:
            for piece in pieces:
                for square in range(64):
                    self.piece_keys[(color + piece, square)] = random.getrandbits(64)

        for right in ['K', 'Q', 'k', 'q']:
            self.castling_keys[right] = random.getrandbits(64)

    def hash_board(self, board, side_to_move, castling_rights, en_passant_file):
        h = 0
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece:
                    square = (7 - rank) * 8 + file
                    h ^= self.piece_keys.get((piece, square), 0)

        for right in castling_rights:
            h ^= self.castling_keys.get(right, 0)

        if en_passant_file is not None:
            h ^= self.en_passant_keys[en_passant_file]

        if side_to_move == 'w':
            h ^= self.side_key

        return h
