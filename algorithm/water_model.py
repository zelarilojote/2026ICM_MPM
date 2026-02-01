import numpy as np
from dataclasses import dataclass
from typing import Tuple, Dict
import matplotlib.pyplot as plt

# 引入你之前的成本计算模块 (假设在同目录下，或者直接复制之前的 cost.py)
# from cost import calculate_total_costs, RocketParams, ElevatorParams 
# 为了演示方便，我在这里模拟一个简单的成本计算接口，实际使用时请替换为你自己的 calculate_total_costs
def mock_calculate_total_costs(mass_tons, rocket_freq, elev_util):
    """
    模拟调用之前的物流模型。
    实际使用时，请删除此函数，直接 import 你写好的 calculate_total_costs
    """
    # 假设 Stage 3 的平均运力效率
    # 这里只是为了让代码能跑通并展示逻辑
    if mass_tons == 0: return 0.0, 0.0
    
    # 简化的估算逻辑 (基于你之前的 Stage 3 数据)
    # 假设: 运 1吨 约需 50万美元 (混合模式), 速度极快
    cost_per_ton_wan = 50.0 # 万美元
    total_capacity_year = 500000.0 # 年运力 50万吨
    
    econ_cost = mass_tons * cost_per_ton_wan
    time_cost = mass_tons / total_capacity_year
    
    return econ_cost, time_cost

# ==========================================
# 1. 水资源需求模型 (Water Demand Model)
# ==========================================

@dataclass
class WaterConfig:
    population: int = 100000       # 殖民地人口
    daily_use_per_capita: float = 50.0  # 人均日用水量 (kg) - 含生活、卫生、农业流转
    recycling_efficiency: float = 0.95  # 水循环回收率 (ECLSS 效率)
    safety_buffer_days: int = 30   # 安全库存天数 (断供时的缓冲)
    
    # ISRU (原位资源利用) 参数
    isru_efficiency_ratio: float = 100.0 # 1吨设备每年能产多少吨水
    isru_equipment_lifespan: int = 10    # 设备使用年限

class WaterDemandCalculator:
    def __init__(self, config: WaterConfig):
        self.cfg = config

    def calculate_annual_needs(self) -> Dict[str, float]:
        """计算年度水资源需求量 (kg 和 吨)"""
        # 1. 总循环需求 (Total Circulation)
        total_daily_circulation = self.cfg.population * self.cfg.daily_use_per_capita
        
        # 2. 每日损耗 (Daily Loss / Makeup)
        # 损耗来源：气闸泄漏、生物质锁定、处理残渣、蒸发逃逸
        daily_loss = total_daily_circulation * (1.0 - self.cfg.recycling_efficiency)
        
        # 3. 年度补给需求 (Annual Makeup)
        annual_makeup_kg = daily_loss * 365
        
        # 4. 安全库存 (Initial Buffer) - 仅首年或扩容时需要
        safety_stock_kg = total_daily_circulation * self.cfg.safety_buffer_days
        
        return {
            "daily_loss_tons": daily_loss / 1000,
            "annual_makeup_tons": annual_makeup_kg / 1000,
            "safety_stock_tons": safety_stock_kg / 1000,
            "total_first_year_tons": (annual_makeup_kg + safety_stock_kg) / 1000
        }

    def calculate_isru_requirements(self, water_tons_needed: float) -> float:
        """
        计算如果采用 ISRU 策略，需要运送多少设备 (吨)
        """
        # 设备重量 = 目标产水量 / 产水率
        equipment_mass_tons = water_tons_needed / self.cfg.isru_efficiency_ratio
        return equipment_mass_tons

# ==========================================
# 2. 策略评估与分析 (Strategy Analysis)
# ==========================================

def run_water_logistics_analysis():
    print("💧 MOON COLONY WATER SUSTAINMENT ANALYSIS")
    print("=" * 60)
    
    # --- A. 初始化模型参数 ---
    # 场景：高回收效率 (96%), 10万人
    config = WaterConfig(
        population=100000, 
        recycling_efficiency=0.96, # 96% 回收率 (参考 ISS 先进水平)
        daily_use_per_capita=45.0  # 45kg/人 (高效节水)
    )
    water_model = WaterDemandCalculator(config)
    
    # 计算需求
    needs = water_model.calculate_annual_needs()
    
    print(f"[Model Parameters]")
    print(f"Population: {config.population:,}")
    print(f"Recycling Rate: {config.recycling_efficiency:.1%} (Loss: {1-config.recycling_efficiency:.1%})")
    print(f"Daily Use: {config.daily_use_per_capita} kg/person")
    print("-" * 60)
    print(f"[Demand Calculation]")
    print(f"Daily Water Loss (Makeup): {needs['daily_loss_tons']:.2f} tons/day")
    print(f"Annual Water Makeup Needed: {needs['annual_makeup_tons']:.2f} tons/year")
    print(f"Safety Buffer ({config.safety_buffer_days} days): {needs['safety_stock_tons']:.2f} tons")
    print("-" * 60)

    # --- B. 策略对比 ---
    # 假设使用 Stage 3 的成熟运力配置 (火箭频率 2000, 电梯利用率 50%)
    rocket_freq = 2000
    elev_util = 0.5
    
    print(f"\n[Logistics Strategy Comparison]")
    print(f"Transport Context: Fully Operational Phase (Stage 3 Capability)")
    
    # 策略 1: 地球直接供水 (Earth Supply)
    # 任务载荷 = 年度补给量
    mass_strategy_1 = needs['annual_makeup_tons']
    cost_1, time_1 = mock_calculate_total_costs(mass_strategy_1, rocket_freq, elev_util)
    
    # 策略 2: ISRU 原位制水 (In-Situ Resource Utilization)
    # 任务载荷 = 采矿设备重量 (假设采矿效率 1:150)
    # 只需要运一次设备，就能解决未来 10 年的水
    config.isru_efficiency_ratio = 150.0 
    mass_strategy_2 = water_model.calculate_isru_requirements(mass_strategy_1)
    cost_2, time_2 = mock_calculate_total_costs(mass_strategy_2, rocket_freq, elev_util)

    # --- C. 输出结果表格 ---
    print(f"{'Strategy':<25} | {'Payload (Tons)':<15} | {'Cost (Billion $)':<18} | {'Time (Days)':<12}")
    print("-" * 75)
    
    # 转换单位：万美元 -> 十亿美元 (Billion), 年 -> 天
    cost_1_b = cost_1 / 100000 
    time_1_d = time_1 * 365
    
    cost_2_b = cost_2 / 100000
    time_2_d = time_2 * 365
    
    print(f"{'1. Direct Water Delivery':<25} | {mass_strategy_1:>15.2f} | ${cost_1_b:>17.4f} | {time_1_d:>11.2f}")
    print(f"{'2. ISRU Equipment':<25} | {mass_strategy_2:>15.2f} | ${cost_2_b:>17.4f} | {time_2_d:>11.2f}")
    
    print("-" * 75)
    print("\n[Strategic Conclusion]")
    if cost_2 < cost_1:
        savings = (cost_1 - cost_2) / 100000
        ratio = mass_strategy_1 / mass_strategy_2
        print(f"✅ RECOMMENDATION: Adopt Strategy 2 (ISRU).")
        print(f"   By transporting mining equipment instead of water, payload is reduced by {ratio:.1f}x.")
        print(f"   Annual operational savings: ${savings:.4f} Billion.")
        print(f"   Logistics impact is negligible ({time_2_d*24:.1f} hours of transport time).")
    else:
        print("⚠️ RECOMMENDATION: Direct delivery is cheaper (Check ISRU efficiency parameters).")

if __name__ == "__main__":
    run_water_logistics_analysis()