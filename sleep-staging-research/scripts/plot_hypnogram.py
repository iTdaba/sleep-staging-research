#!/usr/bin/env python3
"""hypnogram 绘图：真值 vs 预测（错误处标红点），可选叠加连续深度曲线。

标签约定 0=W 1=N1 2=N2 3=N3 4=REM；深度值 s∈[0,1]（0=清醒，1=最深）。
用法:
  python scripts/plot_hypnogram.py --true y_true.npy --pred y_pred.npy --out hyp.png
  python scripts/plot_hypnogram.py --true y_true.npy --pred y_pred.npy --depth s.npy --out hyp.png
  可选 --start-hour 0（时间轴起点）--title "..." --dpi 150
"""
import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

STAGES = ["W", "N1", "N2", "N3", "REM"]
COLORS = {"true": "#1f77b4", "pred": "#ff7f0e", "depth": "#2ca02c"}


def load_arr(path: str, dtype=np.int64) -> np.ndarray:
    a = np.load(path) if path.endswith(".npy") else np.loadtxt(path, delimiter=",")
    return np.asarray(a).ravel().astype(dtype)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--true", required=True)
    ap.add_argument("--pred", help="预测标签；缺省则只画真值")
    ap.add_argument("--depth", help="连续深度 s∈[0,1]，同长；给出则叠加子图")
    ap.add_argument("--out", required=True, help="输出 PNG 路径")
    ap.add_argument("--start-hour", type=float, default=0.0, help="时间轴起点（小时）")
    ap.add_argument("--title", default="Hypnogram")
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args()

    y_true = load_arr(args.true)
    n = len(y_true)
    t = (np.arange(n) * 30 / 3600.0) + args.start_hour  # 小时
    y_pred = load_arr(args.pred) if args.pred else None
    depth = load_arr(args.depth, dtype=np.float64) if args.depth else None
    if y_pred is not None and len(y_pred) != n:
        raise SystemExit("pred 与 true 长度不一致")
    if depth is not None and len(depth) != n:
        raise SystemExit("depth 与 true 长度不一致")

    n_rows = 2 if depth is not None else 1
    fig, axes = plt.subplots(n_rows, 1, figsize=(14, 2.2 * n_rows + 0.8), sharex=True,
                             gridspec_kw={"height_ratios": [3, 1.2] if depth is not None else [1]})
    ax = axes[0] if depth is not None else axes

    where = "post"
    ax.step(t, y_true, where=where, color=COLORS["true"], lw=1.2, label="true")
    if y_pred is not None:
        ax.step(t, y_pred - 0.06, where=where, color=COLORS["pred"], lw=0.9, alpha=0.85, label="pred")
        err = y_pred != y_true
        ax.scatter(t[err], y_true[err] + 0.18, marker="x", s=14, color="red", zorder=3,
                   label=f"error ({err.mean() * 100:.1f}%)")
    ax.set_yticks(range(5))
    ax.set_yticklabels(STAGES)
    ax.set_ylim(-0.5, 4.9)
    ax.set_ylabel("stage")
    ax.set_title(args.title)
    ax.legend(loc="upper right", fontsize=8, ncol=3, framealpha=0.5)
    ax.grid(axis="y", ls=":", alpha=0.4)

    if depth is not None:
        axes[1].plot(t, depth, color=COLORS["depth"], lw=1.0)
        axes[1].set_ylabel("depth s∈[0,1]")
        axes[1].set_ylim(-0.02, 1.02)
        axes[1].grid(ls=":", alpha=0.4)
        axes[1].set_xlabel("time (h)")
    else:
        ax.set_xlabel("time (h)")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=args.dpi)
    print(f"已保存 {out}（{n} epochs = {n * 30 / 3600:.1f} h）")


if __name__ == "__main__":
    main()
