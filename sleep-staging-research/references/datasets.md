# 公开 PSG 数据集卡片

每张卡片：规模 / 人群 / 通道 / 采样率 / 标注 / 获取 / **标准评测协议** / 常见坑。数字出处见文内标注（第一作者+年份）。

---

## Sleep-EDF Expanded（PhysioNet，最常用基准）

- **构成**：两个子集。**Sleep Cassette (SC)**：78 名健康白人（25–101 岁），每人 2 个全天记录（受试者 13/36/52 各缺 1 夜，共 153 夜）；**Sleep Telemetry (ST)**：44 夜（服用替马西泮/唑吡坦者，18–79 岁）。SC 常用通道：Fpz-Cz、Pz-Oz EEG + 水平 EOG + 颏下 EMG，均 100 Hz。
- **标注**：R&K（存于 EDF annotations）：W, S1–S4, REM, MOVEMENT, UNKNOWN。**使用前必须转换**：S3+S4→N3，MOVEMENT/UNKNOWN 剔除。
- **获取**：PhysioNet `sleep-edfx`（EDF+hypnogram 合一）；本地原始数据：`~/code/Sleep/CD`。
- **标准协议（两条，绝不混表）**：
  - **EDF-20**：前 20 名受试者 39 夜（年轻 25–34 岁），20 折/LOSO；
  - **EDF-78**：全 78 人 153 夜，**按受试者 10 折 CV，每折从训练受试者中留 7 人做验证**，单导 Fpz-Cz，**仅保留在床时段前后各 30 min 的 W**（协议由 SleepTransformer 确立，Phan 2022 TBME；XSleepNet、Yu 2025 TBME 沿用）。epoch 总数 ~19.5–19.6 万（裁剪口径不同会浮动，CTBSleep 报 196,350）。
- **常见坑**：①"Sleep-EDF"一词在不同论文里指 2013 版（20 人）/Expanded 版（78 人）不明确；②裁剪规则是隐性变量——"仅 in-bed"（Phan 2019/2021）与"±30 min"（Phan 2022）会引入大量易分 W，acc 可差数个点（TBME 组精读结论）；③78 人年龄跨度 25–101，WN-Sleep 指出其各年龄段样本少是它比 SHHS 难的原因之一。
- **引用**：Kemp et al. 2000, "The sleep-edf database"。

## SHHS（Sleep Heart Health Study）

- **构成**：SHHS-1 5,791 人（39–90 岁，心血管队列），EEG C4-A1（及 C3-A2）、EOG、EMG 等，125 Hz；SHHS-2 3,295 人。R&K 标注（N3/N4 须合并，MOVEMENT/UNKNOWN 剔除）。
- **标准协议（两套并行，引用必须注明）**：
  - **全库**：剔除不含全部五期的记录后 ~5,463 夜，**按受试者 70/30 划分 + 训练集留 100 人验证**（Phan 2022 TBME；L-SeqSleepNet 2023、WN-Sleep 2026、SSC-SleepNet 2025、Anido-Alonso 2023 沿用）；
  - **329 人子集**：AHI<5 的健康受试者（ViSTA-SleepNet 2026 JBHI、CareSleepNet 派、MMS-SleepNet 2025 用）。
- **注意**：PFTSleep（Fox 2025 SLEEP）指出 SHHS-2 常被用作预训练——若测试集在 SHHS-1，须自查两库受试者重叠（SleepGPT 披露其 756 人重叠仅致 ~0.5 点差异，但必须声明）。
- **获取**：NSRR（sleepdata.org），需注册。

## MASS（Montreal Archive of Sleep Studies）

- **构成**：200 夜、5 个 session：SS1 53 人（AASM）、SS2 19（R&K）、SS3 62（AASM，健康 20–69 岁，常用）、SS4 40（R&K）、SS5 26（R&K）；256 Hz，EEG+EOG+EMG。
- **标准协议**：SeqSleepNet 系（Phan）用 **200 人全库**（C4-A1 EEG+ROC-LOC EOG+chin EMG，LOSO/20 折）；单导/子集实验多取 **SS3 62 人**（如 Zhou 2026 BSPC 用 31 折 leave-two-out）。
- **坑**：MASS 是 20 s epoch 标注——对齐 30 s 需**前后各补 5 s**（SleepGPT 的做法）或改用 20 s 协议；获取需签协议（massdb.ca）。
- **基准数字**：SeqSleepNet 87.1 acc / 83.3 MF1 / κ0.815（Phan 2019 TBME）。

## ISRUC-Sleep

- **构成**：S1 100 名成人**睡眠障碍患者**（20–85 岁，AASM）；S2 16；S3 10 名健康人。200 Hz，6 EEG+2 EOG+EMG+ECG。
- **用途**：病理压力测试库——各模型在此普遍比健康库低（Phan 2022 综述：病理库 κ 明显不足；Yang 2026 综述：CAP 类病理库比标准库低 10–15 点）。
- **协议**：10 折按受试者（健康 S3 小，常 1 人验证+测试）。数字见 sota-benchmarks.md。

## CAP Sleep Database

- 108 名受试者（混合病理：NREM 异态睡眠/发作性睡病/失眠等，R&K）。PhysioNet 可得。**各模型最低档**（AttnSleep 系列 76.9–78.8 acc，Yue 2024 SMR 综述表）。含 CAP 事件标注（周期性交替模式），也用于微事件研究。

## NSRR 队列：MESA / MrOS / CFS

- **MESA**：2,056 人多种族社区队列（含完整 PSG+PPG），1,850/204 训测（SleepPPG-Net 用）；**MrOS**：老年男性（v1 2,900 / v2 1,025）；**CFS**（Cleveland Family Study）。
- **CSDI 论文（Zhou 2025 npj DM）的协议范本**：MESA/MrOS/CFS 训练+内部验证（按受试者 7:3），**SHHS-1 完全留作外部验证**——多队列"内部+外部"设计是睡眠深度回归任务的标准解法。
- 获取：sleepdata.org 注册。

## HMC（Haaglanden Medisch Centrum）

- 151 夜临床人群（85 男 66 女，53.9±15.4 岁，含 OSA/失眠等），AASM。SSC-SleepNet（Lin 2025 JBHI）作为第四数据集；Anido-Alonso 2023 跨库实验之一。开源于 Zenodo。

## DOD-H / DOD-O（Dreem Open Datasets）

- **DOD-H** 25 名健康人、**DOD-O** 55 名 OSA 患者，250 Hz，**每夜 3 个中心 5 名技师独立评分（AASM v2.5）**，多数投票共识标签。
- **价值**：①"对人评测"范式——人类均值 F1 86.8（DOD-H）/84.8（DOD-O），最佳自动模型 SimpleSleepNet 89.9/88.3 已超人（Guillot 2020 arXiv）；②AASM 评分员间一致率仅 82.6%，**N1 仅 63.0%**——单评分员基准有系统性上限；③DOD-O→DOD-H 迁移 F1 84.8 尚可、反向骤降至 62.6（含病理数据是泛化关键）。Dreem 开源（github.com/Dreem-org/dreem-learning-open）。

## PhysioNet/CinC Challenge 2018

1,983 名患者（55±14 岁），arousal 标注为主，AASM 评分。SleepGPT 预训练库之一；BayesSleepNet 用的 994 人版本 5 折。

## 其他

- **SIESTA** 295 人（20–90 岁，AASM）：HRV 分期文献（Radha LSTM 4 类 77% κ0.61）与 PFTSleep 外部队列来源之一。
- **MIT-BIH PSG**：18 名疑 OSA 男性，250 Hz——心呼吸分期老基准（ECG/EDR 特征法）。
- **ear-EEG/cEEGrid**：耳内与耳周电极小队列（Mikkelsen、Phan 2021 TL 的 Surrey-cEEGrid 12 人；Borup 2023 的 20 人×4 夜）。
- **CHAT**：儿童腺样体切除试验（5–10 岁，轻中度 OSA）——儿科 PPG 唯一公开库（Haimov 2025 TBME）。

---

## R&K → AASM 转换规则（所有 R&K 库通用）

| R&K 原标签 | 处理 |
|---|---|
| W | → W（并按协议裁剪在床窗口） |
| S1 / S2 | → N1 / N2 |
| S3 + S4 | **合并 → N3** |
| REM | → REM |
| MOVEMENT / UNKNOWN | **剔除**（不计入样本，不映射为 W） |

不声明转换与裁剪规则的论文数字不可直接引用（Phan 2022 综述"不可脱离评估设定比较"）。

## 类别先验（写采样/加权时参考）

健康成人整夜时间分布约：**W 5%（裁剪后更多）、N1 5–9%、N2 ~50%、N3 ~20%、REM ~25%**（Djanian 2022 SM 综述）；SHHS N1 仅 3.71%（CrossFusion 2026 统计）。EDF-78 19.5 万 epoch 中 W 65,795 / N1 21,469 / N2 68,633 / N3 12,991 / REM 25,767（eNeuroLingua 2026 转录）。
