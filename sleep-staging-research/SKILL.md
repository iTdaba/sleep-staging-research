---
name: sleep-staging-research
description: 睡眠分期（sleep staging / automatic sleep scoring）科研助手。查公开 PSG 数据集卡片与标准评测协议（Sleep-EDF-20/78、SHHS、MASS、ISRUC、CAP、MESA、DOD 等）、各数据集×协议的 SOTA 基准排行表（带论文出处）、AASM 分期规则与各期占比先验、指标定义与报告规范、模型谱系（SeqSleepNet / SleepTransformer / U-Sleep / L-SeqSleepNet / SleepGPT 等到 2026 基础模型）、可穿戴与非 EEG 模态基准；并可执行实验流程：Sleep-EDF 预处理、按受试者 k 折划分、MF1/κ/per-class F1 评测出表、hypnogram 绘图。当用户提到睡眠分期、自动睡眠评分、PSG、EEG 睡眠分析、hypnogram、AASM/R&K、N1 困难、MF1/Cohen's kappa、连续睡眠深度/CSDI/SDI、睡眠基础模型、或要设计/复现/评测睡眠分期实验、写论文找对标数字时，使用本技能。
---

# 睡眠分期科研助手

两条主线：**查知识**（数据集/协议/SOTA/规则/谱系，全部带出处）与**跑实验**（预处理/划分/评测/出图，脚本固化协议）。

## 任务路由

先判断用户意图，再按表读取对应 reference（按需读，不要一次全读）：

| 用户在做的事 | 先读 | 再用 |
|---|---|---|
| 选/查数据集、问规模通道采样率、下载获取 | `references/datasets.md` | `scripts/sleepedf_prepare.py`（Sleep-EDF） |
| 设计实验协议、折数、划分、裁剪规则 | `references/metrics-protocol.md` | `scripts/cv_split.py` |
| 找对标数字、报 SOTA、"现在最好是多少" | `references/sota-benchmarks.md` | — |
| 问分期规则、各期特征、R&K↔AASM、N1 为什么难 | `references/aasm-rules.md` + `references/domain-facts.md` | — |
| 选模型/基线、了解方法谱系、基础模型 | `references/model-zoo.md` | — |
| 预处理：滤波/重采样/切 epoch/标签对齐/类不平衡 | `references/preprocessing.md` | `scripts/sleepedf_prepare.py` |
| 评测出表、混淆矩阵、写结果段落 | `references/metrics-protocol.md` | `scripts/evaluate_staging.py` |
| 画 hypnogram / 深度曲线 / 结果图 | — | `scripts/plot_hypnogram.py` |
| 可穿戴/PPG/ECG/耳脑电/视频等非 PSG 场景 | `references/wearable-branches.md` | — |
| SleepSDIM 项目（CSDI 连续深度、SleepGPT-EBC）上下文 | `references/sleepsdim-walkthrough.md` | — |

## 快速路径

### A. 查 SOTA（最常见的问法）
1. 问清：哪个数据集、几分类、单导还是多通道、按受试者划分吗。
2. 读 `references/sota-benchmarks.md`，按"数据集×协议×通道"选表。
3. 回答时**逐行带出处**（第一作者+年份+期刊），并注明协议；表外数字一律不给。

### B. 设计/复现一个 Sleep-EDF-78 实验
1. 读 `references/datasets.md` 的 Sleep-EDF 卡片 + `references/metrics-protocol.md` 协议红线。
2. 预处理：`python scripts/sleepedf_prepare.py --edf-dir <目录> --out-dir epochs/`（默认 Fpz-Cz、100 Hz、±30 min 裁剪、30 s epoch，输出每记录一个 .npz + manifest.csv）。
3. 划分：受试者清单取自 manifest.csv，`python scripts/cv_split.py --subjects-file <受试者清单> --k 10 --val-per-fold 7 --out folds.json`（按受试者，断言无跨折泄漏）。
4. 训练后评测：`python scripts/evaluate_staging.py --true y_true.npy --pred y_pred.npy --fold-ids ids.npy --out results`（ids.npy 为样本级折编号 0..k-1；MF1/κ/acc/per-class F1/混淆矩阵，逐折+汇总 mean±SD，输出 .md 与 CSV）。
5. 出图：`python scripts/plot_hypnogram.py --true y_true.npy --pred y_pred.npy --depth s.npy --out hypnogram.png`（depth 可选，叠加深度的曲线）。

### C. 写论文时的数字纪律
1. 对标数字只从 `references/sota-benchmarks.md` 取，注明协议与出处。
2. 引用人类一致性作参照（`references/domain-facts.md`）。
3. 报告规范模板见 `references/metrics-protocol.md` 末尾。

## scripts 约定

- 环境：Python 3.9+；核心依赖 numpy/pandas/scikit-learn/matplotlib，`sleepedf_prepare.py` 另需 mne。先跑 `python scripts/check_env.py`。
- 所有脚本 `--help` 可查参数；标签顺序统一 **0=W, 1=N1, 2=N2, 3=N3, 4=REM**。
- 协议常量（100 Hz、0.3–35 Hz、30 s、按受试者折）如需偏离，必须在输出/论文中显式声明。

## 禁做清单（都有出处级的理由，见 domain-facts.md / metrics-protocol.md）

1. **不得凭记忆报任何性能数字**——只引用 sota-benchmarks.md 中带出处的行；表里没有就先查论文再入库。
2. **不得跨协议混表**——EDF-20/EDF-78、SHHS 全库/329 人子集、按受试者/按记录、单导/多通道、从头训/预训练，任何一项不同即不可比（Phan 2022 综述明确警告）。
3. **不得按夜（record-wise）划分折**——同一受试者两夜分属训练/测试即泄漏；划分一律按受试者。
4. **4 分期（合并 N1/N2）或唤醒二分的结果不得与 5 分期同表**——必须显式声明类别数。
5. **R&K 标签必须做转换**（N3+N4 合并、剔 MOVEMENT/UNKNOWN）并声明；裁剪规则（是否 ±30 min 在床窗口）必须写明。
6. **"超 SOTA"结论必须对照人类评分者间一致性**（κ≈0.76 / 一致率 79–86%，N1 仅 63%）。
7. record-wise 协议的论文数字（如 Nakamura 2020 ear-EEG）只可降权参考，不作锚点。
8. 存疑数字（如 MMS-SleepNet 89.8，见 sota-benchmarks.md 标注）不得用作对标上限。

## 知识来源与更新

本技能知识库提炼自 59 篇本地精读论文（2020–2026，含 10 篇综述）与公开综述/代码库；各 reference 内每个数字后注明出处。用户 Zotero 库中有原文 PDF（路径见各条目）。发现新论文/新数字时：先核对原文，再更新对应 reference 并补出处，禁止无出处入库。
