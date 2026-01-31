import matplotlib.pyplot as plt
import numpy as np
import time
import os
import logging

class NSGARunner:
    def __init__(self, algo, max_gen=100, verbose=True, log_dir="log", stage_tag="Stage"):
        self.algo = algo
        self.max_gen = max_gen
        self.verbose = verbose
        self.log_dir = log_dir
        self.stage_tag = stage_tag
        
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        self.logger = self._setup_logging()

    def _setup_logging(self):
        log_file = os.path.join(self.log_dir, f"run_{self.stage_tag}.log")
        logger = logging.getLogger(f"NSGARunner_{self.stage_tag}")
        logger.setLevel(logging.INFO)
        
        if logger.hasHandlers():
            logger.handlers.clear()

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        logger.addHandler(file_handler)

        if self.verbose:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter('%(message)s'))
            logger.addHandler(console_handler)
        return logger

    def run(self):
        start_time = time.time()
        self.logger.info("="*50)
        self.logger.info(f"🚀 {self.stage_tag} START. Target: {self.algo.prob.stage_mass} Tons")
        
        final_vals = None
        for g in range(1, self.max_gen + 1):
            pop, final_vals = self.algo.evolve()
            
            if g % 50 == 0 or g == 1:
                min_cost = np.min(final_vals[:, 0])
                min_time = np.min(final_vals[:, 1])
                self.logger.info(f"[{self.stage_tag}] Gen {g:3d} | Min Cost: {min_cost:.2e} | Min Time: {min_time:.2f}Y")

        elapsed = time.time() - start_time
        self.logger.info(f"✅ {self.stage_tag} COMPLETED in {elapsed:.1f}s")
        
        self.plot_pareto(final_vals, self.stage_tag)
        return self.algo.population, final_vals

    def plot_pareto(self, vals, tag):
        plt.figure(figsize=(10, 6))
        # 转换坐标轴单位：万美元 -> 亿美元 (可选)
        plt.scatter(vals[:, 0], vals[:, 1], c='blue', alpha=0.6, edgecolors='k')
        
        plt.title(f'Pareto Front: Economic vs Time ({tag})')
        plt.xlabel('Total Economic Cost (Wan USD)')
        plt.ylabel('Total Time Duration (Years)')
        plt.grid(True, linestyle='--', alpha=0.5)
        
        img_path = os.path.join(self.log_dir, f"pareto_{tag}.png")
        plt.savefig(img_path)
        plt.close() # 必须关闭，防止下一次绘图重叠