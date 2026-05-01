import sys

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


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.display_text = '0'
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('iPhone Style Calculator')
        self.setFixedSize(360, 620)
        self.setStyleSheet('background-color: #000000;')

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 24, 16, 16)
        main_layout.setSpacing(12)

        self.display = QLabel(self.display_text)
        self.display.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.display.setMinimumHeight(150)
        self.display.setStyleSheet(
            'color: white;'
            'background-color: #000000;'
            'padding: 16px 8px;'
        )
        self.display.setFont(QFont('Arial', 36))

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
            self.display_text = '0'
        elif value == '+/-':
            self.toggle_sign()
        elif value == '%':
            self.append_percent()
        elif value == '=':
            self.display_text = self.display_text
        elif value in '+-*/':
            self.append_operator(value)
        elif value == '.':
            self.append_decimal()
        else:
            self.append_number(value)

        self.display.setText(self.display_text)

    def append_number(self, value):
        if self.display_text == '0':
            self.display_text = value
        else:
            self.display_text += value

    def append_operator(self, value):
        if self.display_text[-1] in '+-*/':
            self.display_text = self.display_text[:-1] + value
        else:
            self.display_text += value

    def append_decimal(self):
        current_token = self.get_current_token()
        if '.' in current_token:
            return

        if self.display_text[-1] in '+-*/':
            self.display_text += '0.'
        else:
            self.display_text += '.'

    def toggle_sign(self):
        token = self.get_current_token()
        if token in ('', '0'):
            return

        start_index = len(self.display_text) - len(token)

        if token.startswith('-'):
            self.display_text = (
                self.display_text[:start_index] + token[1:]
            )
        else:
            self.display_text = (
                self.display_text[:start_index] + '-' + token
            )

    def append_percent(self):
        token = self.get_current_token()
        if not token or token.endswith('%'):
            return

        self.display_text += '%'

    def get_current_token(self):
        token = ''
        for char in reversed(self.display_text):
            if char in '+*/':
                break
            if char == '-' and token:
                token = char + token
                break
            token = char + token
        return token


def main():
    app = QApplication(sys.argv)
    window = Calculator()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
