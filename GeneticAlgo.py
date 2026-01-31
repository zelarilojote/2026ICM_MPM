import numpy as np
import random
# 模拟一个机器学习模型的评估函数
def evaluate_model(parameters):
    # 这里用随机数模拟评估结果
    accuracy = random.uniform(0.7, 0.99)  # 模拟准确度
    resource_consumption = random.uniform(0.1, 1.0)  # 模拟资源消耗
    return accuracy, resource_consumption
# 适应度函数
def fitness(accuracy, resource_consumption):
    # 这里我们希望准确度高且资源消耗低
    return accuracy / resource_consumption
# 初始化种群
def initialize_population(pop_size, param_size):
    return np.random.rand(pop_size, param_size)
# 选择操作
def selection(population, fitnesses, num_parents):
    parents = np.empty((num_parents, population.shape[1]))
    for parent_num in range(num_parents):
        max_fitness_idx = np.where(fitnesses == np.max(fitnesses))
        max_fitness_idx = max_fitness_idx[0][0]
        parents[parent_num, :] = population[max_fitness_idx, :]
        fitnesses[max_fitness_idx] = -999999
    return parents
# 交叉操作
def crossover(parents, offspring_size):
    offspring = np.empty(offspring_size)
    crossover_point = np.uint8(offspring_size[1]/2)
    for k in range(offspring_size[0]):
        parent1_idx = k % parents.shape[0]
        parent2_idx = (k+1) % parents.shape[0]
        offspring[k, 0:crossover_point] = parents[parent1_idx, 0:crossover_point]
        offspring[k, crossover_point:] = parents[parent2_idx, crossover_point:]
    return offspring
# 变异操作
def mutation(offspring_crossover):
    for idx in range(offspring_crossover.shape[0]):
        random_value = np.random.uniform(-1.0, 1.0, 1)
        offspring_crossover[idx, :] = offspring_crossover[idx, :] + random_value
    return offspring_crossover
# 遗传算法主函数
def genetic_algorithm(pop_size, param_size, num_generations):
    population = initialize_population(pop_size, param_size)
    for generation in range(num_generations):
        fitnesses = []
        for individual in population:
            accuracy, resource_consumption = evaluate_model(individual)
            fitnesses.append(fitness(accuracy, resource_consumption))
        parents = selection(population, np.array(fitnesses), pop_size//2)
        offspring_crossover = crossover(parents, (pop_size-parents.shape[0], param_size))
        offspring_mutation = mutation(offspring_crossover)
        population[0:parents.shape[0], :] = parents
        population[parents.shape[0]:, :] = offspring_mutation
    return population
# 参数设置
pop_size = 10  # 种群大小
param_size = 5  # 参数个数
num_generations = 5  # 迭代次数
# 运行遗传算法
optimized_population = genetic_algorithm(pop_size, param_size, num_generations)
print("Optimized Parameters:\n", optimized_population)