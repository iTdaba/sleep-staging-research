#!/usr/bin/env python3
"""依赖检查：睡眠分期科研 skill 运行环境。

用法: python scripts/check_env.py
核心依赖: numpy pandas scikit-learn matplotlib
可选依赖: mne（sleepedf_prepare.py 需要）
"""
import sys

REQUIRED = ["numpy", "pandas", "sklearn", "matplotlib"]
OPTIONAL = {"mne": "sleepedf_prepare.py 需要", "edfio": "生成/导出 EDF 需要", "yasa": "快速特征法基线（可选）"}


def main() -> int:
    ok = True
    print("Python:", sys.version.split()[0])
    for mod in REQUIRED:
        try:
            m = __import__(mod)
            print(f"  [OK]  {mod:12s} {getattr(m, '__version__', '?')}")
        except ImportError:
            print(f"  [缺失] {mod:12s} → pip install {mod}")
            ok = False
    for mod, why in OPTIONAL.items():
        try:
            m = __import__(mod)
            print(f"  [OK]  {mod:12s} {getattr(m, '__version__', '?')}（{why}）")
        except ImportError:
            print(f"  [--]  {mod:12s} 未安装（{why}，可跳过）")
    if not ok:
        print("\n核心依赖缺失，请先安装。")
        return 1
    print("\n环境就绪。标签约定: 0=W 1=N1 2=N2 3=N3 4=REM")
    return 0


if __name__ == "__main__":
    sys.exit(main())
