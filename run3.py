import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
from algorithm.nsga import NSGA2
from problem.problem3 import LunarLogisticsProblem1
from runner import NSGARunner

# 创建 logs 文件夹
LOGS_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)


def plot_pareto_front_3d(all_vals, all_tags, title="3D Pareto Front", save_path=None):
    """
    Plot 3D Pareto front
    """
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    colors = ['blue', 'green', 'red']
    markers = ['o', 's', '^']
    
    for i, (vals, tag) in enumerate(zip(all_vals, all_tags)):
        ax.scatter(
            vals[:, 0],
            vals[:, 1],
            vals[:, 2],
            c=colors[i % len(colors)],
            marker=markers[i % len(markers)],
            alpha=0.6,
            s=50,
            label=tag
        )
    
    ax.set_xlabel('Economic Cost (10k USD)', fontsize=12)
    ax.set_ylabel('Time Cost (Years)', fontsize=12)
    ax.set_zlabel('Environmental Cost', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(loc='upper left')
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
    plt.show()


def plot_pareto_front_2d_projections(all_vals, all_tags, save_path=None):
    """
    Plot 2D projections of Pareto front
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    colors = ['blue', 'green', 'red']
    labels_pairs = [
        ('Economic Cost (10k USD)', 'Time Cost (Years)'),
        ('Economic Cost (10k USD)', 'Environmental Cost'),
        ('Time Cost (Years)', 'Environmental Cost')
    ]
    idx_pairs = [(0, 1), (0, 2), (1, 2)]
    
    for ax, (xlabel, ylabel), (xi, yi) in zip(axes, labels_pairs, idx_pairs):
        for i, (vals, tag) in enumerate(zip(all_vals, all_tags)):
            ax.scatter(
                vals[:, xi],
                vals[:, yi],
                c=colors[i % len(colors)],
                alpha=0.6,
                s=50,
                label=tag
            )
        ax.set_xlabel(xlabel, fontsize=11)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('Pareto Front 2D Projections', fontsize=14)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
    plt.show()


def plot_single_stage_pareto(vals, tag, save_path=None):
    """
    Plot single stage Pareto front (3D)
    """
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')
    
    ax.scatter(
        vals[:, 0],
        vals[:, 1],
        vals[:, 2],
        c='blue',
        alpha=0.6,
        s=50
    )
    
    ax.set_xlabel('Economic Cost (10k USD)', fontsize=12)
    ax.set_ylabel('Time Cost (Years)', fontsize=12)
    ax.set_zlabel('Environmental Cost', fontsize=12)
    ax.set_title(f'Pareto Front - {tag}', fontsize=14)
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
    plt.show()


def select_best_strategy(pop, vals, priority="balanced"):
    """Select best strategy from Pareto front based on priority"""
    min_vals = vals.min(axis=0)
    max_vals = vals.max(axis=0)
    norm_vals = (vals - min_vals) / (max_vals - min_vals + 1e-6)
    
    weights = {
        "time": np.array([0.2, 0.6, 0.2]),
        "balanced": np.array([0.5, 0.4, 0.1]),
        "cost": np.array([0.8, 0.1, 0.1])
    }
    
    w = weights.get(priority, weights["balanced"])
    scores = np.dot(norm_vals, w)
    best_idx = np.argmin(scores)
    
    return pop[best_idx], vals[best_idx]


def main():
    stage_configs = [
        {"mass": 2e7, "priority": "time",     "tag": "Stage_1_Core"},
        {"mass": 6e7, "priority": "balanced", "tag": "Stage_2_Expand"},
        {"mass": 2e7, "priority": "cost",     "tag": "Stage_3_Sustain"}
    ]
    
    summary_results = []
    all_pareto_vals = []
    all_tags = []
    base_year = 2050

    print("LUNAR INFRASTRUCTURE STRATEGIC OPTIMIZER")
    print("-" * 50)

    for config in stage_configs:
        problem = LunarLogisticsProblem1(stage_mass=config['mass'])
        algo = NSGA2(problem=problem, pop_size=100)
        runner = NSGARunner(algo, max_gen=200, stage_tag=config['tag'])
        pop, vals = runner.run()
        
        # Get Pareto front
        pareto_pop, pareto_vals = algo.get_pareto_front()
        all_pareto_vals.append(pareto_vals)
        all_tags.append(config['tag'])
        
        # Save individual stage Pareto front
        stage_save_path = os.path.join(LOGS_DIR, f"pareto_front_{config['tag']}.png")
        plot_single_stage_pareto(pareto_vals, config['tag'], save_path=stage_save_path)
        
        best_x, best_v = select_best_strategy(pop, vals, config['priority'])
        
        summary_results.append({
            "tag": config['tag'],
            "rocket_freq": best_x[0],
            "elevator_util": best_x[1],
            "cost": best_v[0],
            "duration": best_v[1],
            "env_cost": best_v[2] if len(best_v) > 2 else 0
        })

    # --- Visualize combined Pareto fronts ---
    print("\nGenerating Pareto Front Visualizations...")
    
    # Save combined 3D plot
    combined_3d_path = os.path.join(LOGS_DIR, "pareto_front_3d_all_stages.png")
    plot_pareto_front_3d(all_pareto_vals, all_tags, "3D Pareto Front - All Stages", save_path=combined_3d_path)
    
    # Save 2D projections
    projections_path = os.path.join(LOGS_DIR, "pareto_front_2d_projections.png")
    plot_pareto_front_2d_projections(all_pareto_vals, all_tags, save_path=projections_path)

    # --- Print summary table ---
    print("\n" + "="*80)
    print(f"{'Phase':<15} | {'Rocket Freq':<12} | {'Elev Util':<10} | {'Cost(B USD)':<12} | {'Years':<8} | {'Env Cost':<10}")
    print("-" * 80)
    
    total_cost = 0
    total_time = 0
    total_env = 0
    
    for res in summary_results:
        cost_billion = res['cost'] / 10000 
        print(f"{res['tag']:<15} | {res['rocket_freq']:>12.2f} | {res['elevator_util']:>10.2%} | {cost_billion:>12.2f} | {res['duration']:>8.2f} | {res['env_cost']:>10.2f}")
        total_cost += cost_billion
        total_time += res['duration']
        total_env += res['env_cost']

    print("-" * 80)
    print(f"TOTAL: {total_time:.1f} Years | Cost: ${total_cost:.2f}B | Env: {total_env:.2f}")
    print(f"ESTIMATED COMPLETION: Year {int(base_year + total_time)}")
    print("="*80)
    print(f"\nAll figures saved to: {LOGS_DIR}")


if __name__ == "__main__":
    main()