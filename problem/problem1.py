from .base_problem import BaseProblem
import numpy as np
from algorithm.cost import RocketCostCalculator, ElevatorCostCalculator, RocketParams, ElevatorParams
from typing import Tuple


class LunarLogisticsProblem1(BaseProblem):
    def __init__(self, stage_mass, rocket_params=None, elevator_params=None):
        # 明确定义每个变量的上下界
        # 变量 0: 火箭频率 (1 到 365)
        # 变量 1: 电梯利用率 (0.05 到 1.0)
        self.lower_bounds = np.array([1.0, 0.05])
        self.upper_bounds = np.array([365.0, 1.0])
        super().__init__(dim=2, bounds=[self.lower_bounds, self.upper_bounds])
        
        self.rocket_params = rocket_params
        self.elevator_params = elevator_params
        self.stage_mass = stage_mass

    def evaluate(self, x) -> Tuple[float, float]:
        rocket_freq = x[0]
        elevator_util = x[1]

        econ_cost, time_cost, rocket_econ, elevator_econ = self.calculate_total_costs(
            total_mass=self.stage_mass,
            elevator_utilization=elevator_util,
            rocket_launch_frequency=rocket_freq,
            rocket_params=self.rocket_params,
            elevator_params=self.elevator_params
        )
        
        # NSGA2 默认最小化。如果你的时间成本是越短越好，直接返回即可。
        return [econ_cost, time_cost]
    
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
        
        return total_economic_cost, total_time_cost, rocket_economic, elevator_economic
