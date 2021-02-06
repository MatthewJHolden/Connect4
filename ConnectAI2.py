import numpy as np
import random
import pygame
import sys
import math

# https://en.wikipedia.org/wiki/Minimax#Pseudocode
# https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning
#


BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER = 0
AI = 1

PLAYER_PIECE = 1
AI_PIECE = 2

WINDOWLENGTH = 4
EMPTY = 0

def create_board():
    board = np.zeros((ROW_COUNT,COLUMN_COUNT))
    return board


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0


def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r


def print_board(board):
    print(np.flip(board, 0))


def winning_move(board, piece):
    # check all horizontal locations for win
    for c in range(COLUMN_COUNT-3): #COLUMN_COUNT-3 because working from left to right if there is no piece
        # at position COLUMN_COUNT-3 then not possible to have winning move -> same logic for rest
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
    # Check for vertical locations for win
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
             return True
    # Check for positively sloped diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True
    # Check for negatively sloped diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(3,ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE
    if window.count(piece) == 4:
        score += 4
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score

def score_position(board, piece):
    score = 0
    # Score Centre
    centre_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
    centre_count = centre_array.count(piece)
    score += centre_count * 3

    # Score Horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT-3):
            window = row_array[c:c+WINDOWLENGTH]
            score += evaluate_window(window, piece)
    # Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT-3):
            window = col_array[r:WINDOWLENGTH]
            score += evaluate_window(window, piece)
    # Score positive sloped diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+i][c+i] for i in range(WINDOWLENGTH)]
            score += evaluate_window(window, piece)
    # Score negative sloped diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+3-i][c+i] for i in range(WINDOWLENGTH)]
            score += evaluate_window(window, piece)

    return score


def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 10000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000)
            else: # Game is over, no more valid moves
                return (None, 0)
        else: #Depth is zero
            return (None, score_position(board, AI_PIECE))
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board,col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else: #minimising player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
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
        if is_valid_location(board,col):
            valid_locations.append(col)
    return valid_locations


def pick_best_move(board,piece):
    valid_locations = get_valid_locations(board)
    best_score = -1000
    best_col = random.choice(valid_locations)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col

    return best_col

class button():
    def __init__(self, color, x, y, width, height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, win, outline=None):
        # Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)

        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)

        if self.text != '':
            font = pygame.font.SysFont('comicsans', 60)
            text = font.render(self.text, 1, (0, 0, 0))
            win.blit(text, (
            self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    def isOver(self, pos):
        # Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True

        return False

def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED, (int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(screen, YELLOW,(int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)),RADIUS)
    pygame.display.update()

def text_objects(msg):
    font = pygame.font.Font(pygame.font.get_default_font(), 36)
    textSurface = font.render(msg, True, YELLOW)
    # pygame.display.update(textSurface)
    return textSurface, textSurface.get_rect()


def draw_main_screen(difficulty):
    # pygame.draw.rect(screen, BLUE, (SQUARESIZE, SQUARESIZE, SQUARESIZE, SQUARESIZE))
    startbutton.draw(screen,(0,0,0))
    level1button.draw(screen,(0,0,0))
    level2button.draw(screen, (0, 0, 0))
    level3button.draw(screen, (0, 0, 0))
    level4button.draw(screen, (0, 0, 0))
    level5button.draw(screen, (0, 0, 0))
    # label = mainfont.render("Select Difficulty Level", 1, YELLOW)
    # screen.blit(label, (125, 350))
    # color = (0, 255, 0)
    msg = f'Select Difficulty Level:'
    textSurf, textRect = text_objects(msg)
    textRect.center = (width/2), STARTHEIGHT + 275
    screen.blit(textSurf,textRect)
    msg2 = f'Difficulty Level: {difficulty}'
    textSurf, textRect = text_objects(msg2)
    textRect.center = (width/2), STARTHEIGHT + 175
    screen.blit(textSurf,textRect)
    pygame.display.update()

board = create_board()
print_board(board)
game_over = False

pygame.init()

SQUARESIZE = 100

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE
size = (width,height)
RADIUS = int(SQUARESIZE/2 - 5)
STARTHEIGHT = 100
screen = pygame.display.set_mode(size)
startbutton = button((0, 255, 0), 225, STARTHEIGHT, 250, 100, 'Start Game')
difficultyY = STARTHEIGHT + 325
difficulty = 3
level1button = button((0, 255, 0), 25, difficultyY, 100, 100, '1')
level2button = button((0, 255, 0), (550/4+25), difficultyY, 100, 100, '2')
level3button = button((0, 255, 0), (550/4*2+25), difficultyY, 100, 100, '3')
level4button = button((0, 255, 0), (550/4*3+25), difficultyY, 100, 100, '4')
level5button = button((0, 255, 0), 575, difficultyY, 100, 100, '5')
myfont = pygame.font.SysFont("monospace", 75)
mainfont = pygame.font.SysFont("monospace", 25)
# Main Screen Loop
home = True

turn = random.randint(PLAYER,AI)

while not game_over:

    while home:
        pygame.display.update()
        draw_main_screen(difficulty)

        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()

            if event.type == pygame.QUIT:
                sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if startbutton.isOver(pos):
                home = False
            if level1button.isOver(pos):
                screen.fill((0,0,0))
                difficulty = 1
                draw_main_screen(difficulty)
            if level2button.isOver(pos):
                screen.fill((0, 0, 0))
                difficulty = 2
                draw_main_screen(difficulty)
            if level3button.isOver(pos):
                screen.fill((0, 0, 0))
                difficulty = 3
                draw_main_screen(difficulty)
            if level4button.isOver(pos):
                screen.fill((0, 0, 0))
                difficulty = 4
                draw_main_screen(difficulty)
            if level5button.isOver(pos):
                screen.fill((0, 0, 0))
                difficulty = 5
                draw_main_screen(difficulty)

        if event.type == pygame.MOUSEMOTION:
            if startbutton.isOver(pos):
                startbutton.color = (255, 0, 0)
            else:
                startbutton.color = (0, 255, 0)
            if level1button.isOver(pos):
                level1button.color = (255, 0, 0)
            else:
                level1button.color = (0, 255, 0)
            if level2button.isOver(pos):
                level2button.color = (255, 0, 0)
            else:
                level2button.color = (0, 255, 0)
            if level3button.isOver(pos):
                level3button.color = (255, 0, 0)
            else:
                level3button.color = (0, 255, 0)
            if level4button.isOver(pos):
                level4button.color = (255, 0, 0)
            else:
                level4button.color = (0, 255, 0)
            if level5button.isOver(pos):
                level5button.color = (255, 0, 0)
            else:
                level5button.color = (0, 255, 0)

    draw_board(board)
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0,0,width,SQUARESIZE))
            posx = event.pos[0]
            if turn == PLAYER:
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
            # else:
            #     pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE / 2)), RADIUS)
        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            # print(event.pos)
            # Ask for Player 1 Input
            if turn == PLAYER:
                posx = event.pos[0]
                col = int(math.floor(posx/SQUARESIZE))

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER_PIECE)
                    pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))

                    if winning_move(board, PLAYER_PIECE):
                        pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                        label = myfont.render("Player 1 Wins!!", 1, RED)
                        screen.blit(label, (40,10))
                        game_over = True

                    turn += 1
                    turn = turn % 2

                    # print_board(board)
                    draw_board(board)


    # Ask for AI Input
    if turn == AI and not game_over:

        # col = random.randint(0, COLUMN_COUNT-1)#
        # col = pick_best_move(board, AI_PIECE)
        col,mimimax_score = minimax(board,difficulty, -math.inf, math.inf, True)

        if is_valid_location(board, col):
            pygame.time.wait(500)
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, AI_PIECE)

            if winning_move(board, AI_PIECE):
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                label = myfont.render("Player 2 Wins!!", 1, YELLOW)
                screen.blit(label, (40,10))
                game_over = True

            print_board(board)
            draw_board(board)

            turn += 1
            turn = turn % 2

    while game_over:
        msg = f'Press X to Exit'
        font = pygame.font.Font(pygame.font.get_default_font(), 36)
        textSurf = font.render(msg, True, (255,255,255))
        textRect = textSurf.get_rect()
        textSurf, textRect = text_objects(msg)
        textRect.center = (width / 2), 95
        screen.blit(textSurf, textRect)
        pygame.display.update()

        game_over = True
        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()

            if event.type == pygame.QUIT:
                sys.exit()
