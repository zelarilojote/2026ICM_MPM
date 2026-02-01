# 2026ICM_MPM

2026 ICM problem B

## run in seperate way

```bash
python run.py --mode separate --pop-size 120 --max-gen 200
```

## run in integrated way

```bash
python run.py --mode separate --stage-masses 2e7,6e7,2e7 --priorities time,balanced,cost
```
