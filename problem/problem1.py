from .base_problem import BaseProblem
import numpy as np

class LunarLogisticsProblem1(BaseProblem):
    def __init__(self):
        # 20个决策变量，代表200年内每10年的平均发射强度
        super().__init__(dim=4, bounds=[0.01, 1.0])
        # 这里可以初始化你自己的 calculator 实例
        # self.calculator = MyInternalCalculator() 

    def evaluate(self, x):
        pass