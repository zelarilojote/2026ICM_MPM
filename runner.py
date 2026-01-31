import matplotlib.pyplot as plt
import numpy as np
import time
import os
import logging

class NSGARunner:
    def __init__(self, algo, max_gen=100, verbose=True, log_dir="log"):
        self.algo = algo
        self.max_gen = max_gen
        self.verbose = verbose
        self.log_dir = log_dir
        
        # 1. 自动创建日志目录
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        # 2. 配置日志记录器
        self.logger = self._setup_logging()

    def _setup_logging(self):
        # 以当前时间命名日志文件
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(self.log_dir, f"run_{timestamp}.log")
        
        logger = logging.getLogger("NSGARunner")
        logger.setLevel(logging.INFO)
        
        # 清除已有的 handler (防止重复打印)
        if logger.hasHandlers():
            logger.handlers.clear()

        # 文件处理器 (写入 log 文件)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # 控制台处理器 (如果 verbose 为 True)
        if self.verbose:
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter('%(message)s') # 控制台保持简洁
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
            
        return logger

    def run(self):
        start_time = time.time()
        self.logger.info("="*50)
        self.logger.info(f"🚀 Runner started. Problem: {self.algo.prob.__class__.__name__}")
        self.logger.info(f"Target Cargo: {self.algo.prob.target_cargo/1e6:.1f}M Tons | Max Gen: {self.max_gen}")
        self.logger.info("="*50)
        
        final_vals = None
        for g in range(1, self.max_gen + 1):
            _, final_vals = self.algo.evolve()
            
            if g % 20 == 0 or g == 1:
                elapsed = time.time() - start_time
                min_cost = np.min(final_vals[:, 0])
                # 同时记录到文件和屏幕
                self.logger.info(f"Gen {g:3d}/{self.max_gen} | Min Cost: {min_cost:.4e} | Elapsed: {elapsed:.1f}s")

        total_time = time.time() - start_time
        self.logger.info("="*50)
        self.logger.info(f"✅ Optimization Finished in {total_time:.2f}s")
        self.logger.info(f"Final Pareto Solutions: {len(final_vals)}")
        
        # 保存最后一代的数据快照 (CSV)
        self._save_results(final_vals)
        
        self.plot_pareto(final_vals)
        return self.algo.population, final_vals

    def _save_results(self, vals):
        """将最终的帕累托前沿值存入文本，方便论文引用"""
        res_file = os.path.join(self.log_dir, f"pareto_results_{time.strftime('%H%M%S')}.csv")
        np.savetxt(res_file, vals, delimiter=",", header="Cost,TimeRisk,Smoothness", comments='')
        self.logger.info(f"💾 Final values saved to {res_file}")

    def plot_pareto(self, vals):
        plt.figure(figsize=(10, 6))
        # 绘制散点图，颜色映射到平滑度（第三个目标）
        sc = plt.scatter(vals[:, 0], vals[:, 1], c=vals[:, 2], cmap='viridis', alpha=0.7)
        plt.colorbar(sc, label='Timeline Smoothness (Lower is Better)')
        
        plt.title('Final Pareto Front: Multi-Stage Integration')
        plt.xlabel('Adjusted Economic Cost (Phase-weighted)')
        plt.ylabel('Adjusted Time Efficiency Index')
        plt.grid(True, linestyle='--', alpha=0.6)
        
        # 自动保存图片
        img_path = os.path.join(self.log_dir, f"pareto_plot_{time.strftime('%H%M%S')}.png")
        plt.savefig(img_path)
        self.logger.info(f"📊 Pareto plot saved to {img_path}")
        plt.show()