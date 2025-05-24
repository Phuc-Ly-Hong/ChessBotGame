import random
import math

class BookMove:
    def __init__(self, move_string, num_times_played):
        self.move_string = move_string
        self.num_times_played = num_times_played

class OpeningBook:
    def __init__(self, file_content=None, file_path=None):
        self.moves_by_position = {}
        self.rng = random.Random()

        if file_content:
            self.load_from_string(file_content)
        elif file_path:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    print("Content of Book.txt:\n", content)  # Debug nội dung file
                    self.load_from_string(content)
                print("Successfully loaded opening book with", len(self.moves_by_position), "positions")  # Debug số lượng vị trí
            except Exception as e:
                print(f"Failed to load opening book from {file_path}: {e}")

    def load_from_string(self, content):
        entries = [e.strip() for e in content.strip().split("pos")[1:] if e.strip()]
        for entry in entries:
            entry_data = entry.strip().split('\n')
            position_fen = entry_data[0].strip()
            move_data = entry_data[1:]
            book_moves = []
            for move_line in move_data:
                move_string, num_played = move_line.split()
                book_moves.append(BookMove(move_string, int(num_played)))
            self.moves_by_position[self.remove_move_counters_from_fen(position_fen)] = book_moves

    def has_book_move(self, position_fen):
        return self.remove_move_counters_from_fen(position_fen) in self.moves_by_position

    def try_get_book_move(self, board, color, turn, castling_rights, last_move, weight_pow=0.5):
        position_fen = self.get_current_fen(board, turn, castling_rights, last_move)
        print(f"\n[Opening Book] Current position FEN: {position_fen}")
    
        fen_key = self.remove_move_counters_from_fen(position_fen)
        print(f"[Opening Book] Lookup key: {fen_key}")
    
        if fen_key in self.moves_by_position:
            moves = self.moves_by_position[fen_key]
            print(f"[Opening Book] Found {len(moves)} book moves for this position")
        
            # In ra 5 nước đi đầu tiên để debug
            for i, move in enumerate(moves[:5]):
                print(f"  {i+1}. {move.move_string} (played {move.num_times_played} times)")
            
            total_play_count = sum(m.num_times_played ** weight_pow for m in moves)
            weights = [(m.num_times_played ** weight_pow) / total_play_count for m in moves]
        
            selected_move = random.choices(moves, weights=weights, k=1)[0]
            print(f"[Opening Book] Selected move: {selected_move.move_string}")
        
            move_coords = self.algebraic_to_coords(selected_move.move_string, board, color)
            if move_coords:
                print(f"[Opening Book] Converted to coordinates: {move_coords}")
                return move_coords
            else:
                print("[Opening Book] Failed to convert move to coordinates")
        else:
            print("[Opening Book] No book moves found for this position")
    
        return None

    def weighted_play_count(self, play_count, weight_pow):
        return math.ceil(play_count ** weight_pow)

    def remove_move_counters_from_fen(self, fen):
        parts = fen.rsplit()
        if len(parts) >= 4:
            return ' '.join(parts[:4])
        return fen

    def get_current_fen(self, board, turn, castling_rights, last_move):
        fen_parts = []
    
        # 1. Piece placement
        for rank in range(8):
            empty = 0
            rank_str = ""
            for file in range(8):
                piece = board[rank][file]
                if piece:  # Kiểm tra xem ô có quân cờ không
                    if empty > 0:
                        rank_str += str(empty)
                        empty = 0
                    # Thêm ký tự đại diện cho quân cờ
                    rank_str += piece[1].lower() if piece[0] == 'b' else piece[1].upper()
                else:
                    empty += 1
            if empty > 0:
                rank_str += str(empty)
            fen_parts.append(rank_str)
        piece_placement = "/".join(fen_parts)
    
        # 2. Active color
        active_color = 'w' if turn else 'b'
    
        # 3. Castling availability
        castling = castling_rights if castling_rights else '-'
    
        # 4. En passant (sửa phần này)
        en_passant = '-'
        if last_move and len(last_move) == 2:
            start_pos, end_pos = last_move
            start_file, start_rank = start_pos
            end_file, end_rank = end_pos
        
            # Kiểm tra xem có phải nước đi tốt không
            if 0 <= start_rank < 8 and 0 <= start_file < 8:
                piece = board[start_rank][start_file]
                if piece and piece[1] == 'P':  # Nếu là quân tốt
                    if abs(start_rank - end_rank) == 2:  # Đi 2 ô
                        ep_rank = str(3 if piece[0] == 'w' else 6)  # Hàng 3 cho trắng, 6 cho đen
                        ep_file = chr(ord('a') + end_file)
                        en_passant = f"{ep_file}{ep_rank}"
    
        # 5. Halfmove clock và fullmove number (tạm hardcode)
        halfmove_clock = '0'
        fullmove_number = '1'
    
        return f"{piece_placement} {active_color} {castling} {en_passant} {halfmove_clock} {fullmove_number}"

    def algebraic_to_coords(self, move, board, color):
        # Ký hiệu tọa độ (coordinate notation): e2e4, g8f6
        if len(move) == 4 and move[0].islower() and move[1].isdigit() and move[2].islower() and move[3].isdigit():
            try:
                start_file = ord(move[0]) - ord('a')
                start_rank = 8 - int(move[1])
                end_file = ord(move[2]) - ord('a')
                end_rank = 8 - int(move[3])

                #Validate Coordinate
                if not (0 <= start_file < 8 and 0 <= start_rank < 8 and 0 <= end_file < 8 and 0 <= end_rank < 8):
                    return None
                
                #Check if piece exists or color matches
                piece = board[start_rank][start_file]
                if not piece or piece[0].lower() != color.lower():
                    return None
                
                return ((start_file, start_rank), (end_file,end_rank))
            except:
                return None
        
        return None    