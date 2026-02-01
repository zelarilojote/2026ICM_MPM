import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import sys
import os
from tqdm import tqdm  # 进度条库
from scipy.stats import pearsonr

# ==========================================
# 0. 环境与样式设置
# ==========================================
# 创建 logs 文件夹
LOGS_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# 设置出版级绘图风格
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 10,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'lines.linewidth': 2
})

# 引入你的自定义模块
try:
    from algorithm.cost import (
        RocketCostCalculator, 
        ElevatorCostCalculator,
        RocketParams,
        ElevatorParams
    )
except ImportError:
    print("⚠️ Warning: algorithm.cost not found. Please ensure the module exists.")
    sys.exit(1)

# ==========================================
# 1. 全局配置 (Configuration)
# ==========================================
CONFIG = {
    "TOTAL_MASS": 1e8,  
    "PHASE_RATIOS": [0.20, 0.60, 0.20],
    "START_YEAR": 2050,  # 增加起始年份，增强代入感
    
    # --- 蒙特卡洛参数 ---
    "SIMULATION_RUNS": 2000, 
    
    # --- 风险参数 ---
    "SE_EFFICIENCY_MEAN": 0.95, 
    "SE_EFFICIENCY_STD": 0.05, 
    "SE_FAILURE_PROB": 0.02, 
    "SE_REPAIR_TIME": 0.5, 
    "SE_REPAIR_COST": 50, 
    "HUGE_REBUILD_COST": 2000, # 特大灾害重建费用 (调大一点以凸显风险)
    
    "ROCKET_FAILURE_RATE": 0.01, 
    "ROCKET_GROUNDING_TIME": 0.25, 
    "ROCKET_FAILURE_COST_MULTIPLIER": 5.0, 
    "FECTEUR_LEARNING_RATE": 0.99, 
    
    # 物理参数
    "OMEGA_EARTH": 7.2921e-5,
    "TETHER_TENSION_AVG": 6.3e7,
    "CLIMBER_MASS_TONS": 20.0,
    "DESIGN_SPEED": 200.0
}

OPTIMAL_STRATEGY_X = [365, 0.9, 10, 0.67, 1.0, 0.41] 

# 初始化计算器
rocket_calculator = RocketCostCalculator(RocketParams())
elevator_calculator = ElevatorCostCalculator(ElevatorParams())

# ==========================================
# 2. 物理核心 (Physics Core)
# ==========================================
def calculate_physics_based_efficiency(climber_speed_kmh):
    """基于科里奥利力与随机扰动的效率计算"""
    v_ms = climber_speed_kmh / 3.6
    m_kg = CONFIG["CLIMBER_MASS_TONS"] * 1000
    
    # 科里奥利力
    f_coriolis = 2 * m_kg * v_ms * CONFIG["OMEGA_EARTH"]
    
    # 随机扰动 (模拟空间环境的不确定性)
    f_external = f_coriolis * np.random.uniform(-0.5, 0.5) 
    f_total_lateral = f_coriolis + f_external
    
    # 偏转角与几何效率
    tan_theta = f_total_lateral / CONFIG["TETHER_TENSION_AVG"]
    theta_rad = np.arctan(tan_theta)
    efficiency_geometry = np.cos(theta_rad)
    
    # 安全限速折损
    theta_abs = abs(theta_rad)
    if theta_abs > 0.05:
        penalty = 1.0 - (theta_abs - 0.05) * 10
        efficiency_safety = max(0.1, penalty)
    else:
        efficiency_safety = 1.0
        
    return efficiency_geometry * efficiency_safety

# ==========================================
# 3. 模拟引擎 (Simulation Engine)
# ==========================================
# 全局变量：记录所有实验的 phase 切换时间
all_phase_years = []

def run_one_simulation(strategy_x):
    """
    运行单次模拟，并返回详细的指标用于敏感性分析
    """
    total_time = 0
    total_cost = 0
    yearly_cum_cost = []
    phase_years_local = []  # 本次模拟的 phase 切换时间
    
    # === 敏感性追踪指标 (Metrics for Sensitivity Analysis) ===
    metrics = {
        "total_rocket_failures": 0,
        "total_se_breakdowns": 0,
        "total_disasters": 0,
        "avg_weather_efficiency": [],
        "avg_physics_efficiency": []
    }

    # 遍历三个阶段
    for i in range(3):
        phase_years_local.append(total_time)
        target_mass = CONFIG["TOTAL_MASS"] * CONFIG["PHASE_RATIOS"][i]
        delivered_mass = 0
        
        rocket_freq_planned = strategy_x[i * 2]
        se_utilization_plan = np.clip(strategy_x[i * 2 + 1], 0.0, 1.0)

        while delivered_mass < target_mass:
            # --- 1. 环境与物理 ---
            se_weather_efficiency = np.clip(
                np.random.normal(CONFIG["SE_EFFICIENCY_MEAN"], CONFIG["SE_EFFICIENCY_STD"]), 
                0.5, 1.0
            )
            phy_efficiency = calculate_physics_based_efficiency(CONFIG["DESIGN_SPEED"])
            
            metrics["avg_weather_efficiency"].append(se_weather_efficiency)
            metrics["avg_physics_efficiency"].append(phy_efficiency)

            # --- 2. 灾难与故障 (Poisson & Bernoulli) ---
            se_working_ratio = 1.0
            
            # 特大灾害 (Poisson)
            num_disasters = np.random.poisson(lam=0.05) # 降低一点频率，提高破坏力
            if num_disasters > 0:
                se_working_ratio = 0 
                total_cost += CONFIG["HUGE_REBUILD_COST"] * num_disasters
                metrics["total_disasters"] += num_disasters
            
            # 常规故障 (Bernoulli)
            elif np.random.random() < CONFIG["SE_FAILURE_PROB"]:
                se_working_ratio -= CONFIG["SE_REPAIR_TIME"]
                se_working_ratio = max(0, se_working_ratio)
                total_cost += CONFIG["SE_REPAIR_COST"]
                metrics["total_se_breakdowns"] += 1

            # --- 3. 运力计算 ---
            actual_utilization = se_utilization_plan * phy_efficiency * se_weather_efficiency * se_working_ratio
            se_actual_capacity = elevator_calculator.get_annual_capacity(actual_utilization)
            se_cost_detail = elevator_calculator.calculate_economic_cost(actual_utilization)
            total_cost += se_cost_detail['total_cost_per_year'] * 10000 

            # --- 4. 火箭发射 ---
            launches = int(rocket_freq_planned)
            # 引入学习曲线
            current_fail_rate = CONFIG["ROCKET_FAILURE_RATE"] * (CONFIG["FECTEUR_LEARNING_RATE"] ** total_time)
            failures = np.random.binomial(launches, current_fail_rate)
            metrics["total_rocket_failures"] += failures
            
            grounding_penalty = min(CONFIG["ROCKET_GROUNDING_TIME"] * failures, 1.0) if failures > 0 else 0
            effective_freq = int((launches - failures) * (1.0 - grounding_penalty))
            
            rocket_actual_capacity = rocket_calculator.get_annual_capacity(effective_freq)
            rocket_cost_detail = rocket_calculator.calculate_economic_cost(effective_freq)
            
            # 基础成本 + 惩罚成本
            year_rocket_cost = (rocket_cost_detail['total_cost_per_year'] * 10000) + \
                               (failures * rocket_calculator.params.C_rock * 10000 * CONFIG["ROCKET_FAILURE_COST_MULTIPLIER"])
            
            total_cost += year_rocket_cost
            
            # --- 5. 状态更新 ---
            delivered_mass += (se_actual_capacity + rocket_actual_capacity)
            total_time += 1.0
            yearly_cum_cost.append(total_cost)
    
    # 聚合 Metrics
    metrics["avg_weather_efficiency"] = np.mean(metrics["avg_weather_efficiency"])
    metrics["avg_physics_efficiency"] = np.mean(metrics["avg_physics_efficiency"])
    
    return total_cost, total_time, np.array(yearly_cum_cost), metrics, phase_years_local

# ==========================================
# 4. 高级绘图函数 (Advanced Plotting)
# ==========================================

def plot_enhanced_fan_chart(results_paths, avg_phase_years):
    """绘制带叙事性标注的 Fan Chart"""
    # 数据对齐
    max_len = max(len(p) for p in results_paths)
    paths_mat = np.zeros((len(results_paths), max_len))
    for i, p in enumerate(results_paths):
        paths_mat[i, :len(p)] = p
        paths_mat[i, len(p):] = p[-1] # 补齐

    years = np.arange(CONFIG["START_YEAR"], CONFIG["START_YEAR"] + max_len)
    
    mean_path = np.mean(paths_mat, axis=0) / 1e9
    p05, p95 = np.percentile(paths_mat, [5, 95], axis=0) / 1e9
    p25, p75 = np.percentile(paths_mat, [25, 75], axis=0) / 1e9
    
    # 提取最坏路径 (Tail Risk)
    worst_paths = np.sort(paths_mat[:, -1])[-3:] # 最坏的3个结果
    worst_indices = np.argsort(paths_mat[:, -1])[-3:]
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # 绘制置信区间
    ax.fill_between(years, p05, p95, color='#a6cee3', alpha=0.3, label='95% Confidence Interval')
    ax.fill_between(years, p25, p75, color='#1f78b4', alpha=0.4, label='50% Confidence Interval')
    ax.plot(years, mean_path, color='black', linewidth=2.5, label='Expected Path (Mean)')
    
    # 绘制灾难线 (Tail Risk)
    for idx in worst_indices:
        ax.plot(years, paths_mat[idx] / 1e9, color='#e31a1c', linewidth=1, alpha=0.6, linestyle='-')

    # === [新增 1] 背景分区 (Zoning) ===
    # 使用平均 phase 切换年份
    elbow_year = CONFIG["START_YEAR"] + avg_phase_years[1]
    elbow_year_2 = CONFIG["START_YEAR"] + avg_phase_years[2]
    
    ax.axvline(x=elbow_year, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(x=elbow_year_2, color='gray', linestyle='--', alpha=0.5)
    
    # 建设期背景 (PHASE I)
    ax.axvspan(years[0], elbow_year, color='gray', alpha=0.05)
    ax.text(years[0]+2, 1000, "PHASE I:\nHigh-Intensity Construction\n(Rocket Dominant)", 
            fontsize=10, color='dimgray', fontweight='bold', va='top')
    
    # 运维期背景 (PHASE II)
    ax.axvspan(elbow_year, elbow_year_2, color='#e8f4f8', alpha=0.05)
    ax.text(elbow_year+5, 3000, "PHASE II:\nSustainment & Maintenance\n(Elevator Dominant)", 
            fontsize=10, color='dimgray', fontweight='bold')
    
    # 稳定期背景 (PHASE III)
    ax.axvspan(elbow_year_2, years[-1], color='#f0f8f0', alpha=0.05)
    ax.text(elbow_year_2+3, 5000, "PHASE III:\nLong-term Operations\n(Stable State)", 
            fontsize=10, color='dimgray', fontweight='bold')

    # === [新增 2] 嵌入式直方图 (Inset Histogram) ===
    # 在右下角创建一个子图轴
    ax_inset = ax.inset_axes([0.6, 0.1, 0.35, 0.3]) 
    
    # 获取最终成本数据
    final_costs = paths_mat[:, -1] / 1e9
    
    # 绘制直方图
    sns.histplot(final_costs, kde=True, ax=ax_inset, color='#1f77b4', alpha=0.6, element="step")
    
    # 美化子图
    ax_inset.set_title('Distribution of Final Cost (2230)', fontsize=9, fontweight='bold')
    ax_inset.set_xlabel('Cost ($B)', fontsize=8)
    ax_inset.set_ylabel('Freq', fontsize=8)
    ax_inset.tick_params(axis='both', which='major', labelsize=8)
    ax_inset.grid(False) # 去掉子图网格，保持整洁
    
    # 标记均值线在子图中
    ax_inset.axvline(mean_path[-1], color='black', linestyle='--', linewidth=1)

    # 添加标注
    ax.annotate('Tail Risk: Major Disasters\n(Kessler Syndrome / Storms)', 
                xy=(years[-1], paths_mat[worst_indices[-1]][-1]/1e9), 
                xytext=(years[-1]-30, paths_mat[worst_indices[-1]][-1]/1e9 + 500),
                arrowprops=dict(facecolor='#e31a1c', arrowstyle='->'),
                fontsize=10, color='#d62728', fontweight='bold')
    
    ax.set_title(f'Robustness Analysis: Cost Projections & Risk Distribution ({years[0]}-{years[-1]})', fontsize=14, fontweight='bold')
    ax.set_xlabel('Year')
    ax.set_ylabel('Cumulative Cost (Billion USD)')
    ax.legend(loc='upper left')
    
    # 去除多余边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(os.path.join(LOGS_DIR, "enhanced_fan_chart.png"), dpi=300)
    plt.show()

def plot_sensitivity_tornado(df_results):
    """绘制龙卷风图 (Tornado Plot) 用于敏感性分析"""
    # 计算相关系数
    correlations = df_results.corr()['Total Cost (B)'].drop(['Total Cost (B)', 'Time (Years)'])
    correlations = correlations.sort_values(ascending=True)
    
    plt.figure(figsize=(10, 6))
    colors = ['#ff7f0e' if x > 0 else '#1f77b4' for x in correlations.values]
    correlations.plot(kind='barh', color=colors, alpha=0.8)
    
    plt.title('Sensitivity Analysis: What Drives the Cost?', fontsize=14, fontweight='bold')
    plt.xlabel('Correlation with Total Cost (Pearson Coefficient)')
    plt.axvline(0, color='black', linewidth=0.8)
    plt.tight_layout()
    plt.savefig(os.path.join(LOGS_DIR, "sensitivity_tornado.png"), dpi=300)
    plt.show()

def plot_joint_distribution(df_results):
    """
    绘制 O奖级 联合分布图：Hexbin + KDE等高线 + 风险阈值 + 统计标注
    """
    # 1. 设置绘图风格
    sns.set_theme(style="white", font_scale=1.2)
    
    # 2. 创建基础 JointGrid
    g = sns.JointGrid(data=df_results, x="Time (Years)", y="Total Cost (B)", height=9)

    # 3. 绘制中央图像 (Hexbin + KDE)
    # A. 底层：Hexbin (密度热力图)
    g.plot_joint(plt.hexbin, gridsize=25, cmap="BuGn", mincnt=1, edgecolors="white", linewidths=0.2)
    
    # B. 顶层：KDE 等高线 (Topographic Map style)
    g.plot_joint(sns.kdeplot, color="black", levels=5, linewidths=1.0, alpha=0.6)

    # 4. 绘制边缘直方图
    sns.histplot(data=df_results, x="Time (Years)", ax=g.ax_marg_x, color="#4CB391", kde=True, element="step")
    sns.histplot(data=df_results, y="Total Cost (B)", ax=g.ax_marg_y, color="#4CB391", kde=True, element="step")

    # 5. --- 添加 O奖叙事细节 ---

    # A. 标注均值点 (Expected Value)
    mean_time = df_results["Time (Years)"].mean()
    mean_cost = df_results["Total Cost (B)"].mean()
    g.ax_joint.scatter([mean_time], [mean_cost], color='red', s=100, marker='*', zorder=10, label='Expected Scenario')

    # B. 添加风险阈值线 (Constraints)
    budget_cap = 5500
    deadline = 245
    
    g.ax_joint.axhline(budget_cap, color='#e74c3c', linestyle='--', linewidth=2, alpha=0.8)
    g.ax_joint.text(df_results["Time (Years)"].min(), budget_cap + 10, 'Budget Cap ($5.5T)', color='#e74c3c', fontweight='bold')
    
    g.ax_joint.axvline(deadline, color='#e74c3c', linestyle='--', linewidth=2, alpha=0.8)
    g.ax_joint.text(deadline + 0.5, df_results["Total Cost (B)"].min(), 'Deadline (Year 245)', color='#e74c3c', rotation=90, fontweight='bold')

    # C. 计算并标注统计量 (Correlation)
    r, p = pearsonr(df_results["Time (Years)"], df_results["Total Cost (B)"])
    stats_text = (
        f"Statistics:\n"
        f"• Mean Cost: ${mean_cost:.1f}B\n"
        f"• Mean Time: {mean_time:.1f} Yrs\n"
        f"• Correlation (r): {r:.2f}\n"
        f"• Failure Risk: {len(df_results[(df_results['Total Cost (B)'] > budget_cap) | (df_results['Time (Years)'] > deadline)]) / len(df_results):.1%}"
    )
    
    # 将统计数据放在左上角
    g.ax_joint.text(0.05, 0.95, stats_text, transform=g.ax_joint.transAxes, 
                    fontsize=11, verticalalignment='top', 
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="gray", alpha=0.9))

    # 6. 标签与标题
    g.fig.suptitle('Joint Probability Analysis: Cost-Time Trade-off & Risk Assessment', y=1.02, fontsize=16, fontweight='bold')
    g.set_axis_labels('Completion Time (Years)', 'Total Accumulated Cost (Billion USD)', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(os.path.join(LOGS_DIR, "enhanced_joint_distribution.png"), dpi=300, bbox_inches='tight')
    plt.show()

def plot_butterfly_sensitivity(df_results, save_dir='logs'):
    """
    绘制 O奖级 蝴蝶龙卷风图：同时展示对时间和成本的敏感性
    """
    # 1. 准备数据
    targets = ['Total Cost (B)', 'Time (Years)']
    features = ['Rocket Failures', 'SE Breakdowns', 'Disasters', 'Avg Weather Eff', 'Avg Physics Eff']
    
    # 检查数据中是否存在这些列，防止报错
    available_features = [f for f in features if f in df_results.columns]
    
    # 计算相关系数矩阵
    corr_matrix = df_results[available_features + targets].corr()
    
    # 提取针对 Cost 和 Time 的相关性
    cost_corr = corr_matrix['Total Cost (B)'].drop(targets)
    time_corr = corr_matrix['Time (Years)'].drop(targets)
    
    # 创建绘图数据框
    plot_df = pd.DataFrame({
        'Feature': cost_corr.index,
        'Cost Sensitivity': cost_corr.values,
        'Time Sensitivity': time_corr.values
    })
    
    # 按 Cost 敏感性的绝对值排序
    plot_df['abs_cost'] = plot_df['Cost Sensitivity'].abs()
    plot_df = plot_df.sort_values('abs_cost', ascending=True)
    
    # 2. 绘图设置
    fig, axes = plt.subplots(ncols=2, figsize=(14, 8), sharey=True)
    plt.subplots_adjust(wspace=0.05) # 减小中间间距
    
    # 颜色设置
    cost_colors = ['#ff7f0e' if x > 0 else '#1f77b4' for x in plot_df['Cost Sensitivity']]
    time_colors = ['#d62728' if x > 0 else '#2ca02c' for x in plot_df['Time Sensitivity']]
    
    # --- 左侧：Time Sensitivity ---
    axes[0].barh(plot_df['Feature'], plot_df['Time Sensitivity'], color=time_colors, alpha=0.8)
    axes[0].set_title('Impact on Completion TIME', fontsize=14, fontweight='bold', pad=15)
    axes[0].set_xlabel('Correlation with Duration', fontsize=12)
    axes[0].invert_xaxis()
    axes[0].axvline(0, color='black', linewidth=0.8)
    axes[0].grid(linestyle='--', alpha=0.5)
    
    # --- 右侧：Cost Sensitivity ---
    axes[1].barh(plot_df['Feature'], plot_df['Cost Sensitivity'], color=cost_colors, alpha=0.8)
    axes[1].set_title('Impact on Total COST', fontsize=14, fontweight='bold', pad=15)
    axes[1].set_xlabel('Correlation with Budget', fontsize=12)
    axes[1].axvline(0, color='black', linewidth=0.8)
    axes[1].grid(linestyle='--', alpha=0.5)
    
    # 隐藏右图的 Y轴刻度线
    axes[0].tick_params(axis='y', labelsize=12, pad=10)
    axes[1].tick_params(axis='y', left=False)
    
    # --- 添加数值标注 ---
    def add_labels(ax, values):
        for i, v in enumerate(values):
            offset = -0.01 if v >= 0 else 0.01
            ha = 'right' if v >= 0 else 'left'
            if ax == axes[0]: 
                offset = -0.01 if v >= 0 else 0.01
                ha = 'right' if v >= 0 else 'left'
                
            ax.text(v + offset, i, f"{v:.2f}", va='center', ha=ha, fontsize=10, fontweight='bold')

    add_labels(axes[0], plot_df['Time Sensitivity'])
    add_labels(axes[1], plot_df['Cost Sensitivity'])
    
    # 3. 全局标题
    plt.suptitle('Dual-Objective Sensitivity Analysis (The "Butterfly" Chart)', fontsize=16, fontweight='bold', y=0.98)
    
    # 保存
    save_path = os.path.join(save_dir, "butterfly_sensitivity.png")
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()

# ==========================================
# 5. 主程序 (Main Execution)
# ==========================================
if __name__ == "__main__":
    print(f"--- 🚀 Starting Advanced Monte Carlo Simulation ({CONFIG['SIMULATION_RUNS']} Runs) ---")
    
    data_records = []
    all_paths = []
    all_phase_years = []
    
    # 使用 tqdm 显示进度条
    for run in tqdm(range(CONFIG["SIMULATION_RUNS"]), desc="Simulating"):
        cost, time_val, path, metrics, phase_years_local = run_one_simulation(OPTIMAL_STRATEGY_X)
        
        # 记录单次运行的所有数据
        record = {
            "Total Cost (B)": cost / 1e9,
            "Time (Years)": time_val,
            "Rocket Failures": metrics["total_rocket_failures"],
            "SE Breakdowns": metrics["total_se_breakdowns"],
            "Disasters": metrics["total_disasters"],
            "Avg Weather Eff": metrics["avg_weather_efficiency"],
            "Avg Physics Eff": metrics["avg_physics_efficiency"]
        }
        data_records.append(record)
        all_paths.append(path)
        all_phase_years.append(phase_years_local)

    # 转换为 DataFrame 方便分析
    df_results = pd.DataFrame(data_records)
    
    # 计算平均 phase 切换年份
    all_phase_years = np.array(all_phase_years)
    avg_phase_years = np.mean(all_phase_years, axis=0)
    
    print(f"\n📍 Average Phase Switch Years (from {CONFIG['SIMULATION_RUNS']} runs):")
    print(f"   Phase I→II: Year {CONFIG['START_YEAR'] + avg_phase_years[1]:.1f}")
    print(f"   Phase II→III: Year {CONFIG['START_YEAR'] + avg_phase_years[2]:.1f}")

    # --- 统计输出 ---
    print("\n=== 📊 Strategic Insights ===")
    print(df_results[["Total Cost (B)", "Time (Years)"]].describe().T)
    
    prob_success = len(df_results[df_results["Time (Years)"] < 35]) / CONFIG["SIMULATION_RUNS"]
    print(f"\nProbability of completing within 35 years: {prob_success:.1%}")
    
    # --- 绘图 ---
    print("\nGenerating Visualizations...")
    
    # 1. 鲁棒性分析 (Fan Chart)
    plot_enhanced_fan_chart(all_paths, avg_phase_years)
    
    # 2. 敏感性分析 (Tornado Plot)
    plot_sensitivity_tornado(df_results)
    
    # 3. 联合分布 (Joint Plot)
    plot_joint_distribution(df_results)
    
    # 4. 蝴蝶龙卷风图 (Butterfly Sensitivity)
    plot_butterfly_sensitivity(df_results, save_dir=LOGS_DIR)
    
    print(f"\n✅ All plots saved to: {LOGS_DIR}")