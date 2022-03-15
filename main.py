import random


class Error(Exception):
    """Base class for other exceptions"""
    pass


class BoardOutException(Error):
    pass


class BoardBadGeneration(Error):
    pass


class BoardWrongCoordinates(Error):
    pass


class BoardSameException(Error):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f'Точка: {self.x, self.y}'


class Ship:
    def __init__(self, length, head_position, direction):
        self.length = length
        self.head_position = head_position
        self.direction = direction
        self.hp = length

    def __str__(self):
        return f'Ship: Length {self.length} Head Position ({self.head_position.x, self.head_position.y} Direction {self.direction} HP {self.hp})'

    def dots(self):
        ship_dots = [Dot(self.head_position.x, self.head_position.y)]

        if self.direction == 'v':
            for i in range(1, self.length):
                ship_dots.append(Dot(self.head_position.x + i, self.head_position.y))
        elif self.direction == 'h':
            for i in range(1, self.length):
                ship_dots.append(Dot(self.head_position.x, self.head_position.y + i))
        return ship_dots


class Board:
    board = []
    ships = []

    def __init__(self, hid):
        self.dim = Game.get_dim()
        self.board = self.generate_board()
        self.hid = hid

    def add_ships(self, ships):

        for ship in ships:
            result = self.add_ship(ship)
            if not result:
                return False
        return True

    def add_ship(self, ship):

        for dot in (self.contour(ship)):
            if self.board[dot.x][dot.y] == 'ship' or self.board[dot.x][dot.y] == 'ship_hit':
                return False

        for dot in (ship.dots()):
            if self.board[dot.x][dot.y] == 'empty':
                self.board[dot.x][dot.y] = 'ship'
            else:
                return False

        return True

    def generate_board(self):
        return [["empty" for j in range(self.dim)] for i in range(self.dim)]

    def render_board(self):
        # clear screen
        # print('\n' * 100)
        # header
        print('  | ', end='')
        for i in range(0, self.dim):
            print(str(i) + ' | ', end='')
        print('')
        # body
        for i in range(0, self.dim):
            print(str(i) + ' | ', end='')
            for j in range(0, len(self.board[i])):
                character = 'O |'
                if self.board[i][j] == 'empty':
                    character = 'O |'
                elif self.board[i][j] == 'ship' and not self.hid:
                    character = '■ |'
                elif self.board[i][j] == 'ship_hit':
                    character = 'X |'
                elif self.board[i][j] == 'miss':
                    character = 'T |'

                print(str(character) + ' ', end='')
            print('')

    def contour(self, ship):
        dots = []
        dots_to_check = []
        for dot in ship.dots():
            dots_to_check.append(Dot(dot.x - 1, dot.y))
            dots_to_check.append(Dot(dot.x + 1, dot.y))
            dots_to_check.append(Dot(dot.x, dot.y + 1))
            dots_to_check.append(Dot(dot.x, dot.y - 1))
            dots_to_check.append(Dot(dot.x - 1, dot.y - 1))
            dots_to_check.append(Dot(dot.x + 1, dot.y - 1))
            dots_to_check.append(Dot(dot.x + 1, dot.y + 1))
            dots_to_check.append(Dot(dot.x - 1, dot.y + 1))

        for dot in dots_to_check:
            if not self.out(dot) and dot not in dots:
                dots.append(Dot(dot.x, dot.y))

        return dots

    def out(self, dot):
        return False if 0 <= dot.x < self.dim and 0 <= dot.y < self.dim else True

    def shot(self, dot):

        if self.out(dot):
            raise BoardOutException

        if self.board[dot.x][dot.y] == 'ship_hit' or self.board[dot.x][dot.y] == 'miss':
            raise BoardSameException

        if self.board[dot.x][dot.y] == 'ship':
            self.board[dot.x][dot.y] = 'ship_hit'
        else:
            self.board[dot.x][dot.y] = 'miss'

        return self.board[dot.x][dot.y]


class Player:
    def __init__(self, ships):
        self.board_own = Board(False)
        self.board_own.add_ships(ships)

        self.board_enemy = Board(True)
        self.board_enemy.add_ships(ships)

    def ask(self):
        pass

    def move(self, board):
        move_status = 0
        try:
            dot = self.ask()
            move_status = board.shot(dot)
        except BoardOutException:
            print('Координаты вне диапазона!')
            return False
        except BoardSameException:
            print('Выберите другую точку!')
            return False
        except BoardWrongCoordinates:
            print('Неверный формат координат!')
            return False
        # print(f"{move_status}")
        return move_status


class AI(Player):
    name = "Компьютер"

    def ask(self):
        return Dot(random.randrange(0, self.board_own.dim - 1), random.randrange(0, self.board_own.dim - 1))


class User(Player):
    name = "Пользователь"

    def ask(self):
        cmd = input('Введите две координаты через запятую!: x,y ')

        if cmd.count(',') != 1:
            raise BoardWrongCoordinates
        cmd = cmd.replace(' ', '')
        if not cmd.replace(',', '').isnumeric():
            raise BoardWrongCoordinates
        cmd_y, cmd_x = map(int, cmd.split(','))
        return Dot(cmd_x, cmd_y)


class Game:
    _ship_composition = [[3, 1], [2, 2], [1, 4]]

    @staticmethod
    def get_dim():
        return 10

    def __init__(self):
        valid_board = False
        while not valid_board:
            self.player_user_board = self.random_board(False)
            self.player_ships = self.create_ships(self.player_user_board)
            valid_board = self.player_user_board.add_ships(self.player_ships)
        self.player_user = User(self.player_ships)

        valid_board = False
        while not valid_board:
            self.ai_user_board = self.random_board(True)
            self.ai_ships = self.create_ships(self.ai_user_board)
            valid_board = self.ai_user_board.add_ships(self.ai_ships)
        self.ai_user = AI(self.ai_ships)

    def greet(self):
        print("Приветствуем вас в игре Морской Бой")

    def start(self):
        self.greet()
        self.loop()

    def loop(self):
        turn_count = 1
        move_status = 0
        while any('ship' in sublist for sublist in self.player_user_board.board) and any(
                'ship' in sublist for sublist in self.ai_user_board.board):
            print("\n" * 100)
            if (move_status != 'ship_hit'):
                if turn_count % 2:
                    current_player = self.player_user
                    current_board = self.ai_user_board
                else:
                    current_player = self.ai_user
                    current_board = self.player_user_board

            print("Доска пользователя")
            self.player_user_board.render_board()
            print("Доска компьютера")
            self.ai_user_board.render_board()

            move_status = current_player.move(current_board)

            turn_count = turn_count + 1
        print(f"Победил {current_player.name}!")

        return

    def create_ships(self, board):
        ships = []
        directions = ['v', 'h']
        offset = 3
        for ship_composition in self._ship_composition:

            length = ship_composition[0]
            quantity = ship_composition[1]
            direction = random.choice(directions)
            for i in range(0, quantity):
                new_ship = False
                if direction == 'v':
                    new_ship = Ship(length, Dot(random.randrange(0, Game.get_dim() - offset),
                                                random.randrange(0, Game.get_dim() - length - offset)), direction)
                elif direction == 'h':
                    new_ship = Ship(length, Dot(random.randrange(0, Game.get_dim() - length - offset),
                                                random.randrange(0, Game.get_dim() - offset)), direction)

                ships.append(new_ship)

        return ships

    def random_board(self, hid):
        new_board = Board(hid)

        return new_board


the_game = Game()
the_game.start()
