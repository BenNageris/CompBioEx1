from typing import List

import pygame
import typing
import numpy as np

from easygui import multenterbox
import matplotlib.pyplot as plt
from ex1 import wrap_all_around_policy, all_around_policy, LocationShape, DistributionRule
from ex1 import L, P, PERSONS_DISTRIBUTION, MATRIX_SIZE, DoubtLevel, EnvMap

NUMBER_OF_PARAMETERS = 7
DEFAULT_NUMBER_OF_EPISODES = 150

Graph = typing.NamedTuple("Graph", [("graph", typing.List[int]), ("description", str), ("color", str)])


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

        self.clock = pygame.time.Clock()
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

    @staticmethod
    def handle_quit_and_escape_events():
        status = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                status = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    status = False
        return status

    def run(self, number_of_episodes: int = 100):
        # Set the flag to continue the game
        running = True
        surface = pygame.display.set_mode((
            self.board_size * self.tile_size + 40,
            self.board_size * self.tile_size + 40 + 100  # Add 100 to account for the text box and start button
        ))

        # Draw background
        background_image = pygame.image.load('background.jpg')
        surface.blit(background_image, (0, 0))
        believers_percentage = []
        running = True
        # Loop until the user quits
        for i in range(number_of_episodes):
            if not running:
                break

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

            running = self.handle_quit_and_escape_events()
            # Update the display
            pygame.display.update()
            self.clock.tick(100)
            believers_percentage.append(env_map.calculate_percentage_of_believers())

        self.clock.tick(100)
        # Quit Pygame
        pygame.quit()
        return believers_percentage


def input_check(parameters: List[str]):
    def _is_probability(p: float):
        return 0 <= p <= 1

    is_ok = True
    if len(parameters) != NUMBER_OF_PARAMETERS:
        is_ok = False
    else:
        n_episodes, p, d_s1, d_s2, d_s3, d_s4, n_cooldown = parameters

        if sum([float(d_s1), float(d_s2), float(d_s3), float(d_s4)]) != 1:
            is_ok = False
        if not _is_probability(float(p)):
            is_ok = False
        if not n_cooldown.isnumeric() or not n_episodes.isnumeric():
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
    inputs = ["Number of episodes to run",
              "P - Population density - percentage of people in the grid (0-1)",
              "Percentage of S1 people - people who believe to every rumour",
              "Percentage of S2 people - people who believe 2/3 of the times to rumour",
              "Percentage of S3 people - people who believe 1/3 of the times to rumour",
              "Percentage of S4 people - people who don't believe to rumours",
              "L - number of cooldown turns"
    ]
    # list of default params
    default_params = [
        DEFAULT_NUMBER_OF_EPISODES,
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
    n_episodes, p, d_s1, d_s2, d_s3, d_s4, n_cooldown = parameters
    return int(n_episodes), float(p), float(d_s1), float(d_s2), float(d_s3), float(d_s4), int(n_cooldown)


def plot_experiment(graphs: typing.List[Graph], times=None, shape=None, dist=None, p=P):
    for graph in graphs:
        size = len(graph.graph)
        plt.plot(np.arange(0, size), graph.graph, label=graph.description, color=graph.color, marker=".", markersize=5)

    plt.legend()
    plt.title(f"repeated experiment :={times} P:={p} shape:={shape} dist={dist}", fontsize=10)
    plt.suptitle("Rumors statistics graph", fontsize=20)
    plt.show()


def calc_growth(population):
    growth = []
    for pop in range(1, len(population)):
        numbers = (population[pop] - population[pop - 1]) / population[pop - 1] * 100
        growth.append(numbers)
    return growth


if __name__ == "__main__":
    parameters = create_insert_parameters_window()
    n_episodes, p, d_s1, d_s2, d_s3, d_s4, n_cooldown = extract_parameters(parameters)
    peoples_distribution = {
        DoubtLevel.S1: d_s1,
        DoubtLevel.S2: d_s2,
        DoubtLevel.S3: d_s3,
        DoubtLevel.S4: d_s4,
    }
    print(d_s1,d_s2,d_s3,d_s4)
    TILE_SIZE = 5
    env_map = EnvMap(
        n_rows=MATRIX_SIZE,
        n_cols=MATRIX_SIZE,
        population_density=p,
        persons_distribution=peoples_distribution,
        cool_down_l=n_cooldown,
        policy=wrap_all_around_policy,
        location_shape=LocationShape.Random,
        distribution_rule=DistributionRule.Random
    )

    # Create a new Board instance with a board size of MATRIX_SIZE and a tile size of 50
    board = Board(MATRIX_SIZE, TILE_SIZE, env_map)

    # Run the board program
    believers_percentage = board.run(n_episodes)

    plot_experiment(
        [
            Graph(
                graph=believers_percentage,
                color="blue",
                description="believers percentage"
            )
        ],
        times=1,
        p=p,
        shape="random",
        dist="random"
    )
    growth = calc_growth(believers_percentage)
    plot_experiment(
        [
            Graph(
                graph=growth,
                color="red",
                description="Believers percentage growth"
            )
        ],
        times=1,
        p=p,
        shape="random",
        dist="random"
    )
