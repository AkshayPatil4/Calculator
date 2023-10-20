import sys
import math
import matplotlib.pyplot as plt
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QLineEdit, QPushButton, QGridLayout, QTextEdit, QLabel, QDoubleSpinBox, QSizePolicy
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent

class InputField(QLineEdit):
    calculate = Signal()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.calculate.emit()
        else:
            super().keyPressEvent(event)

class Widget(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Calculator")
        self.setGeometry(100, 100, 300, 400)

        self.basic_buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+'
        ]

        self.scientific_buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+',
            'sin', 'cos', 'tan', 'sqrt',
            'exp', '**', '(', ')',
            'log', 'log10', 'π', 'e'
        ]

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.tabs = QTabWidget()
        self.basic_tab = QWidget()
        self.scientific_tab = QWidget()
        self.plotting_tab = QWidget()

        self.tabs.addTab(self.basic_tab, "Basic")
        self.tabs.addTab(self.scientific_tab, "Scientific")
        self.tabs.addTab(self.plotting_tab, "Plotting")

        self.create_calculator(self.basic_tab, self.basic_buttons)
        self.create_calculator(self.scientific_tab, self.scientific_buttons)
        self.create_plotting_tab()

        self.layout.addWidget(self.tabs)

        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.layout.addWidget(self.history_text)

        self.history = []

    def create_calculator(self, tab, button_texts):
        layout = QVBoxLayout()
        input_field = InputField()
        input_field.setPlaceholderText("Enter an expression")
        result_field = QLineEdit()
        result_field.setPlaceholderText("Result will be shown here")
        clear_button = QPushButton("C")
        clear_button.setObjectName("clear-button")

        button_grid = QGridLayout()
        row, col = 0, 0

        for text in button_texts:
            button = QPushButton(text)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.setObjectName("calculator-button")
            if text == '=':
                button.clicked.connect(lambda clicked_button=button, input_field=input_field, result_field=result_field: self.on_equals_clicked(input_field, result_field))
            else:
                button.clicked.connect(lambda text=text, input_field=input_field: self.on_button_clicked(text, input_field))
            button_grid.addWidget(button, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

        layout.addWidget(input_field)
        layout.addWidget(result_field)
        layout.addWidget(clear_button)
        layout.addLayout(button_grid)
        tab.setLayout(layout)

        clear_button.clicked.connect(lambda: self.clear_input(input_field, result_field))
        input_field.setFocus()
        input_field.calculate.connect(lambda: self.on_equals_clicked(input_field, result_field))

    def create_plotting_tab(self):
        layout = QVBoxLayout()

        self.function_input = QLineEdit()
        self.function_input.setPlaceholderText("Enter a function, e.g., sin(x) + x**2")
        x_limit_label = QLabel("X Limit:")
        y_limit_label = QLabel("Y Limit:")

        self.x_limit_input = QDoubleSpinBox()
        self.x_limit_input.setMinimum(-1000)
        self.x_limit_input.setMaximum(1000)

        self.y_limit_input = QDoubleSpinBox()
        self.y_limit_input.setMinimum(-1000)
        self.y_limit_input.setMaximum(1000)

        plot_button = QPushButton("Plot")
        plot_button.setObjectName("plot-button")

        self.plot_widget = plt.figure()
        self.canvas = self.plot_widget.canvas

        layout.addWidget(self.function_input)
        layout.addWidget(x_limit_label)
        layout.addWidget(self.x_limit_input)
        layout.addWidget(y_limit_label)
        layout.addWidget(self.y_limit_input)
        layout.addWidget(plot_button)
        layout.addWidget(self.canvas)

        self.plotting_tab.setLayout(layout)
        plot_button.clicked.connect(self.plot_function)

    def on_button_clicked(self, text, input_field):
        input_field.insert(text)

    def on_equals_clicked(self, input_field, result_field):
        try:
            expression = input_field.text()
            result = str(eval(expression, {"__builtins__": None}, {"sin": math.sin, "cos": math.cos, "tan": math.tan, "sqrt": math.sqrt, "exp": math.exp, "log": math.log, "log10": math.log10, "π": math.pi, "e": math.e}))
            result_field.setText(result)
            self.history.append(f"{expression} = {result}")
            self.update_history()
        except Exception as e:
            result_field.setText("Error")

    def clear_input(self, input_field, result_field):
        input_field.clear()
        result_field.clear()

    def plot_function(self):
        try:
            expression = self.function_input.text()
            x_limit = self.x_limit_input.value()
            y_limit = self.y_limit_input.value()

            x = [x_limit * i / 1000 for i in range(-1000, 1001)]
            y = [eval(expression, {"__builtins__": None}, {"sin": math.sin, "cos": math.cos, "tan": math.tan, "sqrt": math.sqrt, "exp": math.exp, "log": math.log, "log10": math.log10, "π": math.pi, "e": math.e, "x": xi}) for xi in x]

            self.plot_widget.clf()
            plt.plot(x, y)
            plt.xlim(-x_limit, x_limit)
            plt.ylim(-y_limit, y_limit)
            plt.xlabel('x')
            plt.ylabel('y')
            plt.grid(True)
            self.canvas.draw()

            self.history.append(f"Plotted: {expression} with x limit {x_limit} and y limit {y_limit}")
            self.update_history()

        except Exception as e:
            self.history.append("Error plotting function")
            self.update_history()

    def update_history(self):
        self.history_text.setPlainText("\n".join(self.history))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Widget()
    window.setStyleSheet('''
        QWidget {
            background-color: #f5f5f5;
        }

        QLineEdit {
            background-color: #ffffff;
            border: 1px solid #c9c9c9;
            border-radius: 10px;
            padding: 5px;
        }

        QPushButton {
            background-color: #e0e0e0;
            border: 1px solid #b3b3b3;
            border-radius: 10px;
            padding: 5px 15px;
            font-size: 18px;
        }

        QPushButton#clear-button {
            background-color: #e0e0e0;
            border: 1px solid #b3b3b3;
            border-radius: 10px;
            padding: 5px 15px;
            font-size: 18px;
            color: red;
        }

        QPushButton#calculator-button:hover, QPushButton#plot-button:hover {
            background-color: #cccccc;
        }

        QPushButton#plot-button {
            background-color: #50e3c2;
            border: 1px solid #3cbba1;
            color: white;
            font-weight: bold;
        }
    ''')

    window.show()
    sys.exit(app.exec())
