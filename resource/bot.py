import math
import random
import time
from collections import defaultdict
from opening_book import OpeningBook
from evaluation import Evaluation, PIECE_VALUES
from move_generator import MoveGenerator
from bitboard import Bitboards
from zobrist import ZobristHasher
from transposition_table import TranspositionTable, TTEntry
from tactics import detect_forks, detect_pins, detect_skewers, detect_discovered_attacks

class ChessBot:
    def __init__(self, move_validator):
        self.move_validator = move_validator
        self.evaluation = Evaluation(move_validator)
        self.killer_moves = defaultdict(list)
        self.history_table = defaultdict(int)
        self.zobrist = ZobristHasher()
        self.transposition_table = TranspositionTable()
        self.repetition_table = defaultdict(int)
        self.last_move = None

        try:
            self.opening_book = OpeningBook(file_path=r"D:\Chess_Test\resource\Book.txt")
        except FileNotFoundError:
            print("[Bot] Error: Could not find Book.txt")
            self.opening_book = None

        self.max_depth = 4
        self.max_time = 5

    def make_move(self, board, turn, castling_rights, last_move):
        # Dynamic time management
        total_time = self.max_time
        move_count = sum(1 for row in board for p in row if p and p[0] == ('w' if turn else 'b'))
        phase_factor = 1.0 if move_count < 12 else 0.6 if move_count < 24 else 0.3
        allocated_time = max(1.0, total_time * phase_factor)
        self.max_time = allocated_time

        start_time = time.time()
        bot_color = 'b' if not turn else 'w'
        self.last_move = last_move

        if self.opening_book:
            move = self.opening_book.try_get_book_move(board, bot_color, turn, castling_rights, last_move)
            if move:
                self.execute_move(board, move[0], move[1])
                return True

        best_move = None
        best_score = -1_000_000
        for depth in range(1, self.max_depth + 1):
            window = 50
            alpha = best_score - window if best_score != -1_000_000 else -1_000_000
            beta = best_score + window if best_score != -1_000_000 else 1_000_000
            score, move = self.alphabeta(board, depth, alpha, beta, True, bot_color, start_time)
            if score <= alpha or score >= beta:
                score, move = self.alphabeta(board, depth, -1_000_000, 1_000_000, True, bot_color, start_time)
            if move:
                best_move = move
                best_score = score
            if time.time() - start_time > self.max_time:
                break

        if best_move:
            self.execute_move(board, best_move[0], best_move[1])
            return True

        return self.fallback_to_random_move(board, bot_color)


    def alphabeta(self, board, depth, alpha, beta, maximizing, color, start_time, null_move_allowed=True):
        hash_key = self.zobrist.hash_board(board, color, self.move_validator.castling_rights, None)
        tt_entry = self.transposition_table.lookup(hash_key, depth, alpha, beta)

        self.repetition_table[hash_key] += 1
        if self.repetition_table[hash_key] >= 3:
            self.repetition_table[hash_key] -= 1
            return 0, None

        if tt_entry is not None:
            self.repetition_table[hash_key] -= 1
            return tt_entry, None

        if depth == 0:
            self.repetition_table[hash_key] -= 1
            return self.quiescence(board, alpha, beta, color, start_time), None

        best_score = -1_000_000 if maximizing else 1_000_000
        best_move = None
        moves = self.get_ordered_moves(board, color, depth)

        if null_move_allowed and depth >= 3 and not maximizing:
            null_board = self.copy_board(board)
            null_score, _ = self.alphabeta(null_board, depth - 2, -beta, -beta + 1, True, self.opponent_color(color), start_time, False)
            if null_score >= beta:
                self.repetition_table[hash_key] -= 1
                return beta, None

        for i, move in enumerate(moves):
            if time.time() - start_time > self.max_time:
                break

            new_board = self.copy_board(board)
            self.execute_move(new_board, move[0], move[1])
            new_depth = depth - 1

            # LMR: giảm depth cho quiet move không phải killer
            is_quiet = board[move[1][1]][move[1][0]] == ''
            is_killer = move in self.killer_moves[depth]
            if depth >= 3 and i >= 3 and is_quiet and not is_killer:
                new_depth -= 1

            if i == 0:
                score, _ = self.alphabeta(new_board, new_depth, alpha, beta, not maximizing, self.opponent_color(color), start_time)
            else:
                score, _ = self.alphabeta(new_board, new_depth, alpha + 1, alpha + 1, not maximizing, self.opponent_color(color), start_time)
                if alpha < score < beta:
                    score, _ = self.alphabeta(new_board, new_depth, alpha, beta, not maximizing, self.opponent_color(color), start_time)


            if maximizing:
                if score > best_score:
                    best_score = score
                    best_move = move
                alpha = max(alpha, score)
            else:
                if score < best_score:
                    best_score = score
                    best_move = move
                beta = min(beta, score)

            if beta <= alpha:
                self.killer_moves[depth].append(move)
                break

        if best_move:
            self.history_table[(best_move[0], best_move[1])] += 2 ** depth

        flag = 'EXACT'
        if best_score <= alpha:
            flag = 'UPPERBOUND'
        elif best_score >= beta:
            flag = 'LOWERBOUND'

        self.transposition_table.store(hash_key, TTEntry(depth, best_score, flag))
        self.repetition_table[hash_key] -= 1
        return best_score, best_move

    def get_ordered_moves(self, board, color, depth):
        bitboards = Bitboards()
        bitboards.from_board_array(board)
        gen = MoveGenerator(bitboards)
        move_list = []

        forks = detect_forks(board, self.move_validator, color)
        pins = detect_pins(board, self.move_validator, color)
        skewers = detect_skewers(board, self.move_validator, color)
        discovered = detect_discovered_attacks(board, self.move_validator, color)

        fork_squares = {pos for pos, _ in forks}
        pin_squares = {pos for pos, _ in pins}
        skewer_squares = {pos for _, pos, _ in skewers}
        discovered_squares = {src for src, _, _ in discovered}

        print("Forks:", forks)
        print("Pins:", pins)
        print("Skewers:", skewers)
        print("Discovered:", discovered)

        for start_square, end_square in gen.generate_all_moves(color):
            start_pos = (start_square % 8, 7 - start_square // 8)
            end_pos = (end_square % 8, 7 - end_square // 8)
            if self.move_validator.is_valid_move(start_pos, end_pos):
                see_score = self.evaluation.static_exchange_eval(board, start_pos, end_pos)
                move_list.append(((start_pos, end_pos), see_score))

        def score_move(item):
            move, see = item
            if move[0] in fork_squares:
                return 20000
            if move[0] in pin_squares:
                return 15000
            if move[0] in skewer_squares:
                return 12000
            if move[0] in discovered_squares:
                return 11000  # discovered boost
            return self.history_table[(move[0], move[1])] + see

        move_list.sort(key=score_move, reverse=True)
        return [move for move, _ in move_list]

    def quiescence(self, board, alpha, beta, color, start_time):
        stand_pat = self.evaluation.evaluate(board, color)
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        bitboards = Bitboards()
        bitboards.from_board_array(board)
        gen = MoveGenerator(bitboards)
        captures = []
        for start_square, end_square in gen.generate_all_moves(color):
            start_pos = (start_square % 8, 7 - start_square // 8)
            end_pos = (end_square % 8, 7 - end_square // 8)
            if self.move_validator.is_valid_move(start_pos, end_pos):
                tx, ty = end_pos
                if board[ty][tx] and board[ty][tx][0] != color:
                    captures.append((start_pos, end_pos))

        for move in captures:
            if time.time() - start_time > self.max_time:
                break
            new_board = self.copy_board(board)
            self.execute_move(new_board, move[0], move[1])
            score = -self.quiescence(new_board, -beta, -alpha, self.opponent_color(color), start_time)
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha

    def fallback_to_random_move(self, board, color):
        moves = self.get_all_valid_moves(board, color)
        if moves:
            move = random.choice(moves)
            self.execute_move(board, move[0], move[1])
            print("[Bot] Fallback to random move:", move)
            return True
        return False

    def execute_move(self, board, start, end):
        self.last_move = (start, end)
        self.en_passant_capture = None

        sx, sy = start
        ex, ey = end
        piece = board[sy][sx]
        target = board[ey][ex]

        # Không cho phép bắt vua
        if target and target[1] == 'K':
            print("[Bot] ❌ Không được phép bắt vua.")
            return

        print("[BOT DEBUG] Move:", start, "->", end)
        print("[BOT DEBUG] Piece:", piece)
        print("[BOT DEBUG] Target square content:", target)

        # Xử lý en passant
        if piece and piece[1] == 'P' and sx != ex and target == '':
            direction = -1 if piece[0] == 'w' else 1
            captured_y = ey - direction
            captured_piece = board[captured_y][ex]
            
            # Kiểm tra điều kiện en passant
            if (captured_piece and captured_piece[0] != piece[0] and captured_piece[1] == 'P' and
                self.last_move and self.last_move[1] == (ex, captured_y) and
                abs(self.last_move[0][1] - self.last_move[1][1]) == 2):
                
                print("[BOT DEBUG] ✅ En passant triggered — marking for removal:", (ex, captured_y))
                board[captured_y][ex] = ''
                self.en_passant_capture = (ex, captured_y)

        # Thực hiện nước đi chính
        board[ey][ex] = piece
        board[sy][sx] = ''

    def copy_board(self, board):
        return [row[:] for row in board]

    def opponent_color(self, color):
        return 'b' if color == 'w' else 'w'

    def get_all_valid_moves(self, board, color):
        bitboards = Bitboards()
        bitboards.from_board_array(board)
        gen = MoveGenerator(bitboards)
        move_list = []
        for start_square, end_square in gen.generate_all_moves(color):
            start_pos = (start_square % 8, 7 - start_square // 8)
            end_pos = (end_square % 8, 7 - end_square // 8)
            if self.move_validator.is_valid_move(start_pos, end_pos):
                move_list.append((start_pos, end_pos))
        return move_list
