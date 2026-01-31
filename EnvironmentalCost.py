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

def compare_scenarios(total_mass: float = 100e6) -> List[Dict]:
    """
    比较不同情景的环境成本
    
    Args:
        total_mass: 总运输重量（吨），默认1亿吨
    
    Returns:
        比较结果列表
    """
    scenarios = [
        # 情景1: 纯火箭方案
        {'name': '纯火箭', 'elevator_utilization': 0.0, 'rocket_frequency': 365},
        # 情景2: 纯太空电梯
        {'name': '纯太空电梯', 'elevator_utilization': 0.8, 'rocket_frequency': 0},
        # 情景3: 混合方案1 (30%火箭)
        {'name': '混合1(30%火箭)', 'elevator_utilization': 0.56, 'rocket_frequency': 110},
        # 情景4: 混合方案2 (50%火箭)
        {'name': '混合2(50%火箭)', 'elevator_utilization': 0.4, 'rocket_frequency': 183},
        # 情景5: 混合方案3 (70%火箭)
        {'name': '混合3(70%火箭)', 'elevator_utilization': 0.24, 'rocket_frequency': 256},
    ]
    
    results = []
    
    for scenario in scenarios:
        env_cost, time_cost, details = calculate_total_environmental_cost(
            total_mass=total_mass,
            elevator_utilization=scenario['elevator_utilization'],
            rocket_launch_frequency=scenario['rocket_frequency']
        )
        
        # 计算环境绩效指标
        env_cost_per_ton = env_cost / total_mass * 10000  # 美元/吨
        
        # 计算CO2排放强度 - 修复了这里的错误
        rocket_co2 = details['rocket_env_detail']['co2_emissions_tons'] * total_time_cost
        elevator_co2 = details['elevator_env_detail']['co2_emissions_tons'] * total_time_cost
        total_co2 = rocket_co2 + elevator_co2
        co2_per_ton = total_co2 / total_mass if total_mass > 0 else 0
        
        results.append({
            '情景': scenario['name'],
            '总环境成本(万美元)': env_cost,
            '环境成本密度(美元/吨)': env_cost_per_ton,
            '总时间成本(年)': time_cost,
            '火箭年运力(万吨)': details['rocket_capacity'] / 10000,
            '电梯年运力(万吨)': details['elevator_capacity'] / 10000,
            'CO2排放(吨/吨货物)': co2_per_ton,
            '火箭占比(%)': details['rocket_capacity'] / details['total_capacity'] * 100 if details['total_capacity'] > 0 else 0,
            '电梯占比(%)': details['elevator_capacity'] / details['total_capacity'] * 100 if details['total_capacity'] > 0 else 0,
            '火箭CO2排放(万吨)': rocket_co2 / 10000,
            '电梯CO2排放(万吨)': elevator_co2 / 10000
        })
    
    return results

def analyze_optimal_solution(total_mass: float = 100e6, step: float = 0.1) -> Dict:
    """
    分析最优解：寻找最低环境成本的混合比例
    
    Args:
        total_mass: 总运输重量（吨）
        step: 火箭比例搜索步长
    
    Returns:
        最优解信息
    """
    best_solution = None
    best_cost = float('inf')
    all_solutions = []
    
    # 搜索火箭比例从0到1
    rocket_ratios = np.arange(0, 1.01, step)
    
    for rocket_ratio in rocket_ratios:
        # 根据火箭比例计算电梯利用率和火箭频率
        # 简化假设：总运力保持恒定
        elevator_ratio = 1 - rocket_ratio
        
        # 计算对应的参数
        elevator_utilization = 0.8 * elevator_ratio  # 按比例调整
        rocket_frequency = int(365 * rocket_ratio)   # 按比例调整
        
        env_cost, time_cost, details = calculate_total_environmental_cost(
            total_mass=total_mass,
            elevator_utilization=elevator_utilization,
            rocket_launch_frequency=rocket_frequency
        )
        
        solution = {
            'rocket_ratio': rocket_ratio,
            'elevator_utilization': elevator_utilization,
            'rocket_frequency': rocket_frequency,
            'total_env_cost': env_cost,
            'time_cost': time_cost,
            'env_cost_per_ton': env_cost / total_mass * 10000,
            'total_capacity': details['total_capacity']
        }
        
        all_solutions.append(solution)
        
        if env_cost < best_cost:
            best_cost = env_cost
            best_solution = solution
    
    return {
        'best_solution': best_solution,
        'all_solutions': all_solutions,
        'search_range': list(rocket_ratios)
    }

# ==================== 使用示例 ====================

if __name__ == "__main__":
    print("="*70)
    print("月球殖民地运输方案环境成本评估系统")
    print("="*70)
    
    # 示例：总重量1亿吨，太空电梯利用率80%，火箭年发射365次
    print("\n1. 计算示例情景...")
    total_env_cost, total_time_cost, details = calculate_total_environmental_cost(
        total_mass=100e6,  # 1亿吨
        elevator_utilization=0.8,
        rocket_launch_frequency=365
    )
    
    print(f"总环境成本: {total_env_cost:,.2f} 万美元")
    print(f"总时间成本: {total_time_cost:.2f} 年")
    print(f"年均环境成本: {details['annual_env_cost']:,.2f} 万美元/年")
    
    # 火箭环境成本明细
    print(f"\n火箭环境成本明细:")
    print(f"  温室气体成本: {details['rocket_env_detail']['ghg_cost_per_year']:,.2f} 万美元/年")
    print(f"  平流层破坏成本: {details['rocket_env_detail']['stratospheric_cost_per_year']:,.2f} 万美元/年")
    print(f"  海洋污染成本: {details['rocket_env_detail']['marine_cost_per_year']:,.2f} 万美元/年")
    print(f"  噪音污染成本: {details['rocket_env_detail']['noise_cost_per_year']:,.2f} 万美元/年")
    print(f"  年CO2排放: {details['rocket_env_detail']['co2_emissions_tons']:,.0f} 吨")
    print(f"  年黑碳排放: {details['rocket_env_detail']['soot_emissions_tons']:,.0f} 吨")
    print(f"  年发射次数: {details['rocket_env_detail']['total_launches']:,.0f} 次")
    
    # 太空电梯环境成本明细
    print(f"\n太空电梯环境成本明细:")
    print(f"  间接排放成本: {details['elevator_env_detail']['emissions_cost_per_year']:,.2f} 万美元/年")
    print(f"  材料环境成本: {details['elevator_env_detail']['material_env_cost_per_year']:,.2f} 万美元/年")
    print(f"  土地使用成本: {details['elevator_env_detail']['land_use_cost_per_year']:,.2f} 万美元/年")
    print(f"  水资源成本: {details['elevator_env_detail']['water_cost_per_year']:,.2f} 万美元/年")
    print(f"  年能耗: {details['elevator_env_detail']['energy_consumption_kwh']/1e9:.1f} 十亿kWh")
    print(f"  年CO2排放: {details['elevator_env_detail']['co2_emissions_tons']:,.0f} 吨")
    
    # 运输能力
    print(f"\n运输能力分析:")
    print(f"  火箭年运力: {details['rocket_capacity']/10000:.1f} 万吨")
    print(f"  太空电梯年运力: {details['elevator_capacity']/10000:.1f} 万吨")
    print(f"  总年运力: {details['total_capacity']/10000:.1f} 万吨")
    print(f"  火箭占比: {details['rocket_capacity']/details['total_capacity']*100:.1f}%")
    print(f"  太空电梯占比: {details['elevator_capacity']/details['total_capacity']*100:.1f}%")
    
    # 比较不同情景
    print("\n" + "="*70)
    print("不同情景比较分析")
    print("="*70)
    
    comparison_results = compare_scenarios()
    
    print(f"\n{'情景':<20} {'总环境成本(万美元)':<20} {'环境成本密度(美元/吨)':<20} {'总时间(年)':<15} {'火箭占比(%)':<15} {'电梯占比(%)':<15}")
    print("-" * 110)
    
    for result in comparison_results:
        print(f"{result['情景']:<20} {result['总环境成本(万美元)']:<20,.0f} {result['环境成本密度(美元/吨)']:<20.2f} {result['总时间成本(年)']:<15.1f} {result['火箭占比(%)']:<15.1f} {result['电梯占比(%)']:<15.1f}")
    
    # 找到最优方案
    min_env_cost = min(comparison_results, key=lambda x: x['总环境成本(万美元)'])
    min_env_per_ton = min(comparison_results, key=lambda x: x['环境成本密度(美元/吨)'])
    min_time = min(comparison_results, key=lambda x: x['总时间成本(年)'])
    
    print(f"\n最优方案分析:")
    print(f"  最低总环境成本: {min_env_cost['情景']} ({min_env_cost['总环境成本(万美元)']:,.0f} 万美元)")
    print(f"  最低单位环境成本: {min_env_per_ton['情景']} ({min_env_per_ton['环境成本密度(美元/吨)']:.2f} 美元/吨)")
    print(f"  最短运输时间: {min_time['情景']} ({min_time['总时间成本(年)']:.1f} 年)")
    
    # 最优解搜索
    print("\n" + "="*70)
    print("最优解搜索分析")
    print("="*70)
    
    optimal_analysis = analyze_optimal_solution(total_mass=100e6, step=0.05)
    best = optimal_analysis['best_solution']
    
    print(f"最优火箭比例: {best['rocket_ratio']:.1%}")
    print(f"对应电梯利用率: {best['elevator_utilization']:.1%}")
    print(f"对应火箭频率: {best['rocket_frequency']} 次/年/发射台")
    print(f"最低总环境成本: {best['total_env_cost']:,.0f} 万美元")
    print(f"单位环境成本: {best['env_cost_per_ton']:.2f} 美元/吨")
    print(f"运输时间: {best['time_cost']:.1f} 年")
    
    # 敏感性分析
    print("\n" + "="*70)
    print("敏感性分析：电梯利用率的影响")
    print("="*70)
    
    utilizations = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    for util in utilizations:
        env_cost, time_cost, _ = calculate_total_environmental_cost(
            total_mass=100e6,
            elevator_utilization=util,
            rocket_launch_frequency=365
        )
        env_per_ton = env_cost / 100e6 * 10000
        print(f"利用率 {util:.0%}: 总成本={env_cost:,.0f}万$, 单位成本={env_per_ton:.2f}$/吨, 时间={time_cost:.1f}年")
    
    # 综合建议
    print("\n" + "="*70)
    print("给MCM机构的综合建议")
    print("="*70)
    
    print(f"""
基于环境成本分析，建议：

1. 最优方案配置
   - 火箭运输比例: {best['rocket_ratio']:.0%}
   - 太空电梯利用率: {best['elevator_utilization']:.0%}
   - 火箭发射频率: {best['rocket_frequency']} 次/年/发射台
   - 预计总环境成本: {best['total_env_cost']:,.0f} 万美元
   - 预计运输时间: {best['time_cost']:.1f} 年

2. 关键环境绩效指标
   - 单位环境成本: {best['env_cost_per_ton']:.2f} 美元/吨
   - 较纯火箭方案节省: {100*(1-best['total_env_cost']/comparison_results[0]['总环境成本(万美元)']):.0f}%
   - 较纯电梯方案节省时间: {100*(1-best['time_cost']/comparison_results[1]['总时间成本(年)']):.0f}%

3. 环境优化措施
   - 提高太空电梯可再生能源比例至80%以上
   - 开发绿色火箭推进剂(液氢/液氧)
   - 实施碳捕获和补偿机制
   - 建立环境监测和报告系统

4. 成本控制策略
   - 优化运输调度，减少空载率
   - 提高材料回收利用率至90%以上
   - 采用先进的环境技术降低治理成本

5. 风险管理建议
   - 建立环境应急预案
   - 购买环境责任保险
   - 定期进行环境审计
   - 设立环境保护基金
""")