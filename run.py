import numpy as np
from algorithm.nsga import NSGA2
from problem.problem1 import LunarLogisticsProblem1
from runner import NSGARunner

def select_best_strategy(pop, vals, priority="balanced"):
    """归一化选点：从帕累托前沿寻找最符合战略预期的点"""
    min_vals = vals.min(axis=0)
    max_vals = vals.max(axis=0)
    # 防止除零
    norm_vals = (vals - min_vals) / (max_vals - min_vals + 1e-6)
    
    # 权重矩阵 [成本, 时间]
    weights = {
        "time": np.array([0.2, 0.8]),     # 核心建设：时间权重80%
        "balanced": np.array([0.5, 0.5]), # 巩固扩张：均分权重
        "cost": np.array([0.8, 0.2])      # 自持运行：省钱权重80%
    }
    
    w = weights.get(priority, weights["balanced"])
    scores = np.dot(norm_vals, w)
    best_idx = np.argmin(scores)
    
    return pop[best_idx], vals[best_idx]

def main():
    # --- 1. 定义三个阶段的参数 ---
    # 你可以根据实际模型调整任务重量
    stage_configs = [
        {"mass": 2e7, "priority": "time",     "tag": "Stage_1_Core"},
        {"mass": 6e7, "priority": "balanced", "tag": "Stage_2_Expand"},
        {"mass": 2e7, "priority": "cost",     "tag": "Stage_3_Sustain"}
    ]
    
    summary_results = []
    base_year = 2050

    print("🌙 LUNAR INFRASTRUCTURE STRATEGIC OPTIMIZER")
    print("-" * 50)

    for config in stage_configs:
        # A. 实例化问题
        problem = LunarLogisticsProblem1(stage_mass=config['mass'])
        
        # B. 初始化算法
        algo = NSGA2(problem=problem, pop_size=100)
        
        # C. 运行优化
        runner = NSGARunner(algo, max_gen=200, stage_tag=config['tag'])
        pop, vals = runner.run()
        
        # D. 战略选点
        best_x, best_v = select_best_strategy(pop, vals, config['priority'])
        
        summary_results.append({
            "tag": config['tag'],
            "rocket_freq": best_x[0],
            "elevator_util": best_x[1],
            "cost": best_v[0],
            "duration": best_v[1]
        })

    # --- 2. 最终总结表格打印 ---
    print("\n" + "="*70)
    print(f"{'Phase':<15} | {'Rocket Freq':<12} | {'Elev Util':<10} | {'Cost(B USD)':<12} | {'Years':<8}")
    print("-" * 70)
    
    total_cost = 0
    total_time = 0
    
    for res in summary_results:
        # 将万美元转成亿美元便于阅读
        cost_billion = res['cost'] / 10000 
        print(f"{res['tag']:<15} | {res['rocket_freq']:>12.2f} | {res['elevator_util']:>10.2%} | {cost_billion:>12.2f} | {res['duration']:>8.2f}")
        total_cost += cost_billion
        total_time += res['duration']

    print("-" * 70)
    print(f"TOTAL LOGISTICS PLAN: {total_time:.1f} Years | Final Cost: ${total_cost:.2f} Billion")
    print(f"ESTIMATED COMPLETION: Year {int(base_year + total_time)}")
    print("="*70)

if __name__ == "__main__":
    main()