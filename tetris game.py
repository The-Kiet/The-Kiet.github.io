import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Size and title
WIDTH =  900
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Tetris Game')

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)

# Define game grid size
COLS = 15
ROWS = 30
BLOCK_SIZE = 20  # Size of each square block

# Position x,y of the grid on the screen
GRID_X = (WIDTH - COLS * BLOCK_SIZE) // 2
GRID_Y = HEIGHT - ROWS * BLOCK_SIZE - 50

# Define Tetris shapes using simple 2D lists of 1s and 0s
SHAPES = [
    # S shape
    [[0,1,1],
     [1,1,0],
     [0,0,0]],

    # Z shape
    [[1,1,0],
     [0,1,1],
     [0,0,0]],

    # I shape
    [[1,1,1,1]],

    # O shape (square)
    [[1,1],
     [1,1]],

    # J shape
    [[1,0,0],
     [1,1,1],
     [0,0,0]],

    # L shape
    [[0,0,1],
     [1,1,1],
     [0,0,0]],

    # T shape
    [[0,1,0],
     [1,1,1],
     [0,0,0]],
]

# Color for each shape
SHAPE_COLORS = [
    (0,255,0),    # Green
    (255,0,0),    # Red
    (0,255,255),  # Cyan
    (255,255,0),  # Yellow
    (0,0,255),    # Blue
    (255,165,0),  # Orange
    (128,0,128),  # Purple
]

# Game states
STATE_MENU = 'menu'
STATE_PLAYING = 'playing'
STATE_GAMEOVER = 'gameover'

# Difficulty speeds in milliseconds for pieces to move down automatically
DIFFICULTY_SPEEDS = {
    'Easy': 700,
    'Medium': 400,
    'Hard': 200,
}

# Font setup
FONT_SMALL = pygame.font.SysFont('Arial', 20)
FONT_LARGE = pygame.font.SysFont('Arial', 40)


def draw_text(text, font, color, surface, x, y):
    """Draw text on the screen at (x,y)."""
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def draw_grid(surface, grid):
    """Draw the grid and the blocks."""
    for row in range(ROWS):
        for col in range(COLS):
            color = grid[row][col]
            pygame.draw.rect(surface, color,
                             (GRID_X + col*BLOCK_SIZE,
                              GRID_Y + row*BLOCK_SIZE,
                              BLOCK_SIZE, BLOCK_SIZE))
            # Draw border for each block
            pygame.draw.rect(surface, GRAY,
                             (GRID_X + col*BLOCK_SIZE,
                              GRID_Y + row*BLOCK_SIZE,
                              BLOCK_SIZE, BLOCK_SIZE), 1)

def create_grid():
    """Create an empty grid (2D list) with all blocks black (empty)."""
    return [[BLACK for _ in range(COLS)] for _ in range(ROWS)]

def check_collision(grid, shape, offset):
    """
    Check if the shape at the given offset collides with placed blocks or edges.
    shape is a 2D list, offset is (x, y) tuple for grid coordinates.
    """
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                grid_x = off_x + x
                grid_y = off_y + y
                # Check height boundaries
                if grid_x < 0 or grid_x >= COLS or grid_y >= ROWS:
                    return True
                # Ignore parts above the screen (grid_y < 0)
                if grid_y >= 0 and grid[grid_y][grid_x] != BLACK:
                    return True
    return False

def remove_complete_lines(grid):
    """
    Remove all full lines from the grid.
    Return number of lines removed.
    """
    lines_removed = 0
    # Make a new grid and fill lines that are not full.
    new_grid = []
    for row in grid:
        if BLACK not in row:
            lines_removed += 1
        else:
            new_grid.append(row)
    # Add empty rows at the top for removed lines
    for _ in range(lines_removed):
        new_grid.insert(0, [BLACK for _ in range(COLS)])
    # Copy back to original grid
    for r in range(ROWS):
        grid[r] = new_grid[r]
    return lines_removed

def rotate_shape(shape):
    """Rotate the shape clockwise by transposing and reversing rows."""
    rotated = zip(*shape[::-1])
    return [list(row) for row in rotated]

def draw_menu(surface):
    """Draw the main menu for selecting difficulty."""
    surface.fill(WHITE)
    draw_text('Simple Tetris', FONT_LARGE, BLACK, surface, WIDTH // 2 - 100, 80)
    draw_text('Choose Difficulty:', FONT_SMALL, BLACK, surface, WIDTH // 2 - 70, 150)

    # Draw buttons for difficulties and quit
    easy_button = pygame.Rect(WIDTH // 2 - 100, 200, 200, 40)
    medium_button = pygame.Rect(WIDTH // 2 - 100, 260, 200, 40)
    hard_button = pygame.Rect(WIDTH // 2 - 100, 320, 200, 40)
    quit_button = pygame.Rect(WIDTH // 2 - 100, 380, 200, 40)

    pygame.draw.rect(surface, (180, 230, 180), easy_button, border_radius=8)
    pygame.draw.rect(surface, (230, 230, 180), medium_button, border_radius=8)
    pygame.draw.rect(surface, (230, 180, 180), hard_button, border_radius=8)
    pygame.draw.rect(surface, (240, 100, 100), quit_button, border_radius=8)

    draw_text('Easy', FONT_SMALL, BLACK, surface, easy_button.x + 80, easy_button.y + 10)
    draw_text('Medium', FONT_SMALL, BLACK, surface, medium_button.x + 70, medium_button.y + 10)
    draw_text('Hard', FONT_SMALL, BLACK, surface, hard_button.x + 80, hard_button.y + 10)
    draw_text('Quit', FONT_SMALL, WHITE, surface, quit_button.x + 85, quit_button.y + 10)

    pygame.display.update()

    return easy_button, medium_button, hard_button, quit_button

def draw_game_over(surface, score):
    """Show Game Over text and buttons."""
    surface.fill(WHITE)
    draw_text('Game Over', FONT_LARGE, (200, 0, 0), surface, WIDTH // 2 - 90, HEIGHT // 2 - 100)
    draw_text(f'Score: {score}', FONT_SMALL, BLACK, surface, WIDTH // 2 - 40, HEIGHT // 2 - 40)

    # Retry, Menu, Quit buttons
    retry_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 40)
    menu_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 40)
    quit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 40)

    pygame.draw.rect(surface, (200, 255, 200), retry_button, border_radius=8)
    pygame.draw.rect(surface, (255, 255, 180), menu_button, border_radius=8)
    pygame.draw.rect(surface, (255, 200, 200), quit_button, border_radius=8)

    draw_text('Retry', FONT_SMALL, BLACK, surface, retry_button.x + 80, retry_button.y + 10)
    draw_text('Menu', FONT_SMALL, BLACK, surface, menu_button.x + 85, menu_button.y + 10)
    draw_text('Quit', FONT_SMALL, BLACK, surface, quit_button.x + 80, quit_button.y + 10)

    pygame.display.update()

    return retry_button, menu_button, quit_button

def draw_score(surface, score):
    """Draw the current score on the screen."""
    draw_text(f'Score: {score}', FONT_SMALL, BLACK, surface, 10, 10)

def draw_difficulty(surface, diff):
    """Draw current difficulty."""
    draw_text(f'Difficulty: {diff}', FONT_SMALL, BLACK, surface, WIDTH - 140, 10)

def draw_controls(surface):
    """Draw small text on controls."""
    draw_text('Arrow keys: Move and rotate', FONT_SMALL, BLACK, surface, 10, HEIGHT - 80)
    draw_text('M: Menu, R: Retry, Q: Quit', FONT_SMALL, BLACK, surface, 10, HEIGHT - 50)

def main():
    clock = pygame.time.Clock()
    running = True
    state = STATE_MENU
    difficulty = 'Easy'

    # Game variables
    grid = create_grid()
    current_shape = random.choice(SHAPES)
    current_color = SHAPE_COLORS[SHAPES.index(current_shape)]
    shape_x = COLS // 2 - len(current_shape[0]) // 2
    shape_y = -2  # Start above the visible grid (rows < 0)
    fall_time = 0
    fall_speed = DIFFICULTY_SPEEDS[difficulty]
    score = 0

    while running:
        if state == STATE_MENU:
            # Show menu and wait for difficulty selection or quit
            easy_btn, med_btn, hard_btn, quit_btn = draw_menu(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if easy_btn.collidepoint((mx, my)):
                        difficulty = 'Easy'
                        fall_speed = DIFFICULTY_SPEEDS[difficulty]
                        # Reset the game
                        grid = create_grid()
                        current_shape = random.choice(SHAPES)
                        current_color = SHAPE_COLORS[SHAPES.index(current_shape)]
                        shape_x = COLS // 2 - len(current_shape[0]) // 2
                        shape_y = -2
                        score = 0
                        state = STATE_PLAYING
                    elif med_btn.collidepoint((mx, my)):
                        difficulty = 'Medium'
                        fall_speed = DIFFICULTY_SPEEDS[difficulty]
                        grid = create_grid()
                        current_shape = random.choice(SHAPES)
                        current_color = SHAPE_COLORS[SHAPES.index(current_shape)]
                        shape_x = COLS // 2 - len(current_shape[0]) // 2
                        shape_y = -2
                        score = 0
                        state = STATE_PLAYING
                    elif hard_btn.collidepoint((mx, my)):
                        difficulty = 'Hard'
                        fall_speed = DIFFICULTY_SPEEDS[difficulty]
                        grid = create_grid()
                        current_shape = random.choice(SHAPES)
                        current_color = SHAPE_COLORS[SHAPES.index(current_shape)]
                        shape_x = COLS // 2 - len(current_shape[0]) // 2
                        shape_y = -2
                        score = 0
                        state = STATE_PLAYING
                    elif quit_btn.collidepoint((mx, my)):
                        running = False
                        break

        elif state == STATE_PLAYING:
            # Game playing state
            fall_time += clock.get_time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        # Move left if no collision
                        if not check_collision(grid, current_shape, (shape_x -1, shape_y)):
                            shape_x -= 1
                    elif event.key == pygame.K_RIGHT:
                        # Move right if no collision
                        if not check_collision(grid, current_shape, (shape_x +1, shape_y)):
                            shape_x += 1
                    elif event.key == pygame.K_DOWN:
                        # Move down faster
                        if not check_collision(grid, current_shape, (shape_x, shape_y +1)):
                            shape_y += 1
                    elif event.key == pygame.K_UP:
                        # Rotate shape
                        rotated = rotate_shape(current_shape)
                        if not check_collision(grid, rotated, (shape_x, shape_y)):
                            current_shape = rotated
                    elif event.key == pygame.K_m:
                        # M key: back to menu
                        state = STATE_MENU
                    elif event.key == pygame.K_r:
                        # R key: retry game
                        grid = create_grid()
                        current_shape = random.choice(SHAPES)
                        current_color = SHAPE_COLORS[SHAPES.index(current_shape)]
                        shape_x = COLS // 2 - len(current_shape[0]) // 2
                        shape_y = -2
                        score = 0
                    elif event.key == pygame.K_q:
                        # Q key: quit game
                        running = False
                        break

            # Automatic fall after timer
            if fall_time > fall_speed:
                fall_time = 0
                if not check_collision(grid, current_shape, (shape_x, shape_y +1)):
                    shape_y += 1
                else:
                    # Fix shape on the grid
                    for y, row in enumerate(current_shape):
                        for x, cell in enumerate(row):
                            if cell:
                                grid_y = shape_y + y
                                grid_x = shape_x + x
                                if grid_y < 0:
                                    # Game over condition: block above screen
                                    state = STATE_GAMEOVER
                                    break
                                grid[grid_y][grid_x] = current_color
                    # Clear full lines
                    lines_cleared = remove_complete_lines(grid)
                    score += lines_cleared * 10
                    # Spawn new shape
                    current_shape = random.choice(SHAPES)
                    current_color = SHAPE_COLORS[SHAPES.index(current_shape)]
                    shape_x = COLS // 2 - len(current_shape[0]) // 2
                    shape_y = -2

                    if state == STATE_GAMEOVER:
                        continue

            # Draw everything in playing state
            screen.fill(WHITE)
            draw_grid(screen, grid)
            # Draw current falling piece
            for y, row in enumerate(current_shape):
                for x, cell in enumerate(row):
                    if cell:
                        draw_x = GRID_X + (shape_x + x)*BLOCK_SIZE
                        draw_y = GRID_Y + (shape_y + y)*BLOCK_SIZE
                        pygame.draw.rect(screen, current_color,
                                         (draw_x, draw_y, BLOCK_SIZE, BLOCK_SIZE))
                        pygame.draw.rect(screen, GRAY,
                                         (draw_x, draw_y, BLOCK_SIZE, BLOCK_SIZE), 1)

            draw_score(screen, score)
            draw_difficulty(screen, difficulty)
            draw_controls(screen)
            pygame.display.update()

        elif state == STATE_GAMEOVER:
            # Show game over screen with options
            retry_btn, menu_btn, quit_btn = draw_game_over(screen, score)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if retry_btn.collidepoint((mx, my)):
                        # Retry same difficulty
                        grid = create_grid()
                        current_shape = random.choice(SHAPES)
                        current_color = SHAPE_COLORS[SHAPES.index(current_shape)]
                        shape_x = COLS // 2 - len(current_shape[0]) // 2
                        shape_y = -2
                        score = 0
                        state = STATE_PLAYING
                    elif menu_btn.collidepoint((mx, my)):
                        # Back to menu
                        state = STATE_MENU
                    elif quit_btn.collidepoint((mx, my)):
                        running = False
                        break

        clock.tick(30)  # Limit to 30 frames per second

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()