# SOTA 基准排行表（按 数据集 × 协议 × 通道 分组）

所有数字转录自论文原文（59 篇精读库）。**使用规则**：只引用与本表协议一致的行；跨表比较前先核对四要素（数据集子集 / 划分方式 / 通道数 / 从头训还是预训练）；† 表示原文即声明不可直接比；⚠ 表示本库精读发现方法学风险。

---

## 1. Sleep-EDF-78 · 单导 Fpz-Cz · 按受试者 10 折 · ±30 min 裁剪（SleepSDIM 直接赛道）

| 模型 | acc | κ | MF1 | N1 F1 | 出处 |
|---|---|---|---|---|---|
| SleepTransformer*（SHHS 预训练初始化） | **84.9** | **0.789** | **78.8** | 48.5 | Phan 2022 TBME Table I |
| BayesSleepNet | 84.4 | 0.783 | 78.6 | 50.3 | Yu 2026 JBHI Table III |
| XSleepNet2 | 84.0 | 0.778 | 77.9 | 49.9 | Phan 2022 TBME Table I |
| Yu MV-SSL（微调） | 83.8 | — | — | 三库 N1 最佳 | Yu 2025 TBME |
| FCNN+RNN | 82.8 | 0.761 | 76.6 | — | Phan 2022 TBME Table I |
| SeqSleepNet | 82.6 | 0.760 | 76.4 | — | 同上 |
| MobileSleepNet（11K 参数） | 81.5±4.2 | 0.741 | — | 33±9 | Zhou 2026 JBHI Table III |
| SleepTransformer（从头训） | 81.4 | 0.743 | 74.3 | 40.4 | Phan 2022 TBME |
| AttnSleep | 81.3 | 0.74 | 75.1 | — | Phan 2022 TBME Table I |
| MSA-CNN large（多通道 4 导） | 81.4±0.3 | 0.737 | 73.8 | — | Goerttler 2026 BSPC（重复 CV） |
| SleepEEGNet | 80.0 | 0.730 | 73.6 | — | Phan 2022 TBME Table I |
| U-Sleep† | — | — | 79.0 | — | 协议/通道不同（EEG+EOG） |

**可信区间结论**：单导 10 折 acc 81–85、κ 0.74–0.79、N1 F1 40–50。跨库预训练（SHHS→EDF）+3.5 acc / +4.5 MF1 是已被反复验证的收益（Phan 2022；Phan 2021 TL）。
**注**：SleepGPT 在 EDF-78 的确切数字在其补充表 7（正文未给），需回查补充材料/Figshare（10.6084/m9.figshare.30626870）。

## 2. Sleep-EDF-78 · 多通道（EEG+EOG±EMG）· 20 折为主

| 模型 | acc | κ | MF1 | N1 F1 | 出处 |
|---|---|---|---|---|---|
| MMS-SleepNet ⚠ | 89.8 | 0.80 | 77.4 | 77.8(acc口径) | Duan 2025 BSPC。**⚠ 疑似划分前 N1 overlap 增强造成泄漏 + 消融表 0.953 与主表 92.9 矛盾；只作上限参考，不作对标** |
| CrossFusionSleepNet | 87.5 | 0.83 | 83.0 | 59.4 | Cao 2026 BSPC（10 折；3-epoch 输入时 N1 63.7） |
| CTBSleep | 87.5 | 0.82 | 80.4 | 50.1 | Shi 2026 BSPC（10 折） |
| eNeuroLingua | 85.3±1.7 | 0.796 | 80.0 | 51.8 | Samaee 2026 BSPC（20 折，3.52M 参数） |
| ViSTA-SleepNet | 85.0 | 0.79 | 80.5 | 52.4 | Wang 2026 JBHI（20 折，0.52M 参数） |
| MultiChannelSleepNet | 85.0 | — | 79.6 | 53.0 | Dai 2023 JBHI（经 CTBSleep 基线表转录） |

## 3. Sleep-EDF-20 · 20 折 / LOSO（注意：与 78 人版差 5+ 点，绝不混表）

| 模型 | acc | MF1 | N1 F1 | 出处 |
|---|---|---|---|---|
| SleepGPT（预训练） | 89.1 | 85.1 | — | Huang 2026 Nat Commun（κ0.847） |
| CrossFusionSleepNet | 89.0 | 84.0 | 57.2 | Cao 2026 BSPC |
| CTBSleep | 88.5 | 81.2 | 50.5 | Shi 2026 BSPC |
| ViSTA-SleepNet | 88.8 | 83.6 | 55.3 | Wang 2026 JBHI |
| TBSTSleepNet | 87.2 | 82.3 | 53.3 | He 2024 BSPC ⚠（overlap 平衡采样，口径存疑） |
| BayesSleepNet | 86.75 | 81.12 | 51.2 | Yu 2026 JBHI |
| MMS-SleepNet ⚠ | 92.9 | 81.3 | 74.1 | Duan 2025 BSPC（同上 ⚠） |
| MSA-CNN large | 84.4±0.3 | 77.7 | — | Goerttler 2026 BSPC（~4 万参数） |
| DeepSleepNet | 82.0 | 76.9 | 50.1 | 多篇转录一致 |

## 4. SHHS · 全库 ~5,463–5,791 夜 · 按受试者 70/30 + 100 人验证

| 模型 | acc | κ | MF1 | N1 F1 | 出处 |
|---|---|---|---|---|---|
| WN-Sleep（S4D 整夜 SSM） | 89.2–89.7 | 0.85+ | 82.8 | PR-AUC 0.555 | Zhou 2026 JBHI |
| SleepGPT | 89.1 | 0.845 | 82.4 | — | Huang 2026 Nat Commun |
| L-SeqSleepNet | 88.4 | — | — | — | Phan 2023 JBHI |
| SleepTransformer | 87.7 | 0.828 | 80.1 | 46.1 | Phan 2022 TBME |
| XSleepNet2 / 1 | 87.6 / 87.5 | 0.826 | 80.7 / 81.0 | 49.9 | 同上 |
| PFTSleep（整夜自监督） | 86.07 | 0.80 | 76.53 | 35.9 | Fox 2025 SLEEP |
| SeqSleepNet | 86.5 | 0.811 | 78.5 | — | Phan 2022 TBME Table I |
| AttnSleep†（子集） | 84.2 | 0.78 | 75.3 | — | 同上 |

**子集协议（AHI<5，329 人）另列**：ViSTA 89.7/83.2（N1 52.4）；MMS ⚠ 90.0/76.5。与全库协议不互比。

## 5. MASS

| 模型 | 协议 | acc | κ | MF1 | N1 F1 | 出处 |
|---|---|---|---|---|---|---|
| SeqSleepNet | 200 人全库 | 87.1 | 0.815 | 83.3 | — | Phan 2019 TBME |
| Zhou 节律+SCRL | SS3 62 人 | 87.2 | 0.810 | 82.3 | 59.3 | Zhou 2026 BSPC |
| BayesSleepNet | 全库 10 折 | 86.85 | 0.811 | 82.46 | 59.7 | Yu 2026 JBHI |
| Yu MV-SSL | 全库 | 85.5 | — | — | — | Yu 2025 TBME |

## 6. ISRUC（病理压力测试）

- **S3（10 健康人）**：CTBSleep 85.2/83.2/κ0.80（N1 68.1）> MVF-SleepNet 84.1/79.5 > MSA-CNN 79.8±0.9 > SeqSleepNet 78.9/76.3 > MobileSleepNet 77.6±6.3。
- **S1（100 患者）**：MixSleepNet 83.0/κ0.782（6EEG+2EOG+EMG+ECG）> MSF-SleepNet 82.6 > eNeuroLingua 81.9±4.1/κ0.755（N1 0.576）> U-Sleep† 77.0 > MobileSleepNet 71.4。

## 7. 人类参照系（任何"超 SOTA"声明的分母）

- 评分者间一致率 **79–86%**（多篇综述互证），**κ≈0.76**（Phan 2022 引 Danker-Hopfe 2009）；**N1 一致性仅 63.0%（κ≈0.24）**（Chen 2026 J Med Syst；DOD 实测）。
- DOD 共识评测：人类均值 F1 **86.8**（DOD-H 健康人）/ **84.8**（DOD-O 患者），最佳自动模型 89.9 / 88.3（Guillot 2020）。
- EDF 上 R&K 评分员一致率 80.6%（MSA-CNN 引）；ear-EEG 场景人工 κ≈0.82（Borup 2023）。
- 纺锤波专家间一致率 **<50–58%**（Zapata 2024 实测 Dreams/MASS-SS2）。

## 补充：数字可信度分层经验（本库精读结论）

1. 单次运行、无 ±SD 的数字可靠性低一档（MSA-CNN 用固定折重复 CV 重测发现多篇论文数字在统一协议下显著变化）。
2. EDF-20 上 acc>89% 的论文都要先查：是否 overlap/重采样类增强在划分前执行（MMS、TBST 案例）、是否含易分 W 过多（裁剪口径）。
3. 表格为图片型 PDF 的论文（WN-Sleep、SSC、CareSleepNet、Anido、FSDM 主表），只能引用正文明确写出的数字。
