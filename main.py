
from random import choice, random

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Ellipse, Line
from kivy.metrics import dp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window

Window.clearcolor = (.008, .018, .012, 1)


class Board(Widget):
    def __init__(self, **kw):
        super().__init__(**kw)

        self.n = 18
        self.snake = []
        self.food = None
        self.gold_food = None
        self.green_food = None

        self.direction = (1, 0)
        self.next_dir = (1, 0)

        self.running = False
        self.score = 0
        self.start_touch = None

        self.bind(pos=self.draw, size=self.draw)

        self.reset()
        Clock.schedule_interval(self.step, .15)

    def reset(self):
        self.snake = [
            (5, 9), (4, 9), (3, 9), (2, 9), (1, 9)
        ]

        self.direction = (1, 0)
        self.next_dir = (1, 0)

        self.score = 0
        self.running = False

        self.gold_food = None
        self.green_food = None

        self.spawn()
        self.draw()

        if hasattr(self, "score_cb"):
            self.score_cb(0)

    def begin(self):
        self.reset()
        self.running = True

    def spawn(self):
        free = [
            (x, y)
            for x in range(self.n)
            for y in range(self.n)
            if (x, y) not in self.snake
            and (x, y) != self.gold_food
            and (x, y) != self.green_food
        ]

        self.food = choice(free) if free else None

    def spawn_special(self):
        occupied = set(self.snake)

        if self.food:
            occupied.add(self.food)

        free = [
            (x, y)
            for x in range(self.n)
            for y in range(self.n)
            if (x, y) not in occupied
            and (x, y) != self.gold_food
            and (x, y) != self.green_food
        ]

        if not free:
            return

        if self.gold_food is None and random() < .45:
            self.gold_food = choice(free)
            free.remove(self.gold_food)

        if free and self.green_food is None and random() < .35:
            self.green_food = choice(free)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.start_touch = touch.pos
            return True

        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.start_touch:
            dx = touch.x - self.start_touch[0]
            dy = touch.y - self.start_touch[1]

            self.start_touch = None

            if max(abs(dx), abs(dy)) > dp(18):
                if abs(dx) > abs(dy):
                    direction = (1, 0) if dx > 0 else (-1, 0)
                else:
                    direction = (0, 1) if dy > 0 else (0, -1)

                opposite = (
                    -self.direction[0],
                    -self.direction[1]
                )

                if direction != opposite:
                    self.next_dir = direction

            return True

        return super().on_touch_up(touch)

    def step(self, dt):
        if not self.running:
            return

        self.direction = self.next_dir

        x, y = self.snake[0]
        dx, dy = self.direction

        # عبور از دیوار و ورود از سمت مقابل
        head = (
            (x + dx) % self.n,
            (y + dy) % self.n
        )

        # برخورد با بدن مار
        if head in self.snake[:-1]:
            self.running = False

            if hasattr(self, "over_cb"):
                self.over_cb()

            self.draw()
            return

        self.snake.insert(0, head)

        # سیب قرمز
        if head == self.food:
            self.score += 10
            self.spawn()
            self.spawn_special()

        # سیب طلایی
        elif head == self.gold_food:
            self.score += 50
            self.gold_food = None
            self.spawn_special()

        # جایزه سبز
        elif head == self.green_food:
            self.score += 30
            self.green_food = None
            self.spawn_special()

        else:
            self.snake.pop()

        if hasattr(self, "score_cb"):
            self.score_cb(self.score)

        self.draw()

    def draw_food(self, x0, y0, cell, position, kind):
        if position is None:
            return

        fx, fy = position
        px = x0 + fx * cell
        py = y0 + fy * cell

        if kind == "red":
            Color(.8, .015, .025, 1)
            Ellipse(
                pos=(px+cell*.12, py+cell*.12),
                size=(cell*.76, cell*.76)
            )

            Color(1, .4, .3, 1)
            Ellipse(
                pos=(px+cell*.25, py+cell*.62),
                size=(cell*.16, cell*.10)
            )

        elif kind == "gold":
            Color(1, .72, .02, 1)
            Ellipse(
                pos=(px+cell*.10, py+cell*.10),
                size=(cell*.80, cell*.80)
            )

            Color(1, 1, .55, 1)
            Ellipse(
                pos=(px+cell*.22, py+cell*.58),
                size=(cell*.2, cell*.15)
            )

        elif kind == "green":
            Color(.15, 1, .15, 1)
            Ellipse(
                pos=(px+cell*.12, py+cell*.12),
                size=(cell*.76, cell*.76)
            )

            Color(.7, 1, .5, 1)
            Ellipse(
                pos=(px+cell*.28, py+cell*.58),
                size=(cell*.17, cell*.13)
            )

        Color(.4, 1, .2, 1)
        Line(
            points=[
                px+cell*.5, py+cell*.8,
                px+cell*.56, py+cell*.98
            ],
            width=1.4
        )

    def draw(self, *args):
        self.canvas.clear()

        if self.width <= 0 or self.height <= 0:
            return

        side = min(self.width * .94, self.height * .94)

        x0 = self.center_x - side / 2
        y0 = self.center_y - side / 2

        cell = side / self.n

        with self.canvas:
            Color(.02, .12, .045, .5)
            RoundedRectangle(
                pos=(x0-dp(3), y0-dp(3)),
                size=(side+dp(6), side+dp(6)),
                radius=[dp(28)]
            )

            Color(.006, .018, .011, 1)
            RoundedRectangle(
                pos=(x0, y0),
                size=(side, side),
                radius=[dp(26)]
            )

            Color(.13, .23, .16, .38)

            for i in range(self.n + 1):
                Line(
                    points=[
                        x0+i*cell, y0,
                        x0+i*cell, y0+side
                    ],
                    width=.55
                )

                Line(
                    points=[
                        x0, y0+i*cell,
                        x0+side, y0+i*cell
                    ],
                    width=.55
                )

            # غذاها
            self.draw_food(x0, y0, cell, self.food, "red")
            self.draw_food(x0, y0, cell, self.gold_food, "gold")
            self.draw_food(x0, y0, cell, self.green_food, "green")

            # بدن مار
            for i, (sx, sy) in enumerate(reversed(self.snake)):
                px = x0 + sx*cell
                py = y0 + sy*cell

                p = dp(1.2)

                if i == len(self.snake)-1:
                    Color(.1, 1, .1, .2)
                    RoundedRectangle(
                        pos=(px, py),
                        size=(cell, cell),
                        radius=[cell*.25]
                    )

                Color(.12, .95, .08, 1)
                RoundedRectangle(
                    pos=(px+p, py+p),
                    size=(cell-2*p, cell-2*p),
                    radius=[cell*.23]
                )

                Color(.65, 1, .48, .8)
                Line(
                    rounded_rectangle=(
                        px+p, py+p,
                        cell-2*p, cell-2*p,
                        cell*.23
                    ),
                    width=.7
                )

            # چشم سر مار
            hx, hy = self.snake[0]

            cx = x0 + (hx+.5)*cell
            cy = y0 + (hy+.5)*cell

            dx, dy = self.direction

            ex = cx + (dx*.18-dy*.16)*cell
            ey = cy + (dy*.18+dx*.16)*cell

            Color(.005, .008, .003, 1)
            Ellipse(
                pos=(ex-cell*.085, ey-cell*.085),
                size=(cell*.17, cell*.17)
            )


class LuxSnake(App):

    def build(self):
        root = FloatLayout()

        self.score = Label(
            text="امتیاز: 0",
            font_size="22sp",
            bold=True,
            color=(.55, 1, .4, 1),
            size_hint=(1, None),
            height=dp(48),
            pos_hint={"top": 1}
        )

        root.add_widget(self.score)

        self.board = Board(
            size_hint=(.96, .70),
            pos_hint={
                "center_x": .5,
                "center_y": .52
            }
        )

        self.board.score_cb = self.update_score
        self.board.over_cb = self.game_over

        root.add_widget(self.board)

        self.info = Label(
            text="برای تغییر مسیر، انگشتت را روی زمین بکش",
            font_size="14sp",
            color=(.72, .88, .72, 1),
            size_hint=(1, None),
            height=dp(40),
            pos_hint={
                "center_x": .5,
                "y": .105
            }
        )

        root.add_widget(self.info)

        self.button = Button(
            text="شروع بازی",
            font_size="18sp",
            bold=True,
            size_hint=(.55, None),
            height=dp(52),
            pos_hint={
                "center_x": .5,
                "y": .025
            },
            background_normal="",
            background_color=(.16, .75, .12, 1),
            color=(.02, .06, .02, 1)
        )

        self.button.bind(on_release=self.start)
        root.add_widget(self.button)

        return root

    def update_score(self, score):
        self.score.text = f"امتیاز: {score}"

    def game_over(self):
        self.info.text = "بازی تمام شد! دوباره شروع کن"

    def start(self, *args):
        self.board.begin()
        self.info.text = "با کشیدن انگشت، مسیر مار را عوض کن"
        self.button.text = "شروع دوباره"


if __name__ == "__main__":
    LuxSnake().run()
