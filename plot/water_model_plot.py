import matplotlib.pyplot as plt
import matplotlib.patches as patches

def plot_lunar_water_schematic():
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.axis('off')
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    
    # 定义样式
    box_props = dict(boxstyle="round,pad=0.4", fc="white", ec="black", lw=2)
    arrow_props = dict(facecolor='#2C3E50', shrink=0.05, width=2, headwidth=8)
    
    # --- 1. 绘制核心组件 (Nodes) ---
    
    # ISRU (代替雨水收集)
    ax.text(2, 6, "Lunar South Pole\n(Ice Deposits)", ha="center", va="center", fontsize=11, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.4", fc="#D6EAF8", ec="#2980B9", lw=2))
    
    ax.text(2, 4, "ISRU Thermal\nMining Rig", ha="center", va="center", fontsize=11, fontweight='bold',
            bbox=dict(boxstyle="square,pad=0.4", fc="#FCF3CF", ec="#F39C12", lw=2))

    # 基地内部循环 (代替家庭用水)
    ax.text(8, 6, "Habitat Dome\n(Crew & Plants)", ha="center", va="center", fontsize=11, fontweight='bold',
            bbox=dict(boxstyle="circle,pad=0.5", fc="#D5F5E3", ec="#27AE60", lw=2))

    # 水处理中心 (代替过滤器)
    ax.text(5, 2, "ECLSS\nWater Processor\nAssembly (WPA)", ha="center", va="center", fontsize=11, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.5", fc="#E8DAEF", ec="#8E44AD", lw=2))

    # 储水罐 (代替水井)
    ax.text(10, 2, "Potable\nWater Storage", ha="center", va="center", fontsize=11, fontweight='bold',
            bbox=dict(boxstyle="round4,pad=0.5", fc="#AED6F1", ec="#3498DB", lw=2))

    # --- 2. 绘制连接流向 (Arrows) ---
    
    # ISRU -> Processor (Makeup Water)
    ax.annotate("", xy=(2, 4.6), xytext=(2, 5.5), arrowprops=arrow_props) # Ice -> Mining
    ax.annotate("", xy=(3.8, 2.5), xytext=(2, 3.5), arrowprops=arrow_props) # Mining -> ECLSS
    ax.text(2.5, 3, "Extracted Water\n(Makeup)", fontsize=9, rotation=-25)

    # Habitat -> Processor (Grey Water)
    ax.annotate("", xy=(5, 3), xytext=(7.2, 5.2), arrowprops=dict(facecolor='#7F8C8D', shrink=0.05, width=2, headwidth=8))
    ax.text(6.5, 4, "Urine / Humidity\n(Recycling)", fontsize=9, color='#7F8C8D', rotation=35)

    # Processor -> Storage (Clean Water)
    ax.annotate("", xy=(9, 2), xytext=(6.5, 2), arrowprops=dict(facecolor='#3498DB', shrink=0.05, width=3, headwidth=10))
    ax.text(7.8, 2.2, "Purified", fontsize=9, color='#3498DB', ha='center')

    # Storage -> Habitat (Supply)
    ax.annotate("", xy=(8.5, 5.2), xytext=(10, 2.8), arrowprops=dict(facecolor='#3498DB', shrink=0.05, width=2, headwidth=8))
    ax.text(9.8, 4, "Supply", fontsize=9, color='#3498DB', rotation=-50)

    # --- 3. 装饰 ---
    ax.set_title("Figure 3: Integrated Lunar Water Management System (ISRU + ECLSS)", fontsize=14, fontweight='bold', y=0.95)
    
    # 标注虚线框 (System Boundary)
    rect = patches.Rectangle((3.5, 0.5), 8, 7, linewidth=1, edgecolor='gray', facecolor='none', linestyle='--')
    ax.add_patch(rect)
    ax.text(11, 1, "Closed-Loop Boundary", fontsize=10, color='gray', ha='right')

    plt.tight_layout()
    plt.show()

plot_lunar_water_schematic()