# MiRules

基于 [Subconverter](https://github.com/tindy2013/subconverter) 的自定义规则与路由分流策略项目，针对高度定制化的网络环境（包含 AI、TikTok 专线等）设计。

## 📍 策略组架构

默认生成的客户端配置（如 Clash）包含以下 8 个策略组，满足精细化路由需求：

1. **♻️ 手动切换**（基础节点池，包含所有可用节点）
2. **🏠 家宽代理**（手动指定用于对原生 IP 要求极高的节点）
3. **🎵 TikTok**（默认：`♻️ 手动切换`，备用：直连/家宽）
4. **🤖 AI 服务**（默认：`♻️ 手动切换`，备用：直连/家宽）
5. **🔍 Google**（默认：`♻️ 手动切换`，备用：直连/家宽）
6. **🇺🇳 国外网站**（默认：`♻️ 手动切换`，备用：直连/家宽）
7. **🇨🇳 国内网站**（默认：`DIRECT`，备用：手动切换/家宽）
8. **🐟 规则之外**（默认：`DIRECT`，备用：手动切换/家宽）

## 📁 目录及规则说明

- **/rules**：分类规则集 (.list)
    - `AI.list`: 核心 AI 基础设施 (OpenAI, Claude, Grok, Manus, Cursor 等)
    - `TikTok.list`: 字节跳动海外及全系短视频平台 CDN
    - `Google.list`: Google 核心服务与 YouTube 系媒体
    - `Media.list`: 国际主流流媒体 (Netflix, Disney+, Spotify 等)
    - `Proxy.list`: 综合性墙外服务 (社交、效率工具、新闻、开发者服务以及长尾 AI 工具)
    - `Direct.list`: 国内互联网服务 (阿里/腾讯/百度等)、私有网络及特殊白名单

- **/base**：基础配置文件
    - `pref.ini`: Subconverter 全局配置入口，已集成上述所有的策略组和规则集，开箱即用。

## 🚀 使用方法

### 在线使用 (Clash 等客户端订阅)

将你在用的节点订阅链接，配合本项目根目录的 `pref.ini` 传入 Subconverter 的转换接口。

例如：
```text
https://xxx.subconverter.api/sub?target=clash&url=<你的节点订阅网址>&config=https://raw.githubusercontent.com/teekalpha/MiRules/main/base/pref.ini
```

### 本地开发与调试 (Docker)

如果你需要自行增删规则并测试分流情况：

1. 启动本地调试环境（使用 Nginx 和 Subconverter 本地实例，不污染远程）：
   ```bash
   docker compose up -d
   ```
2. 本地测试用的虚拟订阅与本地规则调用：
   ```text
   http://localhost:25500/sub?target=clash&url=http://rules-server/test-sub.txt
   ```
3. 修改任何 `.list` 规则保存后，直接在客户端刷新订阅即可验证测试，无需重启容器。
