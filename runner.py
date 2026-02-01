import matplotlib.pyplot as plt
import numpy as np
import time
import os
import logging
from algorithm.cost import calculate_total_costs # 导入物理计算函数

class NSGARunner:
    def __init__(self, algo, max_gen=100, log_dir="log", stage_tag="Stage", integrated=False, priority="balanced"):
        self.algo = algo
        self.max_gen = max_gen
        self.log_dir = log_dir
        self.stage_tag = stage_tag
        self.integrated = integrated
        self.priority = priority # 新增：决策偏好
        
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        self.logger = self._setup_logging()

    def _setup_logging(self):
        name = f"{self.stage_tag}_int" if self.integrated else self.stage_tag
        logger = logging.getLogger(f"NSGARunner_{name}")
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(message)s'))
            logger.addHandler(handler)
        return logger

    def _select_best(self, pop, vals):
        """内部实现：归一化选点逻辑"""
        min_v, max_v = vals.min(axis=0), vals.max(axis=0)
        norm_v = (vals - min_v) / (max_v - min_v + 1e-6)
        weights = {"time": [0.2, 0.8], "balanced": [0.5, 0.5], "cost": [0.8, 0.2]}
        w = np.array(weights.get(self.priority, [0.5, 0.5]))
        return pop[np.argmin(np.dot(norm_v, w))]

    def run(self):
        """
        核心流程：演化 -> 绘制全局 Pareto -> 选点 -> 还原物理指标 -> 绘制 Roadmap
        """
        self.logger.info(f"🚀 {'INTEGRATED' if self.integrated else 'PHASED'} START | Tag: {self.stage_tag}")
        
        # 1. 执行演化循环
        pop, vals = None, None
        for g in range(1, self.max_gen + 1):
            pop, vals = self.algo.evolve()
            if g % 50 == 0:
                self.logger.info(f"  Gen {g:3d} | Min Econ: {np.min(vals[:,0]):.2e} | Min Time: {np.min(vals[:,1]):.2f}")

        # 2. 绘制全局 Pareto 前沿图 (无论是否集成都画)
        # 这张图展示了 6 维决策空间在【总成本/总时间】上的投影
        self.plot_pareto(vals)

        # 3. 战略选点
        # 基于你传入的 priority (time/balanced/cost) 自动选出最优个体
        best_x = self._select_best(pop, vals)
        
        # 4. 物理指标还原与结果封装
        results = []
        if self.integrated:
            # 自动解析 6 维变量，调用物理计算器还原每个阶段的真实 Cost 和 Years
            results = self._recover_physical_data(best_x)
            # 绘制 Roadmap (展示选中的这个点的各阶段频率/利用率)
            self.plot_integrated_roadmap(best_x)
        else:
            # 2 维单阶段还原
            results = self._recover_physical_data_single(best_x)

        return results

    def plot_pareto(self, vals):
        plt.figure(figsize=(8, 5))
        plt.scatter(vals[:, 0], vals[:, 1], alpha=0.5)
        plt.title(f"Pareto Front - {self.stage_tag}")
        plt.xlabel("Total Economic Cost (USD)")
        plt.ylabel("Total Duration (Years)")
        plt.savefig(os.path.join(self.log_dir, f"pareto_{self.stage_tag}.png"))
        plt.close()

    def plot_integrated_roadmap(self, best_x):
        fig, ax1 = plt.subplots(figsize=(10, 5))
        stages = ['P1', 'P2', 'P3']
        ax1.bar(stages, [best_x[0], best_x[2], best_x[4]], color='skyblue', label='Rocket')
        ax2 = ax1.twinx()
        ax2.plot(stages, [best_x[1], best_x[3], best_x[5]], 'r-o', label='Elevator')
        ax2.set_ylim(0, 1.1)
        plt.savefig(os.path.join(self.log_dir, f"roadmap_{self.stage_tag}.png"))
        plt.close()
        
    def _recover_physical_data_single(self, best_x):
        """单阶段模式：将 2 维解还原为物理指标"""
        rf, eu = best_x[0], best_x[1]
        mass = self.algo.prob.stage_mass # 读取该阶段的任务量
        
        # 调用物理计算器还原
        econ, duration = calculate_total_costs(mass, eu, rf)
        
        return [{
            "tag": self.stage_tag,
            "rf": rf,
            "eu": eu,
            "cost": econ,
            "duration": duration
        }]

    def _recover_physical_data(self, best_x):
        """集成模式：将 6 维解拆解并还原为三个阶段的物理指标"""
        results = []
        masses = self.algo.prob.stage_masses
        tags = ["Stage_1_Core", "Stage_2_Expand", "Stage_3_Sustain"]
        
        for i in range(3):
            rf, eu = best_x[i*2], best_x[i*2+1]
            m = masses[i]
            # 逐阶段还原
            econ, duration = calculate_total_costs(m, eu, rf)
            results.append({
                "tag": tags[i],
                "rf": rf,
                "eu": eu,
                "cost": econ,
                "duration": duration
            })
        return results