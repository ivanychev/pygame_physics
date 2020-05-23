import dataclasses as dc
import turtle
import math
import random

from typing import List

WIDTH = 800
HEIGHT = 500
FRAMES_PER_SECOND = 30
TICK_TIME_SECONDS = 1 / FRAMES_PER_SECOND
TICK_TIME_MILLIS = int(TICK_TIME_SECONDS * 1000)
GRID_GRANULARITY = 100
BALL_MASS = 20
G = 10
GRAVITY_CONST = 20

@dc.dataclass
class Ball:
    turtle: turtle.Turtle
    x: float
    y: float
    dx: float
    dy: float
    m: float

    def __post_init__(self):
        self.turtle.shape("circle")
        self.turtle.color("white")
        self.turtle.penup()
        self.turtle.speed("fastest")
        self.turtle.setx(int(self.x))
        self.turtle.sety(int(self.y))

    @classmethod
    def create_random(cls, x_max=WIDTH, y_max=HEIGHT, velocity_max=10):
        x = x_max * random.random()
        y = y_max * random.random()
        dx = velocity_max * random.random()
        dy = velocity_max * random.random()

        return cls(turtle.Turtle(), x, y, dx, dy, BALL_MASS)

    def tick(self, context):
        x, y, dx, dy = self.x, self.y, self.dx, self.dy

        x += dx * TICK_TIME_SECONDS
        y += dy * TICK_TIME_SECONDS
        dy -= G * TICK_TIME_SECONDS

        # Ball gravity.
        for ball in context.nearby_balls(self):
            r_x = ball.x - x
            r_y = ball.y - y
            r_x_squared = r_x * r_x
            r_y_squared = r_y * r_y
            r_squared = r_x_squared + r_y_squared
            f_abs = GRAVITY_CONST * self.m * ball.m / r_squared
            f_abs_squared = f_abs ** 2
            f_x = math.copysign((r_x_squared / r_squared) * f_abs_squared, r_x)
            f_y = math.copysign((r_y_squared / r_squared) * f_abs_squared, r_y)
            a_x = f_x / self.m
            a_y = f_y / self.m

            dx += a_x * TICK_TIME_SECONDS
            dy += a_y * TICK_TIME_SECONDS


        if x < 0:
            dx = abs(dx)
        if x > WIDTH:
            dx = -abs(dx)
        if y < 0:
            dy = abs(dy)
        if y > HEIGHT:
            dy = -abs(dy)
        if abs(dx) > 100:
            dx = math.copysign(100, dx)
        if abs(dy) > 100:
            dy = math.copysign(100, dy)

        self.x, self.y, self.dx, self.dy = x, y, dx, dy

    def draw(self):
        self.turtle.setx(int(self.x))
        self.turtle.sety(int(self.y))

@dc.dataclass
class BallContext:
    space_greed: List[List[List[Ball]]]

    @classmethod
    def from_balls(cls, balls: List[Ball]):
        grid = [[[] for _ in range(HEIGHT // GRID_GRANULARITY + 1)] for _ in range(WIDTH // GRID_GRANULARITY + 1)]
        for ball in balls:
            grid_x = int(math.floor(ball.x / GRID_GRANULARITY))
            grid_y = int(math.floor(ball.y / GRID_GRANULARITY))
            grid[grid_x][grid_y].append(ball)
        return cls(grid)

    def nearby_balls(self, ball):
        ball_grid_x = int(math.floor(ball.x / GRID_GRANULARITY))
        ball_grid_y = int(math.floor(ball.y / GRID_GRANULARITY))
        for delta_x in (-1, 0, 1):
            for delta_y in (-1, 0, 1):
                grid_x = ball_grid_x + delta_x
                grid_y = ball_grid_y + delta_y
                if (not (0 <= grid_x < len(self.space_greed)) or
                    not (0 <= grid_y < len(self.space_greed[0]))):
                    continue
                for current_ball in self.space_greed[grid_x][grid_y]:
                    if ball is not current_ball:
                        yield current_ball

def simulate(screen, balls, context):
    turtle.tracer(0, 0)
    for ball in balls:
        ball.tick(context)
    for ball in balls:
        ball.draw()
    updated_context = BallContext.from_balls(balls)
    def func():
        simulate(screen, balls, updated_context)
    screen.ontimer(func, TICK_TIME_MILLIS)
    turtle.update()


def main():
    screen = turtle.Screen()
    turtle.tracer(0, 0)
    screen.bgcolor("Black")
    screen.setup(WIDTH + 4, HEIGHT + 4)
    screen.setworldcoordinates(0, 0, WIDTH, HEIGHT)

    balls = [Ball.create_random() for _ in range(100)]
    context = BallContext.from_balls(balls)
    simulate(screen, balls, context)

    screen.mainloop()


if __name__ == "__main__":
    main()
