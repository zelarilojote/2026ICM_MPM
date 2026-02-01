from algorithm.nsga import NSGA2
from problem.problem1 import LunarLogisticsProblem1
from problem.integrated_problem import IntegratedLunarProblem
from runner import NSGARunner
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Run NSGA lunar logistics experiments")
    parser.add_argument('--mode', choices=['integrated', 'separate'], default='integrated',
                        help='Run mode: integrated (single global plan) or separate (per-stage)')
    parser.add_argument('--base-year', type=int, default=2050, help='Base year for final reporting')
    parser.add_argument('--pop-size', type=int, help='Population size (overrides defaults)')
    parser.add_argument('--max-gen', type=int, help='Max generations (overrides defaults)')
    parser.add_argument('--stage-masses', type=str,
                        help='Comma-separated stage masses (e.g., 2e7,6e7,2e7) to override defaults')
    parser.add_argument('--priorities', type=str,
                        help='Comma-separated priorities for stages when running separate mode')
    parser.add_argument('--smooth', action='store_true', help='Use smooth=True for IntegratedLunarProblem')
    parser.add_argument('--seed', type=int, help='Optional random seed')
    parser.add_argument('--tag', type=str, default='Global_Plan', help='Stage tag for integrated mode')
    return parser.parse_args()

def main():
    args = parse_args()
    INTEGRATED = (args.mode == 'integrated')
    BASE_YEAR = args.base_year

    # 默认配置，保持原有行为
    default_configs = [
        {"mass": 2e7, "priority": "time", "tag": "Stage_1_Core"},
        {"mass": 6e7, "priority": "balanced", "tag": "Stage_2_Expand"},
        {"mass": 2e7, "priority": "cost", "tag": "Stage_3_Sustain"}
    ]

    # 根据命令行覆盖阶段质量
    if args.stage_masses:
        masses = [float(x) for x in args.stage_masses.split(',') if x.strip()]
        mass_configs = []
        for i, default in enumerate(default_configs):
            mass = masses[i] if i < len(masses) else default['mass']
            mass_configs.append({"mass": mass, "priority": default['priority'], "tag": default['tag']})
    else:
        mass_configs = default_configs

    # 根据命令行覆盖优先级（仅在分步模式时使用）
    if args.priorities:
        prios = [p.strip() for p in args.priorities.split(',') if p.strip()]
        for i, p in enumerate(prios):
            if i < len(mass_configs):
                mass_configs[i]['priority'] = p

    if args.seed is not None:
        import random
        try:
            import numpy as _np
            _np.random.seed(args.seed)
        except Exception:
            pass
        random.seed(args.seed)

    results = []
    if INTEGRATED:
        pop_size = args.pop_size if args.pop_size is not None else 150
        max_gen = args.max_gen if args.max_gen is not None else 300
        # 1. 集成模式：直接跑一次
        problem = IntegratedLunarProblem(stage_masses=[c['mass'] for c in mass_configs], smooth=args.smooth)
        algo = NSGA2(problem=problem, pop_size=pop_size, integrated=True)
        runner = NSGARunner(algo, max_gen=max_gen, stage_tag=args.tag, integrated=True, priority="balanced")
        results = runner.run()
    else:
        pop_size = args.pop_size if args.pop_size is not None else 100
        max_gen = args.max_gen if args.max_gen is not None else 200
        # 2. 分步模式：循环跑三次
        for conf in mass_configs:
            problem = LunarLogisticsProblem1(stage_mass=conf['mass'])
            algo = NSGA2(problem=problem, pop_size=pop_size)
            runner = NSGARunner(algo, max_gen=max_gen, stage_tag=conf['tag'], priority=conf['priority'])
            results.extend(runner.run())

    # --- 统一打印输出 ---
    print("\n" + "=" * 75)
    print(f"Mode: {'INTEGRATED' if INTEGRATED else 'SEPARATE'} | Base Year: {BASE_YEAR} | Pop: {pop_size} | Max Gen: {max_gen}")
    print(f"{'Phase':<15} | {'Rocket Freq':<12} | {'Elev Util':<10} | {'Cost(B USD)':<12} | {'Years':<8}")
    print("-" * 75)
    total_cost, total_time = 0, 0
    for r in results:
        print(f"{r['tag']:<15} | {r['rf']:>12.2f} | {r['eu']:>10.2%} | {r['cost']/10000:>12.2f} | {r['duration']:>8.2f}")
        total_cost += r['cost']
        total_time += r['duration']
    print("-" * 75)
    print(f"TOTAL: {total_time:.1f} Years | Cost: ${total_cost/10000:.2f} Billion | Year: {int(BASE_YEAR+total_time)}")
    print("=" * 75)


if __name__ == "__main__":
    main()