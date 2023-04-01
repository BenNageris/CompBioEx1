from enum import Enum

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


POPULATION_DISTRIBUTION = {
    DoubtLevel.S1: 1/4,
    DoubtLevel.S2: 1/4,
    DoubtLevel.S3: 1/4,
    DoubtLevel.S4: 1/4,
}

PROBABILITY_TO_BELIEVE = {
    DoubtLevel.S1: 1,
    DoubtLevel.S2: 2/3,
    DoubtLevel.S3: 1/3,
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
