import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D 
import numpy as np
import os
import logging
import json
from datetime import datetime
from algorithm.nsga import NSGA2
from problem.problem_noenv import LunarLogisticsProblem
from problem.problem_env import LunarLogisticsProblem_env
from problem.integrated_problem import IntegratedLunarProblem

class NSGARunner:
    def __init__(self, log_dir="logs", with_env=False):
        self.with_env = with_env
        self.base_log_dir = log_dir
        if not os.path.exists(self.base_log_dir):
            os.makedirs(self.base_log_dir)

    def _setup_logger(self, log_path):
        logger = logging.getLogger(log_path)
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(message)s'))
            logger.addHandler(handler)
        return logger

    def execute_strategy(self, mode, configs, pop_size=None, max_gen=None, smooth=False, priority="balanced"):
        """
        核心集成方法：封装了从问题实例化到结果打印的全过程
        """
        # 1. 创建本次实验的独立文件夹
        timestamp = datetime.now().strftime('%m%d_%H%M')
        run_dir = os.path.join(self.base_log_dir, f"{mode}_{'env' if self.with_env else 'std'}_{timestamp}")
        os.makedirs(run_dir, exist_ok=True)
        logger = self._setup_logger(os.path.join(run_dir, "run.log"))

        # 2. 内部逻辑调度
        results = []
        if mode == 'integrated':
            p_size = pop_size or 150
            m_gen = max_gen or 300
            self.prob = IntegratedLunarProblem(stage_masses=[c['mass'] for c in configs], smooth=smooth)
            algo = NSGA2(self.prob, pop_size=p_size, integrated=True)
            results = self._run_core(algo, m_gen, run_dir, "Global", True, priority, logger)
        else:
            p_size = pop_size or 100
            m_gen = max_gen or 200
            for conf in configs:
                self.prob = LunarLogisticsProblem_env(stage_mass=conf['mass']) if self.with_env else LunarLogisticsProblem(stage_mass=conf['mass'])
                algo = NSGA2(self.prob, pop_size=p_size)
                # 分步模式下每个阶段追加结果
                res = self._run_core(algo, m_gen, run_dir, conf['tag'], False, conf['priority'], logger)
                results.extend(res)

        self._print_summary(results, mode, logger)
        return results

    def _run_core(self, algo, max_gen, run_dir, tag, integrated, priority, logger):
        """核心演化与还原逻辑"""
        logger.info(f"🚀 Running {tag}...")
        for g in range(1, max_gen + 1):
            pop, vals = algo.evolve()
            if g % 50 == 0:
                logger.info(f"  Gen {g:3d} | Econ: {np.min(vals[:,0]):.2e} | Time: {np.min(vals[:,1]):.2f}")

        # 绘图
        self._plot_pareto(vals, run_dir, tag)
        
        # 选点
        best_x = self._select_best(pop, vals, priority)
        
        # 还原
        if integrated:
            self._plot_roadmap(best_x, run_dir, tag)
            return self._recover_data_integrated(self.prob.stage_masses, best_x)
        else:
            return self._recover_data_single(best_x, tag)

    def _select_best(self, pop, vals, priority):
        min_v, max_v = vals.min(axis=0), vals.max(axis=0)
        norm_v = (vals - min_v) / (max_v - min_v + 1e-6)
        n_objs = vals.shape[1]
        
        if self.with_env and n_objs >= 3:
            w_map = {"time": [0.1, 0.7, 0.2], "balanced": [0.33, 0.33, 0.34], "cost": [0.7, 0.1, 0.2]}
        else:
            w_map = {"time": [0.2, 0.8], "balanced": [0.5, 0.5], "cost": [0.8, 0.2]}
            norm_v = norm_v[:, :2]
            
        w = np.array(w_map.get(priority, w_map["balanced"]))
        return pop[np.argmin(np.dot(norm_v, w))]

    # --- 辅助方法：物理还原 ---
    def _recover_data_single(self, x, tag):
        if self.with_env:
            econ, duration, env = self.prob.evaluate(x)
            return [{"tag": tag, "rf": x[0], "eu": x[1], "cost": econ, "duration": duration, "env": env}]
        else:
            econ, duration = self.prob.evaluate(x)
            return [{"tag": tag, "rf": x[0], "eu": x[1], "cost": econ, "duration": duration}]
        

    def _recover_data_integrated(self, masses, x):
        res = []
        tags = ["Stage_1", "Stage_2", "Stage_3"]

        for i in range(3):
            rf, eu = x[i*2], x[i*2+1]
            m = masses[i]
            
            if self.with_env:
                econ, duration, env = self.prob.calculate_total_costs(m, eu, rf)
                res.append({
                    "tag": tags[i], "rf": rf, "eu": eu, 
                    "cost": econ, "duration": duration, "env": env
                })
            else:
                econ, duration = self.prob.calculate_total_costs(m, eu, rf)
                res.append({
                    "tag": tags[i], "rf": rf, "eu": eu, 
                    "cost": econ, "duration": duration, "env": 0.0
                })
        return res

    # --- 绘图与总结 ---
    def _plot_pareto(self, vals, run_dir, tag):
        """
        整合版绘图逻辑：
        当 with_env 开启时，自动绘制 3D 全景图及三向 2D 投影图。
        """
        # --- 场景 1: 开启了环境指标且数据列数 >= 3 ---
        if self.with_env and vals.shape[1] >= 3:
            # 1. 绘制 3D 帕累托前沿图
            fig_3d = plt.figure(figsize=(10, 8))
            ax_3d = fig_3d.add_subplot(111, projection='3d')
            sc = ax_3d.scatter(
                vals[:, 0], vals[:, 1], vals[:, 2], 
                c=vals[:, 0], cmap='viridis', s=50, alpha=0.6, edgecolors='w', linewidth=0.5
            )
            ax_3d.set_xlabel('Economic Cost (10k USD)', fontsize=10)
            ax_3d.set_ylabel('Time Cost (Years)', fontsize=10)
            ax_3d.set_zlabel('Environmental Cost', fontsize=10)
            ax_3d.set_title(f'3D Pareto Front - {tag}', fontsize=12)
            plt.colorbar(sc, ax=ax_3d, label='Economic Intensity', pad=0.1)
            plt.savefig(os.path.join(run_dir, f"pareto_3d_{tag}.png"), dpi=300, bbox_inches='tight')
            plt.close()

            # 2. 绘制 2D 投影组合图 (三个视角：E-T, E-Env, T-Env)
            fig_proj, axes = plt.subplots(1, 3, figsize=(18, 5))
            labels_pairs = [
                ('Economic Cost', 'Time Cost'),
                ('Economic Cost', 'Environmental Cost'),
                ('Time Cost', 'Environmental Cost')
            ]
            idx_pairs = [(0, 1), (0, 2), (1, 2)]
            
            for ax, (xlabel, ylabel), (xi, yi) in zip(axes, labels_pairs, idx_pairs):
                ax.scatter(vals[:, xi], vals[:, yi], c='teal', alpha=0.6, s=40, edgecolors='k', linewidth=0.5)
                ax.set_xlabel(xlabel, fontsize=11)
                ax.set_ylabel(ylabel, fontsize=11)
                ax.grid(True, linestyle='--', alpha=0.5)
            
            plt.suptitle(f'Pareto Projections - {tag}', fontsize=14)
            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            plt.savefig(os.path.join(run_dir, f"pareto_projections_{tag}.png"), dpi=300)
            plt.close()

        # --- 场景 2: 标准 2 目标模式 ---
        else:
            plt.figure(figsize=(8, 6))
            plt.scatter(vals[:, 0], vals[:, 1], c='teal', alpha=0.6, edgecolors='k', s=45)
            plt.xlabel('Economic Cost (10k USD)', fontsize=11)
            plt.ylabel('Time Cost (Years)', fontsize=11)
            plt.title(f"Pareto Front (2D) - {tag}", fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.savefig(os.path.join(run_dir, f"pareto_2d_{tag}.png"), dpi=300)
            plt.close()
            
    def _plot_roadmap(self, x, run_dir, tag):
        fig, ax1 = plt.subplots()
        ax1.bar(['P1', 'P2', 'P3'], [x[0], x[2], x[4]], color='skyblue')
        ax2 = ax1.twinx()
        ax2.plot(['P1', 'P2', 'P3'], [x[1], x[3], x[5]], 'r-o')
        plt.savefig(os.path.join(run_dir, f"roadmap_{tag}.png"))
        plt.close()

    def _print_summary(self, results, mode, logger):
        logger.info("\n" + "="*85)
        logger.info(f"{'Phase':<15} | {'Rocket Freq':<12} | {'Elev Util':<10} | {'Cost(B)':<10} | {'Years':<8} | {'Env'}")
        logger.info("-" * 85)
        t_c, t_t, t_e = 0, 0, 0
        for r in results:
            logger.info(f"{r['tag']:<15} | {r['rf']:>12.2f} | {r['eu']:>10.2%} | {r['cost']/10000:>10.2f} | {r['duration']:>8.2f} | {r['env']:>10.2e}")
            t_c += r['cost']/10000; t_t += r['duration']; t_e += r['env']
        logger.info("-" * 85)
        logger.info(f"TOTAL | Cost: ${t_c:.2f}B | Time: {t_t:.1f}Y | Env: {t_e:.2e}")
        logger.info("="*85)