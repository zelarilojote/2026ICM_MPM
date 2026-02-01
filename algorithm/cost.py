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
        total_cost = energy_cost + maintenance_cost + (labor_cost** 2)
        
        return {
            'energy_cost_per_year': energy_cost,
            'maintenance_cost_per_year': maintenance_cost,
            'labor_cost_per_year': labor_cost,
            'total_cost_per_year': total_cost
        }
    
    def get_annual_capacity(self, utilization_rate: float) -> float:
        """获取太空电梯年运输能力（吨）"""
        return self.params.max_capacity_year * utilization_rate * self.params.num_sites_elev


