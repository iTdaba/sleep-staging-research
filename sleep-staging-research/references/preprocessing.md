# 预处理流水线与常见坑

## 标准流水线（Sleep-EDF-78 惯例，与 scripts/sleepedf_prepare.py 一致）

1. **读取**：EDF 用 `mne.io.read_raw_edf`（preload=True）；hypnogram 在 Sleep-EDF 的 EDF annotations 里（`raw.annotations` / `mne.events_from_annotations`），不是独立文件。
2. **通道**：取 Fpz-Cz（EDF 命名 `EEG Fpz-Cz`）；多通道实验按 datasets.md 的通道先验选。
3. **重采样**：100 Hz（领域事实标准；原始即 100 Hz 则跳过；SHHS 125→100、ISRUC 200→100）。
4. **滤波**：0.3–35 Hz 带通（Phan 系惯例；各家口径 0.3–30 / 0.5–45 / 0.3–40 不一，**必须声明**）。50 Hz 陷波（临床数据）。
5. **切 epoch**：30 s（AASM 标准）；`mne.Epochs(events, tmin=0, tmax=30, baseline=None)`。
6. **标签映射**：R&K→AASM（S3/S4→N3，MOVEMENT/UNKNOWN 丢弃该 epoch）；标签顺序 0=W,1=N1,2=N2,3=N3,4=REM。
7. **裁剪**：以"lights off/on"（Sleep-EDF annotation 中的 `Sleep stage ?` 起止与 `Time` 事件）定位在床时段，仅保留 **前 30 min 与后 30 min 的 W**。
8. **归一化**：逐通道 z-score（按训练折统计量！）；跨域场景 IQR 标准化比 z-score 抗伪迹更稳（Rusanen 2023 结论）。
9. **保存**：每受试者一个 `.npz`（X: [n_epochs, 3000]，y: [n_epochs]），划分按文件名中的受试者号分组。

## 时频表示（若用谱输入）

STFT：2 s Hamming 窗、50% 重叠、256 点 FFT → **29×128** 时频图、log 幅度、训练集统计归一化（SeqSleepNet/SleepTransformer 事实标准，BSPC 组同样共用）。MASS 20 s epoch 先前后各补 5 s 对齐 30 s。

## 类别不平衡工具箱（按频次排序，均带出处）

1. 加权 CE / 类频率样本加权（SleepPPG-Net）；**ACR**：W=μ·(1−N_i/N)（N1 召回 37.9→51.1，Li 2025 BSPC）。
2. Focal Loss + 加权 CE 组合（MTRT、ViSTA W1.5/N1 1.5/N2 2/N3 1.5/REM 1.7 + label smoothing 0.3）。
3. 监督对比损失（Zhou SCRL τ=0.07、MMS CCM τ=0.05，均报告主要改善 N1/REM 边界）。
4. 过采样⚠：仅按受试者划分后在训练折内做；MMS 的 N1 overlap 增强（前后 15 s 拼接）疑似泄漏，模仿前自查。
5. W 降采样（裁剪规则本身就是一种）；wake 过采样换特异度的权衡：+20–35% 特异度、−8–12% acc（Birrer 2024 引 Roberts）。
6. 序列结构先验：Viterbi/HMM 转移矩阵（训练折统计）、CRF（ViSTA Stage2）——+1.9 acc 量级，便宜有效。

## 常见坑清单

- **epoch 计数对不上**：先核对裁剪口径（±30 min 与否）——EDF-78 在 19.5–19.6 万、EDF-20 在 41,950–43,141 间浮动都正常（不同论文口径）。
- **受试者号解析**：Sleep-EDF 文件名 `SC4xxxE0-PSG.edf` 中 `SC4xxx` 即受试者号（4191 等）；`SC4191EC-Hypnogram.edf` 在 Expanded 版中已并入 PSG annotations——用 mne 直接读。
- **验证集泄漏**：早停监控训练损失而非测试指标（MSA-CNN 对基线的修正）；归一化统计量只用训练折。
- **两夜同受试者**：cv_split 必须按受试者号分组（本 skill 脚本已断言）。
- **MNE 版本差异**：annotation description 名称（`Sleep stage 1` vs `Sleep stage W`）随数据版本；脚本按映射表处理并报未知标签。
- **NaN/超幅伪迹**：先查各 epoch 最大绝对幅值（>数 mV 多为伪迹段）；临床数据保留 vs 剔除要声明（Liang 2026 全保留 vs Nakamura 剔 23%）。

## 与 YASA 的关系

YASA（`pip install yasa`）提供特征法自动分期（LightGBM）与纺锤波/REM 检测，精度接近评分员间一致——适合做**快速基线/标签 sanity check**（一行代码出 hypnogram），不适合当深度学习对标。深度基线用 SeqSleepNet/SleepTransformer（uSLEEPYLAND 容器可复现）。
