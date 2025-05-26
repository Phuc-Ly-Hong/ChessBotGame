from bitboard_utility import *

class MagicBitboards:
    def __init__(self):
        self.rook_masks = [0] * 64
        self.bishop_masks = [0] * 64
        self.init_rook_masks()
        self.init_bishop_masks()



    def get_rook_attacks(self, square, blockers):
        attacks = 0
        rank, file = divmod(square, 8)
        # Up
        for r in range(rank + 1, 8):
            sq = r * 8 + file
            attacks |= 1 << sq
            if (blockers >> sq) & 1:
                break
        # Down
        for r in range(rank - 1, -1, -1):
            sq = r * 8 + file
            attacks |= 1 << sq
            if (blockers >> sq) & 1:
                break
        # Right
        for f in range(file + 1, 8):
            sq = rank * 8 + f
            attacks |= 1 << sq
            if (blockers >> sq) & 1:
                break
        # Left
        for f in range(file - 1, -1, -1):
            sq = rank * 8 + f
            attacks |= 1 << sq
            if (blockers >> sq) & 1:
                break
        return attacks

    def get_bishop_attacks(self, square, blockers):
        attacks = 0
        rank, file = divmod(square, 8)
        # ↗
        r, f = rank + 1, file + 1
        while r < 8 and f < 8:
            sq = r * 8 + f
            attacks |= 1 << sq
            if (blockers >> sq) & 1:
                break
            r += 1
            f += 1
        # ↖
        r, f = rank + 1, file - 1
        while r < 8 and f >= 0:
            sq = r * 8 + f
            attacks |= 1 << sq
            if (blockers >> sq) & 1:
                break
            r += 1
            f -= 1
        # ↙
        r, f = rank - 1, file - 1
        while r >= 0 and f >= 0:
            sq = r * 8 + f
            attacks |= 1 << sq
            if (blockers >> sq) & 1:
                break
            r -= 1
            f -= 1
        # ↘
        r, f = rank - 1, file + 1
        while r >= 0 and f < 8:
            sq = r * 8 + f
            attacks |= 1 << sq
            if (blockers >> sq) & 1:
                break
            r -= 1
            f += 1
        return attacks
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