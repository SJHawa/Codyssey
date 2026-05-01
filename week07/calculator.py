import os
import math
import sys
from pathlib import Path

try:
    import PyQt6
except ModuleNotFoundError:
    PyQt6 = None


def configure_qt_plugin_path():
    if PyQt6 is None:
        return

    pyqt_root = Path(PyQt6.__file__).resolve().parent
    plugin_path = pyqt_root / 'Qt6' / 'plugins' / 'platforms'

    if plugin_path.exists():
        os.environ.setdefault('QT_QPA_PLATFORM_PLUGIN_PATH', str(plugin_path))


configure_qt_plugin_path()

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont
    from PyQt6.QtWidgets import (
        QApplication,
        QGridLayout,
        QLabel,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )
except ModuleNotFoundError:
    print('PyQt6가 설치되어 있지 않습니다.')
    print('다음 명령으로 설치한 뒤 다시 실행하세요:')
    print('python3 -m pip install PyQt6')
    sys.exit(1)


BUTTON_LAYOUT = [
    [('AC', 'function'), ('+/-', 'function'), ('%', 'function'), ('/', 'operator')],
    [('7', 'number'), ('8', 'number'), ('9', 'number'), ('*', 'operator')],
    [('4', 'number'), ('5', 'number'), ('6', 'number'), ('-', 'operator')],
    [('1', 'number'), ('2', 'number'), ('3', 'number'), ('+', 'operator')],
    [('0', 'number'), ('.', 'number'), ('=', 'operator')],
]

MAX_ABS_VALUE = 1e100
MAX_DISPLAY_LENGTH = 12
DEFAULT_FONT_SIZE = 36
MIN_FONT_SIZE = 18


class CalculatorCore:
    def __init__(self):
        self.reset()

    def reset(self):
        self.display_text = '0'
        self.stored_value = None
        self.pending_operator = None
        self.waiting_for_new_input = False
        self.last_operand = None
        self.error_state = False
        return self.display_text

    def add(self, left, right):
        return left + right

    def subtract(self, left, right):
        return left - right

    def multiply(self, left, right):
        return left * right

    def divide(self, left, right):
        if right == 0:
            raise ZeroDivisionError
        return left / right

    def input_digit(self, digit):
        if self.error_state:
            self.reset()

        if self.waiting_for_new_input:
            self.display_text = digit
            self.waiting_for_new_input = False
            return self.display_text

        if self.display_text == '0':
            self.display_text = digit
        elif self.display_text == '-0':
            self.display_text = f'-{digit}'
        else:
            self.display_text += digit

        return self.display_text

    def input_decimal(self):
        if self.error_state:
            self.reset()

        if self.waiting_for_new_input:
            self.display_text = '0.'
            self.waiting_for_new_input = False
            return self.display_text

        if '.' not in self.display_text:
            self.display_text += '.'

        return self.display_text

    def negative_positive(self):
        if self.error_state:
            return self.display_text

        if self.display_text in ('0', '0.'):
            return self.display_text

        if self.display_text.startswith('-'):
            self.display_text = self.display_text[1:]
        else:
            self.display_text = f'-{self.display_text}'

        return self.display_text

    def percent(self):
        if self.error_state:
            return self.display_text

        try:
            current_value = self._display_to_number()
            percent_value = current_value / 100
            self._ensure_in_range(percent_value)
        except (OverflowError, ValueError):
            return self._set_error('Overflow')

        self.display_text = self._format_number(percent_value)
        self.waiting_for_new_input = False
        return self.display_text

    def set_operator(self, operator):
        if self.error_state:
            return self.display_text

        current_value = self._display_to_number()

        if self.pending_operator and not self.waiting_for_new_input:
            result = self._calculate(self.stored_value, current_value, self.pending_operator)
            if self.error_state:
                return self.display_text
            self.stored_value = result
            self.display_text = self._format_number(result)
        else:
            self.stored_value = current_value

        self.pending_operator = operator
        self.waiting_for_new_input = True
        self.last_operand = None
        return self.display_text

    def equal(self):
        if self.error_state:
            return self.display_text

        if self.pending_operator is None:
            return self.display_text

        current_value = self._display_to_number()

        if self.waiting_for_new_input and self.last_operand is not None:
            operand = self.last_operand
        else:
            operand = current_value
            self.last_operand = operand

        result = self._calculate(self.stored_value, operand, self.pending_operator)
        if self.error_state:
            return self.display_text

        self.display_text = self._format_number(result)
        self.stored_value = result
        self.waiting_for_new_input = True
        return self.display_text

    def _calculate(self, left, right, operator):
        operations = {
            '+': self.add,
            '-': self.subtract,
            '*': self.multiply,
            '/': self.divide,
        }

        try:
            result = operations[operator](left, right)
            self._ensure_in_range(result)
            return result
        except ZeroDivisionError:
            return self._set_error('Error')
        except (OverflowError, ValueError):
            return self._set_error('Overflow')

    def _display_to_number(self):
        return float(self.display_text)

    def _ensure_in_range(self, value):
        if not math.isfinite(value) or abs(value) > MAX_ABS_VALUE:
            raise OverflowError

    def _set_error(self, message):
        self.display_text = message
        self.stored_value = None
        self.pending_operator = None
        self.waiting_for_new_input = True
        self.last_operand = None
        self.error_state = True
        return message

    def _format_number(self, value):
        rounded_value = round(value, 6)

        if math.isclose(rounded_value, int(rounded_value), abs_tol=1e-9):
            return str(int(rounded_value))

        text = f'{rounded_value:.6f}'.rstrip('0').rstrip('.')
        if text == '-0':
            return '0'
        return text


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.core = CalculatorCore()
        self.init_ui()
        self.update_display()

    def init_ui(self):
        self.setWindowTitle('iPhone Style Calculator')
        self.setFixedSize(360, 620)
        self.setStyleSheet('background-color: #000000;')

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 24, 16, 16)
        main_layout.setSpacing(12)

        self.display = QLabel(self.core.display_text)
        self.display.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.display.setMinimumHeight(150)
        self.display.setStyleSheet(
            'color: white;'
            'background-color: #000000;'
            'padding: 16px 8px;'
        )
        self.display.setFont(QFont('Arial', DEFAULT_FONT_SIZE))

        main_layout.addWidget(self.display)

        button_layout = QGridLayout()
        button_layout.setSpacing(12)

        for row_index, row in enumerate(BUTTON_LAYOUT):
            column_index = 0
            for label, button_type in row:
                button = self.create_button(label, button_type)

                if label == '0':
                    button_layout.addWidget(button, row_index, column_index, 1, 2)
                    column_index += 2
                else:
                    button_layout.addWidget(button, row_index, column_index)
                    column_index += 1

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def create_button(self, label, button_type):
        button = QPushButton(label)
        button.setMinimumHeight(72)
        button.setFont(QFont('Arial', 22))

        if button_type == 'function':
            style = (
                'background-color: #a5a5a5;'
                'color: black;'
                'border: none;'
                'border-radius: 36px;'
            )
        elif button_type == 'operator':
            style = (
                'background-color: #ff9f0a;'
                'color: white;'
                'border: none;'
                'border-radius: 36px;'
            )
        else:
            style = (
                'background-color: #333333;'
                'color: white;'
                'border: none;'
                'border-radius: 36px;'
            )

        if label == '0':
            style += 'text-align: left; padding-left: 28px;'

        button.setStyleSheet(style)
        button.clicked.connect(lambda checked=False, value=label: self.handle_input(value))
        return button

    def handle_input(self, value):
        if value == 'AC':
            self.core.reset()
        elif value == '+/-':
            self.core.negative_positive()
        elif value == '%':
            self.core.percent()
        elif value == '=':
            self.core.equal()
        elif value in '+-*/':
            self.core.set_operator(value)
        elif value == '.':
            self.core.input_decimal()
        else:
            self.core.input_digit(value)

        self.update_display()

    def update_display(self):
        self.display.setText(self.core.display_text)
        self.display.setFont(QFont('Arial', self._font_size_for_text(self.core.display_text)))

    def _font_size_for_text(self, text):
        if len(text) <= MAX_DISPLAY_LENGTH:
            return DEFAULT_FONT_SIZE

        extra_length = len(text) - MAX_DISPLAY_LENGTH
        adjusted_size = DEFAULT_FONT_SIZE - (extra_length * 2)
        return max(MIN_FONT_SIZE, adjusted_size)


def main():
    app = QApplication(sys.argv)
    window = Calculator()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
