import random
from enum import Enum
from itertools import product
from typing import Dict
MATRIX_SIZE = 100

P = 0.5  # population density


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
    DoubtLevel.S4: 0
}


class Cell:
    """
    This class represents a cell in the map
    """

    def __init__(self, state, position):
        self._state = state
        self._position = position


class PersonCell(Cell):
    def __init__(self, state, position):
        super().__init__(state=state, position=position)
        self._probability_to_believe = PROBABILITY_TO_BELIEVE[state]


class EmptyCell(Cell):
    def __init__(self, state, position):
        super().__init__(state=state, position=position)


class EnvMap:
    def __init__(self,
                 n_rows: int,
                 n_cols: int,
                 population_density: float,
                 persons_distribution: Dict[DoubtLevel, float]):
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
        self._matrix = self._create_matrix(n_rows=n_rows, n_cols=n_cols)
        self._num_dimensions = 2
        self.init_matrix()

    @staticmethod
    def _create_matrix(n_rows: int, n_cols: int):
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
            n_doubt_level_dict[doubt_level] = int(number_of_persons * persons_distribution[doubt_level])
        return n_doubt_level_dict

    @staticmethod
    def _sample_for_each_doubt_level(persons_location, persons_distribution):
        n_persons = len(persons_location)
        n_doubt_level_dict = EnvMap._get_n_doubt_level_dict(number_of_persons=n_persons,
                                                            persons_distribution=persons_distribution)
        doubt_level_locations_dict = {}
        for doubt_level in DoubtLevel:
            n_doubt_level = n_doubt_level_dict[doubt_level]
            n_doubt_level_randomized_locations = random.sample(persons_location, k=n_doubt_level)
            doubt_level_locations_dict[doubt_level] = n_doubt_level_randomized_locations
            persons_location = list(set(persons_location) - set(n_doubt_level_randomized_locations))
        return doubt_level_locations_dict

    def init_matrix(self):
        # init matrix with cells
        n_person_cells = int(self._n_cols * self._n_rows * self._population_density)

        persons_location = random.sample(population=list(product(range(self._n_rows), range(self._n_cols))),
                                         k=n_person_cells)

        doubt_level_locations_dict = self._sample_for_each_doubt_level(
            persons_location=persons_location,
            persons_distribution=self._persons_distribution)
        print(doubt_level_locations_dict)


if __name__ == "__main__":
    env_map = EnvMap(n_rows=MATRIX_SIZE,
                     n_cols=MATRIX_SIZE,
                     population_density=P,
                     persons_distribution=PERSONS_DISTRIBUTION)
