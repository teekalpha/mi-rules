# MiRules

基于 [Subconverter](https://github.com/tindy2013/subconverter) 的自定义规则与路由分流策略项目，针对高度定制化的网络环境（包含 AI、TikTok 专线等）设计。

## 📍 策略组架构

默认生成的客户端配置（如 Clash）包含以下 11 个策略组，满足精细化路由需求：

1. **🚀 代理节点**（基础节点池，包含所有可用节点）
2. **🏠 家宽节点**（手动指定用于对原生 IP 要求极高的节点）
3. **🔵 Meta 服务**（默认：`🏠 家宽节点`，Facebook、Instagram、WhatsApp、Muse、Quest 等共用出口）
4. **🎵 TikTok**（默认：`🏠 家宽节点`，备用：代理节点/直连）
5. **🤖 AI 服务**（默认：`🏠 家宽节点`，备用：代理节点/直连）
6. **🎙️ 会议直播**（默认：`🚀 代理节点`，备用：家宽节点/直连）
7. **🔍 Google**（默认：`🚀 代理节点`，备用：家宽节点/直连）
8. **Ⓜ️ 微软服务**（默认：`DIRECT`，备用：代理节点/家宽节点）
9. **🇺🇳 国外网站**（默认：`🚀 代理节点`，备用：家宽节点/直连）
10. **🇨🇳 国内网站**（默认：`DIRECT`，备用：代理节点/家宽节点）
11. **🐟 规则之外**（默认：`DIRECT`，备用：代理节点/家宽节点）

## 📁 目录及规则说明

- **/rules**：分类规则集 (.list)
  - `Private.list`: 私网/本地网络 (最高优先级，恒定直连，规则链最前置以减少匹配开销)
  - `Meta.list`: Meta 系服务 (Facebook、Instagram、WhatsApp、Muse、Meta AI、Quest 等)，包含 Android 包名和 Meta ASN 的无域名连接
  - `AI.list`: AI 产品及认证、资源、MCP、下载依赖 (OpenAI、Claude、Grok、Cursor、Copilot、Windsurf、Hugging Face 等)
  - `TikTok.list`: 字节跳动海外及全系短视频平台 CDN
  - `Meeting.list`: 在线视频会议与直播服务 (Zoom, Google Meet, Teams, Discord, Slack, Twitch, VooV 等)
  - `Google.list`: Google 核心服务与 YouTube 系媒体
  - `Developer.list`: GitHub / Actions / Packages、包管理器、容器、VS Code / JetBrains 与前端资源；位于微软规则之前，归入“国外网站”
  - `Microsoft.list`: 微软核心服务 (Office, OneDrive, Azure 等)
  - `Media.list`: 国际主流流媒体 (Netflix, Disney+, Spotify 等)
  - `HomeProxy.list`: 家宽专用服务 (Reddit, 以及 PayPal、Stripe、风控主机商等高防欺诈要求平台)
  - `Proxy.list`: 综合性墙外服务 (其他社交、效率工具、新闻等；开发者和长尾 AI 已分别归入专用规则集)
  - `Direct.list`: 国内互联网服务 (阿里/腾讯/百度等) 及特殊白名单

- **/base**：基础配置文件
  - `pref.ini`: Subconverter 全局配置入口，已集成上述所有的策略组和规则集，开箱即用。Meta 服务规则位于家宽、AI 和通用域名规则之前；所选节点支持 UDP 时，也覆盖 Android 应用无域名的 UDP 连接。

## 🚀 使用方法

### 在线使用 (Clash 等客户端订阅)

将你在用的节点订阅链接，配合本项目的 `base/pref.ini` 传入 Subconverter 的转换接口。

例如：

```text
https://xxx.subconverter.api/sub?target=clash&url=<你的节点订阅网址>&config=https://raw.githubusercontent.com/teekalpha/MiRules/main/base/pref.ini
```

### 本地检查

使用 Python 3，无额外依赖：

```bash
python3 scripts/check-rules.py
python3 tests/test-routing.py -v
```

第一项校验全部规则的格式、CIDR、重复项、策略关联和最终兜底；第二项检查重点业务域名、动态子域、地址边界与分流优先级。测试匹配器不模拟外部 GeoSite / GeoIP / ASN 数据库。

如已安装 Mihomo，可把测试配置输出到仓库外的临时目录，并检查内核兼容性：

```bash
python3 scripts/check-rules.py --config /tmp/mi-rules-check/config.json
mihomo -t -d /tmp/mi-rules-check/profile -f /tmp/mi-rules-check/config.json
```

测试配置仅用 DIRECT 占位来校验规则，不能作为实际代理配置使用。首次检查可能下载地理数据库。仓库不包含 Docker 调试环境；上述检查也不替代 Subconverter 实际转换、客户端订阅刷新与业务连接验收。

## 维护原则与来源

- `DOMAIN-SUFFIX` 已覆盖根域及任意层级子域；MiRules 不需要逐个复制电信清单中的静态子域名。共享 Azure、S3、Cloudflare 等仅加入产品专用主机，避免整片云厂商资源误分流。
- AI 产品及其依赖先于通用开发者规则；原长尾 AI 从“国外网站”归入“AI 服务”，默认出口相应为家宽。Gemini 继续归入 Google，Meta 继续使用原专属分组。
- 开发者规则先于 `microsoft.com`，保证 VS Code / Playwright 更新下载不会被微软默认直连提前匹配；普通 Office / OneDrive 保留原策略。
- Google Play 使用正确的 `xn--ngstr-lra8j.com`，删除历史错误拼写 `xn--ngstr-lra8z.com`；Google API 与下载域名同组。实际下载还需客户端 DNS、节点与 UDP 等网络条件配合验证。
- TikTok 使用显式域名、应用进程和 `GEOSITE,tiktok` 补充；默认 GeoIP 数据库没有可核实的 tiktok 分类，移除该无效引用。
- Anthropic 当前入站段为 `160.79.104.0/23`、`153.61.224.0/22`、`2607:6bc0::/48`；保留旧 `209.249.57.0/24` 兼容项。未混入官方 Outbound 段，原 IPv6 `/32` 已纠正。
- 保留原有影音、网盘等规则。模型、镜像、包和更新下载属于必要业务；需要控制带宽时在实际网络侧设置优先级或限速。

主要核对来源（2026-11-19）：

- [OpenAI 官方网络要求](https://help.openai.com/en/articles/9247338-network-recommendations-for-chatgpt-errors-on-web-and-apps)
- [Claude Code 网络配置](https://code.claude.com/docs/en/network-config)、[Anthropic 官方 IP](https://platform.claude.com/docs/en/api/ip-addresses)
- [Cursor 企业网络要求](https://prod.cursor.com/docs/enterprise/network-configuration)、[Windsurf / Devin 网络排障](https://docs.devin.ai/desktop/troubleshooting/windsurf-common-issues)
- [GitHub 官方动态域名目录](https://api.github.com/meta)、[VS Code 官方网络要求](https://code.visualstudio.com/docs/setup/network)、[Docker 官方允许列表](https://docs.docker.com/desktop/setup/allow-list/)
- [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community/tree/master/data)、[blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script/tree/master/rule/Clash) 用于比对独立资源域名；不机械照搬社区全部条目。
- [Mihomo 规则语法](https://wiki.metacubex.one/config/rules/)、[MetaCubeX Geo 数据](https://github.com/MetaCubeX/meta-rules-dat)

## 进度与交接

2026-11-19：已补齐 AI、TikTok Shop、Google Play 与开发者依赖，并修正开发者 / 微软优先级。静态规则检查、关键业务分流回归和 Mihomo v1.19.34 全量规则内核检查通过（含 TikTok GeoSite、Telegram / CN GeoIP、ASN 数据加载）。检查使用本地规则展开配置，未执行 Subconverter 远程转换、实际业务连接或现场带宽验收。

本轮改动合并为一个本地提交，未推送或配置任何线上设备；已有飞书清单和 CSV 本轮未修改。下一步发布需要推送本仓库，刷新订阅后验证 TikTok、Claude/ChatGPT、Google Play 下载与 GitHub/IDE 业务链路。
