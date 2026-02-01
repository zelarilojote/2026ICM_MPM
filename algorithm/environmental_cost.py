"""
EnvironmentalCost.py
环境成本计算模块
输入：太空电梯年利用率、火箭发射频率
输出：总环境成本（万美元）
与EconomicCost.py保持一致的接口
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple, List

@dataclass
class RocketEnvParams:
    """火箭环境参数配置"""
    fuel_per_launch: float = 1400.0           # 单次发射燃料消耗（吨）
    payload_to_moon: float = 150.0           # 单次有效载荷到月球（吨）
    co2_factor: float = 3.0                  # CO2排放因子：1kg燃料产生3kg CO2
    fuel_cost_per_kg: float = 1.0            # 燃料环境成本（美元/千克）
    soot_factor: float = 0.01                # 黑碳排放因子
    soot_gwp: float = 3000.0                 # 黑碳全球变暖潜势
    alumina_per_launch: float = 50.0         # 氧化铝排放（千克/次）
    marine_risk_factor: float = 0.01         # 海洋污染风险因子
    noise_factor: float = 0.1                # 噪音污染因子
    carbon_tax_rate: float = 50.0            # 碳税（美元/吨CO2）
    stratospheric_damage_cost: float = 1000.0  # 平流层破坏成本（美元/千克）
    marine_cleanup_cost: float = 500.0       # 海洋清理成本（美元/吨）
    noise_compensation: float = 1000.0       # 噪音补偿（美元/次发射）

@dataclass
class ElevatorEnvParams:
    """太空电梯环境参数配置"""
    specific_energy: float = 50.0            # 能耗：kWh/kg（运送1kg到GEO）
    max_capacity_year: float = 179000.0      # 年最大运输能力（吨）
    num_sites_elev: int = 3                  # 电梯数量
    grid_carbon_intensity: float = 0.1       # 电网碳强度（kg CO2/kWh）
    renewable_ratio: float = 0.8             # 可再生能源比例
    construction_material: float = 50000.0   # 建设材料（吨）
    material_carbon_factor: float = 2.0      # 材料碳足迹因子
    material_recycling_rate: float = 0.9     # 材料回收率
    land_area: float = 10.0                  # 单个银河港占地面积（平方公里）
    land_use_cost: float = 1000.0            # 土地使用成本（美元/平方公里·年）
    water_per_kwh: float = 1.5               # 水耗：升/kWh
    water_cost: float = 0.5                  # 水成本（美元/立方米）
    carbon_tax_rate: float = 50.0            # 碳税（美元/吨CO2）

class RocketEnvCostCalculator:
    """火箭环境成本计算器"""
    
    def __init__(self, params: RocketEnvParams = None):
        self.params = params or RocketEnvParams()
    
    def calculate_environmental_cost(self, launch_frequency: int) -> Dict[str, float]:
        """
        计算火箭年度环境成本（万美元）
        
        Args:
            launch_frequency: 每发射台每年发射次数
        
        Returns:
            环境成本明细（万美元）
        """
        # 总发射次数
        total_launches = launch_frequency * 10 * 10  # 10个发射场，每个10个发射台
        
        # 1. 温室气体排放成本
        fuel_per_launch_kg = self.params.fuel_per_launch * 1000
        co2_emissions_kg = total_launches * fuel_per_launch_kg * self.params.co2_factor
        co2_cost = (co2_emissions_kg / 1000) * self.params.carbon_tax_rate  # 美元
        
        # 黑碳排放成本（考虑GWP）
        soot_emissions_kg = total_launches * fuel_per_launch_kg * self.params.soot_factor
        soot_co2_eq_kg = soot_emissions_kg * self.params.soot_gwp
        soot_cost = (soot_co2_eq_kg / 1000) * self.params.carbon_tax_rate
        
        total_ghg_cost = (co2_cost + soot_cost) / 10000  # 转万美元
        
        # 2. 平流层破坏成本
        soot_stratospheric_cost = soot_emissions_kg * self.params.stratospheric_damage_cost
        alumina_stratospheric_cost = total_launches * self.params.alumina_per_launch * self.params.stratospheric_damage_cost
        stratospheric_cost = (soot_stratospheric_cost + alumina_stratospheric_cost) / 10000
        
        # 3. 海洋污染成本
        marine_debris_tons = total_launches * self.params.fuel_per_launch * 0.02
        marine_cleanup_cost = marine_debris_tons * self.params.marine_cleanup_cost
        toxic_leakage_cost = total_launches * self.params.marine_risk_factor * 10000  # 假设每次泄漏成本1万美元
        marine_cost = (marine_cleanup_cost + toxic_leakage_cost) / 10000
        
        # 4. 噪音污染成本
        noise_cost = total_launches * self.params.noise_compensation / 10000
        
        # 5. 燃料环境成本
        fuel_environmental_cost = total_launches * fuel_per_launch_kg * self.params.fuel_cost_per_kg / 10000
        
        # 总环境成本
        total_cost = total_ghg_cost + stratospheric_cost + marine_cost + noise_cost + fuel_environmental_cost
        
        return {
            'ghg_cost_per_year': total_ghg_cost,
            'stratospheric_cost_per_year': stratospheric_cost,
            'marine_cost_per_year': marine_cost,
            'noise_cost_per_year': noise_cost,
            'fuel_env_cost_per_year': fuel_environmental_cost,
            'total_env_cost_per_year': total_cost,
            'co2_emissions_tons': co2_emissions_kg / 1000,
            'soot_emissions_tons': soot_emissions_kg / 1000,
            'total_launches': total_launches
        }
    
    def get_annual_capacity(self, launch_frequency: int) -> float:
        """获取火箭年运输能力（吨）"""
        total_launches = launch_frequency * 10 * 10  # 10个发射场，每个10个发射台
        return total_launches * self.params.payload_to_moon

class ElevatorEnvCostCalculator:
    """太空电梯环境成本计算器"""
    
    def __init__(self, params: ElevatorEnvParams = None):
        self.params = params or ElevatorEnvParams()
    
    def calculate_energy_consumption(self, mass_tons: float) -> float:
        """计算总能耗（kWh）"""
        mass_kg = mass_tons * 1000
        return mass_kg * self.params.specific_energy
    
    def calculate_indirect_emissions_cost(self, mass_tons: float) -> float:
        """计算间接排放成本（万美元）"""
        total_energy_kwh = self.calculate_energy_consumption(mass_tons)
        
        # 考虑可再生能源比例
        renewable_energy = total_energy_kwh * self.params.renewable_ratio
        fossil_energy = total_energy_kwh * (1 - self.params.renewable_ratio)
        
        # 化石能源部分的碳排放
        fossil_co2_kg = fossil_energy * self.params.grid_carbon_intensity
        
        # 碳税成本
        carbon_tax_cost = (fossil_co2_kg / 1000) * self.params.carbon_tax_rate  # 美元
        
        return carbon_tax_cost / 10000  # 转万美元
    
    def calculate_material_env_cost(self, mass_tons: float) -> float:
        """计算材料环境成本（万美元）"""
        # 建筑材料的隐含碳
        material_carbon_tons = self.params.construction_material * self.params.material_carbon_factor
        
        # 考虑回收后的净影响
        net_material_carbon = material_carbon_tons * (1 - self.params.material_recycling_rate)
        
        # 按运输量分摊（假设电梯寿命50年）
        lifetime_transport = self.params.max_capacity_year * self.params.num_sites_elev * 50
        if lifetime_transport > 0:
            material_carbon_per_ton = net_material_carbon / lifetime_transport
        else:
            material_carbon_per_ton = 0
        
        # 碳税成本
        material_carbon_tax = material_carbon_per_ton * mass_tons * self.params.carbon_tax_rate  # 美元
        
        return material_carbon_tax / 10000  # 转万美元
    
    def calculate_land_use_cost(self, transport_years: float) -> float:
        """计算土地使用成本（万美元）"""
        total_land_area = self.params.land_area * self.params.num_sites_elev  # 平方公里
        annual_land_cost = total_land_area * self.params.land_use_cost  # 美元/年
        total_land_cost = annual_land_cost * transport_years  # 美元
        
        return total_land_cost / 10000  # 转万美元
    
    def calculate_water_cost(self, mass_tons: float) -> float:
        """计算水资源成本（万美元）"""
        total_energy_kwh = self.calculate_energy_consumption(mass_tons)
        water_consumption_liters = total_energy_kwh * self.params.water_per_kwh
        water_consumption_cubic_m = water_consumption_liters / 1000
        water_cost = water_consumption_cubic_m * self.params.water_cost  # 美元
        
        return water_cost / 10000  # 转万美元
    
    def calculate_environmental_cost(self, utilization_rate: float) -> Dict[str, float]:
        """
        计算太空电梯年度环境成本（万美元）
        
        Args:
            utilization_rate: 年利用率 (0.0 ~ 1.0)
        
        Returns:
            环境成本明细（万美元）
        """
        annual_mass = self.params.max_capacity_year * utilization_rate * self.params.num_sites_elev  # 吨
        transport_years = annual_mass / (self.params.max_capacity_year * self.params.num_sites_elev) if annual_mass > 0 else 1
        
        # 各项环境成本
        emissions_cost = self.calculate_indirect_emissions_cost(annual_mass)
        material_cost = self.calculate_material_env_cost(annual_mass)
        land_use_cost = self.calculate_land_use_cost(transport_years)
        water_cost = self.calculate_water_cost(annual_mass)
        
        # 总环境成本
        total_cost = emissions_cost + material_cost + land_use_cost + water_cost
        
        # 计算CO2排放
        total_energy_kwh = self.calculate_energy_consumption(annual_mass)
        fossil_energy = total_energy_kwh * (1 - self.params.renewable_ratio)
        co2_emissions_tons = fossil_energy * self.params.grid_carbon_intensity / 1000
        
        return {
            'emissions_cost_per_year': emissions_cost,
            'material_env_cost_per_year': material_cost,
            'land_use_cost_per_year': land_use_cost,
            'water_cost_per_year': water_cost,
            'total_env_cost_per_year': total_cost,
            'energy_consumption_kwh': total_energy_kwh,
            'annual_mass_tons': annual_mass,
            'co2_emissions_tons': co2_emissions_tons,
            'fossil_energy_kwh': fossil_energy
        }
    
    def get_annual_capacity(self, utilization_rate: float) -> float:
        """获取太空电梯年运输能力（吨）"""
        return self.params.max_capacity_year * utilization_rate * self.params.num_sites_elev

def calculate_total_environmental_cost(
    total_mass: float,
    elevator_utilization: float,
    rocket_launch_frequency: int,
    rocket_env_params: RocketEnvParams = None,
    elevator_env_params: ElevatorEnvParams = None
) -> Tuple[float, float, Dict]:
    """
    计算总环境成本和总时间成本
    
    Args:
        total_mass: 总运输重量（吨）
        elevator_utilization: 太空电梯年利用率 (0.0 ~ 1.0)
        rocket_launch_frequency: 火箭年发射频率（次/年/发射台）
    
    Returns:
        (总环境成本（万美元）, 总时间成本（年）, 详细结果字典)
    """
    rocket_calc = RocketEnvCostCalculator(rocket_env_params)
    elevator_calc = ElevatorEnvCostCalculator(elevator_env_params)
    
    # 计算年度环境成本
    rocket_env_detail = rocket_calc.calculate_environmental_cost(rocket_launch_frequency)
    elevator_env_detail = elevator_calc.calculate_environmental_cost(elevator_utilization)
    
    rocket_env_cost = rocket_env_detail['total_env_cost_per_year']
    elevator_env_cost = elevator_env_detail['total_env_cost_per_year']
    annual_env_cost = rocket_env_cost + elevator_env_cost
    
    # 计算运输能力
    rocket_capacity = rocket_calc.get_annual_capacity(rocket_launch_frequency)
    elevator_capacity = elevator_calc.get_annual_capacity(elevator_utilization)
    total_capacity = rocket_capacity + elevator_capacity
    
    # 计算总时间成本
    if total_capacity > 0:
        total_time_cost = total_mass / total_capacity
    else:
        total_time_cost = float('inf')
    
    # 总环境成本 = 年度环境成本 × 运输年数
    total_env_cost = annual_env_cost * total_time_cost
    
    # 详细结果
    details = {
        'rocket_env_detail': rocket_env_detail,
        'elevator_env_detail': elevator_env_detail,
        'rocket_capacity': rocket_capacity,
        'elevator_capacity': elevator_capacity,
        'total_capacity': total_capacity,
        'annual_env_cost': annual_env_cost,
        'total_time_years': total_time_cost,
        'rocket_calc': rocket_calc,
        'elevator_calc': elevator_calc
    }
    
    return total_env_cost, total_time_cost, details