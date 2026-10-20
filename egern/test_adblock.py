"""Offline structure and exact-host regression tests, not the Egern runtime."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import yaml

ROOT = Path(__file__).resolve().parent

class UniqueKeyLoader(yaml.SafeLoader):
    pass

def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f"Duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result

UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream-hosts", type=Path, help="Optional local copy of the pinned upstream hosts file")
    args = parser.parse_args()
    module = yaml.load((ROOT / "adblock-lite.yaml").read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    source = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))
    assert set(module) == {"name", "description", "author", "homepage", "manual", "rules"}
    assert all(isinstance(module[k], str) and module[k] for k in ("name", "description", "author", "homepage", "manual"))
    assert isinstance(module["rules"], list) and len(module["rules"]) == 18
    hosts = []
    for rule in module["rules"]:
        assert isinstance(rule, dict) and set(rule) == {"domain"}
        item = rule["domain"]
        assert set(item) == {"match", "policy"} and item["policy"] == "REJECT"
        host = item["match"]
        assert isinstance(host, str) and re.fullmatch(r"[a-z0-9]+(?:[.-][a-z0-9]+)*\.[a-z]{2,}", host)
        hosts.append(host)
    assert len(set(hosts)) == len(hosts)
    assert hosts == source["domains"]
    assert source["source"] == f'https://raw.githubusercontent.com/StevenBlack/hosts/{source["source_commit"]}/hosts'
    forbidden_parents = {"qq.com", "baidu.com", "xiaomi.com", "google.com", "googleapis.com", "googlevideo.com", "apple.com", "alipay.com", "taobao.com", "alicdn.com", "unity3d.com"}
    assert not (set(hosts) & forbidden_parents)
    # Model only the documented exact-host semantics, with case and dot unchanged.
    blocked = set(hosts).__contains__
    cases = 0
    for host in hosts:
        assert blocked(host)
        for other in ("x." + host, host + ".example.org", "not-" + host):
            assert not blocked(other)
        cases += 4
    for host in ("www.qq.com", "login.weixin.qq.com", "www.baidu.com", "www.alipay.com", "www.taobao.com", "www.apple.com", "api.bilibili.com", "www.youtube.com", "rr1---sn.example.googlevideo.com", "github.com", "www.xiaomi.com", "api.unity3d.com"):
        assert not blocked(host)
        cases += 1
    # Ensure duplicate keys cannot silently override a rule.
    try:
        yaml.load("a: 1\na: 2\n", Loader=UniqueKeyLoader)
    except ValueError:
        pass
    else:
        raise AssertionError("Duplicate-key rejection failed")
    print(f"PASS: native module shape; {len(hosts)} unique exact-host REJECT rules; no scripts/MITM/DNS overrides; {cases} local matching cases; duplicate-key rejection.")
    if args.upstream_hosts:
        data = args.upstream_hosts.read_bytes()
        assert hashlib.sha256(data).hexdigest() == source["source_sha256"], "Not the pinned upstream snapshot"
        upstream = {parts[1] for line in data.decode("utf-8").splitlines() if len(parts := line.split()) >= 2 and parts[0] in {"0.0.0.0", "127.0.0.1"}}
        assert set(hosts) <= upstream
        print(f"PASS: all {len(hosts)} hosts present in the hash-verified pinned source snapshot.")
    print("NOT TESTED: Egern installation/import/runtime, real device traffic, actual ad removal, or all app functionality.")

if __name__ == "__main__":
    main()
