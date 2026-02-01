import numpy as np
import matplotlib.pyplot as plt
import sys

from algorithm.cost import (
    RocketCostCalculator, 
    ElevatorCostCalculator,
    RocketParams,
    ElevatorParams
)

# ==========================================
# 1. 全局配置与不确定性参数 (Uncertainty Config)
# ==========================================
CONFIG = {
    "TOTAL_MASS": 1e8,  
    "PHASE_RATIOS": [0.50, 0.40, 0.10],
    
    # --- 不确定性参数 (The "Chaos" Factors) ---
    "SIMULATION_RUNS": 2000,  # 模拟次数
    
    # 风险1: 太空电梯的不完美
    "SE_EFFICIENCY_MEAN": 0.95, # 天气影响平均效率
    "SE_EFFICIENCY_STD": 0.05, # 天气影响标准差
    "SE_FAILURE_PROB": 0.02, # 故障概率
    "SE_REPAIR_TIME": 0.5, # 维修时间占比
    "SE_REPAIR_COST": 5e8,  # 维修费用（美元）
    
    # 风险2: 火箭发射失败
    "ROCKET_FAILURE_RATE": 0.01, # 失败率
    "ROCKET_GROUNDING_TIME": 0.25, # 停飞时间占比
    "ROCKET_FAILURE_COST_MULTIPLIER": 5.0, # 失败成本倍数
}

# ==========================================
# 2. 输入策略格式
# ==========================================
# 格式: [Phase1火箭频率, Phase1电梯利用率, Phase2火箭频率, Phase2电梯利用率, Phase3火箭频率, Phase3电梯利用率]
OPTIMAL_STRATEGY_X = [50, 0.5, 10, 1.0, 30, 0.8] 

# ==========================================
# 3. 初始化成本计算器
# ==========================================
rocket_calculator = RocketCostCalculator(RocketParams())
elevator_calculator = ElevatorCostCalculator(ElevatorParams())

# ==========================================
# 4. 模拟逻辑函数
# ==========================================
def run_one_simulation_scenario_c(strategy_x):
    """
    运行一次带有随机干扰的模拟 
    """
    total_time = 0
    total_cost = 0
    
    # 遍历三个阶段
    for i in range(3):
        target_mass = CONFIG["TOTAL_MASS"] * CONFIG["PHASE_RATIOS"][i]
        delivered_mass = 0
        
        # 解析策略变量
        rocket_freq_planned = strategy_x[i * 2]
        se_utilization_plan = strategy_x[i * 2 + 1]
        se_utilization_plan = np.clip(se_utilization_plan, 0.0, 1.0)

        # 开始时间步循环
        while delivered_mass < target_mass:
            # === 电梯部分 ===
            # 1. 随机天气效率
            se_weather_efficiency = np.random.normal(
                CONFIG["SE_EFFICIENCY_MEAN"], 
                CONFIG["SE_EFFICIENCY_STD"]
            )
            se_weather_efficiency = np.clip(se_weather_efficiency, 0.5, 1.0)
            
            # 2. 故障判定
            se_working_ratio = 1.0
            if np.random.random() < CONFIG["SE_FAILURE_PROB"]:
                se_working_ratio -= CONFIG["SE_REPAIR_TIME"]
                se_working_ratio = max(0, se_working_ratio)
                total_cost += CONFIG["SE_REPAIR_COST"]
            
            # 3. 实际利用率 = 计划利用率 * 天气效率 * 工作比例
            actual_utilization = se_utilization_plan * se_weather_efficiency * se_working_ratio
            
            # 4. 调用 cost.py 计算电梯年运力和成本
            se_actual_capacity = elevator_calculator.get_annual_capacity(actual_utilization)
            se_cost_detail = elevator_calculator.calculate_economic_cost(actual_utilization)
            year_se_cost = se_cost_detail['total_cost_per_year'] * 10000  # 万美元转美元
            
            # === 火箭部分 ===
            launches_this_year = int(rocket_freq_planned)
            failures = np.random.binomial(launches_this_year, CONFIG["ROCKET_FAILURE_RATE"])
            successes = launches_this_year - failures
            
            # 停飞惩罚
            grounding_penalty = 0
            if failures > 0:
                grounding_penalty = min(CONFIG["ROCKET_GROUNDING_TIME"] * failures, 1.0)
            
            # 有效发射次数
            effective_freq = int(successes * (1.0 - grounding_penalty))
            
            # 调用 cost.py 计算火箭年运力和成本
            rocket_actual_capacity = rocket_calculator.get_annual_capacity(effective_freq)
            rocket_cost_detail = rocket_calculator.calculate_economic_cost(effective_freq)
            year_rocket_cost = rocket_cost_detail['total_cost_per_year'] * 10000  # 万美元转美元
            
            # 失败惩罚成本
            failure_penalty_cost = failures * rocket_calculator.params.C_rock * 10000 * CONFIG["ROCKET_FAILURE_COST_MULTIPLIER"]
            year_rocket_cost += failure_penalty_cost
            
            # === 累加 ===
            year_delivered = se_actual_capacity + rocket_actual_capacity
            delivered_mass += year_delivered
            total_cost += (year_rocket_cost + year_se_cost)
            total_time += 1.0

    return total_cost, total_time


# ==========================================
# 5. 蒙特卡洛主循环
# ==========================================
if __name__ == "__main__":
    print(f"--- Starting Monte Carlo Simulation ({CONFIG['SIMULATION_RUNS']} Runs) ---")
    print("Using cost.py for cost calculations...")
    
    results_cost = []
    results_time = []
    
    for run in range(CONFIG["SIMULATION_RUNS"]):
        c, t = run_one_simulation_scenario_c(OPTIMAL_STRATEGY_X)
        results_cost.append(c)
        results_time.append(t)
        
        if (run+1) % 500 == 0:
            print(f"Completed {run+1} runs...")
            
    # 统计分析
    costs = np.array(results_cost) / 1e9
    times = np.array(results_time)
    
    mean_cost = np.mean(costs)
    std_cost = np.std(costs)
    p95_cost = np.percentile(costs, 95)
    
    mean_time = np.mean(times)
    std_time = np.std(times)
    p95_time = np.percentile(times, 95)
    
    print("\n=== [Task 2 Analysis Results] ===")
    print(f"平均成本: ${mean_cost:.2f} Billion (Std: {std_cost:.2f})")
    print(f"95% 概率成本不超过: ${p95_cost:.2f} Billion")
    print(f"平均时间: {mean_time:.2f} Years (Std: {std_time:.2f})")
    print(f"95% 概率完工时间不超过: {p95_time:.2f} Years")
    
    # ==========================================
    # 6. 可视化
    # ==========================================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    ax1.hist(costs, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
    ax1.axvline(mean_cost, color='red', linestyle='--', linewidth=2, label=f'Mean: ${mean_cost:.2f}B')
    ax1.axvline(p95_cost, color='orange', linestyle=':', linewidth=2, label=f'95% Risk: ${p95_cost:.2f}B')
    ax1.set_title('Uncertainty Distribution of Total Cost')
    ax1.set_xlabel('Total Cost (Billion USD)')
    ax1.set_ylabel('Frequency')
    ax1.legend()
    
    ax2.hist(times, bins=30, color='lightgreen', edgecolor='black', alpha=0.7)
    ax2.axvline(mean_time, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_time:.1f} Years')
    ax2.axvline(p95_time, color='orange', linestyle=':', linewidth=2, label=f'95% Risk: {p95_time:.1f} Years')
    ax2.set_title('Uncertainty Distribution of Timeline')
    ax2.set_xlabel('Completion Time (Years)')
    ax2.legend()
    
    plt.tight_layout()
    plt.show()