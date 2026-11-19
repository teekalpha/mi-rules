# MiRules

用于 Clash / Mihomo 的自定义分流规则，通过 [Subconverter](https://github.com/tindy2013/subconverter) 与节点订阅合并。

## 使用

将节点订阅填入 `url`，并用 `config` 指向 [base/pref.ini](base/pref.ini)。如果订阅地址带参数，先对整个地址做 URL 编码。

```text
https://<subconverter>/sub?target=clash&url=<编码后的节点订阅>&config=https://raw.githubusercontent.com/teekalpha/MiRules/main/base/pref.ini
```

在客户端的「家宽节点」「代理节点」中选好出口。Meta、TikTok 和 AI 服务默认选家宽，会议直播、Google 和国外网站默认选代理，微软、国内网站和未匹配流量默认直连。

Subconverter v0.9.0 的 `target=clash` 会省略 `IP-ASN` 规则。依赖 ASN 分流时，检查生成的配置是否包含这些规则。

## 维护

[base/pref.ini](base/pref.ini) 定义策略和首条匹配顺序，[rules/](rules/) 存放各分类规则。私网优先直连，AI 优先于通用开发者规则，开发者规则优先于微软通用后缀。Gemini 走 Google。

规则按服务分段，同一服务内按主站、认证、资源、遥测等用途排列。`DOMAIN-SUFFIX` 覆盖根域及各层子域，共享 CDN 和云存储优先用产品专用主机精确匹配。

## 验证

```bash
python3 scripts/check-rules.py
python3 tests/test-routing.py -v
```

本地测试只检查仓库规则。可用以下直连占位配置额外检查 Mihomo 能否加载规则和 Geo 数据库。

```bash
python3 scripts/check-rules.py --config /tmp/mi-rules-check/config.json
mihomo -t -d /tmp/mi-rules-check/profile -f /tmp/mi-rules-check/config.json
```
