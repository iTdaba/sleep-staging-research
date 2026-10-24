#!/usr/bin/env python3
"""Sleep-EDF (Expanded) 预处理：EDF 读取 → 通道提取 → 滤波重采样 → 30 s epoch → 标签映射 → 在床裁剪。

固化协议（references/metrics-protocol.md 红线）：
- 默认 Fpz-Cz、100 Hz、0.3–35 Hz 带通、30 s epoch；
- R&K→AASM：S3/S4→N3，MOVEMENT/UNKNOWN/Sleep stage ? 剔除；
- 仅保留在床时段前后各 30 min 的 W（睡眠 epoch 全保留，W 距最近睡眠 epoch 超窗则弃）；
- 输出每记录一个 .npz（X float32 [n,3000]，y int64 [n]，0=W 1=N1 2=N2 3=N3 4=REM）+ manifest.csv。

用法:
  python scripts/sleepedf_prepare.py --edf-dir /path/to/sleep-cassette --out-dir epochs/
  快速试跑: 加 --limit 2（只处理前 2 个文件）
"""
import argparse
import csv
import re
import sys
from pathlib import Path

# 描述 → 标签（0..4）；同时支持 R&K 风格（Sleep stage 1/2/3/4）与 AASM 风格
# （Sleep stage N1/N2/N3），Sleep-EDF 各版本记录混用；未列出的描述一律剔除
LABEL_MAP = {
    "Sleep stage W": 0, "Sleep stage Wake": 0,
    "Sleep stage 1": 1, "Sleep stage N1": 1,
    "Sleep stage 2": 2, "Sleep stage N2": 2,
    "Sleep stage 3": 3, "Sleep stage N3": 3, "Sleep stage 4": 3,
    "Sleep stage R": 4, "Sleep stage REM": 4,
}


def find_channel(ch_names: list[str], want: str) -> str | None:
    if want in ch_names:
        return want
    for c in ch_names:  # 容错：大小写/多余空格
        if re.sub(r"\s+", " ", c).lower() == re.sub(r"\s+", " ", want).lower():
            return c
    return None


def prepare_one(path: Path, args, unknown_seen: set) -> tuple[str, str, int] | None:
    import mne

    mne.set_log_level("ERROR")
    raw = mne.io.read_raw_edf(path, preload=True, verbose="ERROR")
    ch = find_channel(raw.ch_names, args.eeg_ch)
    if ch is None:
        print(f"  [跳过] {path.name}: 无通道 {args.eeg_ch}（现有: {raw.ch_names[:6]}...）")
        return None
    raw.pick([ch])

    # 1) 标签与在床窗口（在重采样前用 annotation 原始 onset，单位秒）
    epochs = []  # (onset_sec, label)
    for onset, _dur, desc in zip(raw.annotations.onset, raw.annotations.duration,
                                 raw.annotations.description):
        d = re.sub(r"\s+", " ", str(desc)).strip()
        if d in LABEL_MAP:
            epochs.append((float(onset), LABEL_MAP[d]))
        else:
            unknown_seen.add(d)
    if not epochs:
        print(f"  [跳过] {path.name}: 无睡眠分期 annotation")
        return None
    epochs.sort()
    n_before = len(epochs)
    sleep_idx = [i for i, (_, lab) in enumerate(epochs) if lab > 0]
    if sleep_idx:
        lo, hi = sleep_idx[0], sleep_idx[-1]
        margin = int(args.trim_min * 60 // 30)  # 30 min → 60 epochs
        keep = [(t, lab) for i, (t, lab) in enumerate(epochs)
                if lab > 0 or (lo - margin <= i <= hi + margin)]
    else:  # 无睡眠的极端记录：全弃
        keep = []
    if not keep:
        print(f"  [跳过] {path.name}: 裁剪后为空")
        return None

    # 2) 滤波 + 重采样
    raw.filter(args.l_freq, args.h_freq, picks="eeg", verbose="ERROR")
    if abs(raw.info["sfreq"] - args.fs) > 1e-6:
        raw.resample(args.fs, verbose="ERROR")
    data = raw.get_data(picks=[ch])[0]
    fs = raw.info["sfreq"]

    # 3) 切 epoch（30 s，按 annotation onset 对齐）
    xs, ys = [], []
    for onset_sec, lab in keep:
        s0 = int(round(onset_sec * fs))
        seg = data[s0:s0 + int(30 * fs)]
        if len(seg) < int(30 * fs):
            continue  # 记录尾部截断
        xs.append(seg.astype("float32"))
        ys.append(lab)

    m = re.search(r"(SC|ST)\d{4}", path.stem.upper())
    subject = m.group(0) if m else path.stem[:6]
    out_name = f"{path.stem}_epochs.npz"
    np = __import__("numpy")
    np.savez(Path(args.out_dir) / out_name,
             X=np.stack(xs), y=np.asarray(ys, dtype=np.int64),
             subject=np.asarray(subject), fs=np.asarray(fs))
    print(f"  [OK] {path.name}: {n_before} → {len(ys)} epochs（裁剪弃 {n_before - len(ys)}，"
          f"含端部截断）；受试者 {subject} → {out_name}")
    return subject, out_name, len(ys)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--edf-dir", required=True, help="Sleep-EDF 目录（含 *PSG.edf / SC*.edf）")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--eeg-ch", default="EEG Fpz-Cz")
    ap.add_argument("--fs", type=float, default=100.0)
    ap.add_argument("--l-freq", type=float, default=0.3)
    ap.add_argument("--h-freq", type=float, default=35.0)
    ap.add_argument("--trim-min", type=float, default=30.0,
                    help="在床前后保留 W 的分钟数（0=不裁剪，全保留）")
    ap.add_argument("--limit", type=int, default=0, help="只处理前 N 个文件（试跑）")
    args = ap.parse_args()

    edf_dir = Path(args.edf_dir)
    files = sorted(p for p in edf_dir.glob("*.edf")
                   if "hypnogram" not in p.name.lower())
    if not files:
        sys.exit(f"{edf_dir} 下没有 .edf 文件")
    if args.limit:
        files = files[: args.limit]

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        import mne  # noqa: F401
    except ImportError:
        sys.exit("需要 mne：pip install mne")

    unknown: set[str] = set()
    manifest = []
    for p in files:
        try:
            r = prepare_one(p, args, unknown)
        except Exception as e:  # 单文件失败不中断批次
            print(f"  [失败] {p.name}: {e}")
            continue
        if r:
            manifest.append(r)

    with open(out_dir / "manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["subject", "file", "n_epochs"])
        w.writerows(manifest)
    total = sum(n for *_, n in manifest)
    print(f"\n完成 {len(manifest)}/{len(files)} 个记录，共 {total} epochs → {out_dir}")
    if unknown:
        print(f"已剔除的 annotation 类型: {sorted(unknown)}")
    print(f"受试者清单已可从 manifest.csv 提取：python scripts/cv_split.py --subjects-file "
          f"<(cut -d, -f1 {out_dir}/manifest.csv | tail -n +2 | sort -u) --k 10 --val-per-fold 7 --out folds.json")


if __name__ == "__main__":
    main()
