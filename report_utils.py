from typing import Callable

from ex1 import EnvMap, MATRIX_SIZE, P, PERSONS_DISTRIBUTION
import matplotlib.pyplot as plt
import numpy as np


def calc_spread_rate(env_map: EnvMap):
    count = 0
    for i in range(env_map._n_rows):
        for j in range(env_map._n_cols):
            if env_map._matrix[i][j].did_hear_rumour_sometime():
                count += 1
    return count / len(env_map.persons_location)


def run_experiment_multiple_times(env_map_creator: Callable[...,EnvMap], times):
    raw_stats = []
    for t in range(times):
        believers = []
        env_map = env_map_creator()
        for i in range(100):
            print(f"turn {i}==================")
            env_map.spread_rumor()
            believers.append(env_map.calculate_percentage_of_believeres())
        raw_stats.append(believers)
    return raw_stats


def calc_growth(population):
    growth = []
    for pop in range(1, len(population)):
        numbers = (population[pop] - population[pop - 1]) / population[pop - 1] * 100
        growth.append(numbers)
    return growth


def calc_average_per_turn(raw_stats):
    total_avgs = []
    for turn_number in range(len(raw_stats[0])):
        sum_for_turn = 0
        for population in raw_stats:
            sum_for_turn = sum_for_turn + population[turn_number]
        total_avgs.append(sum_for_turn / len(raw_stats))
    return total_avgs


def raw_stats_to_growth(raw_stats):
    growth = []
    for population in raw_stats:
        growth.append(calc_growth(population))
    return growth




def plot_experiment(graph, label: str, times=None,cool_down=None):
    size = len(graph)

    plt.plot(np.arange(0, size), graph, label=label, color='blue', marker=".", markersize=5)

    plt.legend()
    plt.title(f"repeated experiment :={times} cool_down:={cool_down}", fontsize=10)
    plt.suptitle("Rumors statistics graph", fontsize=20)
    plt.show()



def main(env_map_creator: Callable[...,EnvMap],times=10) -> None:
    raw_stats = run_experiment_multiple_times(env_map_creator, times)

    for believers_percentage in raw_stats:
        print(f"population belivers percentage:{believers_percentage}")
    print()

    avg_believers = calc_average_per_turn(raw_stats)
    print(f"Average believers per turn:={avg_believers}")

    growth_all = raw_stats_to_growth(raw_stats)
    avg_growth = calc_average_per_turn(growth_all)

    for cnt, growth in enumerate(growth_all):
        print(f"turn {cnt} =============")
        print(growth)
        print()
    print(f"Average growth per turn:={avg_growth}")

    plot_experiment(avg_believers, label="average believers", times=times,cool_down=cool_down)
    plot_experiment(avg_growth, label="average growth", times=times,cool_down=cool_down)

def create_env_map(cool_down):
    return EnvMap(
        n_rows=MATRIX_SIZE,
        n_cols=MATRIX_SIZE,
        population_density=P,
        persons_distribution=PERSONS_DISTRIBUTION,
        cool_down_l=cool_down,
        location_shape='square', distribution_rule='space'
    )


if __name__ == "__main__":
    for cool_down in [2,3,4,6,8,10,1]:
        main(lambda: create_env_map(cool_down))

