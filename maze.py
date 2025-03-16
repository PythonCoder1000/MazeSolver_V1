from collections import deque
import pygame
import random
import sys
import time

pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

CELL_SIZE = 10
MARGIN = 1

def add_tuples(a, b):
    return tuple(x + y for x, y in zip(a, b))

class MazeNode:
    def __init__(self, traversable=True):
        self.traversable = traversable
        self.is_start = False
        self.is_end = False
        self.visited = False

class Maze:
    def __init__(self, maze_layout):
        self.maze = self.create_maze(maze_layout)
        self.rows = len(self.maze)
        self.cols = len(self.maze[0]) if self.rows > 0 else 0
        self.start_node = None
        self.end_node = None

    def create_maze(self, layout):
        return [[MazeNode(cell != '#') for cell in row] for row in layout]

    def set_start(self, row, col):
        self.maze[row][col].is_start = True
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.start_node = (row, col)

    def set_end(self, row, col):
        self.maze[row][col].is_end = True
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.end_node = (row, col)

    def get_available_directions(self, row, col):
        directions = []
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < self.rows and 0 <= new_col < self.cols and 
                self.maze[new_row][new_col].traversable):
                directions.append((dr, dc))
        return directions

class MazeSolver:
    def __init__(self, maze, solver):
        self.maze = maze
        self.current_pos = maze.start_node
        self.facing = 0
        self.solver = solver
    
    def find_move(self, row, col):
        if self.solver == "A*":
            self.A_star(row, col)
        
    def A_star(self, row, col):
        directions = self.maze.get_available_directions(row, col)
        least_dist = float('inf')
        best_move = None
        for direction in directions:
            new_pos = add_tuples(self.current_pos, direction)
            if self.maze.maze[new_pos[0]][new_pos[1]].traversable:
                distance_to_end = self.calculate_distance_to_end(new_pos[0], new_pos[1])
            else:
                continue
            if distance_to_end < least_dist:
                least_dist = distance_to_end
                best_move = direction

        if best_move:
            self.current_pos = add_tuples(self.current_pos, best_move)
        else:
            raise Exception("No available directions to move.") 

    def solve_step(self):
        if self.current_pos == self.maze.end_node:
            return True
        
        row, col = self.current_pos
        self.maze.maze[row][col].visited = True

        self.find_move(row, col)

        return False

    def calculate_distance_to_end(self, start_row, start_col):
        queue = deque([(start_row, start_col, 0)])
        visited = set()

        while queue:
            row, col, distance = queue.popleft()

            if (row, col) == self.maze.end_node:
                return distance

            if (row, col) in visited:
                continue

            visited.add((row, col))

            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_row, new_col = row + dr, col + dc
                if (0 <= new_row < self.maze.rows and 
                    0 <= new_col < self.maze.cols and 
                    self.maze.maze[new_row][new_col].traversable and 
                    (new_row, new_col) not in visited):
                    queue.append((new_row, new_col, distance + 1))

        return float('inf')

def draw_maze(screen, maze, solver):
    screen.fill(BLACK)
    for row in range(maze.rows):
        for col in range(maze.cols):
            node = maze.maze[row][col]
            color = WHITE if not node.traversable else BLACK
            if node.is_end:
                color = RED
            if node.visited:
                color = GRAY
            if (row, col) == solver.current_pos:
                color = BLUE
            if node.is_start:
                color = GREEN
            pygame.draw.rect(screen, color, 
                             [col * (CELL_SIZE + MARGIN) + MARGIN,
                              row * (CELL_SIZE + MARGIN) + MARGIN,
                              CELL_SIZE, CELL_SIZE])
    pygame.display.flip()

class MazeGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.maze = [['#' for _ in range(width)] for _ in range(height)]

    def generate(self):
        self._carve_passages_from(1, 1)
        
        self.maze[1][1] = 'S'
        self.maze[self.height - 2][self.width - 2] = 'E'
        
        return [''.join(row) for row in self.maze]

    def _carve_passages_from(self, cx, cy):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = cx + dx * 2, cy + dy * 2
            if 0 <= nx < self.width and 0 <= ny < self.height and self.maze[ny][nx] == '#':
                self.maze[cy + dy][cx + dx] = ' '
                self.maze[ny][nx] = ' '
                self._carve_passages_from(nx, ny)

def main(test_mode=False, tests=1, speed=5, solver="A*"):
    width = 70
    height = 60
    maze_generator = MazeGenerator(width, height)
    maze_layout = maze_generator.generate()

    maze = Maze(maze_layout)
    maze.set_start(1, 1)
    maze.set_end(height - 2, width - 2)

    solver = MazeSolver(maze, solver)

    if not test_mode:
        screen_width = maze.cols * (CELL_SIZE + MARGIN) + MARGIN
        screen_height = maze.rows * (CELL_SIZE + MARGIN) + MARGIN
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Maze Solver")

        clock = pygame.time.Clock()
        solved = False

        while not solved:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            solved = solver.solve_step()
            draw_maze(screen, maze, solver)
            clock.tick(speed)

        pygame.time.wait(2000)
        pygame.quit()
    else:
        runtimes = []
        for _ in range(tests):
            start = time.time()
            maze_layout = maze_generator.generate()
            maze = Maze(maze_layout)
            maze.set_start(1, 1)
            maze.set_end(25, 31)
            solved = False
            while not solved:
                solved = solver.solve_step()
            end = time.time()
            runtimes.append(end - start)
        average_runtime = sum(runtimes) / len(runtimes) if runtimes else 0
        if average_runtime < 1:
            print(f"Average runtime: {((sum(runtimes) / len(runtimes)) * 1000):.2f} ms")
        else:
            print(f"Average runtime: {average_runtime:.4f} seconds")
                

if __name__ == "__main__":
    main(False, 0, 30, "A*")