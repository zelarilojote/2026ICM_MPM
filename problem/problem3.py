from .base_problem import BaseProblem
import numpy as np
from algorithm.cost import calculate_total_costs  
from algorithm.environmental_cost import calculate_total_environmental_cost

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

    def evaluate(self, x):
        # 这里的 x 是算法生成的 [rocket_freq, elevator_util]
        rocket_freq = x[0]
        elevator_util = x[1]

        econ_cost, time_cost = calculate_total_costs(
            total_mass=self.stage_mass,
            elevator_utilization=elevator_util,
            rocket_launch_frequency=rocket_freq,
            rocket_params=self.rocket_params,
            elevator_params=self.elevator_params
        )

        env_cost, _, _ = calculate_total_environmental_cost(
            total_mass=self.stage_mass,
            elevator_utilization=elevator_util,
            rocket_launch_frequency=rocket_freq
        )
        
        # NSGA2 默认最小化。如果你的时间成本是越短越好，直接返回即可。
        return [econ_cost, time_cost, env_cost]