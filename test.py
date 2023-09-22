import curses
import random

# Initialize the screen
stdscr = curses.initscr()
curses.curs_set(0)  # Hide the cursor
curses.noecho()  # Don't print key presses to the screen
curses.start_color()  # Enable colors

# Set up colors
curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

# Initialize the game state
snake = [(4, 10), (4, 9), (4, 8)]  # Initial snake position
direction = curses.KEY_RIGHT  # Initial direction
food = (10, 20)  # Initial food position
score = 0

# Set up the screen
stdscr.clear()
stdscr.border()

# Main game loop
while True:
    # Move the snake
    head = snake[0]
    x, y = head[0], head[1]
    if direction == curses.KEY_UP:
        y -= 1
    elif direction == curses.KEY_DOWN:
        y += 1
    elif direction == curses.KEY_LEFT:
        x -= 1
    elif direction == curses.KEY_RIGHT:
        x += 1
    snake.insert(0, (x, y))

    # Check if the snake has collided with the wall or itself
    if x == 0 or x == curses.COLS - 1 or y == 0 or y == curses.LINES - 1 or head in snake[1:]:
        break

    # Check if the snake has eaten the food
    if head == food:
        # Generate a new piece of food
        food = None
        while food is None:
            new_food = (random.randint(1, curses.COLS - 2), random.randint(1, curses.LINES - 2))
            if new_food not in snake:
                food = new_food
        score += 1
    else:
        snake.pop()

    # Draw the screen
    stdscr.clear()
    stdscr.border()
    stdscr.addstr(0, 2, 'Score: ' + str(score))
    stdscr.addstr(food[0], food[1], '*', curses.color_pair(1))
    for i, (x, y) in enumerate(snake):
        if i == 0:
            stdscr.addstr(y, x, 'X', curses.color_pair(2))
        else:
            stdscr.addstr(y, x, '#', curses.color_pair(2))
    stdscr.refresh()

    # Wait for user input
    c = stdscr.getch()
    if c in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]:
        direction = c

# End the game
curses.endwin()
print('You scored', score, 'points!')
