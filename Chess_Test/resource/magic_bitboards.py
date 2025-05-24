from bitboard_utility import *

class MagicBitboards:
    def __init__(self):
        self.rook_masks = [0] * 64
        self.bishop_masks = [0] * 64
        self.init_rook_masks()
        self.init_bishop_masks()

    def init_rook_masks(self):
        for square in range(64):
            self.rook_masks[square] = self.get_rook_mask(square)

    def init_bishop_masks(self):
        for square in range(64):
            self.bishop_masks[square] = self.get_bishop_mask(square)

    def get_rook_mask(self, square):
        mask = 0
        rank, file = divmod(square, 8)

        for r in range(rank + 1, 7):
            mask |= 1 << (r * 8 + file)
        for r in range(rank - 1, 0, -1):
            mask |= 1 << (r * 8 + file)
        for f in range(file + 1, 7):
            mask |= 1 << (rank * 8 + f)
        for f in range(file - 1, 0, -1):
            mask |= 1 << (rank * 8 + f)

        return mask

    def get_bishop_mask(self, square):
        mask = 0
        rank, file = divmod(square, 8)

        # Diagonal ↘ and ↖
        r, f = rank + 1, file + 1
        while r <= 6 and f <= 6:
            mask |= 1 << (r * 8 + f)
            r += 1
            f += 1

        r, f = rank - 1, file - 1
        while r >= 1 and f >= 1:
            mask |= 1 << (r * 8 + f)
            r -= 1
            f -= 1

        # Anti-diagonal ↙ and ↗
        r, f = rank + 1, file - 1
        while r <= 6 and f >= 1:
            mask |= 1 << (r * 8 + f)
            r += 1
            f -= 1

        r, f = rank - 1, file + 1
        while r >= 1 and f <= 6:
            mask |= 1 << (r * 8 + f)
            r -= 1
            f += 1

        return mask