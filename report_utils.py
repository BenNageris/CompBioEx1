from ex1 import EnvMap

def calc_spread_rate(env_map:EnvMap):
    count=0
    for i in range(env_map._n_rows):
        for j in range(env_map._n_cols):
            if env_map._matrix[i][j].did_hear_rumour_sometime():
                count += 1
    return count/len(env_map.persons_location)


def run_experiment_multiple_times(env_map:EnvMap,times):
    raw_stats = []
    for t in times:
        belivers = []
        for i in range(100):
            print(f"turn {i}==================")
            env_map.spread_rumor()
            belivers.append(env_map.calculate_percentage_of_believeres())
        raw_stats.append(belivers)
    return raw_stats

def calc_rate(population):
    growth = []
    for pop in range(1, len(population)):
        numbers = ((population[pop] - population[pop - 1]) / population[pop - 1] * 100)
        growth.append(numbers)
    return growth