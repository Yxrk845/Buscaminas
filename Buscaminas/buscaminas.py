import sys
import pygame
import random
from pygame.locals import *

pygame.init()
pygame.font.init()  

WINDOW_SIZE = 600
GRID_SIZE = 8
CELL_SIZE = WINDOW_SIZE // GRID_SIZE
MINE_COUNT = 10

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)

class Cell:
    def __init__(self):
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.adjacent_mines = 0

class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, surface, font):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class MinesweeperGame:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 50))
        pygame.display.set_caption("Buscaminas")
        self.font = pygame.font.Font(None, 36)
        self.reset_game()
        self.ai_button = Button(WINDOW_SIZE - 120, WINDOW_SIZE + 10, 100, 30, "Usar IA", LIGHT_BLUE, BLACK)

    def reset_game(self):
        self.board = [[Cell() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.place_mines()
        self.calculate_adjacent_mines()
        self.game_over = False
        self.game_won = False

    def place_mines(self):
        mines_placed = 0
        while mines_placed < MINE_COUNT:
            row = random.randint(0, GRID_SIZE - 1)
            col = random.randint(0, GRID_SIZE - 1)
            if not self.board[row][col].is_mine:
                self.board[row][col].is_mine = True
                mines_placed += 1

    def calculate_adjacent_mines(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if not self.board[row][col].is_mine:
                    self.board[row][col].adjacent_mines = self.count_adjacent_mines(row, col)

    def count_adjacent_mines(self, row, col):
        count = 0
        for i in range(max(0, row - 1), min(GRID_SIZE, row + 2)):
            for j in range(max(0, col - 1), min(GRID_SIZE, col + 2)):
                if self.board[i][j].is_mine:
                    count += 1
        return count

    def reveal_cell(self, row, col):
        if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE):
            return
        cell = self.board[row][col]
        if cell.is_revealed or cell.is_flagged:
            return
        cell.is_revealed = True
        if cell.is_mine:
            self.game_over = True
        elif cell.adjacent_mines == 0:
            for i in range(row - 1, row + 2):
                for j in range(col - 1, col + 2):
                    self.reveal_cell(i, j)
        self.check_win()

    def flag_cell(self, row, col):
        if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE):
            return
        cell = self.board[row][col]
        if not cell.is_revealed:
            cell.is_flagged = not cell.is_flagged

    def check_win(self):
        for row in self.board:
            for cell in row:
                if not cell.is_mine and not cell.is_revealed:
                    return
        self.game_won = True

    def draw_board(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                cell = self.board[row][col]
                rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if cell.is_revealed:
                    if cell.is_mine:
                        pygame.draw.rect(self.window, RED, rect)
                    else:
                        pygame.draw.rect(self.window, WHITE, rect)
                        if cell.adjacent_mines > 0:
                            text = self.font.render(str(cell.adjacent_mines), True, BLUE)
                            text_rect = text.get_rect(center=rect.center)
                            self.window.blit(text, text_rect)
                else:
                    pygame.draw.rect(self.window, GRAY, rect)
                    if cell.is_flagged:
                        pygame.draw.polygon(self.window, RED, 
                            [(col * CELL_SIZE + 10, row * CELL_SIZE + 10),
                             (col * CELL_SIZE + CELL_SIZE - 10, row * CELL_SIZE + CELL_SIZE // 2),
                             (col * CELL_SIZE + 10, row * CELL_SIZE + CELL_SIZE - 10)])
                pygame.draw.rect(self.window, BLACK, rect, 1)
        
        self.ai_button.draw(self.window, self.font)

    def handle_click(self, pos, right_click=False):
        if self.game_over or self.game_won:
            return
        col = pos[0] // CELL_SIZE
        row = pos[1] // CELL_SIZE
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            if right_click:
                self.flag_cell(row, col)
            else:
                self.reveal_cell(row, col)

    def ai_move(self):
        # Simple AI: Reveal a random unrevealed cell that's not flagged
        unrevealed_cells = [(row, col) for row in range(GRID_SIZE) for col in range(GRID_SIZE)
                            if not self.board[row][col].is_revealed and not self.board[row][col].is_flagged]
        if unrevealed_cells:
            row, col = random.choice(unrevealed_cells)
            self.reveal_cell(row, col)

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if self.ai_button.is_clicked(event.pos):
                            self.ai_move()
                        else:
                            self.handle_click(event.pos)
                    elif event.button == 3:  # Right click
                        self.handle_click(event.pos, right_click=True)

            self.window.fill(WHITE)
            self.draw_board()
            
            if self.game_over:
                text = self.font.render("Perdiste!", True, RED)
            elif self.game_won:
                text = self.font.render("Ganaste!", True, GREEN)
            else:
                text = self.font.render("Buscaminas", True, BLACK)
            
            text_rect = text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE + 25))
            self.window.blit(text, text_rect)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()

class MainMenu:
    def __init__(self):
        self.window = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Menu")
        self.font = pygame.font.Font(None, 48)
        self.title_font = pygame.font.Font(None, 72)
        self.start_button = Button(WINDOW_SIZE // 2 - 100, 300, 200, 50, "Jugar", GREEN, WHITE)
        self.quit_button = Button(WINDOW_SIZE // 2 - 100, 400, 200, 50, "Salir", RED, WHITE)
        
        # Load background image
        self.background = pygame.image.load("Fondo.png")
        self.background = pygame.transform.scale(self.background, (WINDOW_SIZE, WINDOW_SIZE))

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.start_button.is_clicked(event.pos):
                            return True
                        elif self.quit_button.is_clicked(event.pos):
                            pygame.quit()
                            sys.exit()

            # Draw background
            self.window.blit(self.background, (0, 0))

            # Draw semi-transparent overlay to improve text visibility
            overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            self.window.blit(overlay, (0, 0))

            title = self.title_font.render("Buscaminas", True, WHITE)
            title_rect = title.get_rect(center=(WINDOW_SIZE // 2, 150))
            self.window.blit(title, title_rect)

            self.start_button.draw(self.window, self.font)
            self.quit_button.draw(self.window, self.font)

            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    menu = MainMenu()
    while True:
        if menu.run():
            game = MinesweeperGame()
            game.run()