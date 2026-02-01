import numpy as np
import matplotlib.pyplot as plt

# 数据生成 (示例)
years = np.arange(2050, 2100)
n_years = len(years)

# 场景 A: 纯火箭 (排放随时间线性或指数增长)
emissions_rocket_only = np.cumsum(np.random.uniform(100, 120, n_years))

# 场景 B: 混合模式 (前期有建设排放，后期排放骤降)
# 1. 电梯建设排放 (集中在前 10 年)
const_emissions = np.zeros(n_years)
const_emissions[:10] = 50  # 建设期高排放

# 2. 火箭排放 (前期高，后期被电梯替代)
ops_emissions = np.zeros(n_years)
ops_emissions[:15] = 100 # 前期依靠火箭
ops_emissions[15:] = 5   # 后期只有少量火箭

# 累积计算
cumulative_hybrid = np.cumsum(const_emissions + ops_emissions)

# 绘图
plt.figure(figsize=(10, 6))

# 画纯火箭的虚线 (Baseline)
plt.plot(years, emissions_rocket_only, 'k--', label='Baseline (All-Rocket)', linewidth=2)

# 画混合模式的堆叠图
plt.fill_between(years, 0, np.cumsum(const_emissions), color='#1f77b4', alpha=0.6, label='Elevator Construction')
plt.fill_between(years, np.cumsum(const_emissions), cumulative_hybrid, color='#d62728', alpha=0.6, label='Rocket Operations')

# 标注 "减排红利"
plt.fill_between(years, cumulative_hybrid, emissions_rocket_only, color='green', alpha=0.1, hatch='//', label='Avoided Emissions')

plt.xlabel('Year')
plt.ylabel('Cumulative CO2 Emissions (Million Tons)')
plt.title('Environmental Impact: Hybrid Strategy vs. Baseline')
plt.legend(loc='upper left')
plt.grid(True, linestyle='--', alpha=0.5)
plt.show()