import sys
import ast
import operator
import math
#pip install pyside6

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QPushButton,
    QLineEdit,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class SafeCalculator:
    """
    Avaliador seguro de expressões matemáticas.
    Não utiliza eval().
    """

    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
        ast.Mod: operator.mod,
    }

    FUNCTIONS = {
        "sqrt": math.sqrt,
        "abs": abs,
        "round": round,
    }

    @classmethod
    def evaluate(cls, expression):
        expression = expression.replace("^", "**")

        node = ast.parse(expression, mode="eval")

        return cls._eval(node.body)

    @classmethod
    def _eval(cls, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Valor inválido")

        if isinstance(node, ast.BinOp):
            op_type = type(node.op)

            if op_type not in cls.OPERATORS:
                raise ValueError("Operação não permitida")

            left = cls._eval(node.left)
            right = cls._eval(node.right)

            return cls.OPERATORS[op_type](left, right)

        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)

            if op_type not in cls.OPERATORS:
                raise ValueError("Operação não permitida")

            operand = cls._eval(node.operand)

            return cls.OPERATORS[op_type](operand)

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Função inválida")

            func_name = node.func.id

            if func_name not in cls.FUNCTIONS:
                raise ValueError("Função não permitida")

            args = [cls._eval(arg) for arg in node.args]

            return cls.FUNCTIONS[func_name](*args)

        raise ValueError("Expressão inválida")


class Calculator(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Calculadora Segura - PySide6")
        self.resize(420, 550)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(False)
        self.display.setMinimumHeight(70)

        font = QFont()
        font.setPointSize(22)

        self.display.setFont(font)

        layout.addWidget(self.display)

        grid = QGridLayout()

        buttons = [
            ("C", 0, 0),
            ("⌫", 0, 1),
            ("(", 0, 2),
            (")", 0, 3),

            ("7", 1, 0),
            ("8", 1, 1),
            ("9", 1, 2),
            ("/", 1, 3),

            ("4", 2, 0),
            ("5", 2, 1),
            ("6", 2, 2),
            ("*", 2, 3),

            ("1", 3, 0),
            ("2", 3, 1),
            ("3", 3, 2),
            ("-", 3, 3),

            ("0", 4, 0),
            (".", 4, 1),
            ("%", 4, 2),
            ("+", 4, 3),

            ("√", 5, 0),
            ("^", 5, 1),
            ("=", 5, 2, 1, 2),
        ]

        for item in buttons:
            text = item[0]
            row = item[1]
            col = item[2]

            rowspan = 1
            colspan = 1

            if len(item) == 5:
                rowspan = item[3]
                colspan = item[4]

            btn = QPushButton(text)
            btn.setMinimumHeight(60)
            btn.setFont(QFont("Arial", 14))

            btn.clicked.connect(
                lambda checked=False, t=text: self.on_button_click(t)
            )

            grid.addWidget(btn, row, col, rowspan, colspan)

        layout.addLayout(grid)

    def on_button_click(self, text):
        if text == "=":
            self.calculate()

        elif text == "C":
            self.display.clear()

        elif text == "⌫":
            self.display.backspace()

        elif text == "√":
            self.display.insert("sqrt(")

        elif text == "%":
            value = self.display.text()
            self.display.setText(f"({value})/100")

        else:
            self.display.insert(text)

    def calculate(self):
        expr = self.display.text().strip()

        if not expr:
            return

        try:
            result = SafeCalculator.evaluate(expr)

            if isinstance(result, float):
                result = round(result, 10)

            self.display.setText(str(result))

        except ZeroDivisionError:
            self.display.setText("Erro: divisão por zero")

        except Exception:
            self.display.setText("Erro")

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.calculate()
        else:
            super().keyPressEvent(event)


def main():
    app = QApplication(sys.argv)

    window = Calculator()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()