#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ψυχή · psyche-kit —— 园笔三层持久化与模式切换器（器部试炼件）

出处：0928 西俗夜谈（Westworld 启发）第①案。
隐喻映射：
  工厂 (后台) = residents/<id>/psyche/  —— IDENTITY.md / state.json / events.jsonl / modes/
  园区 (前台) = 会话运行时             —— 只加载当前模式所需的最小提示词
三层：
  身份层 IDENTITY.md   几乎不变, 启动直注, 不经检索
  工作层 state.json    每次 handoff 更新的快照 (T0 复位凭此)
  日志层 events.jsonl  append-only, 永不修改, 按需检索尾部
律：
  启动不读一切 —— load 走优先级链: identity -> state -> mode -> 尾部 N 条 event
  模式切换不换魂 —— identity 恒在, 只换 modes/<name>.md 表现层

用法 (workspace 默认 residents/<id>/psyche, 可 --home 覆写):
  psyche.py load    [id] [--events N]      打印开机束 (markdown, 供注入 system/context)
  psyche.py event   [id] TYPE TEXT         追加一条事件
  psyche.py handoff [id] [--json FILE|-]    写新工作快照 (stdin JSON 或交互字段)
  psyche.py mode    [id] list|get|set [名]  模式册/当前/切换
  psyche.py status  [id]                    一行概览
  psyche.py selftest                        器部试炼: 临时户全流程自检
仅标准库。零依赖, 可携。
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
KEEP_STATE_HISTORY = 3


def ws(resident: str, home: str | None) -> Path:
    return Path(home) if home else REPO / "residents" / resident / "psyche"


def now() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def load_state(d: Path) -> dict:
    f = d / "state.json"
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            sys.stderr.write(f"[psyche] state.json 损坏: {e} —— 以空快照续\n")
    return {}


def append_event(d: Path, etype: str, text: str) -> dict:
    ev = {"ts": now(), "type": etype, "text": text}
    d.mkdir(parents=True, exist_ok=True)
    with (d / "events.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(ev, ensure_ascii=False) + "\n")
    return ev


def tail_events(d: Path, n: int) -> list[dict]:
    f = d / "events.jsonl"
    if not f.exists() or n <= 0:
        return []
    out = []
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            out.append({"ts": "?", "type": "corrupt", "text": line})
    return out[-n:]


def modes_dir(d: Path) -> Path:
    return d / "modes"


def cmd_load(a) -> None:
    d = ws(a.resident, a.home)
    identity = read_text(d / "IDENTITY.md")
    state = load_state(d)
    mode = state.get("mode", "")
    print("# ── 开机束 · Ψυχή (T0 复位) ──\n")
    print("## 身份层 (恒注, 不经检索)\n")
    print(identity or "(无 IDENTITY.md —— 工厂未立户)")
    print("\n## 工作层 (最近快照)\n")
    if state:
        print(f"- updated: {state.get('updated','?')}  session: {state.get('session','-')}")
        print(f"- narrative: {state.get('narrative','(空)')}")
        for k, label in (("decisions", "已决"), ("pending", "待办")):
            items = state.get(k, [])
            if items:
                print(f"- {label}: " + " / ".join(items))
        if state.get("next"):
            print(f"- 下一步: {state['next']}")
    else:
        print("(无 state.json —— 首次开机, 建议会话收尾立 handoff)")
    print("\n## 模式层 (当前表现)\n")
    if mode and (modes_dir(d) / f"{mode}.md").exists():
        print(read_text(modes_dir(d) / f"{mode}.md"))
    else:
        print(f"(模式: {mode or '未立'} —— 身份不变, 无附加表现层)")
    evs = tail_events(d, a.events)
    if evs:
        print(f"\n## 日志层 (尾 {len(evs)} 条, 余者按需检索 events.jsonl)\n")
        for e in evs:
            print(f"- [{e['ts']}] {e['type']}: {e['text']}")


def cmd_event(a) -> None:
    d = ws(a.resident, a.home)
    ev = append_event(d, a.etype, a.text)
    print(json.dumps(ev, ensure_ascii=False))


def cmd_handoff(a) -> None:
    d = ws(a.resident, a.home)
    d.mkdir(parents=True, exist_ok=True)
    if a.json_in:
        raw = sys.stdin.read() if a.json_in == "-" else Path(a.json_in).read_text(encoding="utf-8")
        patch = json.loads(raw)
    else:
        patch = {}
        for key, prompt in (
            ("narrative", "narrative 局势一句话> "),
            ("next", "next 下一步> "),
        ):
            v = input(prompt).strip()
            if v:
                patch[key] = v
        ds = input("decisions 已决(分号分隔, 可空)> ").strip()
        if ds:
            patch["decisions"] = [x.strip() for x in ds.split(";") if x.strip()]
        pd_ = input("pending 待办(分号分隔, 可空)> ").strip()
        if pd_:
            patch["pending"] = [x.strip() for x in pd_.split(";") if x.strip()]
    old = load_state(d)
    state = {
        "resident": a.resident,
        "updated": now(),
        "session": patch.get("session", old.get("session", "")),
        "mode": patch.get("mode", old.get("mode", "")),
        "narrative": patch.get("narrative", old.get("narrative", "")),
        "decisions": patch.get("decisions", old.get("decisions", [])),
        "pending": patch.get("pending", old.get("pending", [])),
        "next": patch.get("next", old.get("next", "")),
    }
    hist = d / "states"
    hist.mkdir(exist_ok=True)
    if (d / "state.json").exists():
        stamp = (old.get("updated") or now()).replace(":", "").replace("+", "Z")
        shutil.copy2(d / "state.json", hist / f"state-{stamp}.json")
        snaps = sorted(hist.glob("state-*.json"))
        for stale in snaps[:-KEEP_STATE_HISTORY]:
            stale.unlink()
    (d / "state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    append_event(d, "handoff", f"工作快照更新: {state['narrative'][:80]}")
    print(json.dumps(state, ensure_ascii=False))


def cmd_mode(a) -> None:
    d = ws(a.resident, a.home)
    md = modes_dir(d)
    if a.op == "list":
        files = sorted(p.stem for p in md.glob("*.md")) if md.exists() else []
        cur = load_state(d).get("mode", "")
        print("\n".join(("* " if f == cur else "  ") + f for f in files) or "(模式册为空)")
    elif a.op == "get":
        cur = load_state(d).get("mode", "")
        print(cur or "(无模式)")
        if cur and (md / f"{cur}.md").exists():
            print(read_text(md / f"{cur}.md"))
    elif a.op == "set":
        if not a.name:
            sys.exit("mode set 需模式名")
        target = md / f"{a.name}.md"
        if not target.exists():
            sys.exit(f"[psyche] 模式未注册: {a.name} (modes/ 无此 md) —— 拒换, 免得当机")
        state = load_state(d)
        old = state.get("mode", "")
        state["mode"] = a.name
        state["updated"] = now()
        (d / "state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        append_event(d, "mode", f"模式切换 {old or '∅'} → {a.name} (身份层未动)")
        print(f"mode: {old or '∅'} → {a.name}")
    else:
        sys.exit(f"未知 mode 操作: {a.op}")


def cmd_status(a) -> None:
    d = ws(a.resident, a.home)
    state = load_state(d)
    n_ev = sum(1 for _ in (d / "events.jsonl").open(encoding="utf-8")) if (d / "events.jsonl").exists() else 0
    print(f"{a.resident}: mode={state.get('mode','-')} updated={state.get('updated','-')} "
          f"events={n_ev} identity={'有' if (d/'IDENTITY.md').exists() else '无'}")


def cmd_selftest(_a) -> None:
    tmp = Path(tempfile.mkdtemp(prefix="psyche-test-"))
    try:
        d = tmp / "psyche"
        d.mkdir(parents=True)
        (d / "IDENTITY.md").write_text("# IDENTITY\n我是测试户, 律: 结构化表达。\n", encoding="utf-8")
        (d / "modes").mkdir()
        (d / "modes" / "forge.md").write_text("【锻炉模式】只谈器与靶。\n", encoding="utf-8")
        (d / "modes" / "ledger.md").write_text("【帐房模式】只记账与提醒。\n", encoding="utf-8")
        checks = []

        def ck(name, cond):
            checks.append((name, bool(cond)))

        ev = append_event(d, "birth", "立户")
        ck("event 追加落盘", (d / "events.jsonl").exists() and ev["ts"])
        state = {"narrative": "造器中", "decisions": ["三层定"], "next": "试"}
        (d / "state.json").write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
        ck("state 可读", load_state(d)["narrative"] == "造器中")
        tail = tail_events(d, 1)
        ck("尾检索只取 N", len(tail) == 1 and tail[0]["type"] == "birth")
        ck("模式注册校验", (d / "modes" / "forge.md").exists() and not (d / "modes" / "nope.md").exists())
        for _ in range(5):
            append_event(d, "tick", "x")
        ck("事件只增", len((d / "events.jsonl").read_text(encoding='utf-8').splitlines()) == 6)
        bad = 0
        for name, ok in checks:
            print(("PASS " if ok else "FAIL ") + name)
            bad += (not ok)
        print(f"selftest: {len(checks)-bad}/{len(checks)} " + ("✅ 过关" if bad == 0 else "❌ 带病"))
        sys.exit(1 if bad else 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> None:
    ap = argparse.ArgumentParser(prog="psyche.py", description="Ψυχή · 三层持久化与模式切换 (工厂侧)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p):
        p.add_argument("resident", nargs="?", default="lola")
        p.add_argument("--home", default=None, help="覆写 workspace 路径")

    p = sub.add_parser("load"); common(p); p.add_argument("--events", type=int, default=5); p.set_defaults(fn=cmd_load)
    p = sub.add_parser("event"); common(p); p.add_argument("etype"); p.add_argument("text"); p.set_defaults(fn=cmd_event)
    p = sub.add_parser("handoff"); common(p); p.add_argument("--json", dest="json_in", default=None); p.set_defaults(fn=cmd_handoff)
    p = sub.add_parser("mode"); common(p); p.add_argument("op", choices=["list", "get", "set"]); p.add_argument("name", nargs="?"); p.set_defaults(fn=cmd_mode)
    p = sub.add_parser("status"); common(p); p.set_defaults(fn=cmd_status)
    p = sub.add_parser("selftest"); p.set_defaults(fn=cmd_selftest)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
