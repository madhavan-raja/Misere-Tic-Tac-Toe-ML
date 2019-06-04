import numpy as np
import random
import pickle

# Symbol for occupied and unoccupied spaces in the grid
PLAYER = 'X'
EMPTY = '-'

# File name for the Learning Data
FILE = 'mttt.dat'

# Color for last move
TEXT_COLOR = '31'
BG_COLOR = '48'
COLOR = F'0;{TEXT_COLOR};{BG_COLOR}'

# Global list for the grid
board = [EMPTY for x in range(9)]

game_count = 0
computer_win = 0
player_win = 0

is_learning = False

forbidden_moves = []
current_computer_moves = []


def reset_game():
    global board, game_count
    board = [EMPTY for x in range(9)]
    game_count += 1


def draw_board(last_move):
    for cell in range(9):
        if cell == 3 or cell == 6:
            print()

        if cell == last_move:
            print('\x1b[' + COLOR + 'm' + board[cell] + '\x1b[0m', end=' ')
        else:
            print(board[cell], end=' ')
    print()


def did_end():
    return (board[0] == PLAYER and board[1] == PLAYER and board[2] == PLAYER) or \
           (board[3] == PLAYER and board[4] == PLAYER and board[5] == PLAYER) or \
           (board[6] == PLAYER and board[7] == PLAYER and board[8] == PLAYER) or \
           (board[0] == PLAYER and board[3] == PLAYER and board[6] == PLAYER) or \
           (board[1] == PLAYER and board[4] == PLAYER and board[7] == PLAYER) or \
           (board[2] == PLAYER and board[5] == PLAYER and board[8] == PLAYER) or \
           (board[0] == PLAYER and board[4] == PLAYER and board[8] == PLAYER) or \
           (board[2] == PLAYER and board[4] == PLAYER and board[6] == PLAYER)


def is_empty():
    return board.count(EMPTY) == 9


def player_move():
    global board

    while True:
        try:
            move = int(input('Enter a cell: '))

            if 0 <= move <= 8:
                if board[move] == EMPTY:
                    break
                else:
                    print('The selected cell is not empty!')
            else:
                print('Enter a number between 0 and 8!')
        except ValueError:
            print("Enter a valid number!")

    board[move] = PLAYER

    return move


def computer_move():
    global board, current_computer_moves

    # List all the possible moves excluding all the forbidden moves.
    # If the list is empty, don't exclude the forbidden moves (Pure Random Move).
    possible_moves = [x for (x, val) in enumerate(board[:]) if val == EMPTY
                      and (board[:], x) not in forbidden_moves]
    if not possible_moves:
        possible_moves = [x for (x, val) in enumerate(board[:]) if val == EMPTY]

    move = random.choice(possible_moves)

    # Append information of current move into a list
    if is_learning and not is_empty():
        current_computer_moves.append((board[:], move))

    board[move] = PLAYER

    return move


def main():
    global forbidden_moves, current_computer_moves, player_win, computer_win, is_learning

    # Will the game use an existing Learnt Data?
    save_file_prompt = input('Press Y to use Learning Data from file. ')

    if save_file_prompt[0] == 'y' or save_file_prompt[0] == 'Y':
        try:
            learning_file = open(FILE, 'rb')
            forbidden_moves = pickle.load(learning_file)
            learning_file.close()

            print('Using Learning Data from file.')
        except FileNotFoundError:
            print(F'File {FILE} does not exists!')
    else:
        print('Not using Learning Data from file.')

    # Will the game learn the wrong moves?
    learning_prompt = input('Press Y for the game to Learn. ')

    if learning_prompt[0] == 'y' or learning_prompt[0] == 'Y':
        is_learning = True
        print('Learning is enabled.')
    else:
        print('Learning is disabled.')

    print()

    while True:
        reset_game()

        print(F'GAME {game_count}')

        # Either the player or the computer can start (50/50 chance)
        turn = random.choice(range(2))

        # Draw the board if the player moves first
        if turn == 0:
            draw_board(9)

        while not did_end():
            if turn % 2 == 0:
                last_move = player_move()
                print(F'Player moved at {last_move}.')
            else:
                last_move = computer_move()
                print(F'Computer moved at {last_move}.')

            draw_board(last_move)

            turn += 1

        if turn % 2 == 0:
            print('You Win.')

            # Append the elements of current computer moves to the forbidden moves
            if is_learning:
                # Do this while the list is not empty
                while current_computer_moves:
                    # If the last move is not in forbidden_moves, append it and break
                    # Otherwise, pop it and do it again
                    if current_computer_moves[-1] not in forbidden_moves:
                        normal_list, move = current_computer_moves[-1]

                        indices = np.array(range(9)).reshape(3, 3)
                        indices_right = np.rot90(indices, 1)
                        indices_inverse = np.rot90(indices, 2)
                        indices_left = np.rot90(indices, 3)

                        normal = np.array(normal_list).reshape(3, 3)
                        normal_right = np.rot90(normal, 1)
                        normal_inverse = np.rot90(normal, 2)
                        normal_left = np.rot90(normal, 3)

                        forbidden_moves.append((normal.ravel().tolist(),
                                                indices.ravel().tolist()[move]))
                        forbidden_moves.append((normal_right.ravel().tolist(),
                                                indices_right.ravel().tolist()[move]))
                        forbidden_moves.append((normal_inverse.ravel().tolist(),
                                                indices_inverse.ravel().tolist()[move]))
                        forbidden_moves.append((normal_left.ravel().tolist(),
                                                indices_left.ravel().tolist()[move]))
                        break
                    current_computer_moves.pop()

            player_win += 1
        else:
            print('You Lose.')
            computer_win += 1

        print(F'W/L is {player_win}/{computer_win}.')

        if is_learning:
            current_computer_moves.clear()

        # Play another game?
        next_game_prompt = input('Press Y to play another game. ')
        if next_game_prompt != 'y' and next_game_prompt != 'Y':
            if is_learning:
                # Save the current Learnt Data?
                dump_prompt = input(F'Press Y to save current Learning Data to file ({FILE}). ')
                if dump_prompt == 'y' or dump_prompt == 'Y':
                    try:
                        learning_file = open(FILE, 'wb')
                        pickle.dump(forbidden_moves, learning_file)
                        learning_file.close()
                    except FileNotFoundError:
                        print('Error writing to file!')
            break

        print()


if __name__ == '__main__':
    main()
