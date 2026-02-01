import numpy as np
import matplotlib.pyplot as plt
import numpy as np

import numpy as np

class NSGA2:
    def __init__(self, problem, pop_size=100, integrated=False):
        """
        NSGA-II 算法实现
        :param problem: 优化问题实例 (LunarLogisticsProblem1 或 IntegratedLunarProblem)
        :param pop_size: 种群大小
        :param integrated: 是否为集成全局优化模式 (dim=6)
        """
        self.prob = problem
        self.pop_size = pop_size
        self.integrated = integrated
        
        # 边界感应：自动适配 2 维或 6 维
        self.low_b = self.prob.bounds[0]
        self.high_b = self.prob.bounds[1]
        
        # 初始化种群：在每个维度的边界内生成均匀分布
        self.population = np.random.uniform(
            self.low_b, self.high_b, (pop_size, self.prob.dim)
        )

    def _dominates(self, p_val, q_val):
        """判断 p 是否支配 q"""
        return all(p_val <= q_val) and any(p_val < q_val)

    def _non_dominated_sorting(self, values):
        """快速非支配排序"""
        size = len(values)
        dom_count = np.zeros(size)
        dom_sets = [[] for _ in range(size)]
        for i in range(size):
            for j in range(size):
                if i == j: continue
                if self._dominates(values[i], values[j]): 
                    dom_sets[i].append(j)
                elif self._dominates(values[j], values[i]): 
                    dom_count[i] += 1
        
        fronts = [[i for i in range(size) if dom_count[i] == 0]]
        while fronts[-1]:
            next_f = []
            for i in fronts[-1]:
                for j in dom_sets[i]:
                    dom_count[j] -= 1
                    if dom_count[j] == 0: 
                        next_f.append(j)
            if not next_f: break
            fronts.append(next_f)
        return fronts

    def _crowding_distance(self, front, values):
        """计算拥挤距离，维持解的多样性"""
        dist = np.zeros(len(front))
        if len(front) <= 2: 
            dist[:] = np.inf
            return dist
            
        for m in range(values.shape[1]):
            m_vals = values[front, m]
            idx = np.argsort(m_vals)
            dist[idx[0]] = dist[idx[-1]] = np.inf
            rng = m_vals[idx[-1]] - m_vals[idx[0]]
            if rng == 0: continue
            for i in range(1, len(front)-1):
                dist[idx[i]] += (m_vals[idx[i+1]] - m_vals[idx[i-1]]) / rng
        return dist

    def evolve(self):
        """进化一代"""
        offspring = []
        while len(offspring) < self.pop_size:
            # 1. 锦标赛选择父代
            participants = np.random.choice(self.pop_size, 4, replace=False)
            # 这里简化逻辑：直接从随机选出的两组中选出序号较小的（模拟优胜劣汰）
            p1 = self.population[min(participants[0], participants[1])]
            p2 = self.population[min(participants[2], participants[3])]
            
            # 2. 交叉 (Crossover)
            # 集成模式(dim=6)下，交叉点位置更随机
            pt = np.random.randint(1, self.prob.dim) if self.prob.dim > 1 else 0
            child = np.copy(p1)
            if self.prob.dim > 1:
                child[pt:] = p2[pt:]
            
            # 3. 变异 (Mutation)
            # 变异率设置为 1/dim 是常用的启发式设置
            mut_prob = 1.0 / self.prob.dim
            mask = np.random.rand(self.prob.dim) < mut_prob
            for i in range(self.prob.dim):
                if mask[i]:
                    # 在该维度边界内随机扰动
                    child[i] = np.random.uniform(self.low_b[i], self.high_b[i])
            offspring.append(child)
        
        # 合并父代和子代 (精英保留策略)
        combined_pop = np.vstack((self.population, offspring))
        combined_vals = np.array([self.prob.evaluate(ind) for ind in combined_pop])
        
        # 重新进行非支配排序和筛选
        fronts = self._non_dominated_sorting(combined_vals)
        new_pop, new_vals = [], []
        
        for f in fronts:
            cd = self._crowding_distance(f, combined_vals)
            if len(new_pop) + len(f) <= self.pop_size:
                new_pop.extend(combined_pop[f])
                new_vals.extend(combined_vals[f])
            else:
                # 这一层放不下了，根据拥挤距离取前几个
                idx = np.argsort(-cd)[:self.pop_size - len(new_pop)]
                new_pop.extend(combined_pop[[f[i] for i in idx]])
                new_vals.extend(combined_vals[[f[i] for i in idx]])
                break
                
        self.population = np.array(new_pop)
        return self.population, np.array(new_vals)