#!/usr/bin/env python3
"""校验本地规则，并按 pref.ini 顺序生成供 Mihomo 检查的离线测试配置。"""
import argparse
import ipaddress
import json
from pathlib import Path
import re
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DOMAIN_TYPES = {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD"}


def load_rules():
    rules, groups, used, seen = [], [], set(), set()
    for line in (ROOT / "base/pref.ini").read_text().splitlines():
        if line.startswith("custom_proxy_group="):
            groups.append(line.split("=", 1)[1].split("`", 1)[0])
        if not line.startswith("ruleset="):
            continue
        policy, source = line.split("=", 1)[1].split(",", 1)
        if source.startswith("[]"):
            entries = [("pref.ini", source[2:])]
        else:
            path = urlparse(source).path
            prefix = "/teekalpha/MiRules/main/"
            if not path.startswith(prefix):
                raise ValueError(f"未知规则源：{source}")
            local = ROOT / path[len(prefix):]
            used.add(local.resolve())
            entries = [(f"{local.name}:{n}", value.strip())
                       for n, value in enumerate(local.read_text().splitlines(), 1)
                       if value.strip() and not value.lstrip().startswith("#")]
        for origin, entry in entries:
            parts = entry.split(",")
            kind = parts[0]
            if kind == "FINAL":
                parts = ["MATCH"]
            elif kind not in DOMAIN_TYPES | {"PROCESS-NAME", "IP-CIDR", "IP-CIDR6", "IP-ASN", "GEOIP", "GEOSITE"}:
                raise ValueError(f"{origin}: 未知规则类型 {kind}")
            else:
                if len(parts) not in (2, 3) or not parts[1]:
                    raise ValueError(f"{origin}: 参数错误 {entry}")
                if len(parts) == 3 and (parts[2] != "no-resolve" or kind not in {"IP-CIDR", "IP-CIDR6", "IP-ASN", "GEOIP"}):
                    raise ValueError(f"{origin}: 非法选项 {entry}")
                if kind.startswith("IP-CIDR"):
                    net = ipaddress.ip_network(parts[1], strict=True)
                    if net.version != (6 if kind == "IP-CIDR6" else 4):
                        raise ValueError(f"{origin}: 地址版本错误")
                if kind in {"DOMAIN", "DOMAIN-SUFFIX"}:
                    if not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?", parts[1]) or ".." in parts[1]:
                        raise ValueError(f"{origin}: 非法域名 {parts[1]}")
                if kind == "IP-ASN" and not parts[1].isdigit():
                    raise ValueError(f"{origin}: 非法 ASN")
            key = tuple(parts)
            if key in seen:
                raise ValueError(f"{origin}: 重复规则 {entry}")
            seen.add(key)
            rules.append((parts, policy, origin))
    if used != {p.resolve() for p in (ROOT / "rules").glob("*.list")}:
        raise ValueError("存在未关联到 pref.ini 的规则集")
    if not rules or rules[-1][0] != ["MATCH"]:
        raise ValueError("末尾缺少 FINAL")
    if any(policy not in {*groups, "DIRECT", "REJECT"} for _, policy, _ in rules):
        raise ValueError("存在未定义的策略组")
    return rules, groups


def match_local(rules, domain="", ip=None, process=""):
    """仅匹配本地可判定条件；不模拟外部 GeoSite / GeoIP / ASN 数据库。"""
    domain = domain.lower().rstrip(".")
    for parts, policy, _ in rules:
        kind, value = parts[0], parts[1] if len(parts) > 1 else ""
        matched = (kind == "MATCH"
                   or kind == "DOMAIN" and domain == value
                   or kind == "DOMAIN-SUFFIX" and (domain == value or domain.endswith("." + value))
                   or kind == "DOMAIN-KEYWORD" and value in domain
                   or kind == "PROCESS-NAME" and process == value
                   or kind in {"IP-CIDR", "IP-CIDR6"} and ip is not None
                   and ipaddress.ip_address(ip) in ipaddress.ip_network(value))
        if matched:
            return policy
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, help="测试配置输出路径；使用 DIRECT 占位，不可用于实际代理")
    args = parser.parse_args()
    rules, groups = load_rules()
    if args.config:
        config = {"mode": "rule", "ipv6": True, "geodata-mode": True,
                  "proxy-groups": [{"name": group, "type": "select", "proxies": ["DIRECT"]} for group in groups],
                  "rules": [",".join(parts[:2] + [policy] + parts[2:]) for parts, policy, _ in rules]}
        args.config.parent.mkdir(parents=True, exist_ok=True)
        args.config.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n")
    print(f"通过：{len(rules)} 条规则，{len(groups)} 个策略组；规则源、语法、CIDR、重复项、关联与末尾兜底均有效。")


if __name__ == "__main__":
    main()
