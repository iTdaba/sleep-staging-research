#!/usr/bin/env python3
"""按受试者的 k 折交叉验证划分（协议红线的代码化）。

同一受试者的所有夜必须落在同一折（Sleep-EDF 每人 2 夜，按夜划分即泄漏）。
输出 JSON：{k, seed, val_per_fold, folds: [{fold, test, val}], all_subjects}
程序内置断言：受试者跨折即报错退出。

用法:
  python scripts/cv_split.py --subjects-file subjects.txt --k 10 --out folds.json
  python scripts/cv_split.py --npz-dir epochs/ --k 10 --val-per-fold 7 --out folds.json
subjects.txt 每行一个受试者号；--npz-dir 从文件名 SC4xxx*.npz 提取受试者号。
"""
import argparse
import json
import re
import sys
from pathlib import Path


def collect_subjects(args: argparse.Namespace) -> list[str]:
    if args.subjects_file:
        subs = [ln.strip() for ln in Path(args.subjects_file).read_text().splitlines() if ln.strip()]
    elif args.npz_dir:
        subs = []
        for f in sorted(Path(args.npz_dir).glob("*.npz")):
            m = re.search(r"(SC\d{4}|\d{2,6})", f.stem)
            if m:
                subs.append(m.group(1))
            else:
                sys.exit(f"无法从文件名提取受试者号: {f.name}（请改用 --subjects-file）")
    else:
        sys.exit("需要 --subjects-file 或 --npz-dir 之一")
    if len(subs) < args.k:
        sys.exit(f"受试者数 {len(subs)} < k={args.k}")
    return sorted(set(subs))


def make_folds(subjects: list[str], k: int, seed: int, val_per_fold: int) -> list[dict]:
    import random

    rng = random.Random(seed)
    shuffled = subjects[:]
    rng.shuffle(shuffled)
    folds = [shuffled[i::k] for i in range(k)]
    out = []
    for i, test in enumerate(folds):
        train = [s for j, f in enumerate(folds) if j != i for s in f]
        rng2 = random.Random(seed + i)  # 每折验证集独立可复现
        pool = train[:]
        rng2.shuffle(pool)
        val = sorted(pool[:val_per_fold]) if val_per_fold > 0 else []
        out.append({"fold": i, "test": sorted(test), "val": val,
                    "train": sorted(s for s in train if s not in val)})
    # 协议断言：任一受试者只出现在一个 test 折；val ⊂ train 补集；无 train/test 交集
    seen = [s for f in out for s in f["test"]]
    assert sorted(seen) == sorted(subjects), "受试者在 test 折间丢失或重复"
    for f in out:
        assert not (set(f["train"]) & set(f["test"])), f"fold {f['fold']} 训练/测试泄漏"
        assert not (set(f["val"]) & set(f["test"])), f"fold {f['fold']} 验证/测试泄漏"
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--subjects-file", help="每行一个受试者号")
    ap.add_argument("--npz-dir", help="从 npz 文件名提取受试者号")
    ap.add_argument("--k", type=int, default=10, help="折数（默认 10，EDF-78 惯例）")
    ap.add_argument("--val-per-fold", type=int, default=0,
                    help="每折从训练受试者中留 N 人做验证（EDF-78 惯例 7）")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", required=True, help="输出 JSON 路径")
    args = ap.parse_args()

    subjects = collect_subjects(args)
    folds = make_folds(subjects, args.k, args.seed, args.val_per_fold)
    payload = {"k": args.k, "seed": args.seed, "val_per_fold": args.val_per_fold,
               "n_subjects": len(subjects), "folds": folds, "all_subjects": sorted(subjects)}
    Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    sizes = [len(f["test"]) for f in folds]
    print(f"{len(subjects)} 受试者 → {args.k} 折（test 规模 {min(sizes)}–{max(sizes)}），已断言无跨折泄漏 → {args.out}")


if __name__ == "__main__":
    main()
