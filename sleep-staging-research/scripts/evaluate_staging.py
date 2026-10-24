#!/usr/bin/env python3
"""睡眠五分期评测：acc / macro-F1 / Cohen's κ / 逐类 F1 / 混淆矩阵。

标签约定 0=W 1=N1 2=N2 3=N3 4=REM。支持逐折汇总（mean±SD）。
输出 Markdown 主表 + 逐类 CSV + 混淆矩阵 CSV（报告模板见 references/metrics-protocol.md）。

用法:
  python scripts/evaluate_staging.py --true y_true.npy --pred y_pred.npy --out results
  python scripts/evaluate_staging.py --true y_true.npy --pred y_pred.npy --fold-ids ids.npy --out results
  # 逐折模式：ids.npy 与标签同长，取值 0..k-1 标记每个样本所属折（如按测试受试者分折）
也接受 .csv（单列，无表头）。
"""
import argparse
from pathlib import Path

import numpy as np
from sklearn.metrics import (accuracy_score, cohen_kappa_score, confusion_matrix,
                             f1_score, precision_score, recall_score)

STAGES = ["W", "N1", "N2", "N3", "REM"]


def load_arr(path: str, n_classes: int = 5) -> np.ndarray:
    p = Path(path)
    if p.suffix == ".npy":
        a = np.load(p)
    else:
        a = np.loadtxt(p, delimiter=",", dtype=np.int64).ravel()
    a = np.asarray(a).ravel().astype(np.int64)
    if n_classes and (a.min() < 0 or a.max() >= n_classes):
        raise SystemExit(f"{path}: 值越界 [{a.min()},{a.max()}]，应在 0..{n_classes - 1}"
                         + ("（标签 0=W 1=N1 2=N2 3=N3 4=REM）" if n_classes == 5 else "（折编号）"))
    return a


def fold_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    cm = confusion_matrix(y_true, y_pred, labels=list(range(5)))
    return {
        "acc": accuracy_score(y_true, y_pred) * 100,
        "mf1": f1_score(y_true, y_pred, average="macro", zero_division=0) * 100,
        "kappa": cohen_kappa_score(y_true, y_pred),
        "per_f1": f1_score(y_true, y_pred, average=None, labels=list(range(5)), zero_division=0) * 100,
        "recall": recall_score(y_true, y_pred, average=None, labels=list(range(5)), zero_division=0) * 100,
        "precision": precision_score(y_true, y_pred, average=None, labels=list(range(5)), zero_division=0) * 100,
        "support": cm.sum(axis=1),
        "cm": cm,
    }


def fmt(v, nd=1):
    return f"{v:.{nd}f}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--true", required=True, help="真值（.npy/.csv）")
    ap.add_argument("--pred", required=True, help="预测（.npy/.csv）")
    ap.add_argument("--fold-ids", help="可选：样本所属折（0..k-1），给出则逐折+汇总")
    ap.add_argument("--out", default="results", help="输出前缀（生成 .md/_per_class.csv/_confusion.csv）")
    ap.add_argument("--model-name", default="model", help="表中模型名")
    args = ap.parse_args()

    y_true, y_pred = load_arr(args.true), load_arr(args.pred)
    if len(y_true) != len(y_pred):
        raise SystemExit(f"长度不一致: true={len(y_true)} pred={len(y_pred)}")

    lines = [f"# 分期评测 · {args.model_name}", "",
             f"样本数 {len(y_true)}；标签 0=W 1=N1 2=N2 3=N3 4=REM；协议=按受试者划分", ""]
    header = "| 来源 | acc | MF1 | κ | " + " | ".join(f"{s}-F1" for s in STAGES) + " |"
    sep = "|---|---|---|---|" + "---|" * 5

    if args.fold_ids:
        ids = load_arr(args.fold_ids, n_classes=0)  # 折编号不受 5 类约束
        if len(ids) != len(y_true):
            raise SystemExit(f"fold-ids 长度 {len(ids)} != 标签长度 {len(y_true)}")
        rows, cms = [], []
        per_rows = []
        for f in sorted(set(ids.tolist())):
            m = fold_metrics(y_true[ids == f], y_pred[ids == f])
            rows.append((f"fold{f}", m))
            cms.append(m["cm"])
            per_rows.append((f, m["per_f1"], m["recall"], m["precision"], m["support"]))
        lines += [header, sep]
        for name, m in rows:
            lines.append(f"| {name} | {fmt(m['acc'])} | {fmt(m['mf1'])} | {fmt(m['kappa'], 3)} | "
                         + " | ".join(fmt(x) for x in m["per_f1"]) + " |")

        def ms(key, scale=1.0):
            v = np.array([m[key] for _, m in rows], dtype=float) * scale
            return f"{v.mean():.1f}±{v.std(ddof=1) if len(v) > 1 else 0:.1f}"

        mf1s = np.array([m["per_f1"] for _, m in rows], dtype=float)
        lines.append(f"| **mean±SD** | {ms('acc')} | {ms('mf1')} | "
                     f"{np.mean([m['kappa'] for _, m in rows]):.3f}±{np.std([m['kappa'] for _, m in rows], ddof=1) if len(rows) > 1 else 0:.3f} | "
                     + " | ".join(f"{mf1s[:, i].mean():.1f}±{mf1s[:, i].std(ddof=1) if len(rows) > 1 else 0:.1f}"
                                  for i in range(5)) + " |")
        cm_total = np.sum(cms, axis=0)
    else:
        m = fold_metrics(y_true, y_pred)
        per_rows = [("all", m["per_f1"], m["recall"], m["precision"], m["support"])]
        lines += [header, sep,
                  f"| {args.model_name} | {fmt(m['acc'])} | {fmt(m['mf1'])} | {fmt(m['kappa'], 3)} | "
                  + " | ".join(fmt(x) for x in m["per_f1"]) + " |"]
        cm_total = m["cm"]

    lines += ["", "混淆矩阵（行=真值，列=预测，单位 epoch）：", "",
              "| 真值\\预测 | " + " | ".join(STAGES) + " |", "|---|" + "---|" * 5]
    for i, row in enumerate(cm_total):
        lines.append(f"| {STAGES[i]} | " + " | ".join(str(int(x)) for x in row) + " |")
    lines += ["", "对照：人类评分者间一致率 79–86%（κ≈0.76），N1 一致性 63%（引用见 references/domain-facts.md）。"]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    Path(str(out) + ".md").write_text("\n".join(lines), encoding="utf-8")

    import csv
    with open(str(out) + "_per_class.csv", "w", newline="", encoding="utf-8") as fcsv:
        w = csv.writer(fcsv)
        w.writerow(["source", "metric"] + STAGES)
        for src, f1s, recs, precs, sup in per_rows:
            w.writerow([src, "F1"] + [f"{x:.2f}" for x in f1s])
            w.writerow([src, "recall"] + [f"{x:.2f}" for x in recs])
            w.writerow([src, "precision"] + [f"{x:.2f}" for x in precs])
            w.writerow([src, "support"] + [int(x) for x in sup])
    with open(str(out) + "_confusion.csv", "w", newline="", encoding="utf-8") as fcsv:
        w = csv.writer(fcsv)
        w.writerow(["true\\pred"] + STAGES)
        for i, row in enumerate(cm_total):
            w.writerow([STAGES[i]] + [int(x) for x in row])

    print("\n".join(lines))
    print(f"\n已写出: {out}.md / {out}_per_class.csv / {out}_confusion.csv")


if __name__ == "__main__":
    main()
