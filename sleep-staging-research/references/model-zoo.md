# 模型谱系

分类法沿用 Phan 2022 综述：**seq2seq 框架 = 逐 epoch 编码器 F_E + 序列编码器 F_S**，按输入表示（原始波形/时频图/多视图）× 学习范式（两阶段→端到端→迁移/自监督→基础模型）两条轴组织。

## 主干时间线（2017–2026）

| 年份 | 模型 | 一句话核心 | 关键数字 | 代码 |
|---|---|---|---|---|
| 2017 | DeepSleepNet | 两阶段（CNN 特征→BiLSTM），首破传统方法 | EDF-20 82.0/76.9 | akaraspt/deep-sleep-net |
| 2019 | SeqSleepNet | 时频图 29×129 + 可学习 filterbank + attention BiGRU，L=20 | MASS 87.1/83.3/κ0.815 | pquochuy/SeqSleepNet |
| 2019 | U-Time | U-Net 式全卷积 seq2seq，跨 14 库训练 | EDF-78 MF1 76.0† | pquochuy/u-time |
| 2020 | TinySleepNet | 轻量化 DeepSleepNet（SOTA 1/20 参数） | EDF-20 85.4/80.5 | opoolab/our_tinysleepnet |
| 2020 | AttnSleep | 纯 epoch 内注意力（FM-CNN+BiLSTM 注意力池化） | EDF-20 84.4/78.1 | emadeldeen24/attnsleep |
| 2021 | XSleepNet1/2 | 原始波形+时频**双视图**联合 | SHHS 87.5/81.0；EDF-78 84.0/77.9 | pquochuy/xsleepnet |
| 2022 | SleepTransformer | 纯 Transformer（epoch 内 4 层 + 序列间 4 层），注意力可解释 + 熵不确定度；3.7M 参数，L=21 最优 | EDF-78 84.9/0.789/78.8（SHHS 预训练） | pquochuy/SleepTransformer |
| 2023 | L-SeqSleepNet | **折叠式长序列**：L=200（一个睡眠周期）折成 B=10×K=20，时间复杂度亚线性；0.63M | SHHS 88.4；ear-EEG κ0.829 | — |
| 2023 | U-Sleep | 多数据集（15 库）多通道 FCN，通道任意组合 | EDF-78 MF1 79.0† | perslev/u-sleep（braindecode 可调） |
| 2024–26 | 多通道融合系 | MultiChannelSleepNet（分通道 Transformer+融合块+残差）、CrossFusionSleepNet（时域×时频交叉注意力）、ViSTA（多视图+人口 FiLM+CRF）、CareSleepNet（co-attention 跨模态上下文） | EDF-78 多通道档 85–87.5 | MobileSleepNet: dongdongzhou1017/MobileSleepNet |
| 2026 | WN-Sleep | **整夜**（1000+ epoch）S4D 状态空间模型 + 门控融合局部/全局；Transformer 直连 >200 epoch 会退化，折叠与 SSM 是两条解法 | SHHS 89.2–89.7 | — |

**共识**：一个睡眠周期的上下文基本够用（L-SeqSleepNet 消融）；L=200 vs 400 差 0.3 点。

## 基础模型线（2024–2026 爆发）

| 模型 | 预训练 | 核心思想 | 代表结果 | 出处 |
|---|---|---|---|---|
| StagerNet（前置） | MESA/SHHS 自监督 30s 卷积 | 睡眠 SSL 开山 | — | Banville 2021 |
| ContraWR / 2SLS / MAEEG / SleepVST | 各库 | 对比重构式 SSL；5% 标签≈全监督 | EDF-78 线性探针 82.6 | Yang 2023 等 |
| **SleepFM** | Stanford 私有 14,068 夜（19 通道 EEG+ECG+呼吸） | **leave-one-out 对比学习**（单模态 vs 其余模态均值，>2 模态时优于 pairwise） | 分期 AUROC 0.906 vs 监督 CNN 0.842 | Thapa 2024（Nat Med 2026） |
| **PFTSleep** | 13,888 夜整夜 8h×7 通道，PatchTST masked 重建 | **整夜任务无关表征**；分期头=冻结骨干+双向 GRU | SHHS 86.07/κ0.80；**MESA 只重训 GRU 头 κ 0.60→0.76（等效全量重训）——冻结骨干+轻量头最有力的已发表证据** | Fox 2025 SLEEP |
| **SleepFounder** | 23 库 50,223 人 78 万小时（**仅呼吸+心跳**） | 生理启发生成代理：呼吸心跳**重建 EEG 频谱 + 预测 SpO2 脱氧曲线**；各层隐状态可学习加权聚合 | 内部 κ0.693；外部平均 0.649；**BCG 睡垫直迁 κ0.617 / AHI ICC 0.926**；2–15% 标注即持平 | Nie 2025（同洪申达团队） |
| **SleepGPT** | 14 库 86,335h / 8,377 人（8 通道） | **UTF Transformer：共享注意力 + T/F/U 三种域选择 PCN**——即 VLMo 的 MoME 模态专家从"视觉/语言"换成"时域/频域"（论文明确引用 Bao 2022）；channel-wise conv + masked MSA 容忍缺失通道；多代理预训练（时频对比+难负匹配+MAE）。134M 参数，epoch embedding 768 维 | SHHS 89.1/82.4/κ0.845；生成增强使 2 受试者场景 MF1 +34.7；纺锤波 F1 71.7–79.1；代码 github.com/LordXX505/SleepGPT，权重 Figshare 10.6084/m9.figshare.30626870 | Huang 2026 Nat Commun |
| sleep2vec | 42,249 夜 9 模态 | **元数据感知 InfoNCE**（年龄/性别/站点动态加权负样本，抑制队列捷径）+ 夜间生物信号 scaling law | 抗传感器脱落 | arXiv 2602.13857 |

## 方法支线

- **知识嵌入**：MMS-SleepNet（AASM 显著波→卷积核尺寸映射：kernel=Fs/freq，捕 K-复合波 1Hz/δ 2Hz/α 10Hz）；eNeuroLingua（30s epoch→13 个 3s token，模拟人工分段的 tokenizer）；Zhou 2026（FIR 显式分解 δ/θ/α/β/γ 五节律+SE 加权，86.6/81.3）。
- **多视图对比**：Yu 2025 TBME（时域+时频**跨视图 CLIP 式对称对比**，5% 标签≈全监督，EDF-78 83.8）；MV-TTFC（IMSST 高能量集中时频视图）；Zhou SCRL（监督对比 τ=0.07）。**注意：BSPC 同行全是"对比损失+分类损失"组合，无人做显式原型对齐**——SleepSDIM 的 CLIP 式原型头在此有对话空间。
- **生成式/概率**：FSDM（van Gorp 2025 JBHI）——因子化分数扩散，任意传感器组合零样本分期（单 EEG 85.6/κ0.791 达评分员间水平；PPG+气流+呼吸 79.0/κ0.697），"每传感器信息增益"与性能线性相关 r=0.91；SleepGPT 生成增强。
- **概率/结构后处理**：Viterbi/HMM（SleepSDIM v3/v4、MobileSleepNet 的转移矩阵统计先验）、CRF（ViSTA Stage2）、转移矩阵校正（Liang 2026 耳脑电）。共识：序列先验比更深网络便宜且有效（+1.9 acc）。
- **N1 专项**：SSC-SleepNet（伪孪生 WCE+FL+对比动态加权，N1 F1 55–60）；ACR 抗类比例损失（N1 召回 37.9→51.1）；MMS 的 N1 overlap 过采样⚠。
- **轻量化/边缘**：MSA-CNN（1 万参数 81.4 acc EDF-78，比 DeepSleepNet 少 3 个数量级）；MobileSleepNet（11K 参数 0.94ms/epoch 手机端）；NeuroSleep（神经形态事件流，省 53.6% 算力但 acc 降至 74.2——效率-精度帕累托的一个点）。
- **不确定性**：SleepTransformer 熵置信度（拒 50% 低置信 epoch 圈出 >90% 错误，低置信集中于 N1 与转换期）；BayesSleepNet（贝叶斯 MC dropout + 主动学习，20% 标注 +7.6 acc）。
- **长序列**：见主干时间线 L-SeqSleepNet/WN-Sleep。

## 迁移/域适应要点（写泛化实验时引用）

- **直接迁移会崩塌**：SeqSleepNet+ MASS→cEEGrid −62.2 点；成人 PPG→儿童直迁 κ0.68 vs 微调 0.88（Haimov 2025）；DOD-H→DOD-O F1 89.9→62.6。
- **微调几乎总是必要，但 11–13 个目标受试者即可收敛**；弱基座迁移收益更大（DeepSleepNet+ +10.9 vs SeqSleepNet+ +1.4）（Phan 2021 TBME）。
- 跨库直迁 κ 平均掉 0.2–0.4（Anido-Alonso 2023 六库实验）；联邦学习 ssFedSGD 外部 κ 0.65 几乎追平中心化 0.66。
- 物理先验合成数据（LORETA 头模型把源库 EEG 映射到目标电极，Waters 2024）：+0.5 acc，且证明简单冻结+微调胜过 CORAL/DDC 等复杂域适应。
- 传统工具箱（非深度）：**YASA**（特征+LightGBM，接近评分员间一致，eLife 2021，pip 可装）；SleepECG（心率分期）；uSLEEPYLAND（U-Sleep/SleepTransformer/DeepResNet 统一基准容器）。
