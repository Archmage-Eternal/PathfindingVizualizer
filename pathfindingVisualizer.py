import pygame
import math
from queue import PriorityQueue

WIDTH = 700
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption('A* Path Finding Algorithim')

DEFAULT = (255, 255, 255)
START = (194, 82, 255)
END = (61, 0, 94)
OPEN = (97, 255, 171)
CLOSED = (15, 255, 128)
WALL = (0, 9, 56)
PATH = (247, 255, 97)
GRID_LINE = (154, 229, 252)


class Node:
    def __init__(self, row, column, width, totalRows):
        self.row = row
        self.column = column
        self.x = row * width
        self.y = column * width
        self.colour = DEFAULT
        self.neighbours = []
        self.width = width
        self.totalRows = totalRows

    def getPosition(self):
        return self.row, self.column

    def isClosed(self):
        return self.colour == CLOSED

    def isOpen(self):
        return self.colour == OPEN

    def isWall(self):
        return self.colour == WALL

    def isStart(self):
        return self.colour == START

    def isEnd(self):
        return self.colour == END

    def reset(self):
        self.colour = DEFAULT

    def makeOpen(self):
        self.colour = OPEN

    def makeClosed(self):
        self.colour = CLOSED

    def makeWall(self):
        self.colour = WALL

    def makeStart(self):
        self.colour = START

    def makeEnd(self):
        self.colour = END

    def makePath(self):
        self.colour = PATH

    def draw(self, win):
        pygame.draw.rect(win, self.colour,
                         (self.x, self.y, self.width, self.width))

    def updateNeighbours(self, grid):
        self.neighbours = []
        # Bottom boundry check.
        if self.row < self.totalRows - 1 and not grid[self.row + 1][self.column].isWall():
            self.neighbours.append(grid[self.row + 1][self.column])

        # Top boundry check.
        if self.row > 0 and not grid[self.row - 1][self.column].isWall():
            self.neighbours.append(grid[self.row - 1][self.column])

        # Right boundry check.
        if self.column < self.totalRows - 1 and not grid[self.row][self.column + 1].isWall():
            self.neighbours.append(grid[self.row][self.column + 1])

        # Left boundry check.
        if self.column > 0 and not grid[self.row][self.column - 1].isWall():
            self.neighbours.append(grid[self.row][self.column - 1])

    def __lt__(self, other):
        return False


def herustic(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.makePath()
        draw()


def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = herustic(start.getPosition(), end.getPosition())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            start.makeStart()
            end.makeEnd()
            return True

        for neighbour in current.neighbours:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbour]:
                came_from[neighbour] = current
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = temp_g_score + \
                    herustic(neighbour.getPosition(), end.getPosition())
                if neighbour not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbour], count, neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.makeOpen()

        draw()

        if current != start:
            current.makeClosed()

    return False


def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)

    return grid


def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GRID_LINE, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GRID_LINE, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
    win.fill(DEFAULT)

    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()


def get_clicked_position(position, rows, width):
    gap = width // rows
    y, x = position

    row = y // gap
    column = x // gap

    return row, column


def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:  # LEFT
                position = pygame.mouse.get_pos()
                row, col = get_clicked_position(position, ROWS, width)
                node = grid[row][col]
                if not start and node != end:
                    start = node
                    start.makeStart()

                elif not end and node != start:
                    end = node
                    end.makeEnd()

                elif node != end and node != start:
                    node.makeWall()

            elif pygame.mouse.get_pressed()[2]:  # RIGHT
                position = pygame.mouse.get_pos()
                row, column = get_clicked_position(position, ROWS, width)
                node = grid[row][column]
                node.reset()
                if node == start:
                    start = None
                elif node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.updateNeighbours(grid)

                    algorithm(lambda: draw(win, grid, ROWS, width),
                              grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()


main(WIN, WIDTH)
