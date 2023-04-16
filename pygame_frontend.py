from typing import List

import pygame
from easygui import multenterbox

from ex1 import EnvMap, all_around_policy, four_directions_policy
from ex1 import L, P, PERSONS_DISTRIBUTION, MATRIX_SIZE, DoubtLevel

NUMBER_OF_PARAMETERS = 6


class Board:
    def __init__(self, board_size, tile_size, env_map: EnvMap):
        self.board_size = board_size
        self.tile_size = tile_size
        self.env_map = env_map
        # Define the colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (128, 128, 128)
        self.RED = (255, 0, 0)

        # Create the board
        self.board = [[None] * self.env_map._n_rows for _ in range(self.env_map._n_cols)]
        # Initialize Pygame
        pygame.init()

        # Set the screen dimensions
        screen_width = self.board_size * self.tile_size
        screen_height = self.board_size * self.tile_size
        self.screen = pygame.display.set_mode((screen_width, screen_height))

        # Set the window caption
        pygame.display.set_caption("Board")

    def update_board(self):
        for i in range(self.env_map._n_rows):
            for j in range(self.env_map._n_cols):
                if self.env_map._matrix[i][j].did_hear_rumour_sometime():
                    self.board[i][j] = self.BLACK
                else:
                    self.board[i][j] = self.WHITE
        return board

    def run(self):
        cell_margin = 1
        left_margin = 20
        top_margin = 1
        # Set the flag to continue the game
        running = True
        surface = pygame.display.set_mode((
            self.board_size * self.tile_size + 40,
            self.board_size * self.tile_size + 40 + 100  # Add 100 to account for the text box and start button
        ))

        # Draw background
        background_image = pygame.image.load('background.jpg')
        surface.blit(background_image, (0, 0))

        # Loop until the user quits
        for i in range(100):
            if not running:
                break
            # Check for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONUP:
                    # Check if the click occurred within the quit button
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    button_width = 100
                    button_height = 50
                    button_x = self.board_size * self.tile_size - button_width
                    button_y = self.board_size * self.tile_size - button_height
                    if button_x <= mouse_x < button_x + button_width and button_y <= mouse_y < button_y + button_height:
                        running = False


            # Draw the board
            print(f"turn {i}==================")
            self.env_map.spread_rumor()
            self.update_board()
            # Draw the board
            for i in range(self.board_size):
                for j in range(0, self.board_size):
                    tile_rect = pygame.Rect(j * self.tile_size, i * self.tile_size, self.tile_size, self.tile_size)
                    pygame.draw.rect(surface, self.board[i][j], tile_rect, 0)
                    pygame.draw.rect(surface, self.GRAY, tile_rect, 1)

            # Update the display
            pygame.display.update()

            # Draw the quit button
            button_width = 100
            button_height = 50
            button_x = self.board_size * self.tile_size - button_width
            button_y = self.board_size * self.tile_size - button_height
            pygame.draw.rect(surface, self.RED, (button_x, button_y, button_width, button_height))
            font = pygame.font.Font(None, 36)
            text = font.render("Quit", True, self.WHITE)
            text_rect = text.get_rect(center=(button_x + button_width / 2, button_y + button_height / 2))
            surface.blit(text, text_rect)

            # Update the screen
            pygame.display.flip()

        # Quit Pygame
        pygame.quit()


def input_check(parameters: List[str]):
    def _is_probability(p: float):
        return 0 <= p <= 1

    is_ok = True
    if len(parameters) != NUMBER_OF_PARAMETERS:
        is_ok = False
    else:
        p, d_s1, d_s2, d_s3, d_s4, n_cooldown = parameters

        if sum([float(d_s1), float(d_s2), float(d_s3), float(d_s4)]) != 1:
            is_ok = False
        if not _is_probability(float(p)):
            is_ok = False
        if not n_cooldown.isnumeric():
            # L value
            is_ok = False
    return is_ok


def create_insert_parameters_window():
    # getting the user input for the simulation
    # window title
    title = "Rumour Spread simulation parameters"
    # informing the user which are the default params
    text = ("Those are the default parameters to the rumour spread simulation. \n"
            "You are more than welcome to change them!")
    # inputs fields
    inputs = ["P - Population density - percentage of people in the grid (0-1)",
              "Percentage of S1 people - people who believe to every rumour",
              "Percentage of S2 people - people who believe 2/3 of the times to rumour",
              "Percentage of S3 people - people who believe 1/3 of the times to rumour",
              "Percentage of S4 people - people who don't believe to rumours",
              "L - number of cooldown turns"
    ]
    # list of default params
    default_params = [
        P,
        PERSONS_DISTRIBUTION[DoubtLevel.S1],
        PERSONS_DISTRIBUTION[DoubtLevel.S2],
        PERSONS_DISTRIBUTION[DoubtLevel.S3],
        PERSONS_DISTRIBUTION[DoubtLevel.S4],
        L,
    ]

    output = multenterbox(text, title, inputs, default_params)
    if not input_check(output):
        print("Wrong input, Default params are being used..")
        parameters = default_params
    else:
        parameters = output

    print(f"using parameters:{parameters}")
    return parameters


def extract_parameters(parameters: List[str]):
    p, d_s1, d_s2, d_s3, d_s4, n_cooldown = parameters
    return float(p), float(d_s1), float(d_s2), float(d_s3), float(d_s4), int(n_cooldown)


if __name__ == "__main__":
    parameters = create_insert_parameters_window()
    p, d_s1, d_s2, d_s3, d_s4, n_cooldown = extract_parameters(parameters)

    TILE_SIZE = 5
    env_map = EnvMap(
        n_rows=MATRIX_SIZE,
        n_cols=MATRIX_SIZE,
        population_density=P,
        persons_distribution=PERSONS_DISTRIBUTION,
        n_cooldown=n_cooldown,
        policy=all_around_policy
    )

    # Create a new Board instance with a board size of MATRIX_SIZE and a tile size of 50
    board = Board(MATRIX_SIZE, TILE_SIZE, env_map)

    # Run the board program
    board.run()