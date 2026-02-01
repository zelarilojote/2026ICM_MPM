import numpy as np
import matplotlib.pyplot as plt


class NSGA2:
    def __init__(self, problem, pop_size=100):
        self.prob = problem
        self.pop_size = pop_size
        
        # 解析边界
        self.low_b = np.array(self.prob.bounds[0])
        self.high_b = np.array(self.prob.bounds[1])
        
        # 初始化种群
        self.population = np.random.uniform(
            self.low_b, self.high_b, (pop_size, self.prob.dim)
        )
        
        # 初始化目标值存储
        self.n_obj = None  # 目标数量，首次评估时确定

    def _evaluate_population(self, pop):
        """
        评估种群，返回标准化的目标值数组
        支持任意数量的目标
        """
        vals_list = []
        for ind in pop:
            result = self.prob.evaluate(ind)
            # 确保结果是一维数组
            if np.isscalar(result):
                result = [result]
            vals_list.append(np.array(result).flatten())
        
        # 检查所有结果维度一致
        if self.n_obj is None:
            self.n_obj = len(vals_list[0])
        
        # 转换为统一形状的数组
        vals_array = np.zeros((len(vals_list), self.n_obj))
        for i, v in enumerate(vals_list):
            vals_array[i, :len(v)] = v[:self.n_obj]
        
        return vals_array

    def _dominates(self, p_val, q_val):
        """判断 p 是否支配 q"""
        return np.all(p_val <= q_val) and np.any(p_val < q_val)

    def _non_dominated_sorting(self, values):
        """非支配排序"""
        size = len(values)
        dom_count = np.zeros(size, dtype=int)
        dom_sets = [[] for _ in range(size)]
        
        for i in range(size):
            for j in range(size):
                if i == j:
                    continue
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
            if not next_f:
                break
            fronts.append(next_f)
        
        # 移除空的最后一层
        if not fronts[-1]:
            fronts.pop()
        
        return fronts

    def _crowding_distance(self, front, values):
        """计算拥挤度距离"""
        n = len(front)
        if n == 0:
            return np.array([])
        if n <= 2:
            return np.full(n, np.inf)
        
        dist = np.zeros(n)
        n_obj = values.shape[1]
        
        for m in range(n_obj):
            m_vals = values[front, m]
            idx = np.argsort(m_vals)
            dist[idx[0]] = np.inf
            dist[idx[-1]] = np.inf
            
            rng = m_vals[idx[-1]] - m_vals[idx[0]]
            if rng == 0:
                continue
            
            for i in range(1, n - 1):
                dist[idx[i]] += (m_vals[idx[i + 1]] - m_vals[idx[i - 1]]) / rng
        
        return dist

    def evolve(self):
        """进化一代"""
        offspring = []
        
        while len(offspring) < self.pop_size:
            # 锦标赛选择
            idx1, idx2 = np.random.choice(self.pop_size, 2, replace=False)
            p = self.population[[idx1, idx2]]
            
            # 单点交叉
            c = np.copy(p[0])
            if self.prob.dim > 1:
                pt = np.random.randint(1, self.prob.dim)
                c[pt:] = p[1][pt:]
            
            # 变异
            mask = np.random.rand(self.prob.dim) < 0.2
            for i in range(self.prob.dim):
                if mask[i]:
                    c[i] = np.random.uniform(self.low_b[i], self.high_b[i])
            
            offspring.append(c)
        
        offspring = np.array(offspring)
        combined_pop = np.vstack((self.population, offspring))
        
        # 使用安全的评估方法
        combined_vals = self._evaluate_population(combined_pop)
        
        # 非支配排序
        fronts = self._non_dominated_sorting(combined_vals)
        
        # 选择下一代
        new_pop = []
        new_vals = []
        
        for f in fronts:
            if len(f) == 0:
                continue
            
            cd = self._crowding_distance(f, combined_vals)
            
            if len(new_pop) + len(f) <= self.pop_size:
                for i, fi in enumerate(f):
                    new_pop.append(combined_pop[fi])
                    new_vals.append(combined_vals[fi])
            else:
                remain = self.pop_size - len(new_pop)
                idx = np.argsort(-cd)[:remain]
                for i in idx:
                    new_pop.append(combined_pop[f[i]])
                    new_vals.append(combined_vals[f[i]])
                break
        
        self.population = np.array(new_pop)
        return self.population, np.array(new_vals)
    
    def get_pareto_front(self):
        """获取当前种群的帕累托前沿"""
        vals = self._evaluate_population(self.population)
        fronts = self._non_dominated_sorting(vals)
        
        if fronts and fronts[0]:
            pareto_pop = self.population[fronts[0]]
            pareto_vals = vals[fronts[0]]
            return pareto_pop, pareto_vals
        
        return self.population, vals