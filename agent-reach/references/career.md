# 职场招聘

LinkedIn、Boss直聘。

## LinkedIn

```powershell
# 获取个人资料
mcporter call linkedin.get_person_profile linkedin_username="username" sections="experience,education"

# 搜索人才
mcporter call linkedin.search_people keywords="AI engineer" location="Shanghai"

# 获取公司资料
mcporter call linkedin.get_company_profile company_name="openai" sections="posts,jobs"

# 搜索职位
mcporter call linkedin.search_jobs keywords="software engineer" location="Remote" max_pages=2
```

> **需要登录**：首次使用前运行 `uvx mcp-server-linkedin@latest --login` 保存登录态。

### Fallback 方案

MCP 不可用时使用 Jina Reader：

```powershell
curl.exe -s "https://r.jina.ai/https://linkedin.com/in/username"
```

## Boss直聘

当用户说“帮我配 Boss直聘”时，按本节完成安装（需先获得安装授权后运行 `agent-reach install --env=local --system --channels=boss`）、启动专用 Chrome、等待用户手动登录和最终验证。不要把 9222 端口细节先甩给用户，也不要替用户输入账号、扫码或过滑块。

> **关键区分：登录门槛 ≠ 反爬安全校验**
> zhipin.com 落地后可能停在：已登录 `web/geek/job`、未登录 `web/user/`、或反爬**安全校验页**（URL 含 `security-check` / `zhipin-security` / `_security_check`）。安全校验页与登录无关（已登录且带 CDP 端口几乎必现）。**绝不用当前页 URL 判断登录态。**

> **双登录态存储（严格 CDP 模式下以浏览器为准）**
> 两个凭据存储**都不能删**，分别服务不同通道：
>
> | 存储 | 角色 |
> |---|---|
> | `~/.boss-agent/auth/session.enc` | ① `_get_browser()` 的前置读取门槛（读不到会报 `AuthRequired`）；② httpx 低危通道（`status`/`detail`/`cities`/`job_card_httpx`）使用的 cookies + stoken；③ **不是** CDP 复用 Chrome 搜索时的实际认证凭据 |
> | 专用 Chrome profile 内浏览器 cookie | CDP 模式下 `search` 等高危操作实际携带的凭据（以 `wt2` cookie 为准） |
>
> **`boss status` / `status --live` 只校验 `session.enc`**，不代表 CDP 浏览器已登录：
> 1. 拉起专用 Chrome 后，必须**暂停并让用户肉眼确认**右上角已有头像，确认后才允许搜索；
> 2. 以 `agent-reach doctor` 的浏览器 `wt2` cookie 探测为准；
> 3. **`AUTH_EXPIRED` 是未登录的 ground truth**：直接走登录流程 + `login --cdp`，不要解释成安全校验；
> 4. 不要删除 `session.enc`，刷新它请跑 `login --cdp`。

### 首选：直接调用本地 `boss` CLI

执行搜索时必须使用严格 CDP 模式（全局选项放在子命令之前）：

```powershell
# 体检（无副作用，不搜索）
agent-reach doctor

# 严格 CDP 搜索（串行、低频调用，不要无提示连续翻页）
boss --browser-source existing-browser --cdp-url http://localhost:9222 search "大模型" --city 深圳 --page 1
```

> **等待属预期，不是卡死**：连续搜索命中节流时，`boss-agent-cli` 可能静默等待 5–10 秒。等待窗口内不要重试、不要拉起新浏览器、不要切换 profile。

### 进阶：Python SDK 批量抓取 JD（仅在 CLI 不满足时）

由于 `pipx` / `uv tool` 为隔离环境，若需通过 Python SDK 调用 `job_card_browser()` 抓取完整 JD，请先将脚本写入系统临时目录（如 `$env:TEMP\boss_fetch.py` 或 `/tmp/boss_fetch.py`，避免在 PowerShell 使用 bash heredoc），再用已安装 `boss-agent-cli` 的解释器运行（若尚未安装再通过 `uv run --with boss-agent-cli python "$env:TEMP\boss_fetch.py"`，优先使用正式发行版而非每次拉取裸 git commit）：

```python
from pathlib import Path
from boss_agent_cli.api.client import AccountRiskError, BossClient, EnvironmentRiskError
from boss_agent_cli.auth.manager import AuthManager
from boss_agent_cli.platforms.zhipin import BossPlatform

auth = AuthManager(Path.home() / ".boss-agent")

# 严格 CDP 模式：复用已登录浏览器、CDP 失败立即抛错、永不 headless
with BossClient(
    auth,
    cdp_url="http://localhost:9222",
    browser_source="existing-browser",
) as boss:
    raw = boss.search_jobs("大模型", city="深圳", page=1)
    if raw.get("code") != 0:
        code, message = BossPlatform(boss).parse_error(raw)
        raise RuntimeError(f"{code}: {message}")
    for item in raw.get("zpData", {}).get("jobList", []):
        card = boss.job_card_browser(item["securityId"], item["lid"])
        post_desc = card.get("zpData", {}).get("jobCard", {}).get("postDescription", "")
        print(item.get("jobName"), post_desc)
```

### 环境体检与恢复（抓取前排查）

若 `agent-reach doctor` 报 boss 为 `off` 或 `warn`，按序排查：

1. **检查 CDP 端口**：
   ```powershell
   curl.exe -s http://localhost:9222/json/version   # 有 Browser 字段 = 端口通
   ```

2. **启动专用 Chrome**（仅绑定 `127.0.0.1`，长期复用该 profile，不切日常主 Chrome）：
   - Windows PowerShell：
     ```powershell
     Start-Process chrome.exe -ArgumentList "--remote-debugging-address=127.0.0.1","--remote-debugging-port=9222","--user-data-dir=$env:USERPROFILE\.boss-chrome-profile","https://www.zhipin.com/web/geek/job"
     ```
   - macOS：
     ```bash
     open -na "Google Chrome" --args --remote-debugging-address=127.0.0.1 \
       --remote-debugging-port=9222 --user-data-dir="$HOME/.boss-chrome-profile" \
       "https://www.zhipin.com/web/geek/job"
     ```
   - Linux：
     ```bash
     google-chrome --remote-debugging-address=127.0.0.1 \
       --remote-debugging-port=9222 --user-data-dir="$HOME/.boss-chrome-profile" \
       "https://www.zhipin.com/web/geek/job"
     ```

   **拉起后第一步：暂停并让用户肉眼确认窗口内已登录（右上角有头像）。**

3. **用户手动登录（未登录时）**：让用户在专用窗口登录或扫码，确认完成后保存 CDP 登录态：
   ```powershell
   boss --cdp-url http://localhost:9222 login --cdp
   agent-reach doctor
   ```
   若停在 `security-check` / `zhipin-security` 安全校验页，等待自动放行或让用户手动过滑块，不要误判为未登录。

4. **错误码处置**：
   - `AUTH_EXPIRED` → **ground truth** 浏览器未登录，直接走第 3 步登录 + `login --cdp`；
   - `code 36`（`ACCOUNT_RISK`）→ 立即停止，手动到 BOSS 页面处理，不自动重试；
   - `code 9`（`RATE_LIMITED`）→ 冷却后重试；
   - `code 37` + `环境存在异常` → `ENVIRONMENT_RISK`，立即停止，不刷新 Token、不重新登录、不自动重试；
   - `code 37` + 明确 token/stoken 过期 → `TOKEN_REFRESH_FAILED`，客户端最多自动刷新并重试一次，仍失败再重新登录。
