import random
from collections import Counter
from enum import Enum
from itertools import product
from typing import Dict, Tuple, List
import typing

Location = typing.NamedTuple("Location", [("x", int), ("y", int)])

MATRIX_SIZE = 100

P = 0.5  # population density
L = 10


class DoubtLevel(Enum):
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"
    S4 = "S4"


class CellStates(Enum):
    S1 = DoubtLevel.S1
    S2 = DoubtLevel.S2
    S3 = DoubtLevel.S3
    S4 = DoubtLevel.S4
    EMPTY = "Empty"


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
        pass

    def should_believe_to_rumour(self) -> bool:
        return False

    def set_spread_already(self, spread_already=True):
        print("something is wrong, shouldn't call this function in Cell")
        pass

    def can_spread_rumour(self):
        return False


class PersonCell(Cell):
    def __init__(
            self,
            state,
            position,
            heard_rumour: bool = False,
            cool_down_episode_countdown: int = L):
        super().__init__(state=state.value, position=position)
        self._probability_to_believe = PROBABILITY_TO_BELIEVE[state]
        self._heard_rumour = heard_rumour
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
        self._n_cool_down_episodes_countdown = self._n_cool_down_episodes_countdown - 1

    def set_heard_rumour(self, heard_rumour: bool = True):
        self._heard_rumour = heard_rumour

    def set_spread_already(self, spread_already=True):
        self._spread_already = spread_already

    def should_believe_to_rumour(self):
        return random.random() < self._probability_to_believe

    def can_spread_rumour(self):
        return self._heard_rumour is True and self._n_cool_down_episodes_countdown == 0


class EmptyCell(Cell):
    def __init__(self, position):
        super().__init__(state=CellStates.EMPTY.value, position=position)


class EnvMap:
    def __init__(
            self,
            n_rows: int,
            n_cols: int,
            population_density: float,
            persons_distribution: Dict[DoubtLevel, float],
    ):
        self.doubt_level_locations_dict = None
        self.persons_location = None
        self._n_rows = n_rows
        self._n_cols = n_cols
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
        self.init_matrix()

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
                persons_location, k=n_doubt_level
            )
            for loca in n_doubt_level_randomized_locations:
                doubt_level_locations_dict[loca] = doubt_level
            persons_location = list(
                set(persons_location) - set(n_doubt_level_randomized_locations)
            )
        return doubt_level_locations_dict

    def init_matrix(self):
        # init matrix with cells
        n_person_cells = int(self._n_cols * self._n_rows * self._population_density)

        self.persons_location = random.sample(
            population=list(product(range(self._n_rows), range(self._n_cols))),
            k=n_person_cells,
        )

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
            )
        for row in range(self._n_rows):
            for col in range(self._n_cols):
                if self._matrix[row][col] is None:
                    self._matrix[row][col] = EmptyCell(
                        position=Location(x=row, y=col)
                    )

    def _get_doubt(self, location: Location):
        for di in self.doubt_level_locations_dict:
            if location in di:
                return di

    def _cell_got_rumor(self, location: Location) -> bool:
        # if no such location or rumor was previously accepted\rejected
        if (
                location not in self.persons_location
                # or self._matrix[location.x][location.y] is not None
        ):
            return False
        return self._matrix[location.x][location.y].should_believe_to_rumour()

    def get_cell_location(self, cell: Cell) -> Tuple[int, int]:
        for row in range(self._n_rows):
            for col in range(self._n_cols):
                if self._matrix[row][col] is cell:
                    return row, col
        print(f"Something is wrong, cell not found")
        return None, None

    def _get_all_neighbors_location(self, location: Location) -> Counter[Location]:
        all_neighbors = Counter()
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if i == 0 and j == 0:
                    # can't tell a rumour to myself
                    continue
                neighbor_location = Location(location.x + i, location.y + j)
                if neighbor_location in self.persons_location:
                    all_neighbors.update([neighbor_location])
        return all_neighbors

    def _get_believed_neighbors_location(self, x: int, y: int) -> List[Location]:
        rumours_believers: List[Location] = []
        # TODO: fix WRAP-AROUND policy is not an obligation!
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if i == 0 and j == 0:
                    # can't tell a rumour to myself
                    continue
                neighbor = Location(x + i, y + j)
                if self._cell_got_rumor(neighbor):
                    print(f"neighbor {neighbor} believes in rumour")
                    rumours_believers.append(neighbor)
        return rumours_believers

    def spread_around(self, cell: Cell):
        x, y = self.get_cell_location(cell)
        print(f"({x},{y})")
        if not cell.can_spread_rumour():
            print(f"cell located in ({x},{y}) can't spread rumour,"
                  f" {str(cell)}")
            return
        cell.set_spread_already()
        rumours_believers_location = self._get_believed_neighbors_location(x=x, y=y)
        for rumour_believer_location in rumours_believers_location:
            cell = self._matrix[rumour_believer_location.x][rumour_believer_location.y]
            cell.set_heard_rumour(heard_rumour=True)

    def _init_first_spread_rumor(self) -> None:
        first_spreader: PersonCell = self._get_random_person_cell()
        first_spreader.set_heard_rumour(heard_rumour=True)
        first_spreader.set_n_cool_down_episode_countdown(n=0)
        print(f"first spreader:{first_spreader}")

    def spread_rumor(self):
        # iterate over matrix,  spread rumour and create the next turn's matrix
        can_spread_person_cells: Dict[Location] = {}  # actually List[PersonCell]
        for row in range(self._n_rows):
            for col in range(self._n_cols):
                if self._matrix[row][col].can_spread_rumour():
                    print(f"can spread rumour:({row}:{col})")
                    can_spread_person_cells[Location(x=row, y=col)] = self._matrix[row][col]

        total_rumour_spreads_in_episode = Counter()
        for spread_rumour_location, cell in can_spread_person_cells.items():
            neighbors = self._get_all_neighbors_location(spread_rumour_location)
            total_rumour_spreads_in_episode.update(neighbors)

        print(f"total rumour spreads:{total_rumour_spreads_in_episode}")
        # Check who got the rumour twice+ (will cause probability to believe deduct).

    def _get_random_person_cell(self) -> PersonCell:
        x, y = random.choice(self.persons_location)
        return self._matrix[x][y]


if __name__ == "__main__":
    env_map = EnvMap(
        n_rows=MATRIX_SIZE,
        n_cols=MATRIX_SIZE,
        population_density=P,
        persons_distribution=PERSONS_DISTRIBUTION,
    )
    print(f"turn 1==================")
    env_map.spread_rumor()

    # print(f"turn 2==================")
    # env_map.spread_rumor()

    # print(env_map._matrix)
