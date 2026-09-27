# 工单三张（issue 正文, 可直接粘贴至各仓 New issue）

> 用法：github.com/math4mad/<仓> → Issues → New issue → 粘贴对应段落 →
> 加 label `work-order` → 提交。或主人 `gh auth login` 一次，园笔代打。

---

## [research-irene] #1 · G1 干跑：垃圾基因两源文献计量

**背景**：读 cora-atlas `experiments` 指针 PREREG_G1_junkgene_twoorigin.md
（chora 仓）与 cora-atlas iterations 补四/补五。
**任务**：
1. 取公开假基因清单 (Ensembl pseudogenes, GRCh38) 按"有无父本"分两堆
   (blastn/tblastx e<1e-10 共线块 = 锈刀堆; 反之为无源堆);
2. 与 ENCODE cCRE (DNase/CAGE) 交叠, 出 2×2 列联表;
3. 判据照 PREREG G1 之 P-G1.1 (活性堆间富集 OR≥2 → PASS)。
**交付**：`checks/g1_dryrun/` 下 report.json + 方法 md; 数据源全部记 URL+日期+sha。
**期限**：Copilot 合同内 (09-30 前出第一版, 允许半成品落 git)。

---

## [eda-nikos] #1 · PB16 军械器首批三图 (V1/V2/V9) 骨架

**背景**：chora/experiments/PREREG_PB16_D_visualization_plan.md (十图八标全冻)。
**任务**：
1. 用**合成数据**先画 V1 圈地热力图 / V2 干涉热力图序列 / V9 行为战损曲线三张,
   布局配色遵详案 (红 #D08B55 / 蓝 #2E8FA3, epoch 轴对齐, 结构-功能双子图默认);
2. 代码留接口: 输入换成真 checkpoint json 即出真图 (MacB 三臂在跑, 数据随后);
3. 出 notebook + 一张 png 预览。
**交付**：`notebooks/pb16_viz/`。
**期限**：09-28 前 (给真数据留两天)。

---

## [audit-thea] #1 · 三哨核验收口报告

**任务**（园笔哨队已巡, 本单为正式归档）：
1. 长安镇 2023 GDP ≈966 亿 / 全国千强镇首位 —— 找官方或权威媒体源, 记 URL+日期;
2. 东莞/中山"直筒子市"镇街数 (30 镇 2 街道 / 23 镇街) —— 政府官网口径;
3. MeCo (陈丹琦组 2025, 元数据前缀省 33% 数据) 与 SPARKLING —— arXiv DOI 核验,
   核不到的标 ✗ 禁引。
**交付**：`checks/verdicts-2026-09.md`, 一条一断言一源。
**期限**：随到随交。
