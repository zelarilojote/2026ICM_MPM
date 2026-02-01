import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 0. 学术绘图风格设置 (Academic Style)
# ==========================================
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'figure.dpi': 300,
    'lines.linewidth': 2.5,
    'axes.spines.top': False,
    'axes.spines.right': False,
})

def plot_strategic_roadmap():
    # ==========================================
    # 1. 输入你的优化结果 (决策变量)
    # ==========================================
    # 格式: (火箭年发射频率, 电梯年利用率 0-1.0)
    # 请填入你模型跑出来的最优解
    OPTIMIZED_STRATEGIES = [
        (4500, 0.95),  # Stage 1 (Core): 疯狂发火箭 + 电梯全开
        (200, 1.00),   # Stage 2 (Expand): 火箭几乎停掉，全靠电梯
        (50, 0.60)     # Stage 3 (Sustain): 进入低功耗维护模式
    ]
    
    # 阶段目标 (累积质量，单位：吨)
    STAGE_TARGETS = [5e7, 9e7, 1e8] # 假设总目标 1.2亿吨 (5000w -> 4000w -> 3000w)
    
    # 基础参数 (单位：吨)
    ROCKET_CAPACITY_PER_LAUNCH = 150.0  # 单枚火箭运力
    # 假设电梯满负荷年运力 (3座电梯 * 17.9万吨 * 效率因子)
    ELEVATOR_MAX_ANNUAL_CAPACITY = 179000.0 * 3 * 0.9 

    # ==========================================
    # 2. 模拟时间推移
    # ==========================================
    years = []
    cumulative_rocket = []
    cumulative_elevator = []
    
    current_year = 2050
    total_mass_rocket = 0
    total_mass_elevator = 0
    total_mass = 0
    
    stage_transition_years = [] # 记录阶段切换年份
    current_stage = 0
    
    # 初始点
    years.append(current_year)
    cumulative_rocket.append(0)
    cumulative_elevator.append(0)
    
    while total_mass < STAGE_TARGETS[-1]:
        # 获取当前阶段的策略
        strat_rocket_freq, strat_elev_util = OPTIMIZED_STRATEGIES[current_stage]
        
        # 计算当年的运量
        year_rocket_mass = strat_rocket_freq * ROCKET_CAPACITY_PER_LAUNCH
        year_elev_mass = strat_elev_util * ELEVATOR_MAX_ANNUAL_CAPACITY
        
        # 累加
        total_mass_rocket += year_rocket_mass
        total_mass_elevator += year_elev_mass
        total_mass = total_mass_rocket + total_mass_elevator
        
        current_year += 1
        
        # 记录数据用于绘图
        years.append(current_year)
        cumulative_rocket.append(total_mass_rocket)
        cumulative_elevator.append(total_mass_elevator)
        
        # 检查是否切换阶段
        if current_stage < 2:
            if total_mass >= STAGE_TARGETS[current_stage]:
                stage_transition_years.append(current_year)
                current_stage += 1
                
    # ==========================================
    # 3. 绘制 O奖级 堆叠面积图
    # ==========================================
    plt.figure(figsize=(12, 7))
    
    # 转换为 Million Tons (百万吨) 方便显示
    y_rocket = np.array(cumulative_rocket) / 1e6
    y_elev = np.array(cumulative_elevator) / 1e6
    
    # 绘制堆叠图
    # 顺序：先画电梯(下)，再画火箭(上)
    # 注意：stackplot 的输入是各层的"增量"，不是累积量。
    # 但我们这里 y_elev 和 y_rocket 本身就是累积量，且需要堆叠。
    # 修正：Matplotlib stackplot 需要 y轴的分量。
    # 我们需要展示的是：总运量中，多少来自电梯，多少来自火箭。
    
    plt.stackplot(years, y_elev, y_rocket, 
                  labels=['Space Elevator Transport', 'Rocket Launch Transport'],
                  colors=['#1f77b4', '#ff7f0e'], 
                  alpha=0.85)
    
    # --- O奖细节装饰 ---
    
    # 1. 绘制阶段分割线
    # 计算分界线标注的y位置（靠近顶部）
    split_label_y = (total_mass / 1e6) * 0.95
    for idx, year in enumerate(stage_transition_years, start=1):
        plt.axvline(x=year, color='black', linestyle='--', linewidth=2, alpha=0.7)
        plt.text(year + 0.5, split_label_y, f'Phase {idx}→{idx+1}\n({year})',
                 color='black', fontsize=10, rotation=90, va='top')

    # 2. 标注区域含义
    # 在图中间找个位置写字
    mid_idx = len(years) // 2
    # 电梯层标注
    plt.text(years[mid_idx], y_elev[mid_idx]/2, 'Base Load:\nSpace Elevator', 
             ha='center', va='center', color='white', fontweight='bold', fontsize=12)
    # 火箭层标注
    plt.text(years[5], y_elev[5] + y_rocket[5]/2, 'Initial Burst:\nRocket Fleet', 
             ha='left', va='center', color='white', fontweight='bold', fontsize=10)

    # 3. 装饰坐标轴
    plt.xlim(2050, years[-1])
    plt.ylim(0, 100)  # 1亿吨 = 100 Mt
    plt.xlabel('Year', fontsize=12, fontweight='bold')
    plt.ylabel('Cumulative Transported Mass (Million Tons)', fontsize=12, fontweight='bold')
    
    plt.title('Strategic Logistics Roadmap: Cumulative Mass Delivery (2050-2080)', fontsize=14, fontweight='bold', pad=20)
    plt.legend(loc='upper left', frameon=True, shadow=True)
    plt.grid(True, linestyle='--', alpha=0.3)
    
    # 4. 关键数据标注
    final_year = years[-1]
    final_mass = total_mass / 1e6
    plt.scatter([final_year], [final_mass], color='red', zorder=10)
    plt.annotate(f'Completion: {final_year}\nTotal: {final_mass:.1f} Mt', 
                 (final_year, final_mass), 
                 xytext=(-80, 10), textcoords='offset points',
                 arrowprops=dict(arrowstyle="->", color='red'))

    plt.tight_layout()
    plt.show()

# ==========================================
# 水资源模型辅助函数
# ==========================================

def get_annual_makeup(recycling_rate):
    """计算年度补水需求"""
    POPULATION = 100000
    DAILY_USE = 45.0
    total_daily = POPULATION * DAILY_USE
    daily_loss = total_daily * (1 - recycling_rate)
    return daily_loss * 365 / 1000

def estimate_cost(mass_tons):
    """估算成本 (运费 50万美元/吨 -> 0.0005 Billion/ton)"""
    return mass_tons * 0.0005

def plot_water_analysis():
    """绘制水资源策略对比图"""
    # 参数
    RECYCLING_RATE = 0.96
    ISRU_EFFICIENCY = 150.0
    
    # 核心数据
    mass_water_strategy = get_annual_makeup(RECYCLING_RATE)
    mass_isru_strategy = mass_water_strategy / ISRU_EFFICIENCY
    cost_water_annual = estimate_cost(mass_water_strategy)
    cost_isru_setup = estimate_cost(mass_isru_strategy)
    
    # 创建画布
    fig = plt.figure(figsize=(15, 10))
    gs = fig.add_gridspec(2, 2)
    
    # === 图 1: 载荷对比 (Log Scale) ===
    ax1 = fig.add_subplot(gs[0, 0])
    
    categories = ['Strategy A:\nDirect Water Supply', 'Strategy B:\nISRU Equipment']
    values = [mass_water_strategy, mass_isru_strategy]
    colors = ['#4A90E2', '#F5A623']
    
    bars = ax1.bar(categories, values, color=colors, width=0.5, edgecolor='black', alpha=0.9)
    ax1.set_yscale('log')
    ax1.set_ylim(10, 200000)
    
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height * 1.1,
                 f'{int(val):,} tons',
                 ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    ax1.annotate(f'Payload Reduced by {mass_water_strategy/mass_isru_strategy:.0f}x\n(99.3% Reduction)',
                 xy=(1, mass_isru_strategy), xytext=(0.5, 20000),
                 arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=-0.2", color='#D0021B', lw=2),
                 color='#D0021B', fontweight='bold', ha='center')
    
    ax1.set_title('(a) Annual Logistics Payload Requirement', fontweight='bold')
    ax1.set_ylabel('Mass (Tons) - Logarithmic Scale')
    ax1.grid(axis='y', linestyle='--', alpha=0.5)

    # === 图 2: 敏感性分析 ===
    ax2 = fig.add_subplot(gs[0, 1])
    
    efficiencies = np.linspace(0.85, 0.99, 100)
    makeup_needs = [get_annual_makeup(eff) for eff in efficiencies]
    
    ax2.plot(efficiencies*100, makeup_needs, color='#2C3E50', linewidth=3)
    ax2.scatter([96], [get_annual_makeup(0.96)], color='#D0021B', s=100, zorder=5, label='Current Model (96%)')
    ax2.fill_between(efficiencies*100, 0, makeup_needs, where=(efficiencies < 0.90), 
                     color='#E74C3C', alpha=0.2, label='High Logistics Risk Zone (<90%)')
    
    ax2.set_title('(b) Impact of ECLSS Efficiency on Supply Needs', fontweight='bold')
    ax2.set_xlabel('Recycling Efficiency (%)')
    ax2.set_ylabel('Required Annual Water Makeup (Tons)')
    ax2.legend()
    ax2.grid(True, linestyle='--', alpha=0.5)

    # === 图 3: 长期成本对比 ===
    ax3 = fig.add_subplot(gs[1, :])
    
    years = np.arange(0, 11)
    cum_cost_water = years * cost_water_annual
    maintenance_cost = cost_isru_setup * 0.05
    cum_cost_isru = np.full_like(years, cost_isru_setup, dtype=float) + years * maintenance_cost
    cum_cost_isru[0] = cost_isru_setup
    
    ax3.plot(years, cum_cost_water, label='Strategy A: Direct Earth Supply', color='#4A90E2', linestyle='--', linewidth=2.5)
    ax3.plot(years, cum_cost_isru, label='Strategy B: ISRU (Mining)', color='#F5A623', linewidth=3)
    
    ax3.scatter([0.2], [cost_isru_setup], color='black', s=100, zorder=10)
    ax3.annotate('Immediate Break-even\n(ROI < 1 Month)', 
                 xy=(0.2, cost_isru_setup), xytext=(2, cost_isru_setup + 5),
                 arrowprops=dict(facecolor='black', arrowstyle='->'),
                 fontsize=12, fontweight='bold')
    
    ax3.fill_between(years, cum_cost_isru, cum_cost_water, where=(cum_cost_water > cum_cost_isru),
                     color='#2ECC71', alpha=0.1, label='Accumulated Economic Savings')

    ax3.set_title('(c) 10-Year Cumulative Cost Projection', fontweight='bold')
    ax3.set_xlabel('Years of Operation')
    ax3.set_ylabel('Cumulative Cost (Billion USD)')
    ax3.legend(loc='upper left')
    ax3.set_xlim(0, 10)
    ax3.grid(True, linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig('water_strategy_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'water':
        plot_water_analysis()
    else:
        plot_strategic_roadmap()