from bitboard_utility import *
from magic_bitboards import MagicBitboards

class MoveGenerator:
    def __init__(self, bitboards):
        self.bb = bitboards
        self.magic = MagicBitboards()
        self.moves = []

    def generate_all_moves(self, color):
        self.moves.clear()
        self.generate_rook_moves(color)
        self.generate_bishop_moves(color)
        self.generate_queen_moves(color)
        self.generate_knight_moves(color)
        self.generate_king_moves(color)
        self.generate_pawn_moves(color)
        return self.moves

    def add_moves(self, from_square, target_bb):
        while target_bb:
            to_square, target_bb = pop_lsb(target_bb)
            self.moves.append((from_square, to_square))

    def generate_rook_moves(self, color):
        occupied = self.bb.get_occupied()
        rooks = self.bb.bitboards[color + 'R']
        own_pieces = self.bb.get_color_occupied(color)
        while rooks:
            sq, rooks = pop_lsb(rooks)
            attacks = self.get_rook_attacks(sq, occupied) & ~own_pieces
            self.add_moves(sq, attacks)

    def generate_bishop_moves(self, color):
        occupied = self.bb.get_occupied()
        bishops = self.bb.bitboards[color + 'B']
        own_pieces = self.bb.get_color_occupied(color)
        while bishops:
            sq, bishops = pop_lsb(bishops)
            attacks = self.get_bishop_attacks(sq, occupied) & ~own_pieces
            self.add_moves(sq, attacks)

    def generate_queen_moves(self, color):
        self.generate_rook_moves(color)
        self.generate_bishop_moves(color)

    def generate_knight_moves(self, color):
        knights = self.bb.bitboards[color + 'N']
        own_pieces = self.bb.get_color_occupied(color)
        while knights:
            sq, knights = pop_lsb(knights)
            attacks = self.knight_attack_mask(sq) & ~own_pieces
            self.add_moves(sq, attacks)

    def generate_king_moves(self, color):
        kings = self.bb.bitboards[color + 'K']
        own_pieces = self.bb.get_color_occupied(color)
        while kings:
            sq, kings = pop_lsb(kings)
            attacks = self.king_attack_mask(sq) & ~own_pieces
            self.add_moves(sq, attacks)

    def generate_pawn_moves(self, color):
        own_pawns = self.bb.bitboards[color + 'P']
        empty = ~self.bb.get_occupied() & 0xFFFFFFFFFFFFFFFF
        enemy = self.bb.get_color_occupied('b' if color == 'w' else 'w')

        if color == 'w':
            single_push = shift_north(own_pawns) & empty
            double_push = shift_north(single_push & 0x0000000000FF0000) & empty
            left_captures = shift_northwest(own_pawns) & enemy
            right_captures = shift_northeast(own_pawns) & enemy
        else:
            single_push = shift_south(own_pawns) & empty
            double_push = shift_south(single_push & 0x0000FF0000000000) & empty
            left_captures = shift_southwest(own_pawns) & enemy
            right_captures = shift_southeast(own_pawns) & enemy

        self.add_pawn_moves(own_pawns, single_push, direction='N' if color == 'w' else 'S')
        self.add_pawn_moves(own_pawns, double_push, direction='N' if color == 'w' else 'S', double=True)
        self.add_pawn_captures(own_pawns, left_captures, 'left', color)
        self.add_pawn_captures(own_pawns, right_captures, 'right', color)

    def add_pawn_moves(self, pawns, targets, direction='N', double=False):
        while targets:
            to_sq, targets = pop_lsb(targets)
            if direction == 'N':
                from_sq = to_sq - (16 if double else 8)
            else:
                from_sq = to_sq + (16 if double else 8)
            self.moves.append((from_sq, to_sq))

    def add_pawn_captures(self, pawns, captures, side, color):
        while captures:
            to_sq, captures = pop_lsb(captures)
            if color == 'w':
                from_sq = to_sq - 7 if side == 'left' else to_sq - 9
            else:
                from_sq = to_sq + 9 if side == 'left' else to_sq + 7
            self.moves.append((from_sq, to_sq))

    def get_rook_attacks(self, square, blockers):
        return self.magic.get_rook_attacks(square, blockers)
        attacks = 0
        rank, file = divmod(square, 8)
        for r in range(rank + 1, 8):
            sq = r * 8 + file
            attacks |= 1 << sq
            if (blockers >> sq) & 1:
                break
        for r in range(rank - 1, -1, -1):
            sq = r * 8 + file
            attacks |= 1 << sq
            if (blockers >> sq) & 1:
                break
        for f in range(file + 1, 8):
            sq = rank * 8 + f
            attacks |= 1 << sq
            if (blockers >> sq) & 1:
                break
        for f in range(file - 1, -1, -1):
            sq = rank * 8 + f
            attacks |= 1 << sq
            if (blockers >> sq) & 1:
                break
        return attacks

    def get_bishop_attacks(self, square, blockers):
        return self.magic.get_bishop_attacks(square, blockers)
        attacks = 0
        rank, file = divmod(square, 8)
        r, f = rank + 1, file + 1
        while r < 8 and f < 8:
            sq = r * 8 + f
            attacks |= 1 << sq
            if (blockers >> sq) & 1: break
            r += 1; f += 1
        r, f = rank - 1, file - 1
        while r >= 0 and f >= 0:
            sq = r * 8 + f
            attacks |= 1 << sq
            if (blockers >> sq) & 1: break
            r -= 1; f -= 1
        r, f = rank - 1, file + 1
        while r >= 0 and f < 8:
            sq = r * 8 + f
            attacks |= 1 << sq
            if (blockers >> sq) & 1: break
            r -= 1; f += 1
        r, f = rank + 1, file - 1
        while r < 8 and f >= 0:
            sq = r * 8 + f
            attacks |= 1 << sq
            if (blockers >> sq) & 1: break
            r += 1; f -= 1
        return attacks

    def knight_attack_mask(self, square):
        rank, file = divmod(square, 8)
        moves = [(-2, -1), (-1, -2), (-2, 1), (-1, 2), (1, -2), (2, -1), (1, 2), (2, 1)]
        result = 0
        for dr, df in moves:
            r, f = rank + dr, file + df
            if 0 <= r < 8 and 0 <= f < 8:
                result |= 1 << (r * 8 + f)
        return result

    def king_attack_mask(self, square):
        rank, file = divmod(square, 8)
        moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        result = 0
        for dr, df in moves:
            r, f = rank + dr, file + df
            if 0 <= r < 8 and 0 <= f < 8:
                result |= 1 << (r * 8 + f)
        return result