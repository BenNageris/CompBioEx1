import functools
from typing import Callable

from ex1 import EnvMap, all_around_policy, four_directions_policy, wrap_all_around_policy
from ex1 import EnvMap, MATRIX_SIZE, P, PERSONS_DISTRIBUTION
import matplotlib.pyplot as plt
import numpy as np
import typing

Graph = typing.NamedTuple("Graph", [("graph", typing.List[int]), ("description", str), ("color", str)])


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
        for i in range(150):
            print(f"turn {i}==================")
            env_map.spread_rumor()
            believers.append(env_map.calculate_percentage_of_believers())
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


def plot_experiment(graphs: typing.List[Graph], times=None, shape=None, dist=None, p=P):
    for graph in graphs:
        size = len(graph.graph)
        plt.plot(np.arange(0, size), graph.graph, label=graph.description, color=graph.color, marker=".", markersize=5)

    plt.legend()
    plt.title(f"repeated experiment :={times} P:={p} shape:={shape} dist={dist}", fontsize=10)
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

    plot_experiment(avg_believers, label="average believers", times=times,cool_down=4, shape='square', dist='3 lines space',p=P)
    plot_experiment(avg_growth, label="average growth", times=times,cool_down=4,shape='square', dist='3 lines space',p=P)


def create_env_map(cool_down):
    print(f"cool down:{cool_down}")
    return EnvMap(
        n_rows=MATRIX_SIZE,
        n_cols=MATRIX_SIZE,
        population_density=P,
        persons_distribution=PERSONS_DISTRIBUTION,
        cool_down_l=cool_down,
        policy=all_around_policy,
        location_shape='random',
        distribution_rule='default'
    )


if __name__ == "__main__":
    TIMES = 30
    env_cooldown_2 = functools.partial(create_env_map, cool_down=2)
    env_cooldown_3 = functools.partial(create_env_map, cool_down=3)
    env_cooldown_4 = functools.partial(create_env_map, cool_down=4)
    env_cooldown_5 = functools.partial(create_env_map, cool_down=5)
    env_cooldown_6 = functools.partial(create_env_map, cool_down=6)
    env_cooldown_8 = functools.partial(create_env_map, cool_down=8)
    env_cooldown_10 = functools.partial(create_env_map, cool_down=10)

    raw_stats_cooldown_2 = run_experiment_multiple_times(env_cooldown_2, TIMES)
    raw_stats_cooldown_3 = run_experiment_multiple_times(env_cooldown_3, TIMES)
    raw_stats_cooldown_4 = run_experiment_multiple_times(env_cooldown_4, TIMES)
    raw_stats_cooldown_5 = run_experiment_multiple_times(env_cooldown_5, TIMES)
    raw_stats_cooldown_6 = run_experiment_multiple_times(env_cooldown_6, TIMES)
    raw_stats_cooldown_8 = run_experiment_multiple_times(env_cooldown_8, TIMES)
    raw_stats_cooldown_10 = run_experiment_multiple_times(env_cooldown_10, TIMES)


    # for believers_percentage in raw_stats_cooldown_1:
    #     print(f"population believers percentage:{believers_percentage}")
    # print()

    avg_believers_cooldown_2 = calc_average_per_turn(raw_stats_cooldown_2)
    avg_believers_cooldown_3 = calc_average_per_turn(raw_stats_cooldown_3)
    avg_believers_cooldown_4 = calc_average_per_turn(raw_stats_cooldown_4)
    avg_believers_cooldown_5 = calc_average_per_turn(raw_stats_cooldown_5)
    avg_believers_cooldown_6 = calc_average_per_turn(raw_stats_cooldown_6)
    avg_believers_cooldown_8 = calc_average_per_turn(raw_stats_cooldown_8)
    avg_believers_cooldown_10 = calc_average_per_turn(raw_stats_cooldown_10)


    #
    # growth_all = raw_stats_to_growth(raw_stats)
    # avg_growth = calc_average_per_turn(growth_all)
    #
    # for cnt, growth in enumerate(growth_all):
    #     print(f"turn {cnt} =============")
    #     print(growth)
    #     print()
    # print(f"Average growth per turn:={avg_growth}")
    #
    plot_experiment(
        [
            Graph(graph=avg_believers_cooldown_2, description="L=2", color="blue"),
            Graph(graph=avg_believers_cooldown_3, description="L=3", color="red"),
            Graph(graph=avg_believers_cooldown_4, description="L=4", color="cyan"),
            Graph(graph=avg_believers_cooldown_5, description="L=5", color="magenta"),
            Graph(graph=avg_believers_cooldown_6, description="L=6", color="yellow"),
            Graph(graph=avg_believers_cooldown_8, description="L=8", color="black"),
            Graph(graph=avg_believers_cooldown_10, description="L=10", color="green"),
        ],
        times=TIMES,
        shape="random",
        dist="default",
        p=P)
    # plot_experiment(avg_growth, label="average growth", times=times, cool_down=4, shape='square', dist='3 lines space',
    #                 p=P)

    # for cool_down in [2, 3, 4, 6, 8, 10, 1]:
    #     main(lambda: create_env_map(cool_down))

