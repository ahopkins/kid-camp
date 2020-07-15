import random
import sys
import time
import turtle
from dataclasses import dataclass, field
from functools import partial
from operator import add, sub
from queue import Queue

SEED = int(sys.argv[1])
SIZE = 400
PIXEL = 25
LOOP = 0.15

LEFT = (int(SIZE / 2) - PIXEL) * -1
RIGHT = int(SIZE / 2) - PIXEL
BOTTOM = (int(SIZE / 2) - PIXEL) * -1
TOP = int(SIZE / 2) - PIXEL


wall_points = []
visited = []
points = {}
target = None
freestyle = True


@dataclass
class Point:
    x: int
    y: int
    is_wall: bool = field(default=True, hash=False)

    def __post_init__(self):
        global wall_points
        wall_points.append(self)
        points[(self.x, self.y)] = self

    @property
    def neighbors(self):
        global points
        return [
            points.get((self.x - PIXEL, self.y)),
            points.get((self.x + PIXEL, self.y)),
            points.get((self.x, self.y - PIXEL)),
            points.get((self.x, self.y + PIXEL)),
        ]


class Wall(turtle.Turtle):
    def __init__(self, point):
        super().__init__()
        self.speed(0)
        self.shape("square")
        self.color("gray")
        self.penup()
        self.point = point
        self.goto(self.point.x, self.point.y)


class Target(turtle.Turtle):
    def __init__(self, point):
        super().__init__()
        self.speed(0)
        self.shape("square")
        self.color("yellow")
        self.penup()
        self.point = point
        self.goto(self.point.x, self.point.y)


random.seed(SEED)
window = turtle.Screen()
window.bgcolor("green")
window.setup(width=SIZE, height=SIZE)
window.tracer(0)
do_quit = False


def quit():
    global do_quit
    do_quit = True
    print("Quit")


def crash():
    print("Crashed!")


def oob():
    print("Out of bounds!")


def win():
    print("You win!")


for x in range(LEFT, RIGHT, PIXEL):
    for y in range(BOTTOM, TOP, PIXEL):
        point = Point(x, y)

current = points.get((LEFT, BOTTOM))
current.is_wall = False
wall_points.remove(current)
visited.append(current)
wall_list = list(filter(lambda x: x and x.is_wall, current.neighbors))
target = None
while wall_list:
    current = random.choice(wall_list)
    # neighbors = list(filter(lambda x: x, current.neighbors))
    if (
        current not in visited
        and len(list(filter(lambda x: x and not x.is_wall, current.neighbors))) == 1
    ):
        target = current
        current.is_wall = False
        points[(current.x, current.y)].is_wall = False
        wall_points.remove(current)
        visited.append(current)
        wall_list += list(filter(lambda x: x and x.is_wall, current.neighbors))
    wall_list.remove(current)


def setup():
    global wall_points
    global target
    global freestyle

    freestyle = False
    target = Target(target)

    for point in wall_points:
        Wall(point)


class GameTurtle(turtle.Turtle):
    def __init__(self):
        super().__init__()
        self.speed(10)
        self.shape("arrow")
        self.color("black")
        self.penup()
        self.goto(LEFT, BOTTOM)
        self.pendown()
        self.point = points.get((LEFT, BOTTOM))
        self.direction = 90
        self.instructions = Queue()

    _f = turtle.Turtle.forward
    _l = turtle.Turtle.left
    _r = turtle.Turtle.right
    _b = turtle.Turtle.backward

    def forward(self, value=1):
        global freestyle
        for _ in range(value):
            self.instructions.put(partial(self._f, PIXEL))
            if not freestyle:
                self.instructions.put(self.update_point)

    def left(self, value=90):
        global freestyle
        if not freestyle and value % 90 != 0:
            raise Exception("Right angles only")
        self.instructions.put(partial(self._l, value))
        if not freestyle:
            self.instructions.put(partial(self.turn, value * -1))

    def right(self, value=90):
        global freestyle
        if not freestyle and value % 90 != 0:
            raise Exception("Right angles only")
        self.instructions.put(partial(self._r, value))
        if not freestyle:
            self.instructions.put(partial(self.turn, value))

    def backward(self, value=1):
        global freestyle
        for _ in range(value):
            self.instructions.put(partial(self._b, PIXEL))
            if not freestyle:
                self.instructions.put(partial(self.update_point, True))

    def turn(self, value):
        self.direction += value
        self.direction = (self.direction + 360) % 360

    def update_point(self, backward=False):
        a = sub if backward else add
        s = add if backward else sub
        if self.direction == 0:
            self.point = points.get((self.point.x, a(self.point.y, PIXEL)))
        elif self.direction == 90:
            self.point = points.get((a(self.point.x, PIXEL), self.point.y))
        elif self.direction == 180:
            self.point = points.get((self.point.x, s(self.point.y, PIXEL)))
        elif self.direction == 270:
            self.point = points.get((s(self.point.x, PIXEL), self.point.y))

    def do_instruction(self):
        if not self.instructions.empty():
            self.instructions.get()()


t = GameTurtle()


window.listen()
window.onkey(quit, "q")


def debug():
    while True:
        window.update()
        time.sleep(LOOP)

        if do_quit:
            break


def run():
    global t

    while True:
        window.update()
        t.do_instruction()
        time.sleep(LOOP)

        if do_quit:
            break

        if not freestyle:
            if t.point.is_wall:
                crash()
                break
            elif not t.point:
                oob()
                break
            elif t.point == target.point:
                win()
                break

    while True:
        window.update()
        time.sleep(LOOP)
        if do_quit:
            break
