import numpy as np
import matplotlib.pyplot as plt
import numpy as np

class NSGA2:
    def __init__(self, problem, pop_size=100):
        self.prob = problem
        self.pop_size = pop_size
        
        # 解析边界: 假设 problem.bounds 是 [low_array, high_array]
        self.low_b = self.prob.bounds[0]
        self.high_b = self.prob.bounds[1]
        
        # 初始化种群：在每个维度的边界内生成
        self.population = np.random.uniform(
            self.low_b, self.high_b, (pop_size, self.prob.dim)
        )

    def _dominates(self, p_val, q_val):
        return all(p_val <= q_val) and any(p_val < q_val)

    def _non_dominated_sorting(self, values):
        size = len(values)
        dom_count = np.zeros(size)
        dom_sets = [[] for _ in range(size)]
        for i in range(size):
            for j in range(size):
                if i == j: continue
                if self._dominates(values[i], values[j]): dom_sets[i].append(j)
                elif self._dominates(values[j], values[i]): dom_count[i] += 1
        
        fronts = [[i for i in range(size) if dom_count[i] == 0]]
        while fronts[-1]:
            next_f = []
            for i in fronts[-1]:
                for j in dom_sets[i]:
                    dom_count[j] -= 1
                    if dom_count[j] == 0: next_f.append(j)
            if not next_f: break
            fronts.append(next_f)
        return fronts

    def _crowding_distance(self, front, values):
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
        offspring = []
        while len(offspring) < self.pop_size:
            # 锦标赛选择
            idx1, idx2 = np.random.choice(self.pop_size, 2, replace=False)
            p = self.population[[idx1, idx2]]
            
            # 单点交叉
            pt = np.random.randint(1, self.prob.dim) if self.prob.dim > 1 else 0
            c = np.copy(p[0])
            if self.prob.dim > 1:
                c[pt:] = p[1][pt:]
            
            # 变异: 每个维度独立应用其边界
            mask = np.random.rand(self.prob.dim) < 0.2 # 提高变异率增加多样性
            for i in range(self.prob.dim):
                if mask[i]:
                    c[i] = np.random.uniform(self.low_b[i], self.high_b[i])
            offspring.append(c)
        
        combined_pop = np.vstack((self.population, offspring))
        combined_vals = np.array([self.prob.evaluate(ind) for ind in combined_pop])
        
        fronts = self._non_dominated_sorting(combined_vals)
        new_pop, new_vals = [], []
        for f in fronts:
            cd = self._crowding_distance(f, combined_vals)
            if len(new_pop) + len(f) <= self.pop_size:
                new_pop.extend(combined_pop[f])
                new_vals.extend(combined_vals[f])
            else:
                idx = np.argsort(-cd)[:self.pop_size - len(new_pop)]
                new_pop.extend(combined_pop[[f[i] for i in idx]])
                new_vals.extend(combined_vals[[f[i] for i in idx]])
                break
        self.population = np.array(new_pop)
        return self.population, np.array(new_vals)