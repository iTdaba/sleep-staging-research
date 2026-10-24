# sleep-staging-research · 睡眠分期科研 Skill

睡眠分期（sleep staging）领域的 AI 科研助手技能：**查知识**（数据集/协议/SOTA/规则/谱系，全部带论文出处）+ **跑实验**（预处理/划分/评测/出图，脚本固化协议）。

## 组成

```
sleep-staging-research/
├── SKILL.md                 # 入口：触发条件、任务路由、快速路径、禁做清单
├── references/              # 按需加载的知识库（9 份）
│   ├── datasets.md          # 数据集卡片：Sleep-EDF/SHHS/MASS/ISRUC/CAP/MESA/HMC/DOD…+ 标准协议 + R&K→AASM
│   ├── sota-benchmarks.md   # 按 数据集×协议×通道 分组的排行表，每行带出处与可比性标注
│   ├── model-zoo.md         # 模型谱系：DeepSleepNet→…→WN-Sleep 主干 + 基础模型线（SleepGPT 等）+ 方法支线
│   ├── domain-facts.md      # 六大领域事实：N1 瓶颈、人类天花板、模态阶梯、域偏移、冻结骨干证据、规范趋势
│   ├── aasm-rules.md        # AASM 五分期规则速查、占比先验、通道-分期对应
│   ├── metrics-protocol.md  # 指标定义、十条协议红线、报告模板
│   ├── preprocessing.md     # 预处理流水线、类不平衡工具箱、常见坑
│   ├── wearable-branches.md # 可穿戴/非 EEG 模态分支基准
│   └── sleepsdim-walkthrough.md  # SleepSDIM 项目（CSDI/SleepGPT-EBC）上下文与待补实验
└── scripts/                 # 可独立运行的 CLI
    ├── check_env.py         # 依赖检查
    ├── sleepedf_prepare.py  # Sleep-EDF → 30s epoch npz（协议固化：100Hz/0.3-35Hz/±30min/标签映射）
    ├── cv_split.py          # 按受试者 k 折划分（断言无泄漏）
    ├── evaluate_staging.py  # acc/MF1/κ/逐类F1/混淆矩阵，逐折+mean±SD，md+csv
    └── plot_hypnogram.py    # 真值 vs 预测 hypnogram + 可选深度曲线
```

## 安装（已生效）

技能目录软链在 `~/.agents/skills/sleep-staging-research`。修改本仓库文件即实时生效；在新机器上安装：

```bash
git clone <本仓库地址> && cd <仓库名>
ln -sfn "$(pwd)/sleep-staging-research" ~/.agents/skills/sleep-staging-research
```

## 使用

在任意 ZCode/Claude 会话中直接提问即可触发，例如：

- "Sleep-EDF-78 上按受试者十折现在的 SOTA 是多少？"（→ sota-benchmarks.md）
- "帮我跑 Sleep-EDF 预处理和十折划分"（→ scripts）
- "N1 为什么这么难，有什么处理手段？"（→ aasm-rules.md + domain-facts.md）
- "SHHS 和 MASS 协议有什么区别？"（→ datasets.md）

## 知识来源

59 篇本地论文精读（Zotero 库，2020–2026，含 10 篇综述）+ Phan 2022 / Yang 2026 等公开综述与官方代码库核对。每个性能数字标注出处；引用规则与可信度分层见 `references/sota-benchmarks.md`。
