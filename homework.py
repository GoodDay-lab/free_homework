from PyQt5.QtWidgets import QLineEdit, QPushButton, QWidget, QLabel, QCheckBox
import sys
from PyQt5.QtWidgets import QApplication


class Example(QWidget):
    ALPHABET = {'a': '·−', 'b': '−···', 'c': '−·−·', 'd': '−··', 'e': '·', 'f': '··−·',
                'g': '-−·', 'h': '····', 'i': '··', 'j': '·−−−', 'k': '−·−', 'l': '·−··',
                'm': '−−', 'n': '−·', 'o': '−−−', 'p': '·−−·', 'q': '−−·−', 'r': '·−·',
                's': '···', 't': '−', 'u': '··−', 'v': '···−', 'w': '·−−', 'x': '−··−',
                'y': '−·−−', 'z': '−−··'}

    def __init__(self):
        super().__init__()
        self.next()

    def next(self):
        buttons = []
        count = 0
        for letter in Example.ALPHABET:
            btn = QPushButton(letter, self)
            y = count // 5
            btn.setGeometry(20 * (count % 5) + 20, 20 * y + 20, 20, 20)
            btn.clicked.connect(self.func)
            buttons.append(btn)
            count += 1

        self.line_edit = QLineEdit(self)
        self.line_edit.setGeometry(10, 140, 250, 20)

        self.checkbox = QCheckBox(self)
        self.checkbox.stateChanged.connect(self.help)
        self.checkbox.setGeometry(10, 180, 10, 10)

        self.label = QLabel('Помощник', self)
        self.label.setGeometry(25, 180, 60, 10)

        self.setWindowTitle('Program v1.0')
        self.setGeometry(500, 500, 300, 240)

        self.helper = ''

    def func(self):
        name = self.sender().text()
        text = self.line_edit.text()
        self.line_edit.setText(text + self.helper + Example.ALPHABET[name])

    def help(self):
        box = self.sender()
        if box.checkState():
            print('+')
            self.helper = '|'
        else:
            print('-')
            self.helper = ''


if True:
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())