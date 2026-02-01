import numpy as np
import matplotlib.pyplot as plt

def make_radar_chart():
    categories = ['Economic Cost', 'Time to Completion', 'CO2 Emissions', 'Ozone Depletion', 'Ocean Impact']
    N = len(categories)
    
    # 数据 (归一化到 0-1, 越小越好)
    # values_A: 纯火箭 (快，但贵且脏)
    values_A = [0.8, 0.2, 0.9, 0.9, 0.8] 
    # values_B: 纯电梯 (慢，但便宜且干净)
    values_B = [0.2, 0.9, 0.1, 0.1, 0.1]
    # values_C: 混合 (平衡)
    values_C = [0.3, 0.3, 0.3, 0.3, 0.2]
    
    # 闭合曲线
    values_A += values_A[:1]
    values_B += values_B[:1]
    values_C += values_C[:1]
    
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, polar=True)
    
    # Draw A
    ax.plot(angles, values_A, linewidth=2, linestyle='solid', label='Scenario A: All-Rocket')
    ax.fill(angles, values_A, 'b', alpha=0.1)
    
    # Draw B
    ax.plot(angles, values_B, linewidth=2, linestyle='solid', label='Scenario B: All-Elevator')
    ax.fill(angles, values_B, 'g', alpha=0.1)

    # Draw C
    ax.plot(angles, values_C, linewidth=2, linestyle='solid', label='Scenario C: Hybrid (Ours)')
    ax.fill(angles, values_C, 'r', alpha=0.2)
    
    plt.xticks(angles[:-1], categories)
    plt.title('Multi-Criteria Scenario Assessment')
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    plt.show()

make_radar_chart()