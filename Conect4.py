import multiprocessing
import numpy as np
import os
#import time
#slim down latter too bulky
ROW_COUNT = 6

COLUMN_COUNT = 7

possible_wins = 51 # used for count_possible_openings but should double check this 

#DEPTH = 51 #(not using depth anymore but could be used later(for gamemodes)
##################################################################################################
#incorect for the longer games (fix) 
#its close but seems wrong with the %'s(wrong numbers needs tweaking)
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
#find valid space
def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r
####################################################################
####################################################################
####################################################################
player_color_code = ""
ai_color_code = ""

#works well dont toutch
def print_board(board, player_prob, ai_prob, player_wins, ai_wins):
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear terminal (neatness)

    print(" 0 1 2 3 4 5 6")
    flipped_board = np.flip(board, 0)
    
    player_openings = count_possible_openings(board, 1) #player side
    ai_openings = count_possible_openings(board, 2) #AI side

    for r, row in enumerate(flipped_board):
        row_display = '|'
        for val in row:
            if val == 0:
                row_display += '\033[0m |'  # Reset 
            elif val == 1:
                row_display += '\033[91mX\033[0m|'  # Red (Player) 
            else:
                row_display += '\033[92mO\033[0m|'  # Green for AI
        if player_prob > ai_prob:
            player_color_code = '\033[92m'  # Green for higher probability (Player)
            ai_color_code = '\033[91m'  # Red for lower probability (AI)
        elif player_prob < ai_prob:
            player_color_code = '\033[91m'  # Red for lower probability (player)
            ai_color_code = '\033[92m'  # Green for higher probability (AI)
        else:
            player_color_code = '\033[93m'  # Yellow for equal (player) 
            ai_color_code = '\033[93m'  # Yellow for equal (AI
        print(row_display)

    print('---------------')

    print(f"{player_color_code}PLAYER:{player_prob*100:.2f}% ({player_openings} of {possible_wins})\033[0m")
    print(f"{ai_color_code}AI:{ai_prob*100:.2f}% ({ai_openings} of {possible_wins})\033[0m")

######################################################
def count_possible_openings(board, piece):
    openings = 0

    for col in range(COLUMN_COUNT):
        playable = is_valid_location(board, col)
        for row in range(ROW_COUNT - 1, -1, -1):
            if board[row][col] == 0 and playable:            #this is broken (finding wrong # of openings) 
                openings += 1
            elif board[row][col] != 0:
                playable = False

    return openings
######################################################

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

    # center 
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    # horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c + 4]
            score += evaluate_window(window, piece)

    # vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + 4]
            score += evaluate_window(window, piece)

    # positive diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    # negative diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + 3 - i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score

def is_terminal_node(board):
    return winning_move(board, 1) or winning_move(board, 2) or len(get_valid_locations(board)) == 0
#solver(better then depth)
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
        else:  # Depth is zero // (no longer using depth) :(
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
    player_wins = 0
    ai_wins = 0

    while not game_over:
        
        if turn == 0:
            # player's winning move
            _, predicted_player_wins = minimax(board, 5, -np.Inf, np.Inf, False)
            player_wins = predicted_player_wins

            col = int(input("Player 1 Make your selection (0-6):"))
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 1)

                if winning_move(board, 1):
                    print("Player 1 wins!")
                    player_wins += 1
                    game_over = True
                else:
                    # AI winning move
                    _, predicted_ai_wins = minimax(board, 5, -np.Inf, np.Inf, True)
                    ai_wins = predicted_ai_wins
            else:
                print("Invalid move. Try again.")

        else:
            #AI winning move
            _, predicted_ai_wins = minimax(board, 5, -np.Inf, np.Inf, True)
            ai_wins = predicted_ai_wins

            col, _ = minimax(board, 5, -np.Inf, np.Inf, True)
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 2)

                if winning_move(board, 2):
                    print("Player 2 wins!")
                    ai_wins += 1
                    game_over = True

        player1_percent, player2_percent = calculate_probabilities(board)
        print_board(board, player1_percent, player2_percent, f"Player: {player_wins} of {possible_wins} possible_wins", f"AI: {ai_wins} of {possible_wins} possible_wins")

        turn += 1
        turn = turn % 2

def play_ai_vs_connect4():
    board = create_board()
    game_over = False
    turn = 0
    player_wins = 0
    ai_wins = 0

    while not game_over:
        if turn == 0:
            # AI winning move
            _, predicted_ai_wins = minimax(board, 5, -np.Inf, np.Inf, True)
            ai_wins = predicted_ai_wins

            col, minimax_score = minimax(board, 5, -np.Inf, np.Inf, True)
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 2)

                if winning_move(board, 2):
                    print("AI wins!")
                    ai_wins += 1
                    game_over = True
                else:
                    # player winning move
                    _, predicted_player_wins = minimax(board, 5, -np.Inf, np.Inf, False)
                    player_wins = predicted_player_wins

        else:
            col = int(input("Make your selection (0-6):"))
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 1)

                if winning_move(board, 1):
                    print("Player wins!")
                    player_wins += 1
                    game_over = True

        player1_percent, player2_percent = calculate_probabilities(board)
        print_board(board, player1_percent, player2_percent, f"Player: {player_wins} of {possible_wins} possible_wins", f"AI: {ai_wins} of {possible_wins} possible_wins")

        turn += 1
        turn = turn % 2

def play_ai_vs_ai():
    board = create_board()
    game_over = False
    turn = 0
    player1_wins = 0
    player2_wins = 0

    while not game_over:
        if turn == 0:
            # player 1's winning move
            _, predicted_player1_wins = minimax(board, 5, -np.Inf, np.Inf, True)
            player1_wins = predicted_player1_wins

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
                col, _ = max(depth_results, key=lambda item: item[1])

            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 1)

                if winning_move(board, 1):
                    print("Player 1 wins!")
                    player1_wins += 1
                    game_over = True

        else:
            # Predict player 2's winning move
            _, predicted_player2_wins = minimax(board, 5, -np.Inf, np.Inf, False)
            player2_wins = predicted_player2_wins

            with multiprocessing.Manager() as manager:
                return_dict = manager.dict()
                processes = []
                for d in range(1, 6):  # Adjust range for depth (not using anymore)
                    input_data = (board.copy(), d, -np.Inf, np.Inf, False)
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
                    print("Player 2 wins!")
                    player2_wins += 1
                    game_over = True

        player1_percent, player2_percent = calculate_probabilities(board)
        print_board(board, player1_percent, player2_percent, f"Player 1: {player1_wins} of {possible_wins} possible_wins", f"Player 2: {player2_wins} of {possible_wins} possible_wins")

        turn += 1
        turn = turn % 2

#need to add some error handeling 
def main():
    pick = int(input("Enter 1 to play against the AI, 2 to watch the AI play itself: "))
    if pick == 1:
        player_first = int(input("Enter 1 to make the first move, 2 if you want the AI to make the first move: "))
        if player_first == 1:
            play_connect4_vs_ai()
        elif player_first == 2:
            play_ai_vs_connect4()
        else:
            print("bad choice. try again. :P")
    elif pick == 2:
        play_ai_vs_ai()
    else:
        print("bad choice. try again. :P")

if __name__ == "__main__":
    main()
# shouldent be using 3 diffrent defs for gamemodes slim it down latter

#holy mother of god

#                   _ |\_   woof
#                   \` ..\
#              __,.-" =__Y=
#            ."        )
#      _    /   ,    \/\_
#     ((____|    )_-\ \_-`
#    `-----'`-----` `--`




