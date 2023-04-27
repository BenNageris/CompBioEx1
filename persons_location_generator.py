import math
import random
from itertools import product
from typing import List
from DoubtLevel import DoubtLevel


class PersonsLocationGenerator:
    @staticmethod
    def random_locations(n_person_cells=None, n_cols=None, n_rows=None):
        persons_location = random.sample(
            population=list(product(range(n_rows), range(n_cols))),
            k=n_person_cells,
        )
        return set(persons_location)

    @staticmethod
    def lines_location(n_person_cells=None, n_cols=None, n_rows=None):
        counter = 0
        locations = set()
        for i in range(n_rows):
            for j in range(n_cols):
                if counter >= n_person_cells:
                    return locations
                locations.add((i, j))
                counter += 1
        return locations

    @staticmethod
    def square_location(n_person_cells=None, n_cols=None, n_rows=None):
        locations = set()
        root = int(math.floor(math.sqrt(n_person_cells)))
        print(f"root:{root}")
        assert math.pow(root, 2) == n_person_cells, "number of persons cell when square shape used should be n^2 for natural n"
        margin_row = int((n_cols-root)/2)
        margin_col = int((n_rows-root)/2)
        for i in range(margin_row, margin_row+root):
            for j in range(margin_col, margin_col+root):
                locations.add((i, j))
        return locations

    @staticmethod
    def doubt_sample_easy_believer_next_to_not(persons_location):
        doubt_level_locations_dict = {}
        for i, location in enumerate(persons_location):
            if i % 2 == 0:
                doubt_level_locations_dict[location] = DoubtLevel.S1
            else:
                doubt_level_locations_dict[location] = DoubtLevel.S4
        return doubt_level_locations_dict

    @staticmethod
    def doubt_sample_easy_believer_next_to_k_hard_believers(persons_location,k=3):
        doubt_level_locations_dict = {}
        for i, location in enumerate(persons_location):
            if i % k == 0:
                doubt_level_locations_dict[location] = DoubtLevel.S1
            else:
                doubt_level_locations_dict[location] = DoubtLevel.S3
        return doubt_level_locations_dict

    @staticmethod
    def doubt_sample_line_between_easy_believer_hard_believers(persons_location, easy_doubt: List, hard_doubt: List):
        doubt_level_locations_dict = {}
        for i, location in enumerate(persons_location):
            if location[0] % 4 == 0:
                doubt_level_locations_dict[location] = random.choice(easy_doubt)
            else:
                doubt_level_locations_dict[location] = random.choice(hard_doubt)
        return doubt_level_locations_dict

    @staticmethod
    def merge_doubt_dict(first, second):
        di = dict(second)
        for k, v in first.items():
            di[k] = v
        return di
