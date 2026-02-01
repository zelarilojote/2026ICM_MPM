import os
import numpy as np
import matplotlib.pyplot as plt
from algorithm.nsga import NSGA2
from problem.problem1 import LunarLogisticsProblem1
from runner import NSGARunner

# 创建 logs 文件夹
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)


def plot_time_cost_compare(all_vals, all_tags, save_path=None, title="Time-Cost Compare (All Stages)"):
    """
    在 time-cost 二维空间对比每个阶段的 Pareto 前沿
    x: cost, y: time
    """
    plt.figure(figsize=(10, 7))
    colors = ['blue', 'green', 'red']
    markers = ['o', 's', '^']

    for i, (vals, tag) in enumerate(zip(all_vals, all_tags)):
        plt.scatter(
            vals[:, 0],  # cost
            vals[:, 1],  # time
            c=colors[i % len(colors)],
            marker=markers[i % len(markers)],
            alpha=0.6,
            s=50,
            label=tag
        )

    plt.xlabel('Economic Cost (10k USD)', fontsize=11)
    plt.ylabel('Time Cost (Years)', fontsize=11)
    plt.title(title, fontsize=13)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
    plt.show()


def main():
    stage_configs = [
        {"mass": 2e7, "priority": "time",     "tag": "Stage_1_Core"},
        {"mass": 6e7, "priority": "balanced", "tag": "Stage_2_Expand"},
        {"mass": 2e7, "priority": "cost",     "tag": "Stage_3_Sustain"}
    ]

    all_pareto_vals = []
    all_tags = []

    for config in stage_configs:
        problem = LunarLogisticsProblem1(stage_mass=config['mass'])
        algo = NSGA2(problem=problem, pop_size=100)
        runner = NSGARunner(algo, max_gen=200, stage_tag=config['tag'])
        runner.run()

        # 获取帕累托前沿并保存
        _, pareto_vals = algo.get_pareto_front()
        all_pareto_vals.append(pareto_vals)
        all_tags.append(config['tag'])

    save_path = os.path.join(LOGS_DIR, "time_cost_compare_all_stages.png")
    plot_time_cost_compare(all_pareto_vals, all_tags, save_path=save_path)


if __name__ == "__main__":
    main()
