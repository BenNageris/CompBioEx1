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
        return persons_location

    @staticmethod
    def lines_location(n_person_cells=None, n_cols=None, n_rows=None):
        counter = 0
        locations = []
        for i in range(n_rows):
            for j in range(n_cols):
                if counter >= n_person_cells:
                    return locations
                locations.append((i,j))
                counter += 1
        return locations

    @staticmethod
    def square_location(n_person_cells=None, n_cols=None, n_rows=None):
        locations = []
        root = int(math.floor(math.sqrt(n_person_cells)))
        assert math.pow(root,2) == n_person_cells, "number of persons cell when square shape used should be n^2 for natural n"
        margin_row = int((n_cols-root)/2)
        margin_col = int((n_rows-root)/2)
        for i in range(margin_row, margin_row+root):
            for j in range(margin_col, margin_col+root):
                locations.append((i, j))
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
