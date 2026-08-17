from __future__ import annotations

import argparse
import json
import sys

from .client import TrackingError, track


def main() -> None:
    parser = argparse.ArgumentParser(description="日本郵便 物流轨迹查询")
    parser.add_argument("tracking_no", nargs="?", default="955187518666")
    parser.add_argument("--kind", default="S002", help="searchKind，ゆうパック默认 S002")
    args = parser.parse_args()
    try:
        data = track(args.tracking_no, search_kind=args.kind)
    except TrackingError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"request failed: {exc}", file=sys.stderr)
        sys.exit(2)

    meta = data.pop("_meta", {})
    print(json.dumps(data, ensure_ascii=False, indent=2))
    print("\n--- request ---", file=sys.stderr)
    print(f"browser: {meta.get('browser')}", file=sys.stderr)
    print(f"ua: {meta.get('user_agent')}", file=sys.stderr)
    print(f"cookies: {list((meta.get('cookies') or {}).keys())}", file=sys.stderr)


if __name__ == "__main__":
    main()
