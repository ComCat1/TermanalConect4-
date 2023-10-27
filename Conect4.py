#By: CatCom
#10/26/2022

import numpy as np
import multiprocessing
import time
ROW_COUNT = 6
COLUMN_COUNT = 7

#DEPTH = 51

def calculate_probabilities(board):
    if winning_move(board, 1):
        return 1.0, 0.0
    elif winning_move(board, 2):
        return 0.0, 1.0
    else:
        total_positions = ROW_COUNT * COLUMN_COUNT
        player_score = score_position(board, 1)
        ai_score = score_position(board, 2)
        player_prob = player_score / total_positions
        ai_prob = ai_score / total_positions
        return player_prob, ai_prob


def minimax_process(input_data, return_dict):
    board, depth, alpha, beta, maximizingPlayer = input_data
    col, score = minimax(board, depth, alpha, beta, maximizingPlayer)
    return_dict[depth] = (col, score)

def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT))

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def print_board(board, player_prob, ai_prob):
    print(" 0 1 2 3 4 5 6")
    flipped_board = np.flip(board, 0)
    for r, row in enumerate(flipped_board):
        row_display = '|'
        for val in row:
            if val == 0:
                row_display += '\033[0m |'  # Reset color
            elif val == 1:
                row_display += '\033[91mX\033[0m|'  # Red for Player 1
            else:
                row_display += '\033[92mO\033[0m|'  # Green for AI
        if player_prob > ai_prob:
            player_color_code = '\033[92m'  # Green for higher player probability
            ai_color_code = '\033[91m'  # Red for lower AI probability
        elif player_prob < ai_prob:
            player_color_code = '\033[91m'  # Red for lower player probability
            ai_color_code = '\033[92m'  # Green for higher AI probability
        else:
            player_color_code = '\033[93m'  # Yellow for equal probabilities
            ai_color_code = '\033[93m'  # Yellow for equal probabilities
        if r == 0:
            row_display += f" {player_color_code}Player:{player_prob*100:.2f}%\033[0m"
        elif r == 1:
            row_display += f" {ai_color_code}AI:{ai_prob*100:.2f}%\033[0m"
        print(row_display)
    print('---------------')




def winning_move(board, piece):
    # Check horizontal 
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][c + 3] == piece:
                return True

    # Check vertical 
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][c] == piece:
                return True

    # Check positive diagonals
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][c + 3] == piece:
                return True

    # Check negative diagonals
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][c + 3] == piece:
                return True

def evaluate_window(window, piece):
    score = 0
    opponent_piece = 1 if piece == 2 else 2

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2

    if window.count(opponent_piece) == 3 and window.count(0) == 1:
        score -= 4

    return score

def score_position(board, piece):
    score = 0

    # Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Score horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c + 4]
            score += evaluate_window(window, piece)

    # Score vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + 4]
            score += evaluate_window(window, piece)

    # Score positive diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    # Score negative diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + 3 - i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score

def is_terminal_node(board):
    return winning_move(board, 1) or winning_move(board, 2) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, 2):
                return (None, 100000000000000)
            elif winning_move(board, 1):
                return (None, -10000000000000)
            else:  # Game over
                return (None, 0)
        else:  # Depth is zero
            return (None, score_position(board, 2))

    if maximizingPlayer:
        value = -np.Inf
        column = np.random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            board_copy = board.copy()
            drop_piece(board_copy, row, col, 2)
            new_score = minimax(board_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else:  #  player
        value = np.Inf
        column = np.random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            board_copy = board.copy()
            drop_piece(board_copy, row, col, 1)
            new_score = minimax(board_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

board = create_board()
game_over = False
turn = 0

def play_connect4_vs_ai():
    board = create_board()
    game_over = False
    turn = 0

    while not game_over:
        if turn == 0:
            col = int(input("Player 1 Make your selection (0-6):"))
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 1)

                if winning_move(board, 1):
                    print("Player 1 wins!")
                    game_over = True

        else:
            col, minimax_score = minimax(board, 5, -np.Inf, np.Inf, True)
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 2)

                if winning_move(board, 2):
                    print("Player 2 wins!")
                    game_over = True

        player1_percent, player2_percent = calculate_probabilities(board)
        print_board(board, player1_percent, player2_percent)

        turn += 1
        turn = turn % 2

def play_ai_vs_connect4():
    board = create_board()
    game_over = False
    turn = 0

    while not game_over:
        if turn == 0:
            time.sleep(0.1)
            #  search deeper
            with multiprocessing.Manager() as manager:
                return_dict = manager.dict()
                processes = []
                for d in range(1, 6):  # Adjust range for depth
                    input_data = (board.copy(), d, -np.Inf, np.Inf, True)
                    process = multiprocessing.Process(target=minimax_process, args=(input_data, return_dict))
                    processes.append(process)
                    process.start()

                for process in processes:
                    process.join()

                depth_results = [(return_dict[d][0], return_dict[d][1]) for d in range(1, 6)]  # Adjust the range here as well
                col, _ = max(depth_results, key=lambda item: item[1])

            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 2)

                if winning_move(board, 2):
                    print("AI wins!")
                    game_over = True

        else:
            col = int(input("Make your selection (0-6):"))
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 1)

                if winning_move(board, 1):
                    print("Player wins!")
                    game_over = True

        player1_percent, player2_percent = calculate_probabilities(board)
        print_board(board, player1_percent, player2_percent)

        turn += 1
        turn = turn % 2

def play_ai_vs_ai():
    board = create_board()
    game_over = False
    turn = 0

    while not game_over:
        if turn == 0:
            
            with multiprocessing.Manager() as manager:
                return_dict = manager.dict()
                processes = []
                for d in range(1, 6):  # Adjust the range according to the desired depth
                    input_data = (board.copy(), d, -np.Inf, np.Inf, True)
                    process = multiprocessing.Process(target=minimax_process, args=(input_data, return_dict))
                    processes.append(process)
                    process.start()

                for process in processes:
                    process.join()

                depth_results = [(return_dict[d][0], return_dict[d][1]) for d in range(1, 6)]  # Adjust the range here as well
                col, minimax_score = max(depth_results, key=lambda item: item[1])
                
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 1)

                if winning_move(board, 1):
                    print("Player 1 wins!")
                    game_over = True

        else:
            
            with multiprocessing.Manager() as manager:
                return_dict = manager.dict()
                processes = []
                for d in range(1, 6):  # Adjust the range according to the desired depth
                    input_data = (board.copy(), d, -np.Inf, np.Inf, False)
                    process = multiprocessing.Process(target=minimax_process, args=(input_data, return_dict))
                    processes.append(process)
                    process.start()

                for process in processes:
                    process.join()

                depth_results = [(return_dict[d][0], return_dict[d][1]) for d in range(1, 6)]  # Adjust the range here as well
                col, minimax_score = max(depth_results, key=lambda item: item[1])

            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 2)

                if winning_move(board, 2):
                    print("Player 2 wins!")
                    game_over = True

        player1_percent, player2_percent = calculate_probabilities(board)
        print_board(board, player1_percent, player2_percent)

        turn += 1
        turn = turn % 2

def main():
    choice = int(input("Enter 1 to play against the AI, 2 to watch the AI play itself: "))
    if choice == 1:
        player_first = int(input("Enter 1 if you want to make the first move, 2 if you want the AI to make the first move: "))
        if player_first == 1:
            play_connect4_vs_ai()
        elif player_first == 2:
            play_ai_vs_connect4()
        else:
            print("Invalid choice. Please try again.")
    elif choice == 2:
        play_ai_vs_ai()
    else:
        print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
    





#                    |\_|\
#                    \` .. )
#               __,.-" = Y= 
#             ."        )
#           /   ,    \/\_
#      ((____|    )_-\ \_-`
#      `-----'`-----` `--`
