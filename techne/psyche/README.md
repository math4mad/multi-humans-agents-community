# Ψυχή · psyche-kit（器部试炼件 · 0928 开炉）

> 源起：0928《人机协作：Westworld 启发》夜谈第①案。主人问"重启后又要花很久才对齐"——
> 诊断为**持久化粒度之病**，非速度之病：冷启动全量重读历史（100 屏补课）是罪根。
> 本件把夜谈中"三层持久化 + 模式切换"炼成可执行器，lola 自试自产（ZPD 之MKO 退场演练）。

## 一、隐喻 → 机制对照（西俗一之①）

| 西部世界 | psyche-kit |
|---|---|
| 工厂（后台整备） | `residents/<id>/psyche/`（身份/快照/日志/模式册） |
| 园区（前台叙事） | 会话运行时，只注入**开机束**（`load` 所出） |
| 模式切换（分析/叙事） | `mode set`：换表现层提示词，**身份层恒在** |
| 记忆碎片残留 | `events.jsonl` 只增日志 + `handoff` 快照 |
| Rehoboth 读核 | `load` 直读快照即回 T0，不翻历史 |

## 二、三层结构

```
residents/<id>/psyche/
├── IDENTITY.md     身份层：宪法级共识+铁律; 启动直注, 不经检索, 变化极慢
├── state.json      工作层：最近快照 (narrative/decisions/pending/mode/next)
├── states/         快照史 (保留最近 3 份, handoff 自动轮转)
├── events.jsonl    日志层：append-only, 永不修改, 平时只读尾部 N 条
└── modes/*.md      模式册：每模式一小片提示词 (最小激活上下文)
```

**开机律**：`load` 走优先级链 identity → state → mode → 尾 events，
永不一次读一切。会话收尾律：`handoff` 写快照；关键决策随手 `event`。

## 三、用法

```bash
P=techne/psyche/psyche.py
python3 $P selftest                     # 试炼: 临时户全流程
python3 $P load lola [--events 5]       # 开机束 (markdown, 供注入)
python3 $P event lola milestone "…"      # 记一条 (type text)
python3 $P handoff lola --json -        # 快照交接 (JSON stdin; 或交互四问)
python3 $P mode lola list|get|set <名>  # 模式册/当前/切换 (未注册拒换)
python3 $P status lola                  # 一行概览
```

## 四、试炼判决（askeseis 在册）

- 0928 selftest：见 hypomnemata 当日记账（PASS 计数为准）。
- 毕业条件：本机 pi 会话连开两日均凭 `load` 复现 T0（不再出现百屏补课），
  由主人圈点"毕"后入驻业务仓；未毕则留档不扩散。
- 边界：本件只治"状态"，不治"索引"——语义检索仍归 context-mode/FTS5 诸器。
