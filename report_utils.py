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
        belivers = []
        for i in range(100):
            print(f"turn {i}==================")
            env_map.spread_rumor()
            belivers.append(env_map.calculate_percentage_of_believeres())
        raw_stats.append(belivers)
    return raw_stats


def calc_growth(population):
    growth = []
    for pop in range(1, len(population)):
        numbers = (population[pop] - population[pop - 1]) / population[pop - 1] * 100
        growth.append(numbers)
    return growth


def calc_average_per_turn(raw_stats):
    avgs = []
    for i in range(len(raw_stats)):
        sum = 0
        for j in range(len(raw_stats[0])):
            sum += raw_stats[i][j]
        avgs.append(sum / len(raw_stats[0]))
    return avgs


def raw_stats_to_growth(raw_stats):
    growth = []
    for population in raw_stats:
        growth.append(calc_growth(population))
    return growth


if __name__ == "__main__":
    TIMES = 10
    env_map = EnvMap(
        n_rows=MATRIX_SIZE,
        n_cols=MATRIX_SIZE,
        population_density=P,
        persons_distribution=PERSONS_DISTRIBUTION,
    )
    raw_stats = run_experiment_multiple_times(env_map, TIMES)
    print("Average believers per turn:=", calc_average_per_turn(raw_stats))
    growth_all = raw_stats_to_growth(raw_stats)
    print("Average growth per turn:=", calc_average_per_turn(growth_all))
