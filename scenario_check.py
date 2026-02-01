import numpy as np
from problem.problem1 import LunarLogisticsProblem1
from algorithm.cost import calculate_total_costs # 确保路径正确

def check_cost_magnitudes():
    # 1. 初始化一个特定阶段的任务（以 Stage 1 为例）
    # 使用你之前跑出的 5e7 吨
    test_mass = 5e7 
    problem = LunarLogisticsProblem1(stage_mass=test_mass)
    
    # 2. 选取决策空间的四个极端点进行压力测试
    # [火箭频率, 电梯利用率]
    test_cases = {
        "Min Intensity (Low Freq, Low Util)": [1.0, 0.05],
        "Max Intensity (High Freq, High Util)": [365.0, 1.0],
        "Mixed (High Freq, Low Util)": [365.0, 0.05],
        "Mixed (Low Freq, High Util)": [1.0, 1.0]
    }

    print("="*70)
    print(f"📊 SCENARIO MAGNITUDE CHECK (Target Mass: {test_mass:.1e} Tons)")
    print("="*70)
    print(f"{'Test Case':<40} | {'Economic (B USD)':<15} | {'Time (Y)':<10}")
    print("-" * 70)

    for desc, x in test_cases.items():
        # 调用原始 evaluate
        econ_wan, time_years = problem.evaluate(np.array(x))
        
        # 转换为十亿美元 (Billion USD) 方便观察
        econ_billion = econ_wan / 10000 
        
        print(f"{desc:<40} | {econ_billion:>15.2f} | {time_years:>10.2f}")

    print("-" * 70)
    
    # 3. 计算数量级差异（Loss Scaling Check）
    # 模拟一个典型的解
    e_val, t_val = problem.evaluate(np.array([180.0, 0.5]))
    magnitude_ratio = (e_val / t_val) if t_val != 0 else 0
    print(f"💡 Current Magnitude Ratio (Econ/Time): {magnitude_ratio:.2e}")
    
    if magnitude_ratio > 1e4:
        print("\n⚠️  WARNING: Magnitude Gap is too large!")
        print("建议在 NSGA-II 选点或 Evaluate 中引入归一化，或者调整惩罚项系数。")
    print("="*70)

if __name__ == "__main__":
    check_cost_magnitudes()