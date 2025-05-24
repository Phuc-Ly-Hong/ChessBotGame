PIECE_VALUES = {
    'P': 100, 'N': 300, 'B': 320, 'R': 500, 'Q': 900, 'K': 20000
}

PASSED_PAWN_BONUSES = [0, 120, 80, 50, 30, 15, 15]
PASSED_PAWN_BONUS = 50
BISHOP_PAIR_BONUS = 30
ISOLATED_PAWN_PENALTY_BY_COUNT = [0, -10, -25, -50, -75, -75, -75, -75, -75]
KING_PAWN_SHIELD_SCORES = [4, 7, 4, 3, 6, 3]
DEFENDED_PIECE_BONUS = 0.5
HANGING_PIECE_PENALTY = 1.0

POSITION_TABLES = {
    'P': [
         0,   0,   0,   0,   0,   0,   0,   0,
        50,  50,  50,  50,  50,  50,  50,  50,
        10,  10,  20,  30,  30,  20,  10,  10,
         5,   5,  10,  25,  25,  10,   5,   5,
         0,   0,   0,  20,  20,   0,   0,   0,
         5,  -5, -10,   0,   0, -10,  -5,   5,
         5,  10,  10, -20, -20,  10,  10,   5,
         0,   0,   0,   0,   0,   0,   0,   0
    ],
    'P_end': [
         0,   0,   0,   0,   0,   0,   0,   0,
        80,  80,  80,  80,  80,  80,  80,  80,
        50,  50,  50,  50,  50,  50,  50,  50,
        30,  30,  30,  30,  30,  30,  30,  30,
        20,  20,  20,  20,  20,  20,  20,  20,
        10,  10,  10,  10,  10,  10,  10,  10,
        10,  10,  10,  10,  10,  10,  10,  10,
         0,   0,   0,   0,   0,   0,   0,   0
    ],
    'R': [
         0,   0,   0,   0,   0,   0,   0,   0,
         5,  10,  10,  10,  10,  10,  10,   5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
         0,   0,   0,   5,   5,   0,   0,   0
    ],
    'N': [
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50
    ],
    'B': [
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-10,-10,-10,-10,-10,-20
    ],
    'Q': [
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5,  5,  5,  5,  0,-10,
         -5,  0,  5,  5,  5,  5,  0, -5,
          0,  0,  5,  5,  5,  5,  0, -5,
        -10,  5,  5,  5,  5,  5,  0,-10,
        -10,  0,  5,  0,  0,  0,  0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20
    ],
    'K_middle': [
        -80, -70, -70, -70, -70, -70, -70, -80,
        -60, -60, -60, -60, -60, -60, -60, -60,
        -40, -50, -50, -60, -60, -50, -50, -40,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -20, -30, -30, -40, -40, -30, -30, -20,
        -10, -20, -20, -20, -20, -20, -20, -10,
         20,  20,  -5,  -5,  -5,  -5,  20,  20,
         20,  30,  10,   0,   0,  10,  30,  20
    ],
    'K_end': [
        -20, -10, -10, -10, -10, -10, -10, -20,
         -5,   0,   5,   5,   5,   5,   0,  -5,
        -10,  -5,  20,  30,  30,  20,  -5, -10,
        -15, -10,  35,  45,  45,  35, -10, -15,
        -20, -15,  30,  40,  40,  30, -15, -20,
        -25, -20,  20,  25,  25,  20, -20, -25,
        -30, -25,   0,   0,   0,   0, -25, -30,
        -50, -30, -30, -30, -30, -30, -30, -50
    ]
}

class Evaluation:
    def __init__(self, move_validator):
        self.validator = move_validator
        self.phase_weights = {
            'opening': 0.5,
            'middlegame': 0.3,
            'endgame': 0.2
        }
        self.mobility_bonus = [0, 10, 30, 50, 70, 90, 110]

    def evaluate(self, board, color):
        phase = self.get_game_phase(board)

        material = self.material_score(board, color)
        positional = self.position_score(board, color, phase)
        mobility = self.mobility_score(board, color)
        pawn_structure = self.pawn_structure_score(board, color)
        king_safety = self.king_safety_score(board, color, phase)
        bishop_pair = self.bishop_pair_score(board, color)
        rook_open_file = self.rook_open_file_score(board, color)
        knight_outpost = self.knight_outpost_score(board, color)
        bishop_mobility = self.bishop_mobility_score(board, color)
        queen_safety = self.queen_safety_score(board, color, phase)

        total = (
            material * 0.30 +
            positional * 0.25 +
            mobility * 0.10 +
            pawn_structure * 0.10 +
            king_safety * 0.10 +
            bishop_pair * 0.05 +
            rook_open_file * 0.05 +
            knight_outpost * 0.05 +
            bishop_mobility * 0.025 +
            queen_safety * 0.025
        )
        opponent = 'b' if color == 'w' else 'w'
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece:
                    value = PIECE_VALUES[piece[1]]  # Sửa từ self.piece_values thành PIECE_VALUES
                    total += value if piece[0] == color else -value

        # Phạt nặng nếu vua di chuyển sớm
        king_pos = self.find_king(board, color)
        if king_pos:
            file, rank = king_pos
            if color == 'w' and rank != 7:  # Vua trắng không ở hàng 1
                total -= 300
            elif color == 'b' and rank != 0:  # Vua đen không ở hàng 8
                total -= 300

        # Thưởng cho việc nhập thành
        if self.has_castled(board, color):
            total += 200

        # Đánh giá kiểm soát trung tâm
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        for file, rank in center_squares:
            piece = board[rank][file]
            if piece and piece[0] == color:
                total += 20

        if phase == 'endgame':
            total += self.endgame_evaluation(board, color)

        return total

    def material_score(self, board, color):
        score = 0
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece:
                    val = PIECE_VALUES.get(piece[1], 0)
                    if piece[0] == color:
                        score += val
                    else:
                        score -= val
        return score

    def position_score(self, board, color, game_phase_str):
        score = 0
        phase_weight = 0.0
        if game_phase_str == 'opening':
            phase_weight = 0.0
        elif game_phase_str == 'middlegame':
            phase_weight = 0.5
        elif game_phase_str == 'endgame':
            phase_weight = 1.0

        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece and piece[0] == color:
                    idx = rank * 8 + file
                    if color == 'b':
                        idx = 63 - idx
                    ptype = piece[1]
                    if ptype == 'K':
                        score += (1 - phase_weight) * POSITION_TABLES['K_middle'][idx]
                        score += phase_weight * POSITION_TABLES['K_end'][idx]
                    elif ptype == 'P':
                        score += (1 - phase_weight) * POSITION_TABLES['P'][idx]
                        score += phase_weight * POSITION_TABLES['P_end'][idx]
                    elif ptype in POSITION_TABLES:
                        score += POSITION_TABLES[ptype][idx]
        return score

    def mobility_score(self, board, color):
        moves = 0
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece and piece[0] == color:
                    moves += len(self.validator.get_all_valid_moves((file, rank)))
        return moves

    def pawn_structure_score(self, board, color):
        pawns = []
        opponent_pawns = []
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece == color + 'P':
                    pawns.append((file, rank))
                elif piece and piece[0] != color and piece[1] == 'P':
                    opponent_pawns.append((file, rank))

        score = 0
        for file, rank in pawns:
            is_passed = True
            for delta in [-1, 0, 1]:
                check_file = file + delta
                if 0 <= check_file < 8:
                    for r in range(rank + 1, 8) if color == 'w' else range(rank - 1, -1, -1):
                        if any(p[0] == check_file and p[1] == r for p in opponent_pawns):
                            is_passed = False
                            break
                    if not is_passed:
                        break
            if is_passed:
                advance = rank if color == 'b' else 7 - rank
                score += PASSED_PAWN_BONUSES[min(advance, 6)]
                score += PASSED_PAWN_BONUS

            isolated = True
            for f in [file-1, file+1]:
                if 0 <= f < 8:
                    if any(p[0] == f for p in pawns if p[1] == rank):
                        isolated = False
                        break
            if isolated:
                score += ISOLATED_PAWN_PENALTY_BY_COUNT[len(pawns)]

            for r in range(8):
                if r != rank and (file, r) in pawns:
                    score -= 15
        return score

    def king_safety_score(self, board, color, game_phase):
        score = 0
        king_pos = None
        for rank in range(8):
            for file in range(8):
                if board[rank][file] == color + 'K':
                    king_pos = (file, rank)
                    break
            if king_pos:
                break
        
        if not king_pos:
            return 0
        
        in_check = self.validator.is_king_in_check(board, color)
        if in_check:
            score -= 150
        
        attacker_count = self.count_king_attackers(board, king_pos, color)
        score -= attacker_count * 40
        
        if game_phase == 'opening':
            score += self.evaluate_pawn_shield(board, king_pos, color)
        
        if self.is_king_exposed(board, king_pos, color):
            score -= 80
            
        return score

    def bishop_pair_score(self, board, color):
        bishops = []
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece == color + 'B':
                    square_color = (file + rank) % 2
                    bishops.append(square_color)
        
        if len(bishops) >= 2 and 0 in bishops and 1 in bishops:
            return BISHOP_PAIR_BONUS
        return 0

    def get_game_phase(self, board):
        total_material = sum(PIECE_VALUES.get(p[1], 0) for row in board for p in row if p)
        if total_material > 6200:
            return 'opening'
        elif total_material > 3000:
            return 'middlegame'
        else:
            return 'endgame'

    def endgame_evaluation(self, board, color):
        score = 0
        king_pos = self.find_king(board, color)
        opponent_king_pos = self.find_king(board, 'w' if color == 'b' else 'b')
        
        score -= self.king_centrality(king_pos) * 15
        score += self.king_centrality(opponent_king_pos) * 20
        
        score += self.count_passed_pawns(board, color) * 120
        
        return score

    def exchange_score(self, board, color, start_pos, end_pos):
        target_piece = board[end_pos[1]][end_pos[0]]
        if not target_piece:
            return 0
        score = PIECE_VALUES.get(target_piece[1], 0)
        temp_board = [row[:] for row in board]
        temp_board[end_pos[1]][end_pos[0]] = board[start_pos[1]][start_pos[0]]
        temp_board[start_pos[1]][start_pos[0]] = ''
        if self.is_piece_attacked(temp_board, end_pos, color):
            score -= PIECE_VALUES.get(board[start_pos[1]][start_pos[0]][1], 0)
        return score

    def rook_open_file_score(self, board, color):
        score = 0
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece == color + 'R':
                    open_file = True
                    for r in range(8):
                        if board[r][file] and board[r][file][1] == 'P':
                            open_file = False
                            break
                    if open_file:
                        score += 20
        return score

    def knight_outpost_score(self, board, color):
        score = 0
        opponent_color = 'w' if color == 'b' else 'b'
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece == color + 'N':
                    if (color == 'w' and rank in [2,3]) or (color == 'b' and rank in [4,5]):
                        can_be_attacked = False
                        if color == 'w' and rank > 0:
                            if file > 0 and board[rank-1][file-1] == opponent_color + 'P':
                                can_be_attacked = True
                            if file < 7 and board[rank-1][file+1] == opponent_color + 'P':
                                can_be_attacked = True
                        elif color == 'b' and rank < 7:
                            if file > 0 and board[rank+1][file-1] == opponent_color + 'P':
                                can_be_attacked = True
                            if file < 7 and board[rank+1][file+1] == opponent_color + 'P':
                                can_be_attacked = True
                        if not can_be_attacked:
                            supported = False
                            if color == 'w' and rank < 7:
                                if file > 0 and board[rank+1][file-1] == color + 'P':
                                    supported = True
                                if file < 7 and board[rank+1][file+1] == color + 'P':
                                    supported = True
                            elif color == 'b' and rank > 0:
                                if file > 0 and board[rank-1][file-1] == color + 'P':
                                    supported = True
                                if file < 7 and board[rank-1][file+1] == color + 'P':
                                    supported = True
                            if supported:
                                score += 25
        return score

    def bishop_mobility_score(self, board, color):
        score = 0
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece == color + 'B':
                    same_color_pawns = 0
                    for r in range(8):
                        for f in range(8):
                            if board[r][f] == color + 'P':
                                if (f + r) % 2 == (file + rank) % 2:
                                    same_color_pawns += 1
                    if same_color_pawns > 3:
                        score -= (same_color_pawns - 3) * 10
        return score

    def queen_safety_score(self, board, color, game_phase):
        if game_phase == 'opening':
            score = 0
            for rank in range(8):
                for file in range(8):
                    piece = board[rank][file]
                    if piece == color + 'Q':
                        if (color == 'w' and rank != 7) or (color == 'b' and rank != 0):
                            score -= 50
                        if self.is_piece_attacked(board, (file, rank), color):
                            score -= 100
            return score
        return 0

    def king_centrality(self, pos):
        file, rank = pos
        return abs(3.5 - file) + abs(3.5 - rank)
    
    def find_king(self, board, color):
        for rank in range(8):
            for file in range(8):
                if board[rank][file] == color + 'K':
                    return (file, rank)
        return None

    def count_passed_pawns(self, board, color):
        count = 0
        for rank in range(8):
            for file in range(8):
                if board[rank][file] == color + 'P':
                    if self.is_passed_pawn(board, (file, rank), color):
                        count += 1
        return count

    def is_passed_pawn(self, board, pos, color):
        file, rank = pos
        opponent_pawns = []
        for r in range(8):
            for f in range(8):
                piece = board[r][f]
                if piece and piece[0] != color and piece[1] == 'P':
                    opponent_pawns.append((f, r))
        
        is_passed = True
        for delta in [-1, 0, 1]:
            check_file = file + delta
            if 0 <= check_file < 8:
                for r in range(rank + 1, 8) if color == 'w' else range(rank - 1, -1, -1):
                    if any(p[0] == check_file and p[1] == r for p in opponent_pawns):
                        is_passed = False
                        break
                if not is_passed:
                    break
        return is_passed

    def count_king_attackers(self, board, king_pos, color):
        opponent_color = 'w' if color == 'b' else 'b'
        attackers = 0
        king_file, king_rank = king_pos
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece and piece[0] == opponent_color:
                    if (king_file, king_rank) in self.validator.get_all_valid_moves((file, rank)):
                        attackers += 1
        return attackers

    def evaluate_pawn_shield(self, board, king_pos, color):
        file, rank = king_pos
        shield_score = 0
        pawn_dir = 1 if color == 'w' else -1
        for f in [file-1, file, file+1]:
            if 0 <= f < 8:
                shield_rank = rank + pawn_dir
                if 0 <= shield_rank < 8:
                    if board[shield_rank][f] == color + 'P':
                        shield_score += 30
                    elif f == file:
                        shield_score -= 20
        return shield_score

    def is_king_exposed(self, board, king_pos, color):
        file, rank = king_pos
        open_file = True
        for r in range(8):
            if r != rank and board[r][file] == color + 'P':
                open_file = False
                break
        return open_file

    def piece_development_score(self, board, color, game_phase):
        if game_phase == 'endgame':
            return 0
        score = 0
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece and piece[0] == color:
                    if piece[1] in ['N', 'B']:
                        if (color == 'w' and rank < 7) or (color == 'b' and rank > 0):
                            score += 30
                    elif piece[1] == 'Q':
                        if (color == 'w' and rank < 7) or (color == 'b' and rank > 0):
                            score -= 30
        king_pos = self.find_king(board, color)
        if king_pos:
            file, rank = king_pos
            if (color == 'w' and rank == 7 and (file in [2, 6])) or \
               (color == 'b' and rank == 0 and (file in [2, 6])):
                score += 100
            if color == 'w' and rank == 7:
                if file == 4 and (board[7][5] == '' and board[7][6] == ''):
                    score += 50
                if file == 4 and (board[7][1] == '' and board[7][2] == '' and board[7][3] == ''):
                    score += 50
            elif color == 'b' and rank == 0:
                if file == 4 and (board[0][5] == '' and board[0][6] == ''):
                    score += 50
                if file == 4 and (board[0][1] == '' and board[0][2] == '' and board[0][3] == ''):
                    score += 50
        return score

    def piece_protection_score(self, board, color):
        score = 0
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece and piece[0] == color:
                    protected = self.is_piece_protected(board, (file, rank), color)
                    if protected:
                        score += 15
                    piece_value = PIECE_VALUES.get(piece[1], 0)
                    if piece_value > 300 and self.is_piece_attacked(board, (file, rank), color):
                        score -= piece_value // 2
                    if piece[1] == 'Q' and self.is_piece_attacked(board, (file, rank), color):
                        score -= 200
        return score

    def is_piece_protected(self, board, pos, color):
        file, rank = pos
        for r in range(8):
            for f in range(8):
                piece = board[r][f]
                if piece and piece[0] == color and piece[1] != 'K':
                    if (file, rank) in self.validator.get_all_valid_moves((f, r)):
                        return True
        return False

    def is_piece_attacked(self, board, pos, color):
        opponent_color = 'w' if color == 'b' else 'b'
        file, rank = pos
        for r in range(8):
            for f in range(8):
                piece = board[r][f]
                if piece and piece[0] == opponent_color:
                    if (file, rank) in self.validator.get_all_valid_moves((f, r)):
                        return True
        return False

    def center_control_score(self, board, color):
        center_squares = [(3,3), (3,4), (4,3), (4,4)]
        score = 0
        for file, rank in center_squares:
            piece = board[rank][file]
            if piece and piece[0] == color:
                score += 15
                if piece[1] == 'Q':
                    score += 30
            for r in range(8):
                for f in range(8):
                    piece = board[r][f]
                    if piece and piece[0] == color:
                        if (file, rank) in self.validator.get_all_valid_moves((f, r)):
                            score += 10
        return score

    def protect_valuable_pieces(self, board, color):
        important_types = ['Q', 'R', 'B', 'N']
        score = 0
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece and piece[0] == color and piece[1] in important_types:
                    pos = (file, rank)
                    under_attack = self.is_under_attack(board, pos, color)
                    if under_attack:
                        score -= PIECE_VALUES[piece[1]] * 0.5
                    defended = self.is_defended(board, pos, color)
                    if defended:
                        score += PIECE_VALUES[piece[1]] * 0.3
        return score

    def is_under_attack(self, board, pos, color):
        opp_color = 'b' if color == 'w' else 'w'
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece and piece[0] == opp_color:
                    if self.validator.is_direct_attack((file, rank), pos, board):
                        return True
        return False

    def is_defended(self, board, pos, color):
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece and piece[0] == color:
                    if self.validator.is_direct_attack((file, rank), pos, board):
                        return True
        return False

    def calculate_defended_pieces_score(self, board, color):
        score = 0
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece and piece[0] == color:
                    if self.is_piece_defended(board, (file, rank), color):
                        piece_value = PIECE_VALUES.get(piece[1], 0)
                        score += piece_value * DEFENDED_PIECE_BONUS
        return score

    def calculate_hanging_pieces_score(self, board, color):
        penalty = 0
        opponent_color = 'w' if color == 'b' else 'b'
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece and piece[0] == color:
                    if self.is_piece_hanging(board, (file, rank), color):
                        piece_value = PIECE_VALUES.get(piece[1], 0)
                        penalty += piece_value * HANGING_PIECE_PENALTY
        return penalty

    def is_piece_defended(self, board, pos, color):
        defenders = []
        for r in range(8):
            for f in range(8):
                piece = board[r][f]
                if piece and piece[0] == color and (f, r) != pos:
                    if pos in self.validator.get_all_valid_moves((f, r)):
                        defenders.append((f, r))
        defending_pieces = [board[d[1]][d[0]] for d in defenders if board[d[1]][d[0]]]
        return any(p[1] != 'K' for p in defending_pieces)

    def is_piece_hanging(self, board, pos, color):
        opponent_color = 'w' if color == 'b' else 'b'
        is_attacked = False
        for r in range(8):
            for f in range(8):
                piece = board[r][f]
                if piece and piece[0] == opponent_color:
                    if pos in self.validator.get_all_valid_moves((f, r)):
                        is_attacked = True
                        break
            if is_attacked:
                break
        if not is_attacked:
            return False
        is_defended = self.is_piece_defended(board, pos, color)
        attackers = []
        defenders = []
        target_value = PIECE_VALUES.get(board[pos[1]][pos[0]][1], 0) if board[pos[1]][pos[0]] else 0
        for r in range(8):
            for f in range(8):
                piece = board[r][f]
                if piece and piece[0] == opponent_color:
                    if pos in self.validator.get_all_valid_moves((f, r)):
                        attackers.append(PIECE_VALUES.get(piece[1], 0))
        for r in range(8):
            for f in range(8):
                piece = board[r][f]
                if piece and piece[0] == color and (f, r) != pos:
                    if pos in self.validator.get_all_valid_moves((f, r)):
                        defenders.append(PIECE_VALUES.get(piece[1], 0))
        defenders.append(target_value)
        attackers_sorted = sorted(attackers)
        defenders_sorted = sorted(defenders)
        if not attackers_sorted:
            return False
        return attackers_sorted[0] < defenders_sorted[0]

    def get_pawn_attackers(self, board, pos, color):
        attackers = 0
        opponent = 'w' if color == 'b' else 'b'
        x, y = pos
        pawn_dir = 1 if opponent == 'w' else -1
        attack_squares = [(x-1, y-pawn_dir), (x+1, y-pawn_dir)]
        for ax, ay in attack_squares:
            if 0 <= ax < 8 and 0 <= ay < 8:
                piece = board[ay][ax]
                if piece == opponent + 'P':
                    attackers += 1
        return attackers

    def is_pawn_protected(self, board, pos, color):
        x, y = pos
        protector_count = 0
        protect_squares = [(x-1, y+1), (x+1, y+1)] if color == 'w' else [(x-1, y-1), (x+1, y-1)]
        for px, py in protect_squares:
            if 0 <= px < 8 and 0 <= py < 8:
                piece = board[py][px]
                if piece and piece[0] == color:
                    protector_count += 1
        return protector_count

    def calculate_pawn_threat_penalty(self, board, color):
        penalty = 0
        opponent = 'w' if color == 'b' else 'b'
        for y in range(8):
            for x in range(8):
                piece = board[y][x]
                if piece and piece[0] == color:
                    pos = (x, y)
                    pawn_attackers = self.get_pawn_attackers(board, pos, color)
                    if pawn_attackers > 0:
                        piece_value = PIECE_VALUES.get(piece[1], 0)
                        penalty += pawn_attackers * piece_value * 0.2
        return penalty

    def get_relative_score(self, board, player_color):
        bot_score = self.evaluate(board, player_color)
        opponent_score = self.evaluate(board, 'w' if player_color == 'b' else 'b')
        return bot_score - opponent_score
    
    def find_king(self, board, color):
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece == f"{color}K":
                    return (file, rank)
        return None

    def has_castled(self, board, color):
        king_pos = self.find_king(board, color)
        if color == 'w':
            return king_pos in [(2, 7), (6, 7)]  # Nhập thành cánh hậu hoặc cánh vua
        else:
            return king_pos in [(2, 0), (6, 0)]