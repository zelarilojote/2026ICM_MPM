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


# ==================== 环境成本参数 ====================
@dataclass
class RocketEnvParams:
    """火箭环境参数配置"""
    fuel_per_launch: float = 1400.0           # 单次发射燃料消耗（吨）
    payload_to_moon: float = 150.0            # 单次有效载荷到月球（吨）
    co2_factor: float = 3.0                   # CO2排放因子：1kg燃料产生3kg CO2
    fuel_cost_per_kg: float = 1.0             # 燃料环境成本（美元/千克）
    soot_factor: float = 0.01                 # 黑碳排放因子
    soot_gwp: float = 3000.0                  # 黑碳全球变暖潜势
    alumina_per_launch: float = 50.0          # 氧化铝排放（千克/次）
    marine_risk_factor: float = 0.01          # 海洋污染风险因子
    noise_factor: float = 0.1                 # 噪音污染因子
    carbon_tax_rate: float = 50.0             # 碳税（美元/吨CO2）
    stratospheric_damage_cost: float = 1000.0 # 平流层破坏成本（美元/千克）
    marine_cleanup_cost: float = 500.0        # 海洋清理成本（美元/吨）
    noise_compensation: float = 1000.0        # 噪音补偿（美元/次发射）

@dataclass
class ElevatorEnvParams:
    """太空电梯环境参数配置"""
    specific_energy: float = 50.0             # 能耗：kWh/kg（运送1kg到GEO）
    max_capacity_year: float = 179000.0       # 年最大运输能力（吨）
    num_sites_elev: int = 3                   # 电梯数量
    grid_carbon_intensity: float = 0.1        # 电网碳强度（kg CO2/kWh）
    renewable_ratio: float = 0.8              # 可再生能源比例
    construction_material: float = 50000.0    # 建设材料（吨）
    material_carbon_factor: float = 2.0       # 材料碳足迹因子
    material_recycling_rate: float = 0.9      # 材料回收率
    land_area: float = 10.0                   # 单个银河港占地面积（平方公里）
    land_use_cost: float = 1000.0             # 土地使用成本（美元/平方公里·年）
    water_per_kwh: float = 1.5                # 水耗：升/kWh
    water_cost: float = 0.5                   # 水成本（美元/立方米）
    carbon_tax_rate: float = 50.0             # 碳税（美元/吨CO2）
    
@dataclass
class RocketParams:
    """火箭参数配置"""
    C_rock: float = 1500.0                    # 每次发射成本（万美元）
    M_rock: float = 150.0                     # 单次载荷能力（吨）
    N_sites: int = 10                         # 发射场数量
    N_plat: int = 10                           # 每个发射场的发射台数量
    maintenance_cost_per_year: float = 200.0  # 年维护成本（万美元）
    alpha: float = 0.002                         # 大量发射折扣系数
    lambda_: float = 0.999                 # 发射价格折扣系数

@dataclass
class ElevatorParams:
    """太空电梯参数配置"""
    C_repair_per_kg: float = 500              # 单位质量维修成本（美元/千克）
    C_labor_per_ton: float = 100.0            # 单位质量人工成本（美元/吨）
    max_capacity_year: float = 179000.0       # 年最大运输能力（吨）
    maintenance_cost_per_year: float = 500.0  # 年固定维护成本（万美元）
    C_supervision_per_year: float = 300.0     # 年监管成本（万美元）
    num_sites_elev: int = 3                   # 电梯数量
    eta: float = 0.8                          # 电机能源利用效率
    mu: float = 0.1                           # 每千克磨损系数