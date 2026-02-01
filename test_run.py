from problem.test_problem import TestProblem3Obj
from algorithm.nsga import NSGA2
from runner import NSGARunner

def test_run():
    # 实例化测试问题
    problem = TestProblem3Obj()
    
    # 初始化算法
    algo = NSGA2(problem=problem, pop_size=100)
    
    # 运行
    runner = NSGARunner(algo, max_gen=100, stage_tag="3Obj_Test")
    pop, vals = runner.run()
    
    print("\n测试运行完成。")
    print(f"帕累托解集大小: {len(vals)}")
    print(f"最优解样例 (f1, f2, f3): \n{vals[0]}")

if __name__ == "__main__":
    test_run()