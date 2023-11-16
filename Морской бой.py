from random import randint


class dot_game_field:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"dot_game_board({self.x}, {self.y})"


class boardException(Exception):
    pass


class boardOutException(boardException):
    def __str__(self):
        return "Вы стреляете за пределы доски"


class boardUserException(boardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class boardWrongShipException(boardException):
    pass


class Ship:
    def __init__(self, bow, length, direction):
        self.bow = bow
        self.length = length
        self.direction = direction
        self.lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            now_x = self.bow.x
            now_y = self.bow.y

            if self.direction == 0:
                now_x += i
            elif self.direction == 1:
                now_y += i

            ship_dots.append(dot_game_field(now_x, now_y))

        return ship_dots

    def shots(self, shot):
        return shot in self.dots


# s = Ship(dot_game_field(1, 2), 3, 0)


class game_board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.avg = [["0"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def ship_add(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise boardWrongShipException()

        for d in ship.dots:
            self.avg[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        around = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in around:
                now = dot_game_field(d.x + dx, d.y + dy)
                if not (self.out(now)) and now not in self.busy:
                    if verb:
                        self.avg[now.x][now.y] = "."
                    self.busy.append(now)

    def __str__(self):
        put = ""
        put += "  | 1 | 2 | 3 | 4 | 5 | 6 |"

        for i, row in enumerate(self.avg):
            put += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            put = put.replace("■", "0")

        return put

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise boardOutException()

        if d in self.busy:
            raise boardUserException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.avg[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!!!)))")
                    return False
                else:
                    print("Корабль ранен!)")
                    return True

        self.avg[d.x][d.y] = "."
        print("Мимо!(")
        return False

    def again(self):
        self.busy = []

    # def defeat(self):
    # return self.count == len(self.ships)


# a = game_board()
# a.ship_add(Ship(dot_game_field(1, 2), 3, 0))
# a.ship_add(Ship(dot_game_field(0, 0), 3, 0))
# print(a)


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except boardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = dot_game_field(randint(0, 5), (randint(0, 5)))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print("Введите 2 координаты")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите числа")
                continue

            x, y = int(x), int(y)

            return dot_game_field(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        Pl = self.random_board()
        Com = self.random_board()
        Com.hid = True

        self.us = User(Pl, Com)
        self.ai = AI(Com, Pl)

    def try_board(self):
        bins = [3, 2, 2, 1, 1, 1, 1]
        board = game_board(size=self.size)
        att = 0
        for length in bins:
            while True:
                att += 1
                if att > 3000:
                    return None
                ship = Ship(dot_game_field(randint(0, self.size), randint(0, self.size)), length, randint(0, 1))
                try:
                    board.ship_add(ship)
                    break
                except boardWrongShipException:
                    pass

        board.again()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def geep(self):
        print("Игра морской бой")
        print("Формат ввода: Х У")
        print("Х - номер строки")
        print("У - номер столбца")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера")
            print(self.ai.board)

            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Выиграл пользователь!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Выиграл компьютер!")
                break
            num += 1

    def start(self):
        self.geep()
        self.loop()


g = Game()
g.start()