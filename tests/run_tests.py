"""CLI and importable entry point for the official/own exam."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.runner import PipelineUnavailable, run_all  # noqa: E402


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--writer-mode", default="offline")
    parser.add_argument("--out", default="exports/test_results.json")
    args = parser.parse_args(argv)
    try:
        result = run_all(args.writer_mode)
    except PipelineUnavailable:
        print("pipeline not available")
        return 2
    target = Path(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f'Exam: {result["summary"]["pass"]}/{result["summary"]["total"]} passed; output written to {target}')
    return 0 if result["summary"]["pass"] == result["summary"]["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
