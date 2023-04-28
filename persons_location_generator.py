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
    def frame_location(n_person_cells=None, n_cols=None, n_rows=None):
        locations = set()
        for i in range(n_cols):
            locations.add((0,i))
            locations.add((n_rows-1,i))
        for j in range(n_rows):
            locations.add((j,0))
            locations.add((j,n_cols-1))
        return locations

    @staticmethod
    def david_star_locations(n_person_cells=None, n_cols=None, n_rows=None):
        locations = set()
        #center
        center_x = n_rows/2
        center_y = n_cols/2

        #sized to make it look lit
        triangle_height = 30
        triangle_width = 26
        extra = -8

        #vertices of the upper triangle
        upper_left_x = center_x - triangle_width // 2
        upper_left_y = center_y - triangle_height // 2
        upper_right_x = center_x + triangle_width // 2
        upper_right_y = center_y - triangle_height // 2
        upper_bottom_x = center_x
        upper_bottom_y = center_y + triangle_height // 2

        #vertices of the lower triangle
        lower_left_x = center_x - triangle_width // 2
        lower_left_y = extra + center_y + triangle_height // 2
        lower_right_x = center_x + triangle_width // 2
        lower_right_y = extra + center_y + triangle_height // 2
        lower_top_x = center_x
        lower_top_y = extra + center_y - triangle_height // 2

        for i in range(n_rows):
            for j in range(n_cols):
                # Check upper triangle
                if (j - upper_left_x) * (upper_bottom_y - upper_left_y) - \
                        (i - upper_left_y) * (upper_bottom_x - upper_left_x) >= 0 and \
                        (j - upper_right_x) * (upper_bottom_y - upper_right_y) - \
                        (i - upper_right_y) * (upper_bottom_x - upper_right_x) <= 0 and \
                        (j - upper_left_x) * (upper_right_y - upper_left_y) - \
                        (i - upper_left_y) * (upper_right_x - upper_left_x) <= 0:
                    locations.add((i,j))
                # Check lower triangle
                if (j - lower_left_x) * (lower_top_y - lower_left_y) - \
                        (i - lower_left_y) * (lower_top_x - lower_left_x) <= 0 and \
                        (j - lower_right_x) * (lower_top_y - lower_right_y) - \
                        (i - lower_right_y) * (lower_top_x - lower_right_x) >= 0 and \
                        (j - lower_left_x) * (lower_right_y - lower_left_y) - \
                        (i - lower_left_y) * (lower_right_x - lower_left_x) >= 0:
                    locations.add((i,j))
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
