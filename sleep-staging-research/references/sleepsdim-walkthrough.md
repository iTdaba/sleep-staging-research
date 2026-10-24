# SleepSDIM 项目走查（本技能作者的贯穿示例）

项目位置：`~/code/vibe_coding/OpenCode/Projects/SleepSDIM/`；原始数据：`~/code/Sleep/CD`（Sleep-EDF Expanded，约 2.9 GB）。

## 任务定义（v4 设计说明第 1 节）

输入整夜 PSG 按 30 s epoch 切分（单导 Fpz-Cz），输出双任务：
1. **回归**：连续睡眠深度指数 CSDI $s_t\in[0,1]$（0=清醒，1=最深）；
2. **分类**：AASM 五分期。
下游：从连续深度曲线提取数字生物标志物（入睡斜率、深睡总量、REM 潜伏期、变异性 CV/SK/RB/AP/ApEn/DFA 等）。

**协议**：Sleep-EDF-78，按受试者 10 折；主指标 MF1 + κ（分类）、Spearman ρ（深度）。

## 版本演进

- **v3**：深度引导 SleepTransformer 十折（`sleep_transformer_depth_v3_kaggle_results.ipynb`）。
- **v4 CSDI-StageNet**：SleepTransformer 共享编码器 + 深度回归头 + 软级联分类头 `g([h_t; s_{t-R:t+R}; Δs_t; r̂_t])` + 一致性/序数损失 + Viterbi 后处理（`CSDI_StageNet_设计说明.md`、`csdi_stagenet.py`、`sleep_transformer_depth_v4_csdi_stagenet.ipynb`）。
- **v5 SleepGPT-EBC**（当前）：**冻结 SleepGPT 骨干**（86,335h 预训练，epoch embedding 768 维，~134M）+ **VPT 提示调优**（32 个可学习 prompt token，唯一注入骨干的可训练参数）→ 共享序列编码器（d'=128）→ **CLIP 式原型头**（可学习原型 + 余弦相似度 ×可学习温度 τ，分期 5 原型 + 深度 4 个 NREM 整数箱）→ **连续深度 = 分箱期望** $s_t=\sum_k q_{t,k}d_k$（同构 CLIP-EBC 密度图）→ **DACE 损失** = CE + λ·一维有序 Wasserstein $W_1(q_t,\delta_{d_y})$ + 一致性 + 平滑；REM 不进深度轴（独立第 5 原型 + 辅助头喂软级联）；三阶段训练（VPT 预热→联合→Viterbi）。原型 `sleepgpt_ebc.py`（`FrozenSleepGPTStub` 占位骨干，链路已验证可训可收敛）。

## 奠基文献对照（写 Related Work 用）

- **CSDI 直接基础 = Zhou 2025 npj Digital Medicine**（`~/Zotero/storage/98RB3HE2/`）：四通道 PSG（C4+EMG+EOG+ECG@100Hz）、NSRR 四队列 11,485 夜（MESA/MrOS/CFS 训练 7:3、**SHHS 完全外部**）；ViT patch=100（1 s，对齐 K-复合波时长）；**成对排序损失**，margin 手工设定 W/N1=1.0、N1/N2=0.5、N2/N3=1.5、W/REM=1.2，**REM 与 NREM 全部配对被掩码**（序数关系不确定）；深度头不加界、事后 Sigmoid；SDI 与后续 30s 觉醒占比 Pearson 0.99+；REM 二分类 AUROC 0.975–0.99；紊乱亚型校正后全因死亡 HR 1.33。代码 github.com/sczzz3/SDI。
- **骨干谱系**：VLMo MoME（模态专家+共享注意力，Bao 2022）→ SleepGPT UTF 块（T/F/U-PCN，Huang 2026 明确引用）→ 本项目 VPT+原型头。
- **DACE 损失对话对象**：Zhou SDI margin 排序（分布外）、ACR 类比例加权（N1 召回 37.9→51.1）、SSC 的 WCE+FL+对比动态加权（N1 F1 58–71）、Zhou SCRL 监督对比（τ=0.07）。BSPC 同行全是"对比+分类"组合，**无人做显式原型对齐**——差异化点。
- **冻结骨干+轻量头证据链**：PFTSleep（只训 GRU 头 = 全量重训）、Phan 2021（11–13 受试者微调收敛）、Yu 2025（5% 标签≈全监督）。

## SleepGPT 集成要点（v5 设计说明第 7、9 节 + 精读补充）

- 输入：`backbone_large_patch200`，`time_size=20`、`patch_size=200`、`decoder_features=768`，官方支持 4 通道（EMG/EOG/Fpz-Cz/Pz-Oz）或 8 通道；取 epoch embedding（不用其自带 Swin 分期头）。权重 Figshare 10.6084/m9.figshare.30626870，代码 github.com/LordXX505/SleepGPT，`use_triton=False` Mac 走 MPS。
- **Sleep-EDF 单导 vs SleepGPT 多通道**：其通道分析显示 Pz 权重最高、单 Pz 使 N1 F1 +15.6——单 Fpz-Cz 性能需实测（v5 风险清单第一条）。
- **其在 EDF-78 的确切数字在补充表 7**（正文未给）——对标前回查。
- 消融开关表（v5 设计说明第 6 节）：HEAD=proto/linear、ADAPT=vpt/frozen/full、DEPTH=expect/regress、LAMBDA_BIN、USE_DEPTH_INPUT、REM_SEPARATE、N_DEPTH_BINS。

## 待补实验（多篇论文共识做法，审稿差异化）

1. **跨库外部验证行**（SHHS/MASSES/MASS 直迁+微调；直迁 κ 掉 0.2–0.4 是领域常态，写了才可信）。
2. **重复 CV 报 ±SD**（固定折 ×3）。
3. **泄漏自查声明**（SleepGPT 预训练库含 SleepEDF-78！——需按 SleepGPT 论文方式报告非重叠受试者子集成绩，这是 v5 特有的必查项）。
4. 参数量 + 推理延迟报告（VPT 可训练参数量远小于 134M 是卖点，量化它）。
5. N1 F1 单独汇报并对照人类 63% 一致性。
