#!/usr/bin/env python3
"""Check local UTF-8 YAML syntax without changing files or running commands."""

import argparse
from pathlib import Path
import sys

import yaml


def main() -> int:
    parser = argparse.ArgumentParser(description="检查本地 UTF-8 YAML 文件的语法")
    parser.add_argument("files", nargs="+", type=Path, help="要检查的 YAML 文件")
    args = parser.parse_args()
    failed = False
    for path in args.files:
        try:
            with path.open("r", encoding="utf-8") as stream:
                for _ in yaml.safe_load_all(stream):
                    pass
        except (OSError, UnicodeError, yaml.YAMLError) as error:
            print(f"FAIL {path}: {error}", file=sys.stderr)
            failed = True
        else:
            print(f"OK {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
