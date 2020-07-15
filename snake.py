import json
import random
import sys
import time
import turtle
from collections import deque
from functools import partial
from pathlib import Path

CONSECUTIVE = 3
POINTS = 5
ACCELERATION = 0.9
GAMESPEED = 0.4
SIZE = 400
PIXEL = 25
MOVE_KEYS = ("Up", "Down", "Left", "Right")
LEVELUP = 3
PLAYERS = (
    "Barry A",
    "Barry R",
    "Erez",
    "Gavi",
    "Ido",
    "Noam",
    "Yonaton",
)

do_quit = False
do_play = False
window = turtle.Screen()
window.bgcolor("green")
window.setup(width=SIZE, height=SIZE)
window.tracer(0)

with open("./state.json", "r") as f:
    state = json.load(f)

player_number = int(
    turtle.numinput(
        "Who is playing?", "\n".join([f"{i + 1}. {p}" for i, p in enumerate(PLAYERS)])
    )
)

if not player_number:
    quit()

last = state.get("last")
if len(set(last)) == 1 and last[0] == player_number and len(last) >= CONSECUTIVE:
    print("Someone else's turn")
    quit()

player_key = f"player{player_number}"
player = state.get("players").get(player_key)
player_name = PLAYERS[player_number - 1]
record_holder = (
    PLAYERS[state.get("high_score_holder") - 1]
    if state.get("high_score_holder")
    else None
)

if not player:
    quit()


def _get_random_spot(reducer=1):
    return random.randint(1, (SIZE / 2 / PIXEL) / reducer) * PIXEL


def game_over():
    global state
    global player_key

    score = snake.score()
    player["games"] += 1
    print(
        f"""

    ~~ Game Over ~~

    Your score: {score}
    """
    )
    if score > state.get("high_score"):
        print(f"New record! {score}")
        print(f"Previous: {state['high_score']}")
        state["high_score"] = score
    elif score > player.get("high_score"):
        print(f"Personal best {score}")
        print(f"Previous: {player['high_score']}")
        player["high_score"] = score

    state["players"][player_key] = player
    state["last"].append(player_number)

    if len(state["last"]) >= CONSECUTIVE:
        state["last"] = state["last"][CONSECUTIVE * -1 :]

    with open("./state.json", "w") as f:
        json.dump(state, f)


def quit():
    global do_quit
    do_quit = True
    print("Quit")


def play():
    global do_play
    do_play = True


class SnakeSegment(turtle.Turtle):
    def __init__(self, x, y):
        super().__init__()
        self.speed(0)
        self.shape("square")
        self.color("gray")
        self.penup()
        self.x = x
        self.y = y
        self.goto(self.x, self.y)


class SnakeHead(turtle.Turtle):
    def __repr__(self):
        return f"<SnakeHead {self.x},{self.y}>"

    def __init__(self):
        super().__init__()
        self.speed(0)
        self.shape("square")
        self.color("white")
        self.penup()
        self.x = _get_random_spot(2)
        self.y = _get_random_spot(2)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Food(turtle.Turtle):
    def __repr__(self):
        return f"<Food {self.x},{self.y}>"

    def __init__(self):
        super().__init__()
        self.speed(0)
        self.shape("square")
        self.color("yellow")
        self.penup()
        self.place()

    def place(self):
        self.x = _get_random_spot(2)
        self.y = _get_random_spot(2)
        self.goto(self.x, self.y)


class Snake:
    def __init__(self, window):
        self.window = window
        self.head = SnakeHead()
        self.body = deque()
        self.food = Food()
        self.moves = 0
        self.length = 0
        self.pace = GAMESPEED
        self.set_direction(random.choice(MOVE_KEYS))

    def set_direction(self, direction):
        self.direction = direction

    def move(self):
        if self.moves > 0:
            self.body.append(SnakeSegment(self.head.x, self.head.y))

            while self.length < len(self.body):
                segment = self.body.popleft()
                segment.hideturtle()
                del segment

        if self.direction == "Up":
            self.head.y += PIXEL
        elif self.direction == "Down":
            self.head.y -= PIXEL
        elif self.direction == "Left":
            self.head.x -= PIXEL
        elif self.direction == "Right":
            self.head.x += PIXEL
        self.head.goto(self.head.x, self.head.y)
        self.moves += 1
        self.window.update()

    def is_off_screen(self):
        return any(
            coord >= SIZE / 2 or coord <= SIZE / 2 * -1
            for coord in (self.head.x, self.head.y)
        )

    def is_collision(self):
        return any(self.head == segment for segment in self.body)

    def is_eating(self):
        return self.head == self.food

    def grow(self):
        self.food.place()
        self.length += 1
        if self.length % LEVELUP == 0:
            snake.pace *= ACCELERATION

    def score(self):
        return sum(
            (x + 1) * POINTS for x in range(self.length)
        )  # + (self.moves * POINTS)


snake = Snake(window)
snake.move()
window.listen()
window.onkey(quit, "q")
window.onkey(play, "space")
score = turtle.Turtle()
score.ht()
for key in MOVE_KEYS:
    window.onkey(partial(snake.set_direction, key), key)
while True:
    score.clear()
    text = f"  Current score for {player_name}: {snake.score()}"
    if record_holder:
        text += f"\n  Record by {record_holder}: {state['high_score']}"
    text += "\n\n"
    score.write(
        text, font=("Arial", 14, "normal"), align="center",
    )
    window.update()
    if do_play:
        snake.move()
    time.sleep(snake.pace)
    window.update()
    if snake.is_off_screen() or snake.is_collision():
        game_over()
        break
    elif snake.is_eating():
        snake.grow()
    elif do_quit:
        break
