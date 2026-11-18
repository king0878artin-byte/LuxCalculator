
import ast
import math
import operator

from kivy.app import App
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle

Window.clearcolor = (0.055, 0.065, 0.09, 1)

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos
}


def safe_calculate(expression):
    tree = ast.parse(expression, mode="eval")

    def solve(node):
        if isinstance(node, ast.Expression):
            return solve(node.body)

        if isinstance(node, ast.Constant):
            if type(node.value) not in (int, float):
                raise ValueError()
            return node.value

        if isinstance(node, ast.BinOp):
            op = OPS.get(type(node.op))
            if op is None:
                raise ValueError()

            a = solve(node.left)
            b = solve(node.right)

            if abs(a) > 1e100 or abs(b) > 1e100:
                raise ValueError()

            result = op(a, b)

            if not math.isfinite(result) or abs(result) > 1e100:
                raise ValueError()

            return result

        if isinstance(node, ast.UnaryOp):
            op = OPS.get(type(node.op))
            if op is None:
                raise ValueError()
            return op(solve(node.operand))

        raise ValueError()

    return solve(tree)


class CalcButton(Button):
    def __init__(self, bg, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.font_size = dp(21)
        self.bold = True

        with self.canvas.before:
            Color(*bg)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(15)]
            )

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class LuxCalculatorApp(App):

    def build(self):
        self.title = "LuxCalculator"
        self.expression = ""
        self.memory = 0
        self.finished = False

        root = BoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(10)
        )

        header = Label(
            text="[b]LUX[/b] [color=55B9FF]CALCULATOR[/color]",
            markup=True,
            font_size=dp(23),
            size_hint_y=.12,
            halign="left"
        )
        root.add_widget(header)

        self.preview = Label(
            text="",
            font_size=dp(20),
            color=(.55, .68, .82, 1),
            size_hint_y=.10,
            halign="right"
        )
        root.add_widget(self.preview)

        self.display = Label(
            text="0",
            font_size=dp(42),
            color=(1, 1, 1, 1),
            size_hint_y=.22,
            halign="right",
            valign="middle",
            shorten=True
        )
        self.display.bind(size=self.display.setter("text_size"))
        root.add_widget(self.display)

        grid = GridLayout(
            cols=4,
            spacing=dp(8),
            size_hint_y=.66
        )

        rows = [
            ["MC", "MR", "M+", "M-"],
            ["AC", "C", "⌫", "÷"],
            ["%", "(", ")", "×"],
            ["7", "8", "9", "-"],
            ["4", "5", "6", "+"],
            ["1", "2", "3", "√"],
            ["±", "0", ".", "="]
        ]

        for row in rows:
            for symbol in row:

                if symbol == "=":
                    bg = (.08, .43, .85, 1)
                elif symbol in ["+", "-", "×", "÷", "√", "%"]:
                    bg = (.12, .25, .38, 1)
                elif symbol in ["AC", "C", "⌫"]:
                    bg = (.34, .13, .18, 1)
                elif symbol in ["MC", "MR", "M+", "M-"]:
                    bg = (.17, .20, .28, 1)
                else:
                    bg = (.105, .13, .19, 1)

                btn = CalcButton(bg, text=symbol)
                btn.bind(
                    on_release=lambda instance, s=symbol: self.press(s)
                )
                grid.add_widget(btn)

        root.add_widget(grid)

        root.add_widget(Label(
            text="[color=687991]LUX CALCULATOR • ANDROID[/color]",
            markup=True,
            font_size=dp(11),
            size_hint_y=.05
        ))

        return root

    def get_value(self):
        exp = self.expression.replace("×", "*").replace("÷", "/")
        return safe_calculate(exp) if exp else 0

    def update_display(self):
        self.display.text = self.expression or "0"

        try:
            result = self.get_value()
            self.preview.text = f"= {result:,.10g}"
        except Exception:
            self.preview.text = ""

    def press(self, key):

        if key in ("AC", "C"):
            self.expression = ""
            self.finished = False

        elif key == "⌫":
            self.expression = self.expression[:-1]

        elif key == "=":
            try:
                self.expression = format(self.get_value(), ".12g")
                self.finished = True
            except Exception:
                self.expression = ""
                self.display.text = "Error"
                self.preview.text = ""
                return

        elif key == "√":
            try:
                value = self.get_value()
                if value < 0:
                    raise ValueError()
                self.expression = format(math.sqrt(value), ".12g")
                self.finished = True
            except Exception:
                self.expression = ""
                self.display.text = "Error"
                return

        elif key == "%":
            try:
                self.expression = format(self.get_value() / 100, ".12g")
                self.finished = True
            except Exception:
                return

        elif key == "±":
            try:
                self.expression = format(-self.get_value(), ".12g")
                self.finished = True
            except Exception:
                return

        elif key in ("MC", "MR", "M+", "M-"):
            try:
                value = self.get_value()
                if key == "MC":
                    self.memory = 0
                elif key == "MR":
                    self.expression = format(self.memory, ".12g")
                elif key == "M+":
                    self.memory += value
                elif key == "M-":
                    self.memory -= value
            except Exception:
                if key == "MC":
                    self.memory = 0

        else:
            operators = ("+", "-", "×", "÷")

            if self.finished and key not in operators:
                self.expression = ""

            if len(self.expression) < 100:
                self.expression += key

            self.finished = False

        self.update_display()


if __name__ == "__main__":
    LuxCalculatorApp().run()
ُ