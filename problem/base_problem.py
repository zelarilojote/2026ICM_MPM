from abc import ABC, abstractmethod
import numpy as np

class BaseProblem(ABC):
    def __init__(self, dim, bounds, target_cargo=1e8):
        self.dim = dim
        self.bounds = bounds
        self.target_cargo = target_cargo

    @abstractmethod
    def evaluate(self, x):
        """所有子类必须实现该方法，返回目标函数值列表"""
        pass

    def get_bounds(self):
        return self.bounds