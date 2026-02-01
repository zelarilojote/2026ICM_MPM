import argparse
from runner import NSGARunner

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['integrated', 'separate'], default='integrated')
    parser.add_argument('--with-env', action='store_true')
    parser.add_argument('--smooth', action='store_true')
    parser.add_argument('--pop', type=int)
    parser.add_argument('--gen', type=int)
    args = parser.parse_args()

    # 分阶段任务质量配置
    configs = [
        {"mass": 2e7, "priority": "time", "tag": "Stage_1"},
        {"mass": 6e7, "priority": "balanced", "tag": "Stage_2"},
        {"mass": 2e7, "priority": "cost", "tag": "Stage_3"}
    ]

    # 一键启动
    runner = NSGARunner(with_env=args.with_env)
    runner.execute_strategy(
        mode=args.mode,
        configs=configs,
        pop_size=args.pop,
        max_gen=args.gen,
        smooth=args.smooth
    )

if __name__ == "__main__":
    main()