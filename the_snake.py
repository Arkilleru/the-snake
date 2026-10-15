from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Словарь направлений
DIRECTIONS = {
    (LEFT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_UP): UP,
    (RIGHT, pg.K_DOWN): DOWN,
    (UP, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_LEFT): LEFT
}

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет камня
ROCK_COLOR = (128, 128, 128)

# Цвет змейки
SNAKE_COLOR = (139, 0, 255)

# Скорость движения змейки:
SPEED = 4

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка, для выхода нажмите escape')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, body_color=None) -> None:
        self.position = CENTER
        self.body_color = body_color

    @staticmethod
    def draw_rect(position, color, border=True) -> None:
        """Метод для отрисовки клетки поля."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)

        if border:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self) -> None:
        """Метод для отрисовки объектов."""
        raise NotImplementedError(
            'Метод draw нужно переопределить в наследниках')


class StaticObject(GameObject):
    """Класс, отвечающий за логику неподвижных объектов"""

    def draw(self) -> None:
        """Метод отрисовывает статические объекты."""
        self.draw_rect(self.position, self.body_color)

    def randomize_position(self, occupied_position) -> None:
        """
        Метод возвращает случайную не занятую
        позицию для статических объектов.
        """
        while True:
            self.position = (randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                             randint(0, GRID_HEIGHT - 1) * GRID_SIZE)
            if self.position not in occupied_position:
                break


class Apple(StaticObject):
    """Класс, отвечающий за логику яблок."""

    def __init__(self, occupied_position=None) -> None:
        super().__init__(APPLE_COLOR)
        self.randomize_position(occupied_position or [])


class Rock(StaticObject):
    """Класс, отвечающий за логику камней."""

    def __init__(self, occupied_position=None) -> None:
        super().__init__(ROCK_COLOR)
        self.randomize_position(occupied_position or [])


class Snake(GameObject):
    """Класс реализует логику работы змеи."""

    def __init__(self) -> None:
        super().__init__(SNAKE_COLOR)
        self.reset()

        # По ТЗ при создании должна двигаться вправо
        self.direction = RIGHT
        self.last = None

    def draw(self) -> None:
        """Метод отвечает за отрисовку змейки."""
        # Отрисовка головы змейки
        self.draw_rect(self.get_head_position(), self.body_color)

        # Затирание последнего сегмента
        if self.last:
            self.draw_rect(self.last, BOARD_BACKGROUND_COLOR, False)

    def get_head_position(self):
        """Метод возвращает позицию головы змеи."""
        return self.positions[0]

    def move(self) -> None:
        """Метод обновляет состояние головы и хвоста змеи."""
        x, y = self.get_head_position()
        dx, dy = self.direction
        self.position = ((x + (dx * GRID_SIZE)) % SCREEN_WIDTH,
                         (y + (dy * GRID_SIZE)) % SCREEN_HEIGHT)

        self.positions.insert(0, self.position)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def update_direction(self, new_direction) -> None:
        """Метод обновляет направление движения."""
        self.direction = new_direction

    def reset(self) -> None:
        """Метод сбрасывает состояние змейки на исходное."""
        self.length = 1

        # После каждого столкновения возвращает в центр
        self.position = CENTER
        self.positions = [self.position]
        self.direction = choice([LEFT, RIGHT, UP, DOWN])


def handle_keys(game_object) -> bool:
    """Функция обрабатывает пользовательский ввод."""
    curr_direction = new_direction = game_object.direction

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                return False
            new_direction = DIRECTIONS.get((curr_direction, event.key),
                                           new_direction)
    game_object.update_direction(new_direction)

    return True


def main() -> None:
    """Главная функция, управляет игровым циклом."""
    # Инициализация pg:
    pg.init()
    snake = Snake()
    apple = Apple(snake.positions)
    rock = Rock(snake.positions + [apple.position])

    while True:
        # Обрабатываем пользовательский ввод
        if not handle_keys(snake):
            break

        snake.move()
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions + [rock.position])

        # Если змея столкнулась сама с собой
        # то сбрасываем состояние на начальное
        elif (snake.positions.count(snake.get_head_position()) > 1
              or snake.get_head_position() == rock.position):
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)
            rock.randomize_position(snake.positions + [apple.position])

        # Готовим отрисовку змейки, яблока и камня
        snake.draw()
        apple.draw()
        rock.draw()

        # Обновляем экран
        pg.display.update()

        clock.tick(SPEED)

    pg.quit()


if __name__ == '__main__':
    main()
