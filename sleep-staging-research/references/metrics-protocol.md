# 指标定义与评测协议规范

## 指标定义

- **acc**：总体准确率。类不平衡下虚高（N2 占 50%），仅作辅助——领域使用率 98.8% 已被综述批评过度依赖（Yang 2026）。
- **MF1（macro-F1）**：各类 F1 的简单平均，对少数类敏感，**主指标之一**（SleepSDIM 主指标）。
- **Cohen's κ**：校正机会一致，不平衡稳健，**主指标之一**；设备验证文献公认最适合（De Gans 2024）。解释档位：>0.81 almost perfect / 0.61–0.80 substantial。
- **per-class F1 / Sensitivity / Specificity**：必报；N1 单独汇报。可补 per-class PR-AUC（WN-Sleep 做法，N1 仅 0.555）。
- **Spearman ρ / Pearson r**：回归任务（CSDI/SDI 深度值）与生物标志物相关。
- **Bland-Altman + ICC**：睡眠结构参数（TST/SE/WASO/REM%）与设备验证。
- 附加：MCC（Birrer 2024 推荐的无偏指标）、AUROC（基础模型论文习惯，如 SleepFM）。

## 协议红线（违反任何一条，数字即不可发表/不可比）

1. **按受试者划分（subject-wise）是最低标准**。同一受试者两夜分属训练/测试 = 泄漏（Sleep-EDF 每人恰好 2 夜，尤其危险）。心呼吸文献 14/35 仍用 epoch 级划分，指标显著膨胀（Chen 2026 的批评）。例外说明：历史文献中 record-wise（如 Nakamura 2020）数字降权使用。
2. **折数与验证集写明**：EDF-78 惯例 10 折（每折训练受试者内留 7 人验证）；EDF-20/ISRUC 惯例 20 折/LOSO；SHHS 惯例 70/30+100 验证。**重复 CV（固定折、≥3 次重复）报 mean±SD 优于单次点估计**（MSA-CNN 范式）。
3. **裁剪规则写明**："在床时段 ±30 min 的 W"（SleepTransformer 协议）vs "仅 in-bed" vs 不裁——可差数个点。
4. **R&K→AASM 转换声明**（N3/N4 合并、MOVEMENT/UNKNOWN 剔除）；MASS 的 20 s epoch 对齐方式声明。
5. **类别数声明**：5 类 / 4 类（W/Light/Deep/REM，N1+N2 合并）/ 3 类 / 唤醒二分——不同类别数绝不同表。
6. **通道数与导联声明**：单导 Fpz-Cz ≠ C4-A1 ≠ 多通道。
7. **从头训 vs 预训练/迁移声明**：跨库预训练初始化在 EDF-78 上 +3.5 acc（Phan 2022），不声明即误导。
8. **外部验证**：主表之外至少一行跨库测试（直迁 + 微调各一行）；基础模型必须自查预训练-测试受试者重叠（SleepGPT 范式）。
9. **人类一致性对照**：给出与评分员间一致率/κ 的相对位置。
10. **增强/过采样在划分之后、且只在训练折内执行**（MMS-SleepNet 反例）。

## 报告模板（论文实验节 / 结果表骨架）

```
数据集与协议：Sleep-EDF Expanded SC（78 受试者/153 夜），单导 Fpz-Cz，100 Hz，
  0.3–35 Hz 带通，30 s epoch；R&K→AASM（N3/N4 合并，MOVEMENT/UNKNOWN 剔除）；
  在床前后各 30 min 之外的 W 剔除；按受试者 10 折（每折 7 名验证受试者），
  重复 3 次，报 mean±SD。
输入与上下文：L=? 个 epoch（±? min）序列输入。
训练：Adam lr=?，batch=?，早停=?；预训练来源声明（无 / SHHS / SleepGPT）。
主表（5 类 W/N1/N2/N3/REM）：
  | 模型 | acc | MF1 | κ | W-F1 | N1-F1 | N2-F1 | N3-F1 | REM-F1 | 参数量 |
  | 人类参照 | ~80.6% 一致率 | | ~0.76 | | (63% 一致) | | | | |
外部验证：SHHS/MASS 直迁 acc=? → 微调(=?受试者) acc=?
泄漏自查：预训练数据与本测试无受试者重叠（或有，另行报告非重叠子集）。
```

对标数字来源：只取 `sota-benchmarks.md` 中同协议行；EDF-78 单导 10 折锚点 = SleepTransformer* 84.9/0.789/78.8（N1 48.5）。
