
import chess
import chess.engine
import random
import time
from evaluation import Evaluation
from move_validator import MoveValidator
from bot import ChessBot

# Load Stockfish
stockfish_path = r"D:\Chess_Test\stockfish\stockfish-windows-x86-64-avx2.exe"
engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
engine.configure({"UCI_LimitStrength": True, "UCI_Elo": 1320})

# Game settings
MAX_GAMES = 300
MOVE_TIME = 1  # seconds per move
wins, draws, losses = 0, 0, 0

def run_game(play_white_as_bot):
    global wins, draws, losses
    board = chess.Board()
    validator = MoveValidator([[''] * 8 for _ in range(8)], "KQkq")
    bot = ChessBot(validator)
    bot_color = chess.WHITE if play_white_as_bot else chess.BLACK

    while not board.is_game_over():
        if board.turn == bot_color:
            board_array = [[str(board.piece_at(i + j * 8)).replace('None', '') for i in range(8)] for j in range(7, -1, -1)]
            validator.board = board_array
            bot.make_move(board_array, board.turn == chess.WHITE, board.castling_xfen(), bot.last_move)
            board.push(random.choice(list(board.legal_moves)))
        else:
            result = engine.play(board, chess.engine.Limit(time=MOVE_TIME))
            board.push(result.move)

    result = board.result()
    if result == "1-0":
        if play_white_as_bot:
            wins += 1
        else:
            losses += 1
    elif result == "0-1":
        if play_white_as_bot:
            losses += 1
        else:
            wins += 1
    else:
        draws += 1

# Main loop
for game_number in range(1, MAX_GAMES + 1):
    run_game(play_white_as_bot=(game_number % 2 == 1))
    print(f"Game {game_number} done.")

print(f"Final result after {MAX_GAMES} games:")
print(f"Wins: {wins}, Draws: {draws}, Losses: {losses}")

engine.quit()
