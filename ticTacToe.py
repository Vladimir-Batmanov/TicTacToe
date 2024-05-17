import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QMessageBox, QVBoxLayout, QHBoxLayout, QComboBox, QLabel
from PyQt5.QtCore import QTimer

# Константы
BUTTON_SIZE = 100
MAX_DEPTH_SMALL = 6
MAX_DEPTH_LARGE = 3

class TicTacToe(QWidget):
    def __init__(self):
        super().__init__()

        self.grid_size = 3
        self.current_player = 'X'
        self.board = []
        self.difficulty = 'Легкий'
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Крестики-нолики')

        main_layout = QVBoxLayout()

        # Создание комбобокса для выбора размера сетки
        self.grid_size_selector = QComboBox(self)
        for size in [3, 4, 5]:
            self.grid_size_selector.addItem(f"{size}x{size}", size)
        self.grid_size_selector.currentIndexChanged.connect(self.change_grid_size)

        # Создание комбобокса для выбора уровня сложности
        self.difficulty_selector = QComboBox(self)
        self.difficulty_selector.addItem("Легкий")
        self.difficulty_selector.addItem("Трудный")
        self.difficulty_selector.currentIndexChanged.connect(self.change_difficulty)

        # Добавление комбобоксов в макет
        layout_top = QHBoxLayout()
        layout_top.addWidget(QLabel("Выберите размер сетки:"))
        layout_top.addWidget(self.grid_size_selector)
        layout_top.addWidget(QLabel("Выберите уровень сложности:"))
        layout_top.addWidget(self.difficulty_selector)

        main_layout.addLayout(layout_top)

        # Создание сеточного макета для кнопок игры
        self.grid_layout = QGridLayout()
        main_layout.addLayout(self.grid_layout)

        self.setLayout(main_layout)
        self.reset_board()
        self.show()

    def change_grid_size(self):
        # Обновление размера сетки и сброс игрового поля
        self.grid_size = self.grid_size_selector.currentData()
        self.reset_board()

    def change_difficulty(self):
        # Обновление уровня сложности
        self.difficulty = self.difficulty_selector.currentText()

    def reset_board(self):
        # Очистка предыдущих кнопок
        while self.grid_layout.count():
            widget = self.grid_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()

        # Создание новой сетки и кнопок
        self.board = [['' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.current_player = 'X'
        self.buttons = []

        for i in range(self.grid_size):
            row = []
            for j in range(self.grid_size):
                button = QPushButton('')
                button.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
                button.clicked.connect(self.make_move)
                self.grid_layout.addWidget(button, i, j)
                row.append(button)
            self.buttons.append(row)

    def make_move(self):
        # Обработка хода игрока
        button = self.sender()
        index = self.grid_layout.indexOf(button)
        row, col = divmod(index, self.grid_size)

        if self.board[row][col] == '':
            self.board[row][col] = self.current_player
            button.setText(self.current_player)

            if self.check_winner(row, col):
                self.show_winner_message(f"Игрок {self.current_player} выиграл!")
                return
            elif self.is_draw():
                self.show_winner_message("Ничья!")
                return

            self.current_player = 'O' if self.current_player == 'X' else 'X'
            if self.current_player == 'O':
                QTimer.singleShot(100, self.pc_move)  # Задержка хода ПК для обновления интерфейса

    def pc_move(self):
        # Ход ПК в зависимости от уровня сложности
        move = self.find_random_move() if self.difficulty == 'Легкий' else self.find_best_move()

        if move:
            row, col = move
            self.board[row][col] = self.current_player
            self.buttons[row][col].setText(self.current_player)

            if self.check_winner(row, col):
                self.show_winner_message(f"Игрок {self.current_player} выиграл!")
                return
            elif self.is_draw():
                self.show_winner_message("Ничья!")
                return

            self.current_player = 'X'

    def find_random_move(self):
        # Поиск случайного хода
        empty_cells = [(i, j) for i in range(self.grid_size) for j in range(self.grid_size) if self.board[i][j] == '']
        return random.choice(empty_cells) if empty_cells else None

    def find_best_move(self):
        # Поиск лучшего хода с использованием Минимакс
        best_score = float('-inf')
        best_move = None
        max_depth = MAX_DEPTH_LARGE if self.grid_size > 3 else MAX_DEPTH_SMALL  # Ограничение глубины для больших сеток

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.board[i][j] == '':
                    self.board[i][j] = self.current_player
                    score = self.minimax(0, False, float('-inf'), float('inf'), max_depth)
                    self.board[i][j] = ''
                    if score > best_score:
                        best_score = score
                        best_move = (i, j)

        return best_move

    def minimax(self, depth, is_maximizing, alpha, beta, max_depth):
        # Алгоритм Минимакс с альфа-бета отсечением
        if self.check_winner_state('O'):
            return 10 - depth
        elif self.check_winner_state('X'):
            return depth - 10
        elif self.is_draw_state() or (max_depth is not None and depth >= max_depth):
            return 0

        best_score = float('-inf') if is_maximizing else float('inf')
        player = 'O' if is_maximizing else 'X'

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.board[i][j] == '':
                    self.board[i][j] = player
                    score = self.minimax(depth + 1, not is_maximizing, alpha, beta, max_depth)
                    self.board[i][j] = ''
                    if is_maximizing:
                        best_score = max(score, best_score)
                        alpha = max(alpha, best_score)
                    else:
                        best_score = min(score, best_score)
                        beta = min(beta, best_score)
                    if beta <= alpha:
                        break

        return best_score

    def check_winner(self, row, col):
        # Проверка победителя после хода
        return self.check_winner_state(self.current_player)

    def check_winner_state(self, player):
        # Проверка победителя на доске
        n = self.grid_size
        for i in range(n):
            if all(self.board[i][j] == player for j in range(n)) or all(self.board[j][i] == player for j in range(n)):
                return True
        if all(self.board[i][i] == player for i in range(n)) or all(self.board[i][n - 1 - i] == player for i in range(n)):
            return True
        return False

    def is_draw(self):
        # Проверка на ничью
        return self.is_draw_state()

    def is_draw_state(self):
        # Проверка на ничью для состояния доски
        return all(self.board[i][j] != '' for i in range(self.grid_size) for j in range(self.grid_size))

    def show_winner_message(self, message):
        # Отображение сообщения о победе или ничьей
        QMessageBox.information(self, "Игра окончена", message)
        self.reset_board()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = TicTacToe()
    sys.exit(app.exec_())
