import numpy as np
from .base_problem import BaseProblem
from cost.cost import RocketCostCalculator, ElevatorCostCalculator
from data.param import RocketParams, ElevatorParams
import numpy as np
from .base_problem import BaseProblem
from typing import Tuple

class IntegratedLunarProblem(BaseProblem):
    def __init__(self, stage_masses=[5e7, 4e7, 1e7], smooth=False):
        # 6维决策空间: [R1, E1, R2, E2, R3, E3]
        low = np.array([1.0, 0.05, 1.0, 0.05, 1.0, 0.05])
        high = np.array([365.0, 1.0, 365.0, 1.0, 365.0, 1.0])
        super().__init__(dim=6, bounds=[low, high])
        
        self.stage_masses = stage_masses
        self.smooth = smooth # 是否开启平滑项开关

    def evaluate(self, x):
        total_weighted_econ = 0
        total_weighted_time = 0
        
        # 定义阶段权重（可根据战略需求调整）
        weights = [
            [0.2, 0.8], # Stage 1: 时间优先
            [0.5, 0.5], # Stage 2: 平衡
            [0.8, 0.2]  # Stage 3: 成本优先
        ]

        # 1. 计算三个阶段的加权损耗
        for i in range(3):
            rf, eu = x[i*2], x[i*2+1]
            # 计算该阶段原始物理值
            econ, duration = self.calculate_total_costs(self.stage_masses[i], eu, rf)
            
            total_weighted_econ += econ * weights[i][0]
            total_weighted_time += duration * weights[i][1]

        # 2. 条件性添加平滑项 (Smoothing Penalty)
        smoothness_penalty = 0
        if self.smooth:
            # 计算火箭发射频率的变动 (R2-R1, R3-R2)
            # 使用差分的平方和作为惩罚，抑制剧烈跳变
            freq_diffs = np.diff(x[::2]) 
            # 乘以一个系数，使其量级与 economic_cost 匹配
            smoothness_penalty = np.sum(freq_diffs**2) * 1e1

        # 返回 NSGA-II 优化的多目标向量
        # 目标1：综合经济损耗（含平滑惩罚）
        # 目标2：综合时间损耗
        return [total_weighted_econ + smoothness_penalty, total_weighted_time]
    
    def calculate_total_costs(
        self,
        total_mass: float,
        elevator_utilization: float,
        rocket_launch_frequency: int,
        rocket_params: RocketParams = None,
        elevator_params: ElevatorParams = None
    ) -> Tuple[float, float]:
        """
        计算总经济成本和总时间成本
        
        Args:
            total_mass: 总运输重量（吨）
            elevator_utilization: 太空电梯年利用率 (0.0 ~ 1.0)
            rocket_launch_frequency: 火箭年发射频率（次/年/发射台）
        
        Returns:
            (总经济成本（万美元）, 总时间成本（年）)
        """
        rocket_calc = RocketCostCalculator(rocket_params)
        elevator_calc = ElevatorCostCalculator(elevator_params)
        
        # 年度经济成本
        rocket_economic = rocket_calc.calculate_economic_cost(rocket_launch_frequency)['total_cost_per_year']
        elevator_economic = elevator_calc.calculate_economic_cost(elevator_utilization)['total_cost_per_year']
        annual_economic_cost = rocket_economic + elevator_economic
        
        # 总时间成本 = 总重量 / (火箭年运输量 + 电梯年运输量)
        rocket_capacity = rocket_calc.get_annual_capacity(rocket_launch_frequency)
        elevator_capacity = elevator_calc.get_annual_capacity(elevator_utilization)
        total_capacity = rocket_capacity + elevator_capacity
        total_time_cost = total_mass / total_capacity if total_capacity > 0 else float('inf')
        
        # 总经济成本 = 年度成本 × 运输年数
        total_economic_cost = annual_economic_cost * total_time_cost
        
        return total_economic_cost, total_time_cost