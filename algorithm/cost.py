"""
火箭与太空电梯经济成本及运输时间成本计算模块
输入：太空电梯年利用率、火箭发射频率
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple

# 环境参数
G = 6.67430e-11       # 万有引力常数 (N·m²/kg²)
M_EARTH = 5.972e24    # 地球质量 (kg)
R_EARTH = 6.371e6     # 地球半径 (m)
R_GEO = 4.2164e7      # 地球同步轨道半径 (m)
p_e = 0.05            # 电费 (美元/kWh)
J_TO_KWH = 1 / 3.6e6  # 焦耳转千瓦时


@dataclass
class RocketParams:
    """火箭参数配置"""
    C_rock: float = 1500.0                    # 每次发射成本（万美元）
    M_rock: float = 150.0                     # 单次载荷能力（吨）
    N_sites: int = 10                         # 发射场数量
    N_plat: int = 10                           # 每个发射场的发射台数量
    maintenance_cost_per_year: float = 200.0  # 年维护成本（万美元）


@dataclass
class ElevatorParams:
    """太空电梯参数配置"""
    C_repair_per_kg: float = 0.5              # 单位质量维修成本（美元/千克）
    C_labor_per_ton: float = 100.0            # 单位质量人工成本（美元/吨）
    max_capacity_year: float = 179000.0       # 年最大运输能力（吨）
    maintenance_cost_per_year: float = 500.0  # 年固定维护成本（万美元）
    C_supervision_per_year: float = 300.0     # 年监管成本（万美元）
    num_sites_elev: int = 3                   # 电梯数量
    eta: float = 0.8                          # 电机能源利用效率
    mu: float = 0.1                           # 每千克磨损系数


class RocketCostCalculator:
    """火箭成本计算器"""
    
    def __init__(self, params: RocketParams = None):
        self.params = params or RocketParams()
    
    def calculate_economic_cost(self, launch_frequency: int) -> Dict[str, float]:
        """
        计算火箭年度经济成本
        
        Args:
            launch_frequency: 每发射台每年发射次数
        """
        total_launches = launch_frequency * self.params.N_sites * self.params.N_plat
        launch_cost = total_launches * self.params.C_rock
        maintenance_cost = self.params.maintenance_cost_per_year
        total_cost = launch_cost + maintenance_cost
        
        return {
            'launch_cost_per_year': launch_cost,
            'maintenance_cost_per_year': maintenance_cost,
            'total_cost_per_year': total_cost
        }
    
    def get_annual_capacity(self, launch_frequency: int) -> float:
        """获取火箭年运输能力（吨）"""
        total_launches = launch_frequency * self.params.N_sites * self.params.N_plat
        return total_launches * self.params.M_rock


class ElevatorCostCalculator:
    """太空电梯成本计算器"""
    
    def __init__(self, params: ElevatorParams = None):
        self.params = params or ElevatorParams()
    
    def calculate_ideal_energy(self, mass_kg: float) -> float:
        """
        计算理想能量消耗（焦耳）
        E_ideal = GMm * (1/R_Earth - 1/R_GEO)
        """
        energy_j = G * M_EARTH * mass_kg * (1/R_EARTH - 1/R_GEO)
        return energy_j
    
    def calculate_energy_cost(self, mass_tons: float) -> float:
        """计算能源成本（万美元）"""
        mass_kg = mass_tons * 1000
        energy_j = self.calculate_ideal_energy(mass_kg)
        energy_actual_j = energy_j / self.params.eta  # 实际能耗 = 理想能耗 / 效率
        energy_kwh = energy_actual_j * J_TO_KWH
        cost_usd = energy_kwh * p_e
        return cost_usd / 10000  # 转万美元
    
    def calculate_maintenance_cost(self, mass_tons: float) -> float:
        """计算维护成本（万美元）"""
        mass_kg = mass_tons * 1000
        variable_cost_usd = mass_kg * self.params.mu * self.params.C_repair_per_kg
        variable_cost_wan = variable_cost_usd / 10000
        fixed_cost_wan = self.params.maintenance_cost_per_year + self.params.C_supervision_per_year
        return variable_cost_wan + fixed_cost_wan
    
    def calculate_labor_cost(self, mass_tons: float) -> float:
        """
        计算人工成本（万美元）
        
        Args:
            mass_tons: 运输质量（吨）
        
        Returns:
            人工成本（万美元）
        """
        cost_usd = mass_tons * self.params.C_labor_per_ton
        return cost_usd / 10000
    
    def calculate_economic_cost(self, utilization_rate: float) -> Dict[str, float]:
        """
        计算太空电梯年度经济成本
        C_e = C_energy + C_maintenance + C_labor
        
        Args:
            utilization_rate: 年利用率 (0.0 ~ 1.0)
        
        Returns:
            成本明细字典（万美元）
        """
        annual_mass = self.params.max_capacity_year * utilization_rate  # 吨
        
        energy_cost = self.calculate_energy_cost(annual_mass)
        maintenance_cost = self.calculate_maintenance_cost(annual_mass)
        labor_cost = self.calculate_labor_cost(annual_mass)
        total_cost = energy_cost + maintenance_cost + labor_cost
        
        return {
            'energy_cost_per_year': energy_cost,
            'maintenance_cost_per_year': maintenance_cost,
            'labor_cost_per_year': labor_cost,
            'total_cost_per_year': total_cost
        }
    
    def get_annual_capacity(self, utilization_rate: float) -> float:
        """获取太空电梯年运输能力（吨）"""
        return self.params.max_capacity_year * utilization_rate * self.params.num_sites_elev


def calculate_total_costs(
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


if __name__ == "__main__":
    # 示例：总重量10000吨，太空电梯利用率80%，火箭年发射50次
    economic_cost, time_cost = calculate_total_costs(
        total_mass=10000.0,
        elevator_utilization=0.8,
        rocket_launch_frequency=365
    )
    
    print(f"总经济成本: {economic_cost:.2f} 万美元")
    print(f"总时间成本: {time_cost:.4f} 年")
    
    # 查看火箭成本明细
    rocket_calc = RocketCostCalculator()
    rocket_detail = rocket_calc.calculate_economic_cost(365)
    print(f"\n火箭年度成本明细:")
    print(f"  发射成本: {rocket_detail['launch_cost_per_year']:.2f} 万美元")
    print(f"  维护成本: {rocket_detail['maintenance_cost_per_year']:.2f} 万美元")
    print(f"  总成本: {rocket_detail['total_cost_per_year']:.2f} 万美元")
    print(f"  年运输能力: {rocket_calc.get_annual_capacity(365):.2f} 吨")
    
    # 查看太空电梯成本明细
    elevator_calc = ElevatorCostCalculator()
    detail = elevator_calc.calculate_economic_cost(0.8)
    print(f"\n太空电梯年度成本明细:")
    print(f"  能源成本: {detail['energy_cost_per_year']:.2f} 万美元")
    print(f"  维护成本: {detail['maintenance_cost_per_year']:.2f} 万美元")
    print(f"  人工成本: {detail['labor_cost_per_year']:.2f} 万美元")
    print(f"  总成本: {detail['total_cost_per_year']:.2f} 万美元")
    print(f"  年运输能力: {elevator_calc.get_annual_capacity(0.8):.2f} 吨")
