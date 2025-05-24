import math
import random
import time
import numpy as np
from collections import defaultdict
from opening_book import OpeningBook
from evaluation import Evaluation, PIECE_VALUES
from move_generator import MoveGenerator
from bitboard import Bitboards
from zobrist import ZobristHasher
from transposition_table import TranspositionTable, TTEntry

class ChessBot:
    def __init__(self, move_validator):
        self.move_validator = move_validator
        self.evaluation = Evaluation(move_validator)
        self.killer_moves = defaultdict(list)
        self.history_table = defaultdict(int)
        self.zobrist = ZobristHasher()
        self.transposition_table = TranspositionTable()
        self.repetition_table = defaultdict(int)

        try:
            self.opening_book = OpeningBook(file_path=r"D:\Chess_Test\resource\Book.txt")
        except FileNotFoundError:
            print(r"[Bot] Error: Could not find Book.txt at D:\Chess_Test\resource\Book.txt")
            self.opening_book = None

        self.max_depth = 4
        self.max_time = 5

    def make_move(self, board, turn, castling_rights, last_move):
        start_time = time.time()
        bot_color = 'b' if not turn else 'w'

        if self.opening_book:
            move = self.opening_book.try_get_book_move(
                board, bot_color, turn, castling_rights, last_move
            )
            if move:
                self.execute_move(board, move[0], move[1])
                return True

        best_move = None
        best_score = -1_000_000
        for depth in range(1, self.max_depth + 1):
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
        hash_key = self.zobrist.hash_board(
            board=board,
            side_to_move=color,
            castling_rights=self.move_validator.castling_rights,
            en_passant_file=None
        )

        tt_entry = self.transposition_table.lookup(hash_key, depth, alpha, beta)
        # Repetition check
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

        # Null Move Pruning
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
            # Late Move Reduction: reduce depth for late non-captures
            if depth >= 3 and i >= 3:
                new_depth -= 1

            score, _ = self.alphabeta(
                new_board, new_depth, alpha, beta,
                not maximizing, self.opponent_color(color), start_time
            )

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
        for start_square, end_square in gen.generate_all_moves(color):
            start_pos = (start_square % 8, 7 - start_square // 8)
            end_pos = (end_square % 8, 7 - end_square // 8)
            if self.move_validator.is_valid_move(start_pos, end_pos):
                move_list.append((start_pos, end_pos))

        def score_move(move):
            if move in self.killer_moves[depth]:
                return 10000
            return self.history_table[(move[0], move[1])]

        move_list.sort(key=score_move, reverse=True)
        return move_list

    def get_all_valid_moves(self, board, color):
        bitboards = Bitboards()
        bitboards.from_board_array(board)
        gen = MoveGenerator(bitboards)
        move_list = []
        for start_square, end_square in gen.generate_all_moves(color):
            start_pos = (start_square % 8, 7 - start_square // 8)
            end_pos = (end_square % 8, 7 - start_square // 8)
            if self.move_validator.is_valid_move(start_pos, end_pos):
                move_list.append((start_pos, end_pos))
        return move_list

    def fallback_to_random_move(self, board, color):
        moves = self.get_all_valid_moves(board, color)
        if moves:
            move = random.choice(moves)
            self.execute_move(board, move[0], move[1])
            print("[Bot] Fallback to random move:", move)
            return True
        return False

    def execute_move(self, board, start, end):
        sx, sy = start
        ex, ey = end
        board[ey][ex] = board[sy][sx]
        board[sy][sx] = ''

    def copy_board(self, board):
        return [row[:] for row in board]

    def opponent_color(self, color):
        return 'b' if color == 'w' else 'w'

    def quiescence(self, board, alpha, beta, color, start_time):
        stand_pat = self.evaluation.evaluate(board, color)
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        # Only consider capture moves
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