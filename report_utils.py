from ex1 import EnvMap, MATRIX_SIZE, P, PERSONS_DISTRIBUTION


def calc_spread_rate(env_map: EnvMap):
    count = 0
    for i in range(env_map._n_rows):
        for j in range(env_map._n_cols):
            if env_map._matrix[i][j].did_hear_rumour_sometime():
                count += 1
    return count / len(env_map.persons_location)


def run_experiment_multiple_times(env_map: EnvMap, times):
    raw_stats = []
    for t in range(times):
        believers = []
        for i in range(100):
            print(f"turn {i}==================")
            env_map.spread_rumor()
            believers.append(env_map.calculate_percentage_of_believeres())
        raw_stats.append(believers)
        env_map = create_env_map()
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

def create_env_map():
    return EnvMap(
        n_rows=MATRIX_SIZE,
        n_cols=MATRIX_SIZE,
        population_density=P,
        persons_distribution=PERSONS_DISTRIBUTION,
    )


if __name__ == "__main__":
    TIMES = 10
    env_map = create_env_map()
    raw_stats = run_experiment_multiple_times(env_map, TIMES)

    for believers_percentage in raw_stats:
        print(f"population belivers percentage:{believers_percentage}")
    print()

    print("Average believers per turn:=", calc_average_per_turn(raw_stats))

    # TODO: check if growth calculation need a fix
    # growth_all = raw_stats_to_growth(raw_stats)
    # print("Average growth per turn:=", calc_average_per_turn(growth_all))
