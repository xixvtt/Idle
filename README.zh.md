<div align="center">

🌐 [English](README.md) | **中文** | [Español](README.es.md) | [한국어](README.ko.md) | [Português](README.pt-BR.md)

# Idle — Claude Code Token 监控器

**一款 macOS 上的实时 token 用量监控悬浮窗，专为 [Claude Code](https://claude.com/claude-code) 设计。**
桌面右上角飘一个小毛玻璃胶囊，让你随时看到所有 Claude Code session 的实时 token 消耗 — 不用切窗口、不用刷新、不用 API key。

<img src="docs/images/hero.png" alt="Idle Claude Code token 监控器悬浮在 macOS 桌面" width="720" />

[![Last commit](https://img.shields.io/github/last-commit/xixvtt/Idle)](https://github.com/xixvtt/Idle/commits/main)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

</div>

---

## Idle 是什么

Idle 是一款免费开源的 **Claude Code token 用量监控工具**。半透明悬浮窗常驻 macOS 桌面，实时追踪：

- **今日累计 token** — 所有 session、所有项目的总和，实时刷新
- **活跃 session 监控** — 一眼看清哪个 workspace 正在跑、在等待、还是空闲
- **多 session 堆叠** — 每个 Claude Code 窗口一行展示
- **任务完成提醒** — Claude 一搞定任务立刻提示

如果你也是 **YOLO 模式**用 Claude Code，刷刷刷一上午发现"额度用完了"，Idle 就是解药。零浏览器 tab、零 dashboard、零 API key — 桌面上一眼就懂。

<div align="center">
  <img src="docs/images/solo.png" alt="Idle 静止态显示今日 Claude Code token 累计" width="380" />
</div>

## 为什么需要 Idle

| 痛点 | Idle 怎么解 |
|---|---|
| Anthropic 不显示每日 token 用量 | Idle 读本地 Claude Code transcript，实时累加今日总数 |
| 同时开多个 `claude` session 根本算不清 | Idle 把每个活跃 session 一行展示在悬浮窗里 |
| 等到 Claude 直接停止响应才知道超了 | Idle 始终显示实时 token，可控可预警 |
| 其他监控工具要 API key、要传数据上云 | Idle 100% 本地运行 — 零外网请求、零 API key |

## 安装（零配置）

下载最新版本：**[Releases 页面 →](https://github.com/xixvtt/Idle/releases)**

| Mac 类型 | 下载文件 |
|---|---|
| Apple Silicon (M1/M2/M3/M4) | `Idle-x.x.x-arm64.zip` |
| Intel | `Idle-x.x.x-x64.zip` |

1. 双击 zip 解压出 `Idle.app`
2. **右键 `Idle.app` → 打开 → 打开**（app 未签名，Gatekeeper 会弹一次）
3. 首次启动选择主题（System / Light / Dark）
4. 正常使用 Claude Code，token 追踪立即生效

不用装 Python、不用打开 terminal、不用改 JSON。Idle 自带的 daemon 和 Claude Code hooks 全自动安装。

### 报错 "Apple 无法验证 Idle 不含恶意软件"

新 macOS Gatekeeper 拦截未签名 app。terminal 跑一行命令清掉 quarantine 标记：

```bash
xattr -cr /Applications/Idle.app
# 或者你解压到别处：
xattr -cr ~/Downloads/Idle.app
```

然后双击 `Idle.app` 即可。

如果还是不行，**系统设置 → 隐私与安全性**，拉到底会看到 "Idle 已被阻止…" 旁边有 **仍要打开** 按钮，点一次就行。

> 未来版本会做正式的 Apple 代码签名 + 公证（每年 $99 开发者会员），到时这些步骤就消失了。当前先用 ad-hoc 签名应付。

## 系统要求

- macOS 12 或更新
- 安装好 [Claude Code](https://claude.com/claude-code)

## Idle 的工作原理（技术细节）

Idle 只读两个本地数据源：

1. **Claude Code hooks** — Claude Code 每次工具调用、权限请求、任务完成都会触发 shell hook。Idle 自带的 daemon 在 `127.0.0.1:7777` 接收事件，实时更新 session 状态。
2. **Transcript JSONL 文件** — Claude Code 把会话写到 `~/.claude/projects/`。Idle 只解析每条 assistant message 里的 `usage` 字段（input + output + cache_creation token），按本地时区过滤"今天"。

启动时全盘扫描一遍，之后每 30 秒 rescan + 每次 hook 触发也 rescan，token 总数永远准确，重启 daemon、重启 Idle 都不丢数。

## 隐私

- **零外网请求** — Daemon 只绑 `127.0.0.1`
- **不需要 API key** — Idle 不调用 Anthropic API
- **永不读取 prompt / 回复内容** — 只读 token 数字字段，AST 单元测试强制保证
- **完全开源（MIT 协议）** — 代码自己审

## 给这个 repo 点个 ⭐

如果 Idle 帮你省了时间或 token，请给 repo 点个 star — 这是让更多 Claude Code 用户发现 Idle 最有效的方式。欢迎提 issue、PR、反馈意见。

---

**关键词:** Claude Code, Claude Code token 监控, Claude Code 用量追踪, Anthropic token 用量, Claude Code dashboard, Claude Code session 管理, Claude Code 限额监控, Claude Code macOS, Claude Code 悬浮窗, AI 编程工具.
