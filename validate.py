#!/usr/bin/python3
"""校验 curation.json 并盖上时间戳。

这个文件是「清单不能变成远程控制通道」这条红线的执行者：
只允许固定字段、只允许白名单域名，多一个字段都拒绝发布。
"""
import json
import sys
import datetime
from urllib.parse import urlparse

PATH = "curation.json"

# 必须与 App 内编译进包的白名单保持一致。改这里之前先改 App。
ALLOWED_HOSTS = {
    "www.coindesk.com", "coindesk.com",
    "cointelegraph.com", "www.cointelegraph.com",
    "decrypt.co", "www.decrypt.co",
}

# 只允许这些字段。多一个都拒绝——开关、跳转、版本判断等一律进不来。
ALLOWED_TOP = {"schema", "updated", "items"}
ALLOWED_ITEM = {"url", "rank", "tag"}


def main() -> int:
    try:
        with open(PATH, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ 找不到 {PATH}")
        return 1
    except json.JSONDecodeError as e:
        print(f"❌ JSON 格式错误：第 {e.lineno} 行，{e.msg}")
        return 1

    errors = []

    if not isinstance(data, dict):
        print("❌ 顶层必须是对象")
        return 1

    extra = set(data) - ALLOWED_TOP
    if extra:
        errors.append(f"顶层出现不允许的字段：{sorted(extra)}")

    if data.get("schema") != 1:
        errors.append("schema 必须为 1")

    items = data.get("items")
    if not isinstance(items, list):
        errors.append("items 必须是数组")
        items = []

    seen = set()
    for i, it in enumerate(items):
        where = f"items[{i}]"
        if not isinstance(it, dict):
            errors.append(f"{where} 必须是对象")
            continue

        extra = set(it) - ALLOWED_ITEM
        if extra:
            errors.append(f"{where} 出现不允许的字段：{sorted(extra)}")

        url = it.get("url")
        if not isinstance(url, str) or not url:
            errors.append(f"{where} 缺少 url")
            continue

        p = urlparse(url)
        if p.scheme != "https":
            errors.append(f"{where} 必须是 https：{url}")
        if p.netloc not in ALLOWED_HOSTS:
            errors.append(f"{where} 域名不在白名单：{p.netloc or '(空)'}")
        if url in seen:
            errors.append(f"{where} url 重复：{url}")
        seen.add(url)

        rank = it.get("rank")
        if rank is not None and not isinstance(rank, int):
            errors.append(f"{where} rank 必须是整数")

        tag = it.get("tag")
        if tag is not None and not isinstance(tag, str):
            errors.append(f"{where} tag 必须是字符串")

    if errors:
        print("❌ 校验未通过，已阻止发布：\n")
        for e in errors:
            print("   •", e)
        return 1

    stamped = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    out = {"schema": 1, "updated": stamped, "items": items}

    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"✅ 校验通过：{len(items)} 条，时间戳已更新为 {stamped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
