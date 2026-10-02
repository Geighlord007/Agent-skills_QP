# 混合协议全规格：jev 主跑 + ZCode 会话接管

适用：jev 在某个控件上卡住（DOM 读取器看不见、模型反复打转），但任务整体仍适合 jev 驱动。接管者是当前 ZCode 会话——读截图、给坐标/文本，零额外 API。

## 协议机制

```
jev 跑任务 ── BLOCKED / 重复3次无变化自动blocked / 预算异常
   │
   ▼
runner 存证：.escalate/escalate_N.png（Page.captureScreenshot）
             .escalate/NEED_ACTION（json：原因/URL/最后动作）
   │
   ▼
runner 轮询 .escalate/action.json（300s 窗口，1.5s 间隔）
   │                                    ▲
   ▼                                    │
ZCode 会话：读截图 → 判断 → 写 action.json
   │
   ▼
runner 执行动作序列 → 存 after_N.png → 删 action.json
   │
   ▼
重置 agent.state["status"] = "ready" → 再调 agent.run() → jev 无缝续跑
   （predict 里的 fresh() 检查会自动重观察被外部改变过的页面）
```

## action.json 格式

```json
{"actions": [
  {"type": "click", "x": 433, "y": 247, "ms": 800},
  {"type": "type", "text": "布宜诺斯艾利斯", "ms": 300},
  {"type": "keypress", "key": "Enter"},
  {"type": "scroll", "x": 560, "y": 390, "dy": 500},
  {"type": "wait", "ms": 1200},
  {"type": "screenshot", "name": "mid.png"}
]}
```
结束接管（剩余步骤会话自己做完时）：`{"type": "finish"}` → runner 进入手动模式，继续消费 action.json 直到再收 finish。

## 坐标铁律（最容易翻车的一条）

**截图像素 ≠ 点击坐标。** `Input.dispatchMouseEvent` 用 CSS 像素；截图是物理像素（受 DPR 影响，direct Chrome 实测 DPR=1.5）。动手前跑 `check_viewport.py`：

```python
window.innerWidth / devicePixelRatio  →  换算比例
点击坐标 = 截图坐标 × (innerWidth / 截图宽度)   ≈  截图坐标 ÷ DPR
```

## 现成脚本（D:\CSsoftware\jev-ultrafast\ 项目根，直接引用勿复制）

- `hybrid_ctrip.py` — 完整 runner：jev 主跑 + 升级协议 + 续跑。携程表单 GOALS 已内置；换任务改 `URL`/`GOALS`/`TYPESAFE_DROP_LABELS` 即可。启动：`uv run --env-file .env-direct python hybrid_ctrip.py`（后台跑），看到 `ESCALATION N` 就接管。
- `manual_finish.py` — 纯接管通道：附身 daemon 默认会话的现有标签页（页面状态不重建），同一 action.json 协议。runner 崩了/想跳过 jev 时用它收尾。
- `check_viewport.py` — 查 CSS 视口 / DPR / 当前页面状态。

## 续跑语义（为什么"重置 status"就能续）

jev 的 `Agent.run()` 在 `status in {done, blocked}` 时结束生成器，且 predict 对停止状态报错。但 Agent 对象持有同一 browser 会话——把 `state["status"]` 重置 `"ready"` 后再调 `run()`，predict 的 `fresh()` 检查发现页面指纹变了会自动重新 observe，决策基于新状态继续。外部动作（click/type）不进 jev 的 history，不影响它的预算计数。

## 升级触发要克制

只在这三种情况升级：模型返回 BLOCKED、"重复 3 次无变化"自动 blocked（jev 自带检测）、预算异常。每步小动作都升级会把 jev 的成本优势抹平——那是给兜底角色的口粮，不是主食。

## 无人值守变体

当前协议的接管者 = ZCode 会话（在场才有效）。做 cron 无人值守时把接管者换成 API 视觉模型：BLOCKED → 截图 → VLM 返回坐标（提示词："找到 X 控件，返回其中心坐标 JSON"）→ 执行 → 续跑，全程进程内闭环。推荐国内直连的视觉款（如 Qwen-VL / GLM 视觉款），按次几厘钱。
