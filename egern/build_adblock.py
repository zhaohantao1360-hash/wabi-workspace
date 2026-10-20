"""Rebuild the frozen Egern v2 selection, offline. SPDX-License-Identifier: GPL-3.0-only."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent

def render():
    source = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))
    entries = source["entries"]
    # Keep the complete MIT notice for the independently selected StevenBlack entries.
    mit = (ROOT / "THIRD-PARTY-LICENSE.txt").read_text(encoding="utf-8").strip()
    lines = [
        "# Egern native YAML module v2.0.0 — frozen, independently licensed selection.",
        "# SPDX-License-Identifier: GPL-3.0-only",
        "# HaGeZi-derived portions and this combined module: GPL-3.0-only.",
        "# Modified selection/conversion: Wabi-assisted examples, 2026-10-20.",
        "# Full GPL license: https://github.com/zhaohantao1360-hash/wabi-workspace/blob/main/egern/LICENSE-GPL-3.0.txt",
        "# Corresponding editable source and reproducible builder: sources.json, build_adblock.py in the same directory.",
        "# StevenBlack portions retain the following MIT notice:",
    ] + ["# " + line if line else "#" for line in mit.splitlines()]
    lines += ["", 'name: "基础去广告 · 无需解密"',
        f'description: "v2.0.0：{len(entries)} 条广告网络规则，含边界安全的子域匹配；不含证书、脚本或远程规则集。非全能去广告。"',
        'author: "Wabi-assisted examples; HaGeZi; Steven Black"',
        'homepage: "https://github.com/zhaohantao1360-hash/wabi-workspace/tree/main/egern"',
        'manual: "https://github.com/zhaohantao1360-hash/wabi-workspace/blob/main/egern/README.md"',
        "rules:"]
    previous = None
    for item in entries:
        if item["group"] != previous:
            lines.append("  # " + item["group"])
            previous = item["group"]
        lines += [f'  - {item["kind"]}:',
                  '      match: ' + json.dumps(item["match"]),
                  '      policy: REJECT',
                  '      name: ' + json.dumps('Wabi广告 · ' + item["group"], ensure_ascii=False)]
    return "\n".join(lines) + "\n"

if __name__ == "__main__":
    path = ROOT / "adblock-lite.yaml"
    path.write_text(render(), encoding="utf-8")
    print(f"Built {path.name}")
