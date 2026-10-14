from collections import deque
from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 4

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, body_color=None, position=None) -> None:
        if position is None:
            self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        else:
            self.position = position
        self.body_color = body_color

    def draw(self) -> None:
        """Метод для отрисовки объектов."""
        pass


class Apple(GameObject):
    """Класс, отвечающий за логику яблок."""

    def __init__(self, snake_position=()) -> None:
        super().__init__(APPLE_COLOR, self.randomize_position(snake_position))

    def draw(self) -> None:
        """Метод отрисовывает яблоко."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def randomize_position(self, snake_pos=()) -> tuple[int, int]:
        """Метод возвращает случайную разрешённую позицию для яблока."""
        position = None

        while position is None or position in snake_pos:
            position = (randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                        randint(0, GRID_HEIGHT - 1) * GRID_SIZE)

        return position


class Snake(GameObject):
    """Класс реализует логику работы змеи."""

    def __init__(self) -> None:
        super().__init__(SNAKE_COLOR)
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None

        # Из-за вставки в начало использую дэк
        self.positions = deque([self.position])
        self.last = None

    def draw(self) -> None:
        """Метод отвечает за отрисовку змейки."""
        for position in self.positions:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """Метод возвращает позицию головы змеи."""
        return self.positions[0]

    def move(self, new_head, is_apple_pos) -> None:
        """Метод обновляет состояние головы и хвоста змеи."""
        self.positions.appendleft(new_head)

        if not is_apple_pos:
            self.last = self.positions.pop()

    def update_direction(self) -> None:
        """Метод обновляет направление движения."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def check_collision(self) -> bool:
        """Метод проверяет столкновение змейки с собой."""
        # Сколько раз поизиция головы встретилась в дэке
        count = 0
        head = self.get_head_position()
        for pos in self.positions:
            if head == pos:
                count += 1

        return count > 1

    def reset(self) -> None:
        """Метод сбрасывает состояние змейки на исходное."""
        self.length = 1
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.positions = deque([self.position])
        self.direction = choice([LEFT, RIGHT, UP, DOWN])


def handle_keys(game_object) -> None:
    """Функция обрабатывает пользовательский ввод."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main() -> None:
    """Главная функция, управляет игровым циклом."""
    # Инициализация PyGame:
    pygame.init()
    snake = Snake()
    apple = Apple(snake.positions)

    while True:
        # Обрабатываем пользовательский ввод
        handle_keys(snake)

        # Обновление направления движения змейки
        snake.update_direction()

        # Расчитываем следующую позицию головы
        new_head = snake.get_head_position()
        x = (new_head[0] + snake.direction[0] * GRID_SIZE) % SCREEN_WIDTH
        y = (new_head[1] + snake.direction[1] * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (x, y)

        # Если новая позиция совпала с яблоком
        # то увеличиваем длину
        # чтобы метод snake.move() не отрезал хвост
        is_apple_pos = False
        if new_head == apple.position:
            snake.length += 1
            is_apple_pos = True

        snake.move(new_head, is_apple_pos)
        if is_apple_pos:
            apple.position = apple.randomize_position(snake.positions)

        # Если змея столкнулась сама с собой
        # то сбрасываем состояние на начальное
        if snake.check_collision():
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)

        # Готовим отрисовку змеи и яблока
        snake.draw()
        apple.draw()

        # Обновляем экран
        pygame.display.update()

        clock.tick(SPEED)


if __name__ == '__main__':
    main()
