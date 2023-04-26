import random
from collections import Counter
from enum import Enum
from itertools import product
from typing import Dict, Tuple, List, Callable
import typing

from DoubtLevel import DoubtLevel
from persons_location_generator import PersonsLocationGenerator

Location = typing.NamedTuple("Location", [("x", int), ("y", int)])

MATRIX_SIZE = 100

P = 0.8  # population density
L = 10



MIN_DOUBT_LEVEL = 1


class CellStates(Enum):
    S1 = DoubtLevel.S1
    S2 = DoubtLevel.S2
    S3 = DoubtLevel.S3
    S4 = DoubtLevel.S4
    EMPTY = 0


PERSONS_DISTRIBUTION = {
    DoubtLevel.S1: 1 / 4,
    DoubtLevel.S2: 1 / 4,
    DoubtLevel.S3: 1 / 4,
    DoubtLevel.S4: 1 / 4,
}

PROBABILITY_TO_BELIEVE = {
    DoubtLevel.S1: 1,
    DoubtLevel.S2: 2 / 3,
    DoubtLevel.S3: 1 / 3,
    DoubtLevel.S4: 0,
}


class Cell:
    """
    This class represents a cell in the map
    """

    def __init__(self, state, position):
        self._state = state
        self._position = Location(*position)

    def __str__(self) -> str:
        return f"{self._position}:{self._state}"

    def set_heard_rumour(self, heard_rumour: bool = True):
        raise NotImplementedError()

    def should_believe_to_rumour(self, n_heard_rumour) -> bool:
        raise NotImplementedError()

    def toggle_heard_rumour_sometime(self):
        raise NotImplementedError()

    def was_told_rumour(self):
        raise NotImplementedError()

    def next_turn(self):
        raise NotImplementedError()

    def did_hear_rumour_sometime(self):
        return False

    def set_spread_already(self, spread_already=True):
        raise NotImplementedError()

    def can_spread_rumour(self):
        raise NotImplementedError()


class PersonCell(Cell):
    def __init__(
            self,
            state,
            position,
            cool_down_episode_countdown):
        super().__init__(state=state.value, position=position)
        self._probability_to_believe = PROBABILITY_TO_BELIEVE[state]
        self._doubt_level = state
        self._heard_rumour_sometime = False
        self._heard_rumour = False
        self._spread_already = False
        self._cool_down_episode_countdown = cool_down_episode_countdown
        self._n_cool_down_episodes_countdown = cool_down_episode_countdown

    def __str__(self) -> str:
        return (f"{super().__str__()},"
                f" believe percentage:{self._probability_to_believe},"
                f" heard rumour:{self._heard_rumour},"
                f" spread already:{self._spread_already},"
                f" number of episodes till rumour spread:{self._n_cool_down_episodes_countdown}")

    def reset_n_cool_down_episodes_countdown(self):
        self._n_cool_down_episodes_countdown = self._cool_down_episode_countdown

    def set_n_cool_down_episode_countdown(self, n):
        self._n_cool_down_episodes_countdown = n

    def dec_n_cool_down_episode_countdown(self):
        if self._n_cool_down_episodes_countdown > 0:
            self._n_cool_down_episodes_countdown = self._n_cool_down_episodes_countdown - 1

    def did_hear_rumour_sometime(self):
        return self._heard_rumour_sometime

    def toggle_heard_rumour_sometime(self):
        self._heard_rumour_sometime = True

    def set_heard_rumour(self, heard_rumour: bool = True):
        self._heard_rumour = heard_rumour

    def set_spread_already(self, spread_already=True):
        self._spread_already = spread_already

    def should_believe_to_rumour(self, n_heard_rumour):
        prob_to_believe = self._probability_to_believe
        # if a person hears 2 or more times the rumour in one episode the probability to believe increases
        if n_heard_rumour >= 2:
            temporal_doubt_level = DoubtLevel(max(self._doubt_level.value - 1, MIN_DOUBT_LEVEL))
            prob_to_believe = PROBABILITY_TO_BELIEVE[temporal_doubt_level]
        return random.random() < prob_to_believe

    def next_turn(self):
        if self._heard_rumour or self._spread_already:
            self.dec_n_cool_down_episode_countdown()
        if self._n_cool_down_episodes_countdown == 0:
            # RESET state of spread already
            self.set_spread_already(spread_already=False)

    def can_spread_rumour(self):
        return self._heard_rumour is True and self._n_cool_down_episodes_countdown == 0

    def was_told_rumour(self):
        # rumour spread to neighbor
        self.set_heard_rumour(True)
        self.set_n_cool_down_episode_countdown(1)
        # HEARD SOMETIME = True
        self.toggle_heard_rumour_sometime()


class EmptyCell(Cell):
    def __init__(self, position):
        super().__init__(state=CellStates.EMPTY.value, position=position)

    def set_heard_rumour(self, heard_rumour: bool = True):
        print("Set heard rumour in EmptyCell - something is wrong")
        pass

    def was_told_rumour(self):
        print("Empty Cell was told rumour")
        pass

    def next_turn(self):
        print("Empty Cell next turn")
        pass

    def can_spread_rumour(self):
        return False

    def should_believe_to_rumour(self, n_heard_rumour) -> bool:
        return False

    def set_spread_already(self, spread_already=True):
        print("Set spread already in EmptyCell  - something is wrong")


class EnvMap:
    def __init__(
            self,
            n_rows: int,
            n_cols: int,
            population_density: float,
            persons_distribution: Dict[DoubtLevel, float],
            policy: Callable,
            cool_down_l: int,
            location_shape: str,
            distribution_rule: str,
            location_generator=PersonsLocationGenerator()
    ):
        self.location_generator = location_generator
        self.cool_down_l = cool_down_l
        self.doubt_level_locations_dict = None
        self.persons_location: Dict[Location, PersonCell] = {}
        self._n_rows = n_rows
        self._n_cols = n_cols
        self._policy = policy
        if population_density > 1 or population_density < 0:
            raise Exception(
                f"Invalid value of population density, it should be between 0 to 1, not:{population_density}"
            )
        self._population_density = population_density
        if len(persons_distribution.keys()) != len(DoubtLevel):
            raise Exception(
                f"Invalid value of persons distribution, it should be have {len(DoubtLevel)} values"
            )
        self._persons_distribution = persons_distribution
        self._matrix: List[List[Cell]] = self._create_matrix(n_rows=n_rows, n_cols=n_cols)
        self._num_dimensions = 2
        self.init_matrix(location_shape=location_shape, distribution_rule=distribution_rule)

    @staticmethod
    def _create_matrix(n_rows: int, n_cols: int) -> typing.List[typing.List[typing.Any]]:
        matrix = []
        for r in range(n_rows):
            row = []
            for col in range(n_cols):
                row.append(None)
            matrix.append(row)
        return matrix

    @staticmethod
    def _get_n_doubt_level_dict(number_of_persons: int, persons_distribution):
        n_doubt_level_dict = {}
        for doubt_level in DoubtLevel:
            n_doubt_level_dict[doubt_level] = int(
                number_of_persons * persons_distribution[doubt_level]
            )
        return n_doubt_level_dict

    @staticmethod
    def _sample_for_each_doubt_level(persons_location, persons_distribution):
        n_persons = len(persons_location)
        n_doubt_level_dict = EnvMap._get_n_doubt_level_dict(
            number_of_persons=n_persons, persons_distribution=persons_distribution
        )
        doubt_level_locations_dict = {}
        for doubt_level in DoubtLevel:
            n_doubt_level = n_doubt_level_dict[doubt_level]
            n_doubt_level_randomized_locations = random.sample(
                list(persons_location), k=n_doubt_level
            )
            for loca in n_doubt_level_randomized_locations:
                doubt_level_locations_dict[loca] = doubt_level
            persons_location = list(
                set(persons_location) - set(n_doubt_level_randomized_locations)
            )
        return doubt_level_locations_dict

    def init_matrix(self, location_shape, distribution_rule):
        # init matrix with cells
        n_person_cells = int(self._n_cols * self._n_rows * self._population_density)

        if location_shape == 'random':
            self.persons_location = self.location_generator.random_locations(n_person_cells=n_person_cells,
                                                                             n_cols=self._n_cols,
                                                                             n_rows=self._n_rows)
        elif location_shape == 'line':
            self.persons_location = self.location_generator.lines_location(n_person_cells=n_person_cells,
                                                                           n_cols=self._n_cols,
                                                                           n_rows=self._n_rows)
        elif location_shape == 'square':
            self.persons_location = self.location_generator.square_location(n_person_cells=n_person_cells,
                                                                            n_cols=self._n_cols,
                                                                            n_rows=self._n_rows)
        if distribution_rule == 'space':
            self.doubt_level_locations_dict = self.location_generator.doubt_sample_easy_believer_next_to_not(
                persons_location=self.persons_location
            )
        elif distribution_rule == 'k_space':
            self.doubt_level_locations_dict = self.location_generator.doubt_sample_easy_believer_next_to_k_hard_believers(
                persons_location=self.persons_location
            )
        elif distribution_rule == 'line_space':
            self.doubt_level_locations_dict =self.location_generator.doubt_sample_line_between_easy_believer_hard_believers(
                persons_location=self.persons_location,easy_doubt=[DoubtLevel.S1],hard_doubt=[DoubtLevel.S4])
        else:
            # default
            self.doubt_level_locations_dict = self._sample_for_each_doubt_level(
                persons_location=self.persons_location,
                persons_distribution=self._persons_distribution,
            )
        self._init_matrix_cells(
            doubt_level_locations_dict=self.doubt_level_locations_dict
        )

        self._init_first_spread_rumor()

    def _init_matrix_cells(self, doubt_level_locations_dict: Dict[Tuple[int, int], DoubtLevel]):
        for (x, y), doubt_level in doubt_level_locations_dict.items():
            self._matrix[x][y] = PersonCell(
                state=doubt_level,
                position=Location(x=x, y=y),
                cool_down_episode_countdown=self.cool_down_l)
        for row in range(self._n_rows):
            for col in range(self._n_cols):
                if self._matrix[row][col] is None:
                    self._matrix[row][col] = EmptyCell(
                        position=Location(x=row, y=col)
                    )

    def _get_all_neighbors_location(self, location: Location):
        all_neighbors = Counter()
        for neighbor_location in self._policy(location):
            if neighbor_location in self.persons_location:
                all_neighbors.update([neighbor_location])
        return all_neighbors

    def _init_first_spread_rumor(self) -> None:
        first_spreader: PersonCell = self._get_random_person()
        first_spreader.toggle_heard_rumour_sometime()
        first_spreader.set_heard_rumour(heard_rumour=True)
        first_spreader.set_n_cool_down_episode_countdown(n=0)
        print(f"first spreader:{first_spreader}")

    def spread_rumor(self):
        # iterate over matrix,  spread rumour and create the next turn's matrix

        # calc who can spread rumour in this episode
        rumour_spreaders: Dict[Location, PersonCell] = {}
        for row, col in self.persons_location:
            if self._matrix[row][col].can_spread_rumour():
                rumour_spreaders[Location(x=row, y=col)] = self._matrix[row][col]

        # Count number of times each cell got rumour
        total_rumour_spreads_in_episode = Counter()
        for spread_rumour_location, cell in rumour_spreaders.items():
            neighbors = self._get_all_neighbors_location(spread_rumour_location)
            total_rumour_spreads_in_episode.update(neighbors)

        # Calculate who believes the rumour
        rumour_believers: List[Cell] = []
        for neighbor_location, number_heard_about_rumour in total_rumour_spreads_in_episode.items():
            cell = self._matrix[neighbor_location.x][neighbor_location.y]
            if cell.should_believe_to_rumour(number_heard_about_rumour):
                rumour_believers.append(cell)
        # print(fr"rumour believers:{rumour_believers}")

        # update the state of cells that were told the rumour in this episode
        for rumour_believer in rumour_believers:
            rumour_believer.was_told_rumour()

        # update the rumour spreaders in this episode: RST cool time, spread_already to False, heard rumour to False
        # print(f"rumour spreaders:{[str(rumour_spearder) for rumour_spearder in rumour_spreaders]}")
        for rumour_spreader_location, rumour_spreader in rumour_spreaders.items():
            rumour_spreader.set_heard_rumour(heard_rumour=False)
            rumour_spreader.set_spread_already(spread_already=True)
            rumour_spreader.reset_n_cool_down_episodes_countdown()

        # Prepare for next turn (for example: dec cooldown values)
        self.next_turn()

        print(f"total rumour spreads:{total_rumour_spreads_in_episode}")
        # Check who got the rumour twice+ (will cause probability to believe deduct).

    def next_turn(self):
        for row, col in self.persons_location:
            self._matrix[row][col].next_turn()

    # def _get_random_person_cell(self) -> PersonCell:
    #     x, y = random.choice(list(self.persons_location))
    #     return self._matrix[x][y]

    def _get_random_person(self) -> PersonCell:
        x, y = random.choice(list(self.persons_location))
        return self._matrix[x][y]

    def calculate_percentage_of_believeres(self):
        n_persons = len(self.persons_location)
        cnt = 0
        for x, y in self.persons_location:
            cell = self._matrix[x][y]
            if cell.did_hear_rumour_sometime():
                cnt += 1
        return cnt / n_persons


def wrap_all_around_policy(location: Location):
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if i == 0 and j == 0:
                continue
            neighbor_x = (location.x + i) % MATRIX_SIZE
            neighbor_y = (location.y + j) % MATRIX_SIZE
            yield Location(neighbor_x, neighbor_y)


def all_around_policy(location: Location):
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if i == 0 and j == 0:
                continue
            neighbor_x = location.x + i
            neighbor_y = location.y + j
            if neighbor_x < 0 or neighbor_x >= MATRIX_SIZE or neighbor_y < 0 or neighbor_y >= MATRIX_SIZE:
                continue
            yield Location(neighbor_x, neighbor_y)


def four_directions_policy():
    for i in [-1, 1]:
        yield 0, i
        yield i, 0


if __name__ == "__main__":
    env_map = EnvMap(
        n_rows=MATRIX_SIZE,
        n_cols=MATRIX_SIZE,
        population_density=P,
        persons_distribution=PERSONS_DISTRIBUTION,
        cool_down_l=4,
        policy=all_around_policy,
        location_shape='random',
        distribution_rule='default'
    )
    for i in range(100):
        print(f"turn {i}==================")
        env_map.spread_rumor()
        print(env_map.calculate_percentage_of_believeres())
