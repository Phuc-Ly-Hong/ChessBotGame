import math
import random
import time
import numpy as np
from collections import defaultdict
from opening_book import OpeningBook
from evaluation import Evaluation, PIECE_VALUES

class ChessBot:
    def __init__(self, move_validator):
        self.move_validator = move_validator
        self.evaluation = Evaluation(move_validator)
        self.killer_moves = defaultdict(list)   
        self.history_table = defaultdict(int)
        self.transposition_table = {}
        
        try:
            self.opening_book = OpeningBook(file_path=r"D:\Chess_Test\resource\Book.txt")
        except FileNotFoundError:
            print(r"Error: Could not find Book.txt at D:\Chess_Test\resource\Book.txt")
            self.opening_book = None

        self.max_depth = 8
        self.max_time = 10

    def make_move(self, board, turn, castling_rights, last_move):
        start_time = time.time()
        bot_color = 'b'  # Assuming bot plays black

        # 1. Try opening book first
        if self.opening_book and self.try_opening_book_move(board, turn, castling_rights, last_move, bot_color):
            return True

        # 2. Use Alpha-Beta search if no book move found
        print("[Bot] Starting Alpha-Beta search...")
        best_move = self.mtdf_search(board, bot_color, start_time)
        
        if best_move:
            self.execute_move(board, best_move[0], best_move[1])
            return True
        
        # Fallback to random move if no valid move found
        return self.fallback_to_random_move(board, bot_color)
    
    def mtdf_search(self, board, color, start_time):
        best_score = -math.inf
        best_move = None
        guess = 0
        depth = 1

        while time.time() - start_time < self.max_time and depth <= self.max_depth:
            score, move = self.alphabeta(board, depth, guess-50, guess+50, True, color, start_time)
            
            if score > best_score:
                best_score = score
                best_move = move
                print(f"[Bot] Depth {depth}: {move} Score {score}")
            
            guess = score
            depth += 1
        
        return best_move

    def try_opening_book_move(self, board, turn, castling_rights, last_move, color):
        try:
            book_move = self.opening_book.try_get_book_move(
                board=board,
                color=color,
                turn=turn,
                castling_rights=castling_rights,
                last_move=last_move,
                weight_pow=0.5
            )
            if book_move:
                print(f"[Bot] Using book move: {book_move}")
                self.execute_move(board, book_move[0], book_move[1])
                return True
        except Exception as e:
            print(f"[Bot] Book error: {str(e)}")
        return False
    
    def alphabeta(self, board, depth, alpha, beta, maximizing, color, start_time):
        tt_entry = self.transposition_table.get(self.board_hash(board))
        if tt_entry and tt_entry['depth'] >= depth:
            if tt_entry['flag'] == 'exact':
                return tt_entry['score'], tt_entry['move']
            elif tt_entry['flag'] == 'lower':
                alpha = max(alpha, tt_entry['score'])
            elif tt_entry['flag'] == 'upper':
                beta = min(beta, tt_entry['score'])
            
            if alpha >= beta:
                return tt_entry['score'], tt_entry['move']

        if depth == 0 or self.is_terminal(board, color):
            return self.quiescence(board, alpha, beta, color, start_time), None

        best_score = -math.inf if maximizing else math.inf
        best_move = None
        moves = self.get_ordered_moves(board, color, depth)
        
        for move in moves:
            if time.time() - start_time > self.max_time:
                break
                
            new_board = self.copy_board(board)
            self.execute_move(new_board, move[0], move[1])
            
            score, _ = self.alphabeta(new_board, depth-1, alpha, beta, not maximizing, 'w' if color == 'b' else 'b', start_time)
            
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
                self.store_killer_move(move, depth)
                break

        flag = 'exact'
        if best_score <= alpha:
            flag = 'upper'
        elif best_score >= beta:
            flag = 'lower'
        
        self.transposition_table[self.board_hash(board)] = {
            'depth': depth,
            'score': best_score,
            'move': best_move,
            'flag': flag
        }
        
        return best_score, best_move
    
    def quiescence(self, board, alpha, beta, color, start_time):
        stand_pat = self.evaluation.get_relative_score(board, color)
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        for move in self.get_captures(board, color):
            if time.time() - start_time > self.max_time:
                break
                
            new_board = self.copy_board(board)
            self.execute_move(new_board, move[0], move[1])
            
            score = -self.quiescence(new_board, -beta, -alpha, 'w' if color == 'b' else 'b', start_time)
            
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        
        return alpha

    def find_best_move_with_alphabeta(self, board, color, start_time, max_time):
        best_move = None
        best_score = -math.inf
        
        for depth in range(2, 6):
            if time.time() - start_time > max_time:
                break
                
            try:
                score, move = self.alphabeta_search(
                    board=board,
                    depth=depth,
                    alpha=-math.inf,
                    beta=math.inf,
                    maximizing_player=True,
                    current_color=color,
                    start_time=start_time,
                    max_time=max_time
                )
                
                if move and score > best_score:
                    best_move = move
                    best_score = score
                    print(f"[Bot] Depth {depth}: move {move} score {score}")
            except TimeoutError:
                print(f"[Bot] Depth {depth} search timed out")
                break

        return best_move
    
    def board_hash(self, board):
        return hash(str(board))

    def alphabeta_search(self, board, depth, alpha, beta, maximizing_player, current_color, start_time, max_time):
        if time.time() - start_time > max_time:
            raise TimeoutError()
            
        if depth == 0 or self.is_terminal_node(board, current_color):
            q_score = self.quiescence_search(board, alpha, beta, current_color, start_time, max_time)
            return q_score, None
            
        if depth >= 3 and not self.has_forced_moves(board, current_color):
            current_eval = self.evaluation.get_relative_score(board, current_color)
            safety_margin = 0.5
            if maximizing_player:
                if current_eval >= beta - safety_margin:
                    return beta, None
                alpha = max(alpha, current_eval)
            else:
                if current_eval <= alpha + safety_margin:
                    return alpha, None
                beta = min(beta, current_eval)
        
        best_move = None
        best_value = -math.inf if maximizing_player else math.inf
        moves = self.get_ordered_moves(board, current_color, depth)
        
        for move in moves:
            new_board = self.copy_board(board)
            self.execute_move(new_board, move[0], move[1])
            
            value, _ = self.alphabeta_search(
                new_board, depth-1, alpha, beta,
                not maximizing_player,
                'w' if current_color == 'b' else 'b',
                start_time, max_time
            )
            
            if maximizing_player:
                if value > best_value:
                    best_value = value
                    best_move = move
                    alpha = max(alpha, best_value)
            else:
                if value < best_value:
                    best_value = value
                    best_move = move
                    beta = min(beta, best_value)
                    
            if beta <= alpha:
                self.store_killer_move(move, depth)
                break
                
        return best_value, best_move
    
    def quiescence_search(self, board, alpha, beta, current_color, start_time, max_time):
        stand_pat = self.evaluation.evaluate(board, current_color)
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        capture_moves = []
        for move in self.get_capture_moves(board, current_color):
            start, end = move
            attacker_val = PIECE_VALUES.get(board[start[1]][start[0]][1], 0)
            target_val = PIECE_VALUES.get(board[end[1]][end[0]][1], 0)
            if target_val >= attacker_val:
                capture_moves.append((target_val - attacker_val, move))
        
        capture_moves.sort(reverse=True, key=lambda x: x[0])
        
        for _, move in capture_moves:
            new_board = self.copy_board(board)
            self.execute_move(new_board, move[0], move[1])

            score = -self.quiescence_search(
                new_board, -beta, -alpha,
                'w' if current_color == 'b' else 'b',
                start_time, max_time
            )

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

        return alpha
    
    def get_captures(self, board, color):
        return [move for move in self.get_all_valid_moves(board, color) if board[move[1][1]][move[1][0]]]
    
    def is_terminal(self, board, color):
        return self.move_validator.is_checkmate(color) or self.move_validator.is_stalemate(color)   

    def is_terminal_node(self, board, color):
        if not self.get_all_valid_moves(board, color):
            return True
        return False

    def get_ordered_moves(self, board, color, depth):
        moves = self.get_all_valid_moves(board, color)
        return self.order_moves(board, moves, depth, color)

    def order_moves(self, board, moves, depth, color):
        opponent = 'b' if color == 'w' else 'w'
        scored_moves = []
        tt_entry = self.transposition_table.get(self.board_hash(board))
        tt_move = tt_entry['move'] if tt_entry and 'move' in tt_entry else None

        for move in moves:
            start, end = move
            piece = board[start[1]][start[0]]
            target = board[end[1]][end[0]]
            score = 0

            if piece[1] == 'K' and abs(end[0] - start[0]) == 2:
                score +=1000
            
            if move == tt_move:
                score += 10000  # Ưu tiên nước đi từ transposition table

            pawn_attackers = self.evaluation.get_pawn_attackers(board, start, color)
            if pawn_attackers > 0:
                if target:
                    if target[1] == 'P':
                        defenders = self.evaluation.get_pawn_attackers(board, end, opponent)
                        if defenders == 0:
                            score += 150
                        else:
                            score -= 200
                else:
                    new_attackers = self.evaluation.get_pawn_attackers(board, end, color)
                    if new_attackers < pawn_attackers:
                        score += 100 * (pawn_attackers - new_attackers)
            
            temp_board = self.copy_board(board)
            self.execute_move(temp_board, start, end)
            if self.evaluation.get_pawn_attackers(temp_board, end, color) > 0:
                score -= PIECE_VALUES.get(piece[1], 0) * 0.5

            if target and target[1] == 'P':
                defenders = self.evaluation.is_pawn_protected(board, end, opponent)
                if defenders == 0:
                    score += 200
                else:
                    score -= PIECE_VALUES.get(piece[1], 0) - 100

            if self.move_validator.is_king_in_check(temp_board, color):
                score -= 1000
                continue
            
            if target:
                score += 10 * PIECE_VALUES.get(target[1], 0) - PIECE_VALUES.get(piece[1], 0)
            
            score += self.evaluation.exchange_score(board, color, start, end) * 5
            
            if self.is_killer_move(move, depth):
                score += 100
                
            score += self.history_table.get(move, 0) * 2
            
            if piece[1] == 'P' and (end[1] == 0 or end[1] == 7):
                score += 500
                
            if piece[1] == 'K' and abs(end[0] - start[0]) == 2:
                score += 200
                
            if self.evaluation.is_piece_attacked(temp_board, end, color):
                score -= PIECE_VALUES.get(piece[1], 0) // 2
                
            if piece[1] == 'Q':
                if self.evaluation.is_piece_attacked(temp_board, end, color):
                    score -= 300
                    
            if target and target[1] == 'Q' and piece[1] == 'Q':
                score -= 100
                material_score = self.evaluation.material_score(board, color)
                if material_score > 300:
                    score += 50
                    
            scored_moves.append((score, move))
        
        scored_moves.sort(reverse=True, key=lambda x: x[0])
        return [move for score, move in scored_moves]

    def is_killer_move(self, move, depth):
        return depth in self.killer_moves and move in self.killer_moves[depth]

    def store_killer_move(self, move, depth):
        if depth not in self.killer_moves:
            self.killer_moves[depth] = []
        generation = 0
        if move not in self.killer_moves[depth]:
            if len(self.killer_moves[depth]) >= 2:
                self.killer_moves[depth].pop()
            self.killer_moves[depth].insert(0, move)

    def get_all_valid_moves(self, board, color):
        moves = []
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece and piece[0] == color:
                    valid_moves = self.move_validator.get_all_valid_moves((file, rank))
                    for move in valid_moves:
                        temp_board = self.copy_board(board)
                        self.execute_move(temp_board, (file, rank), move)
                        if not self.move_validator.is_king_in_check(temp_board, color):
                            moves.append(((file, rank), move))
        return moves

    def execute_move(self, board, start_pos, end_pos):
        start_file, start_rank = start_pos
        end_file, end_rank = end_pos
        piece = board[start_rank][start_file]
        board[end_rank][end_file] = piece
        board[start_rank][start_file] = ''
        
        if piece and piece[1] == 'K' and abs(start_file - end_file) == 2:
            if end_file > start_file:
                rook_start_file = 7
                rook_end_file = 5
                rook = board[start_rank][rook_start_file]
                board[start_rank][rook_end_file] = rook
                board[start_rank][rook_start_file] = ''
            else:
                rook_start_file = 0
                rook_end_file = 3
                rook = board[start_rank][rook_start_file]
                board[start_rank][rook_end_file] = rook
                board[start_rank][rook_start_file] = ''
        
        if piece and piece[1] == 'P' and (end_rank == 0 or end_rank == 7):
            board[end_rank][end_file] = piece[0] + 'Q'
        
        if self.move_validator.is_king_in_check(board, piece[0]):
            print(f"[Warning] Move {start_pos}->{end_pos} leaves king in check!")

    def fallback_to_random_move(self, board, color):
        all_moves = self.get_all_valid_moves(board, color)
        if all_moves:
            random_move = random.choice(all_moves)
            print(f"[Bot] Using random move: {random_move}")
            self.execute_move(board, random_move[0], random_move[1])
            return True
        return False

    def copy_board(self, board):
        return [row[:] for row in board]
    
    def get_capture_moves(self, board, color):
        moves = []
        for rank in range(8):
            for file in range(8):
                piece = board[rank][file]
                if piece and piece[0] == color:
                    start_pos = (file, rank)
                    valid_moves = self.move_validator.get_all_valid_moves(start_pos)
                    for end_pos in valid_moves:
                        target = board[end_pos[1]][end_pos[0]]
                        if target and target[0] != color:
                            moves.append((start_pos, end_pos))
        return moves
    
    def has_forced_moves(self, board, color):
        if self.move_validator.is_king_in_check(board, color):
            return True
        for move in self.get_capture_moves(board, color):
            _, end = move
            target = board[end[1]][end[0]]
            if target and PIECE_VALUES.get(target[1], 0) >= PIECE_VALUES['N']:
                return True
        return False