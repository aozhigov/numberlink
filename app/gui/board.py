import functools
from PyQt5.QtWidgets import QPushButton, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt

from app.algorithms.solver import get_field_from_solution, solve
from app.colors import MAX_COLORS, Color
from app.numberlink import TriangleField, TriangleLink


class CellButton(QPushButton):
    def __init__(self, position, parent):
        super().__init__('0', parent)
        self.position = position
        self.set_number(0)
        self.on_mouse_click = None

    @property
    def number(self):
        return int(self.text()) if self.text() else 0

    def set_number(self, value):
        if value > MAX_COLORS:
            raise ValueError(f'Not supported count '
                             f'color more than {MAX_COLORS}')
        self.setText(str(value) if value > 0 else "0")
        self.setStyleSheet(
            f'QPushButton {{ background-color: {Color(value).name};}}')

    def mousePressEvent(self, e):
        self.set_number(self.parent().current_number % MAX_COLORS)
        if self.on_mouse_click:
            self.on_mouse_click()
        super().mousePressEvent(e)


class TriangleBoard(QWidget):
    def __init__(self, field, parent):
        super().__init__(parent)
        self.field = TriangleField(field)
        self.board_size = self.field.size
        self.cells = []
        self.cell_length = 50
        self.init_ui()
        self._current_number = 1

    def init_ui(self):
        vbox = QVBoxLayout(self)
        vbox.setAlignment(Qt.AlignCenter)

        for i, row in enumerate(self.field):
            hbox = QHBoxLayout(self)
            hbox.setAlignment(Qt.AlignCenter)

            for j, number in enumerate(row):
                cell = CellButton((i, j), self)
                cell.set_number(number)
                cell.setFixedSize(self.cell_length, self.cell_length)
                cell.on_mouse_click = functools.partial(self.cell_click, cell)
                self.cells.append(cell)
                hbox.addWidget(cell, 0, Qt.AlignCenter)

            vbox.addLayout(hbox)
        self.setLayout(vbox)

    def cell_click(self, cell):
        self.field[cell.position] = cell.number

    def clear(self):
        for cell in self.cells:
            cell.set_number(0)
            self.field[cell.position] = cell.number

    @property
    def current_number(self):
        return self._current_number

    @current_number.setter
    def current_number(self, value: int):
        if 0 < value < MAX_COLORS:
            self._current_number = value


class GameBoard(TriangleBoard):
    def __init__(self, field, parent):
        super().__init__(field, parent)
        self.field = TriangleLink(field)
        self.targets = self.field.get_targets()['vertices']
        self.solutions = [TriangleField(
            get_field_from_solution(self.field, solution))
            for solution in solve(self.field)]
        self.when_solved = lambda: None

        for cell in self.cells:
            if cell.position in self.targets:
                cell.setEnabled(False)

    def cell_click(self, cell):
        if cell.position not in self.targets:
            super().cell_click(cell)
            if self.check_solution():
                self.when_solved()

    def check_solution(self):
        return any(self.field == solution for solution in self.solutions)

    def clear(self):
        for cell in self.cells:
            if cell.position not in self.targets:
                cell.set_number(0)
                self.field[cell.position] = 0

    def set_field(self, field):
        for i, row in enumerate(field):
            for j, cell in enumerate(row):
                self.field[i, j] = cell
        for cell in self.cells:
            cell.set_number(self.field[cell.position])
