from algorithm.nsga import NSGA2
from problem.problem1 import LunarLogisticsProblem1
from problem.integrated_problem import IntegratedLunarProblem
from runner import NSGARunner


def main():
    INTEGRATED = True
    BASE_YEAR = 2050
    CONFIGS = [
        {"mass": 2e7, "priority": "time", "tag": "Stage_1_Core"},
        {"mass": 6e7, "priority": "balanced", "tag": "Stage_2_Expand"},
        {"mass": 2e7, "priority": "cost", "tag": "Stage_3_Sustain"}
    ]

    results = []
    if INTEGRATED:
        # 1. 集成模式：直接跑一次
        problem = IntegratedLunarProblem(stage_masses=[c['mass'] for c in CONFIGS], smooth=True)
        algo = NSGA2(problem=problem, pop_size=150, integrated=True)
        runner = NSGARunner(algo, max_gen=300, stage_tag="Global_Plan", integrated=True, priority="balanced")
        results = runner.run()
    else:
        # 2. 分步模式：循环跑三次
        for conf in CONFIGS:
            problem = LunarLogisticsProblem1(stage_mass=conf['mass'])
            algo = NSGA2(problem=problem, pop_size=100)
            runner = NSGARunner(algo, max_gen=200, stage_tag=conf['tag'], priority=conf['priority'])
            results.extend(runner.run())

    # --- 统一打印输出 ---
    print("\n" + "="*75)
    print(f"{'Phase':<15} | {'Rocket Freq':<12} | {'Elev Util':<10} | {'Cost(B USD)':<12} | {'Years':<8}")
    print("-" * 75)
    total_cost, total_time = 0, 0
    for r in results:
        print(f"{r['tag']:<15} | {r['rf']:>12.2f} | {r['eu']:>10.2%} | {r['cost']/10000:>12.2f} | {r['duration']:>8.2f}")
        total_cost += r['cost']
        total_time += r['duration']
    print("-" * 75)
    print(f"TOTAL: {total_time:.1f} Years | Cost: ${total_cost/10000:.2f} Billion | Year: {int(BASE_YEAR+total_time)}")
    print("="*75)

if __name__ == "__main__":
    main()