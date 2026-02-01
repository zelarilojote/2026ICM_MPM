import numpy as np
from .base_problem import BaseProblem

class TestProblem3Obj(BaseProblem):
    def __init__(self):
        # 定义 3 个决策变量，范围假设在 [0, 10] 之间
        # 边界格式：[最小值数组, 最大值数组]
        low = np.array([0.0, 0.0, 0.0])
        high = np.array([10.0, 10.0, 10.0])
        super().__init__(dim=3, bounds=[low, high])
        
        # 模拟 BaseProblem 需要的 target_cargo 属性（如果有的话）
        self.stage_mass = 0 

    def evaluate(self, individual):
        """
        注意：NSGA-II 默认是最小化所有目标函数。
        如果你的 f3 是想求最大值，我们需要取负数。
        """
        x1, x2, x3 = individual
        
        # 目标 1: 线性成本
        f1 = 2 * x1 + 3 * x2 + 4 * x3
        
        # 目标 2: 平方和（倾向于让变量靠近 0）
        f2 = x1**2 + x2**2 + x3**2
        
        # 目标 3: 原始公式是 100 - (x-5)^2，这通常是一个求最大值的函数
        # 为了让优化器找到 (5,5,5) 这个点，我们将其转化为最小化问题：
        # 最小化：- (100 - (x1-5)**2 - (x2-5)**2 - (x3-5)**2)
        f3_raw = 100 - (x1 - 5)**2 - (x2 - 5)**2 - (x3 - 5)**2
        f3 = -f3_raw 
        
        return [f1, f2, f3]