"""
IntegratedCostCalculator.py
综合成本计算模块
整合经济成本、环境成本和时间成本
输入：太空电梯年利用率、火箭发射频率
输出：总成本 = 总时间成本 + 总经济成本 + 总环境成本（万美元）
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple, List

# ==================== 物理常数 ====================
G = 6.67430e-11       # 万有引力常数 (N·m²/kg²)
M_EARTH = 5.972e24    # 地球质量 (kg)
R_EARTH = 6.371e6     # 地球半径 (m)
R_GEO = 4.2164e7      # 地球同步轨道半径 (m)
p_e = 0.05            # 电费 (美元/kWh)
J_TO_KWH = 1 / 3.6e6  # 焦耳转千瓦时

# ==================== 经济成本参数 ====================
@dataclass
class RocketParams:
    """火箭经济参数配置"""
    C_rock: float = 1500.0                    # 每次发射成本（万美元）
    M_rock: float = 150.0                     # 单次载荷能力（吨）
    N_sites: int = 10                         # 发射场数量
    N_plat: int = 10                          # 每个发射场的发射台数量
    maintenance_cost_per_year: float = 200.0  # 年维护成本（万美元）

@dataclass
class ElevatorParams:
    """太空电梯经济参数配置"""
    C_repair_per_kg: float = 0.5              # 单位质量维修成本（美元/千克）
    C_labor_per_ton: float = 100.0            # 单位质量人工成本（美元/吨）
    max_capacity_year: float = 179000.0       # 年最大运输能力（吨）
    maintenance_cost_per_year: float = 500.0  # 年固定维护成本（万美元）
    C_supervision_per_year: float = 300.0     # 年监管成本（万美元）
    num_sites_elev: int = 3                   # 电梯数量
    eta: float = 0.8                          # 电机能源利用效率
    mu: float = 0.1                           # 每千克磨损系数

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

# ==================== 经济成本计算类 ====================
class RocketEconomicCalculator:
    """火箭经济成本计算器"""
    
    def __init__(self, params: RocketParams = None):
        self.params = params or RocketParams()
    
    def calculate_economic_cost(self, launch_frequency: int) -> Dict[str, float]:
        """
        计算火箭年度经济成本（万美元）
        
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

class ElevatorEconomicCalculator:
    """太空电梯经济成本计算器"""
    
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
        fixed_cost_wan = (self.params.maintenance_cost_per_year + 
                         self.params.C_supervision_per_year)
        return variable_cost_wan + fixed_cost_wan
    
    def calculate_labor_cost(self, mass_tons: float) -> float:
        """计算人工成本（万美元）"""
        cost_usd = mass_tons * self.params.C_labor_per_ton
        return cost_usd / 10000
    
    def calculate_economic_cost(self, utilization_rate: float) -> Dict[str, float]:
        """
        计算太空电梯年度经济成本（万美元）
        
        Args:
            utilization_rate: 年利用率 (0.0 ~ 1.0)
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

# ==================== 环境成本计算类 ====================
class RocketEnvCostCalculator:
    """火箭环境成本计算器"""
    
    def __init__(self, params: RocketEnvParams = None):
        self.params = params or RocketEnvParams()
    
    def calculate_environmental_cost(self, launch_frequency: int) -> Dict[str, float]:
        """
        计算火箭年度环境成本（万美元）
        """
        # 总发射次数：10个发射场，每个10个发射台
        total_launches = launch_frequency * 10 * 10
        
        # 1. 温室气体排放成本
        fuel_per_launch_kg = self.params.fuel_per_launch * 1000
        co2_emissions_kg = total_launches * fuel_per_launch_kg * self.params.co2_factor
        co2_cost = (co2_emissions_kg / 1000) * self.params.carbon_tax_rate
        
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
        toxic_leakage_cost = total_launches * self.params.marine_risk_factor * 10000
        marine_cost = (marine_cleanup_cost + toxic_leakage_cost) / 10000
        
        # 4. 噪音污染成本
        noise_cost = total_launches * self.params.noise_compensation / 10000
        
        # 5. 燃料环境成本
        fuel_env_cost = total_launches * fuel_per_launch_kg * self.params.fuel_cost_per_kg / 10000
        
        # 总环境成本
        total_cost = total_ghg_cost + stratospheric_cost + marine_cost + noise_cost + fuel_env_cost
        
        return {
            'ghg_cost_per_year': total_ghg_cost,
            'stratospheric_cost_per_year': stratospheric_cost,
            'marine_cost_per_year': marine_cost,
            'noise_cost_per_year': noise_cost,
            'fuel_env_cost_per_year': fuel_env_cost,
            'total_env_cost_per_year': total_cost,
            'co2_emissions_tons': co2_emissions_kg / 1000,
            'soot_emissions_tons': soot_emissions_kg / 1000,
            'total_launches': total_launches
        }
    
    def get_annual_capacity(self, launch_frequency: int) -> float:
        """获取火箭年运输能力（吨）"""
        total_launches = launch_frequency * 10 * 10
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
        carbon_tax_cost = (fossil_co2_kg / 1000) * self.params.carbon_tax_rate
        
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
        material_carbon_tax = material_carbon_per_ton * mass_tons * self.params.carbon_tax_rate
        
        return material_carbon_tax / 10000  # 转万美元
    
    def calculate_land_use_cost(self, transport_years: float) -> float:
        """计算土地使用成本（万美元）"""
        total_land_area = self.params.land_area * self.params.num_sites_elev
        annual_land_cost = total_land_area * self.params.land_use_cost
        total_land_cost = annual_land_cost * transport_years
        
        return total_land_cost / 10000  # 转万美元
    
    def calculate_water_cost(self, mass_tons: float) -> float:
        """计算水资源成本（万美元）"""
        total_energy_kwh = self.calculate_energy_consumption(mass_tons)
        water_consumption_liters = total_energy_kwh * self.params.water_per_kwh
        water_consumption_cubic_m = water_consumption_liters / 1000
        water_cost = water_consumption_cubic_m * self.params.water_cost
        
        return water_cost / 10000  # 转万美元
    
    def calculate_environmental_cost(self, utilization_rate: float) -> Dict[str, float]:
        """
        计算太空电梯年度环境成本（万美元）
        """
        annual_mass = self.params.max_capacity_year * utilization_rate * self.params.num_sites_elev
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

# ==================== 综合成本计算函数 ====================
def calculate_all_costs(
    total_mass: float,
    elevator_utilization: float,
    rocket_launch_frequency: int,
    rocket_econ_params: RocketParams = None,
    elevator_econ_params: ElevatorParams = None,
    rocket_env_params: RocketEnvParams = None,
    elevator_env_params: ElevatorEnvParams = None
) -> Dict[str, any]:
    """
    计算所有成本：时间成本 + 经济成本 + 环境成本
    
    Args:
        total_mass: 总运输重量（吨）
        elevator_utilization: 太空电梯年利用率 (0.0 ~ 1.0)
        rocket_launch_frequency: 火箭年发射频率（次/年/发射台）
    
    Returns:
        包含所有成本信息的字典
    """
    # 初始化各计算器
    rocket_econ_calc = RocketEconomicCalculator(rocket_econ_params)
    elevator_econ_calc = ElevatorEconomicCalculator(elevator_econ_params)
    rocket_env_calc = RocketEnvCostCalculator(rocket_env_params)
    elevator_env_calc = ElevatorEnvCostCalculator(elevator_env_params)
    
    # ========== 1. 计算运输能力 ==========
    rocket_capacity = rocket_econ_calc.get_annual_capacity(rocket_launch_frequency)
    elevator_capacity = elevator_econ_calc.get_annual_capacity(elevator_utilization)
    total_capacity = rocket_capacity + elevator_capacity
    
    # ========== 2. 计算时间成本 ==========
    if total_capacity > 0:
        total_time_cost = total_mass / total_capacity
    else:
        total_time_cost = float('inf')
    
    # ========== 3. 计算年度经济成本 ==========
    rocket_econ_detail = rocket_econ_calc.calculate_economic_cost(rocket_launch_frequency)
    elevator_econ_detail = elevator_econ_calc.calculate_economic_cost(elevator_utilization)
    
    rocket_econ_cost = rocket_econ_detail['total_cost_per_year']
    elevator_econ_cost = elevator_econ_detail['total_cost_per_year']
    annual_econ_cost = rocket_econ_cost + elevator_econ_cost
    
    # 总经济成本 = 年度经济成本 × 运输年数
    total_economic_cost = annual_econ_cost * total_time_cost
    
    # ========== 4. 计算年度环境成本 ==========
    rocket_env_detail = rocket_env_calc.calculate_environmental_cost(rocket_launch_frequency)
    elevator_env_detail = elevator_env_calc.calculate_environmental_cost(elevator_utilization)
    
    rocket_env_cost = rocket_env_detail['total_env_cost_per_year']
    elevator_env_cost = elevator_env_detail['total_env_cost_per_year']
    annual_env_cost = rocket_env_cost + elevator_env_cost
    
    # 总环境成本 = 年度环境成本 × 运输年数
    total_environmental_cost = annual_env_cost * total_time_cost
    
    # ========== 5. 计算总成本 ==========
    total_cost = total_time_cost + total_economic_cost + total_environmental_cost
    
    # ========== 6. 整理结果 ==========
    result = {
        # 运输能力信息
        'rocket_capacity': rocket_capacity,
        'elevator_capacity': elevator_capacity,
        'total_capacity': total_capacity,
        
        # 时间成本
        'total_time_cost': total_time_cost,
        
        # 经济成本
        'rocket_econ_detail': rocket_econ_detail,
        'elevator_econ_detail': elevator_econ_detail,
        'annual_econ_cost': annual_econ_cost,
        'total_economic_cost': total_economic_cost,
        
        # 环境成本
        'rocket_env_detail': rocket_env_detail,
        'elevator_env_detail': elevator_env_detail,
        'annual_env_cost': annual_env_cost,
        'total_environmental_cost': total_environmental_cost,
        
        # 总成本
        'total_cost': total_cost,
        
        # 各成本占比
        'time_cost_percentage': (total_time_cost / total_cost * 100) if total_cost > 0 else 0,
        'economic_cost_percentage': (total_economic_cost / total_cost * 100) if total_cost > 0 else 0,
        'environmental_cost_percentage': (total_environmental_cost / total_cost * 100) if total_cost > 0 else 0,
        
        # 运输比例
        'rocket_ratio': (rocket_capacity / total_capacity * 100) if total_capacity > 0 else 0,
        'elevator_ratio': (elevator_capacity / total_capacity * 100) if total_capacity > 0 else 0
    }
    
    return result

def compare_scenarios(
    total_mass: float = 100e6,
    scenarios: List[Dict] = None
) -> List[Dict]:
    """
    比较不同情景的成本
    
    Args:
        total_mass: 总运输重量（吨）
        scenarios: 情景列表，每个情景为包含参数的字典
    
    Returns:
        比较结果列表
    """
    if scenarios is None:
        # 默认情景
        scenarios = [
            {'name': '纯火箭方案', 'elevator_utilization': 0.0, 'rocket_frequency': 365},
            {'name': '纯太空电梯', 'elevator_utilization': 0.8, 'rocket_frequency': 0},
            {'name': '混合方案1', 'elevator_utilization': 0.56, 'rocket_frequency': 110},
            {'name': '混合方案2', 'elevator_utilization': 0.4, 'rocket_frequency': 183},
            {'name': '混合方案3', 'elevator_utilization': 0.24, 'rocket_frequency': 256},
        ]
    
    results = []
    
    for scenario in scenarios:
        cost_result = calculate_all_costs(
            total_mass=total_mass,
            elevator_utilization=scenario['elevator_utilization'],
            rocket_launch_frequency=scenario['rocket_frequency']
        )
        
        results.append({
            '情景': scenario['name'],
            '总成本(万美元)': cost_result['total_cost'],
            '时间成本(万美元)': cost_result['total_time_cost'],
            '经济成本(万美元)': cost_result['total_economic_cost'],
            '环境成本(万美元)': cost_result['total_environmental_cost'],
            '运输时间(年)': cost_result['total_time_cost'],
            '时间占比(%)': cost_result['time_cost_percentage'],
            '经济占比(%)': cost_result['economic_cost_percentage'],
            '环境占比(%)': cost_result['environmental_cost_percentage'],
            '火箭占比(%)': cost_result['rocket_ratio'],
            '电梯占比(%)': cost_result['elevator_ratio'],
            '火箭运力(万吨/年)': cost_result['rocket_capacity'] / 10000,
            '电梯运力(万吨/年)': cost_result['elevator_capacity'] / 10000
        })
    
    return results

def find_optimal_solution(
    total_mass: float = 100e6,
    elevator_util_range: Tuple[float, float] = (0.0, 1.0),
    rocket_freq_range: Tuple[int, int] = (0, 365),
    step_size: float = 0.05
) -> Dict[str, any]:
    """
    寻找最优解决方案
    
    Args:
        total_mass: 总运输重量
        elevator_util_range: 电梯利用率范围
        rocket_freq_range: 火箭频率范围
        step_size: 搜索步长
    
    Returns:
        最优解信息
    """
    best_solution = None
    best_cost = float('inf')
    all_solutions = []
    
    elevator_steps = int((elevator_util_range[1] - elevator_util_range[0]) / step_size) + 1
    rocket_steps = int((rocket_freq_range[1] - rocket_freq_range[0]) / 50) + 1
    
    for i in range(elevator_steps):
        elevator_util = elevator_util_range[0] + i * step_size
        elevator_util = min(elevator_util, elevator_util_range[1])
        
        for j in range(rocket_steps):
            rocket_freq = rocket_freq_range[0] + j * 50
            rocket_freq = min(rocket_freq, rocket_freq_range[1])
            
            # 跳过不合理组合（两者都为0）
            if elevator_util == 0 and rocket_freq == 0:
                continue
            
            cost_result = calculate_all_costs(
                total_mass=total_mass,
                elevator_utilization=elevator_util,
                rocket_launch_frequency=rocket_freq
            )
            
            solution = {
                'elevator_utilization': elevator_util,
                'rocket_frequency': rocket_freq,
                'total_cost': cost_result['total_cost'],
                'time_cost': cost_result['total_time_cost'],
                'economic_cost': cost_result['total_economic_cost'],
                'environmental_cost': cost_result['total_environmental_cost'],
                'transport_time': cost_result['total_time_cost'],
                'rocket_ratio': cost_result['rocket_ratio'],
                'elevator_ratio': cost_result['elevator_ratio']
            }
            
            all_solutions.append(solution)
            
            if cost_result['total_cost'] < best_cost:
                best_cost = cost_result['total_cost']
                best_solution = solution
    
    return {
        'best_solution': best_solution,
        'best_cost': best_cost,
        'all_solutions': all_solutions,
        'search_space': {
            'elevator_util_steps': elevator_steps,
            'rocket_freq_steps': rocket_steps,
            'total_combinations': len(all_solutions)
        }
    }

# ==================== 使用示例 ====================
if __name__ == "__main__":
    print("="*80)
    print("月球殖民地运输方案综合成本计算系统")
    print("="*80)
    
    # 示例：计算特定配置
    print("\n1. 计算示例配置...")
    result = calculate_all_costs(
        total_mass=100e6,           # 1亿吨
        elevator_utilization=0.8,   # 电梯利用率80%
        rocket_launch_frequency=365 # 火箭频率365次/年
    )
    
    print(f"总成本: {result['total_cost']:,.2f} 万美元")
    print(f"时间成本: {result['total_time_cost']:,.2f} 万美元")
    print(f"经济成本: {result['total_economic_cost']:,.2f} 万美元")
    print(f"环境成本: {result['total_environmental_cost']:,.2f} 万美元")
    print(f"运输时间: {result['total_time_cost']:.2f} 年")
    
    print(f"\n成本构成:")
    print(f"  时间成本占比: {result['time_cost_percentage']:.1f}%")
    print(f"  经济成本占比: {result['economic_cost_percentage']:.1f}%")
    print(f"  环境成本占比: {result['environmental_cost_percentage']:.1f}%")
    
    print(f"\n运输能力:")
    print(f"  火箭年运力: {result['rocket_capacity']/10000:.1f} 万吨")
    print(f"  电梯年运力: {result['elevator_capacity']/10000:.1f} 万吨")
    print(f"  总年运力: {result['total_capacity']/10000:.1f} 万吨")
    print(f"  火箭占比: {result['rocket_ratio']:.1f}%")
    print(f"  电梯占比: {result['elevator_ratio']:.1f}%")
    
    # 比较不同情景
    print("\n" + "="*80)
    print("不同情景比较")
    print("="*80)
    
    comparison = compare_scenarios()
    
    print(f"\n{'情景':<15} {'总成本(万美元)':<20} {'时间(年)':<15} {'经济成本(万美元)':<20} {'环境成本(万美元)':<20}")
    print("-" * 95)
    
    for scenario in comparison:
        print(f"{scenario['情景']:<15} {scenario['总成本(万美元)']:<20,.0f} {scenario['运输时间(年)']:<15.1f} {scenario['经济成本(万美元)']:<20,.0f} {scenario['环境成本(万美元)']:<20,.0f}")
    
    # 寻找最优解
    print("\n" + "="*80)
    print("最优解搜索")
    print("="*80)
    
    optimal = find_optimal_solution(step_size=0.1)
    best = optimal['best_solution']
    
    print(f"最优电梯利用率: {best['elevator_utilization']:.1%}")
    print(f"最优火箭频率: {best['rocket_frequency']} 次/年")
    print(f"最低总成本: {best['total_cost']:,.0f} 万美元")
    print(f"  时间成本: {best['time_cost']:,.0f} 万美元")
    print(f"  经济成本: {best['economic_cost']:,.0f} 万美元")
    print(f"  环境成本: {best['environmental_cost']:,.0f} 万美元")
    print(f"运输时间: {best['transport_time']:.1f} 年")
    print(f"火箭占比: {best['rocket_ratio']:.1f}%")
    print(f"电梯占比: {best['elevator_ratio']:.1f}%")
    
    # 分析成本敏感度
    print("\n" + "="*80)
    print("成本敏感度分析")
    print("="*80)
    
    util_values = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    for util in util_values:
        res = calculate_all_costs(
            total_mass=100e6,
            elevator_utilization=util,
            rocket_launch_frequency=365
        )
        print(f"电梯利用率 {util:.0%}: 总成本={res['total_cost']/1e4:,.0f}亿$, "
              f"时间={res['total_time_cost']:.1f}年, "
              f"火箭占比={res['rocket_ratio']:.0f}%")
    
    # 输出建议
    print("\n" + "="*80)
    print("给MCM机构的建议")
    print("="*80)
    
    print(f"""
基于综合成本分析，建议如下：

1. 推荐方案配置
   - 太空电梯利用率: {best['elevator_utilization']:.0%}
   - 火箭发射频率: {best['rocket_frequency']} 次/年
   - 预计总成本: {best['total_cost']/1e4:.0f} 亿美元
   - 预计运输时间: {best['transport_time']:.1f} 年

2. 成本构成优化
   - 时间成本: {best['time_cost']/best['total_cost']*100:.0f}%
   - 经济成本: {best['economic_cost']/best['total_cost']*100:.0f}%
   - 环境成本: {best['environmental_cost']/best['total_cost']*100:.0f}%

3. 运输效率
   - 火箭运输比例: {best['rocket_ratio']:.0f}%
   - 太空电梯比例: {best['elevator_ratio']:.0f}%
   - 综合年运输能力: {(result['rocket_capacity'] + result['elevator_capacity'])/1e4:.1f} 万吨/年

4. 关键措施
   - 优先发展太空电梯系统
   - 优化火箭发射调度
   - 实施环境成本控制
   - 建立综合成本监控系统
""")