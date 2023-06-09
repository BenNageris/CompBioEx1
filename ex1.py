import random
from collections import Counter
from enum import Enum
from typing import Dict, Tuple, List, Callable
import typing

from DoubtLevel import DoubtLevel
from persons_location_generator import PersonsLocationGenerator

Location = typing.NamedTuple("Location", [("x", int), ("y", int)])

MATRIX_SIZE = 100

P = 0.81  # population density
L = 10
MIN_DOUBT_LEVEL = 1

class LocationShape(Enum):
    Random = 1
    Square = 2
    Lines = 3
    DavidStar = 4
    Frame = 5

class DistributionRule(Enum):
    Random = 1
    Space = 2
    K_Space = 3
    Line_Space = 4


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

    def set_heard_rumour_last_turn(self, heard_rumour_last_turn: bool = True):
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
        self._heard_rumour_last_turn = False
        self._is_in_cooldown = False
        self._cool_down_episode_countdown = cool_down_episode_countdown
        self._n_cool_down_episodes_countdown = cool_down_episode_countdown

    def __str__(self) -> str:
        return (f"{super().__str__()},"
                f" believe percentage:{self._probability_to_believe},"
                f" heard rumour last turn:{self._heard_rumour_last_turn},"
                f" number of episodes till end cooldown:{self._n_cool_down_episodes_countdown},"
                f" is in cooldown:{self._is_in_cooldown}")

    def reset_n_cool_down_episodes_countdown(self):
        self._n_cool_down_episodes_countdown = self._cool_down_episode_countdown

    def set_is_in_cooldown(self, val):
        self._is_in_cooldown = val

    def set_n_cool_down_episode_countdown(self, n):
        self._n_cool_down_episodes_countdown = n

    def dec_n_cool_down_episode_countdown(self):
        if self._n_cool_down_episodes_countdown > 0:
            self._n_cool_down_episodes_countdown = self._n_cool_down_episodes_countdown - 1

    def did_hear_rumour_sometime(self):
        return self._heard_rumour_sometime

    def toggle_heard_rumour_sometime(self):
        self._heard_rumour_sometime = True

    def set_heard_rumour_last_turn(self, heard_rumour_last_turn: bool = True):
        self._heard_rumour_last_turn = heard_rumour_last_turn

    def should_believe_to_rumour(self, n_heard_rumour):
        if self._is_in_cooldown is True:
            return False
        prob_to_believe = self._probability_to_believe
        # if a person hears 2 or more times the rumour in one episode the probability to believe increases
        if n_heard_rumour >= 2:
            temporal_doubt_level = DoubtLevel(max(self._doubt_level.value - 1, MIN_DOUBT_LEVEL))
            prob_to_believe = PROBABILITY_TO_BELIEVE[temporal_doubt_level]
        return random.random() < prob_to_believe

    def next_turn(self):
        if self._heard_rumour_last_turn or self._is_in_cooldown:
            self.dec_n_cool_down_episode_countdown()
        # Cooldown finished
        if self._n_cool_down_episodes_countdown == 0:
            self.set_is_in_cooldown(False)

    def can_spread_rumour(self):
        return self._heard_rumour_last_turn is True and self._n_cool_down_episodes_countdown == 0

    def was_told_rumour(self):
        # rumour spread to neighbor
        self.set_heard_rumour_last_turn(True)
        self.set_n_cool_down_episode_countdown(1)
        # HEARD SOMETIME = True
        self.toggle_heard_rumour_sometime()


class EmptyCell(Cell):
    def __init__(self, position):
        super().__init__(state=CellStates.EMPTY.value, position=position)

    def set_heard_rumour_last_turn(self, heard_rumour_last_turn: bool = True):
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


class EnvMap:
    def __init__(
            self,
            n_rows: int,
            n_cols: int,
            population_density: float,
            persons_distribution: Dict[DoubtLevel, float],
            policy: Callable,
            cool_down_l: int,
            location_shape: LocationShape,
            distribution_rule: DistributionRule,
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

    def init_matrix(self, location_shape: LocationShape, distribution_rule):
        # init matrix with cells
        n_person_cells = int(self._n_cols * self._n_rows * self._population_density)

        if location_shape == LocationShape.Random:
            self.persons_location = self.location_generator.random_locations(n_person_cells=n_person_cells,
                                                                             n_cols=self._n_cols,
                                                                             n_rows=self._n_rows)
        elif location_shape == LocationShape.Lines:
            self.persons_location = self.location_generator.lines_location(n_person_cells=n_person_cells,
                                                                           n_cols=self._n_cols,
                                                                           n_rows=self._n_rows)
        elif location_shape == LocationShape.Square:
            self.persons_location = self.location_generator.square_location(n_person_cells=n_person_cells,
                                                                            n_cols=self._n_cols,
                                                                            n_rows=self._n_rows)
        elif location_shape == LocationShape.DavidStar:
            self.persons_location = self.location_generator.david_star_locations(n_person_cells=n_person_cells,
                                                                            n_cols=self._n_cols,
                                                                            n_rows=self._n_rows)
        elif location_shape == LocationShape.Frame:
            self.persons_location = self.location_generator.frame_location(n_person_cells=n_person_cells,
                                                                            n_cols=self._n_cols,
                                                                            n_rows=self._n_rows)

        if distribution_rule == DistributionRule.Space:
            self.doubt_level_locations_dict = self.location_generator.doubt_sample_easy_believer_next_to_not(
                persons_location=self.persons_location
            )
        elif distribution_rule == DistributionRule.K_Space:
            self.doubt_level_locations_dict = self.location_generator.doubt_sample_easy_believer_next_to_k_hard_believers(
                persons_location=self.persons_location
            )
        elif distribution_rule == DistributionRule.Line_Space:
            self.doubt_level_locations_dict =self.location_generator.doubt_sample_line_between_easy_believer_hard_believers(
                persons_location=self.persons_location,easy_doubt=[DoubtLevel.S1],hard_doubt=[DoubtLevel.S4])
        else:
            # default (Random)
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
        randomized_person_location = self._get_random_person_location()
        first_spreader: PersonCell = self._matrix[randomized_person_location.x][randomized_person_location.y]
        first_spreader.toggle_heard_rumour_sometime()
        first_spreader.set_heard_rumour_last_turn(True)
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
        for spread_rumour_location in rumour_spreaders:
            neighbors = self._get_all_neighbors_location(spread_rumour_location)
            total_rumour_spreads_in_episode.update(neighbors)

        # update the rumour spreaders in this episode: RST cool time, cooldown to False, heard rumour to False
        for rumour_spreader_location in rumour_spreaders:
            rumour_spreader: PersonCell = self._matrix[rumour_spreader_location.x][rumour_spreader_location.y]
            rumour_spreader.set_heard_rumour_last_turn(False)
            rumour_spreader.reset_n_cool_down_episodes_countdown()
            rumour_spreader.set_is_in_cooldown(True)

        # Calculate who believes the rumour
        rumour_believers: Dict[Location, Cell] = {}
        for neighbor_location, number_heard_about_rumour in total_rumour_spreads_in_episode.items():
            cell = self._matrix[neighbor_location.x][neighbor_location.y]
            # Check who got the rumour twice+ (will cause probability to believe deduct).
            if cell.should_believe_to_rumour(number_heard_about_rumour):
                rumour_believers[neighbor_location] = cell

        # update the state of cells that were told the rumour in this episode
        for location, rumour_believer in rumour_believers.items():
            rumour_believer.was_told_rumour()

        # Prepare for next turn (for example: dec cooldown values)
        self.next_turn()

    def next_turn(self):
        for row, col in self.persons_location:
            self._matrix[row][col].next_turn()

    def _get_random_person_location(self) -> Location:
        x, y = random.choice(list(self.persons_location))
        return Location(x=x, y=y)

    def calculate_percentage_of_believers(self):
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


def four_directions_policy(location: Location):
    for diff in [-1, 1]:
        location_x = location.x + diff
        location_y = location.y + diff
        if 0 <= location_y <= MATRIX_SIZE:
            yield Location(x=location.x, y=location_y)
        if 0 <= location_x <= MATRIX_SIZE:
            yield Location(x=location_x, y=location.y)


if __name__ == "__main__":
    env_map = EnvMap(
        n_rows=MATRIX_SIZE,
        n_cols=MATRIX_SIZE,
        population_density=P,
        persons_distribution=PERSONS_DISTRIBUTION,
        cool_down_l=4,
        policy=all_around_policy,
        location_shape=LocationShape.Frame,
        distribution_rule=DistributionRule.Random
    )
    for i in range(100):
        print(f"turn {i}==================")
        env_map.spread_rumor()
        print(env_map.calculate_percentage_of_believers())
