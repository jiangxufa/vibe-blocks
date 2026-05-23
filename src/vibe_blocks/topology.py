"""服务拓扑自动推导。

基于积木的 services 字段，按命名规则自动归类为 4 层：
- BFF 层：xxx-server / xxx-bff / xxx-gateway
- 核心业务层：xxx-service / xxx-svc / 其余微服务
- 基础设施：PolarDB / MySQL / Redis / MQ / OSS / 缓存 / 数据库 等
- 外部系统：alipay / wechat / 微信支付 / 第三方 等

注：基础设施 / 外部系统在可视化中**抽象为通用名**展示
（如 PolarDB → 数据库，RocketMQ → 消息队列，微信支付 → 支付平台），
积木原文中的具体技术名保持不变。
"""

from __future__ import annotations

import re
from typing import Iterable

INFRA_PATTERNS = [
    r"polar.*db",
    r"mysql",
    r"postgres",
    r"oracle",
    r"mongo",
    r"redis",
    r"memcache",
    r"rocket\s*mq",
    r"kafka",
    r"rabbit\s*mq",
    r"^mq$",
    r"nsq",
    r"oss",
    r"^s3$",
    r"^cos$",
    r"elastic\s*search",
    r"^es$",
    r"^cdn$",
    r"^db$",
    r"database",
    r"缓存",
    r"消息队列",
    r"对象存储",
    r"数据库",
]

EXTERNAL_PATTERNS = [
    r"alipay",
    r"支付宝",
    r"wechat",
    r"weixin",
    r"微信",
    r"third[\s_-]*party",
    r"第三方",
    r"sms\b",
    r"短信",
    r"oauth",
    r"google",
    r"apple",
    r"facebook",
    r"twitter",
    r"github",
    r"stripe",
    r"paypal",
]

BFF_PATTERNS = [
    r"-server$",
    r"-bff$",
    r"^bff[-_]",
    r"-gateway$",
    r"^gateway[-_]",
    r"^api[-_]gateway",
    r"-portal$",
    r"^portal[-_]",
    r"-admin$",
    r"-web$",
]


# 抽象别名规则：把具体技术名归类到通用展示名。
# 顺序敏感：先匹配的优先（更具体的规则放前面）。
INFRA_ALIASES = [
    (r"polar.*db|mysql|postgres|oracle|mongo|^db$|database|数据库", "数据库"),
    (r"redis|memcache|缓存", "缓存"),
    (r"rocket\s*mq|kafka|rabbit\s*mq|nsq|^mq$|消息队列", "消息队列"),
    (r"oss|^s3$|^cos$|对象存储", "对象存储"),
    (r"elastic\s*search|^es$", "搜索引擎"),
    (r"^cdn$", "CDN"),
]

EXTERNAL_ALIASES = [
    (r"alipay|支付宝|wechat\s*pay|微信\s*支付|stripe|paypal", "支付平台"),
    (r"sms|短信", "短信网关"),
    (r"oauth|google|apple|facebook|twitter|github", "第三方登录"),
    (r"wechat|weixin|微信", "微信开放平台"),
    (r"third[\s_-]*party|第三方", "第三方系统"),
]


def classify_service(name: str) -> str:
    """返回 'bff' / 'core' / 'infra' / 'external'。"""
    n = name.lower().strip()
    if any(re.search(p, n) for p in INFRA_PATTERNS):
        return "infra"
    if any(re.search(p, n) for p in EXTERNAL_PATTERNS):
        return "external"
    if any(re.search(p, n) for p in BFF_PATTERNS):
        return "bff"
    return "core"


def abstract_display_name(name: str, kind: str) -> str:
    """把具体技术名抽象为通用展示名（仅用于可视化层）。

    - 'infra'/'external' 类型才走映射，其他原样返回
    - 找不到匹配也原样返回（保持可用）

    示例：
        abstract_display_name("PolarDB", "infra")   → "数据库"
        abstract_display_name("RocketMQ", "infra")  → "消息队列"
        abstract_display_name("微信支付", "external") → "支付平台"
        abstract_display_name("admin-server", "bff") → "admin-server"  # 不抽象 BFF/core
    """
    if kind == "infra":
        rules = INFRA_ALIASES
    elif kind == "external":
        rules = EXTERNAL_ALIASES
    else:
        return name
    n = name.lower()
    for pattern, alias in rules:
        if re.search(pattern, n):
            return alias
    return name


def _bff_subgroup(name: str) -> str:
    """BFF 层内细分子分组（用于多 BFF 项目展示）。"""
    n = name.lower()
    if "admin" in n or "运营" in n or "后台" in n:
        return "运营后台"
    if "mini" in n or "wx" in n or "weixin" in n or "qywx" in n or "小程序" in n:
        return "C 端用户"
    if "outer" in n or "open" in n or "third" in n or "第三方" in n:
        return "第三方对接"
    if "gateway" in n or "网关" in n:
        return "网关层"
    return "BFF"


def derive_layers(services: Iterable[str]) -> list[dict]:
    """根据积木涉及的服务集合，自动生成 layers 拓扑。

    BFF / core 层保留服务原名；
    infra / external 层抽象为通用展示名（数据库 / 消息队列 / 支付平台 等），
    同类项自动合并。

    返回结构与 HTML 模板期望的 layers 一致：
        [{'label': str, 'type': str, 'services': [str, ...]}, ...]
    """
    bff: dict[str, list[str]] = {}
    core: list[str] = []
    infra_aliases: list[str] = []  # 保序去重
    infra_set: set[str] = set()
    external_aliases: list[str] = []
    external_set: set[str] = set()

    seen: set[str] = set()
    for svc in services:
        if not svc or svc in seen:
            continue
        seen.add(svc)
        kind = classify_service(svc)
        if kind == "bff":
            bff.setdefault(_bff_subgroup(svc), []).append(svc)
        elif kind == "infra":
            alias = abstract_display_name(svc, "infra")
            if alias not in infra_set:
                infra_set.add(alias)
                infra_aliases.append(alias)
        elif kind == "external":
            alias = abstract_display_name(svc, "external")
            if alias not in external_set:
                external_set.add(alias)
                external_aliases.append(alias)
        else:
            core.append(svc)

    layers: list[dict] = []
    # BFF 层（多分组按名称排序，固定常见顺序）
    order = ["运营后台", "C 端用户", "第三方对接", "网关层", "BFF"]
    sorted_groups = sorted(bff.keys(), key=lambda g: order.index(g) if g in order else 99)
    for group in sorted_groups:
        layers.append({
            "label": f"入口层 BFF — {group}" if group != "BFF" else "入口层 BFF",
            "type": "bff",
            "services": sorted(bff[group]),
        })

    if core:
        layers.append({"label": "核心业务层", "type": "core", "services": sorted(core)})
    if infra_aliases:
        layers.append({"label": "基础设施", "type": "infra", "services": infra_aliases})
    if external_aliases:
        layers.append({"label": "外部系统", "type": "external", "services": external_aliases})

    return layers


def collect_services_from_blocks(output_data: dict) -> list[str]:
    """从 build 解析出的分组数据里聚合所有出现过的服务名。"""
    seen: list[str] = []
    seen_set: set[str] = set()
    for blocks in output_data.values():
        for b in blocks:
            for s in b.get("services", []) or []:
                if s and s not in seen_set:
                    seen_set.add(s)
                    seen.append(s)
    return seen


# 触发方常见名（从 mermaid participant 里识别基础设施/外部系统时排除）
TRIGGER_NAMES = {
    "客户端", "用户", "前端", "浏览器", "user", "client", "browser",
    "小程序", "运营后台", "管理后台", "App", "app", "APP",
    "C", "U", "Admin", "admin",  # 单字母别名
}


def collect_extras_from_mermaid(output_data: dict, known: set[str]) -> list[str]:
    """从积木的 mermaid 时序图中提取额外的 participant。

    用于识别基础设施（PolarDB / RocketMQ / Redis 等）和外部系统（微信支付 / Alipay 等），
    这些通常不在积木 frontmatter 的 services 字段里。

    排除：触发方（客户端/小程序/运营后台等），以及已在 known 里的服务。
    """
    import re

    extras: list[str] = []
    extras_set: set[str] = set()
    for blocks in output_data.values():
        for b in blocks:
            for line in b.get("mermaid", "").split("\n"):
                m = re.match(r"\s*participant\s+\w+\s+as\s+(.+)", line.strip())
                if not m:
                    continue
                name = m.group(1).strip().strip("`")
                if not name or name in known or name in extras_set:
                    continue
                if name in TRIGGER_NAMES:
                    continue
                # 仅把基础设施 / 外部系统加入（核心业务理论上应该在 services 字段里）
                kind = classify_service(name)
                if kind in ("infra", "external"):
                    extras_set.add(name)
                    extras.append(name)
    return extras
