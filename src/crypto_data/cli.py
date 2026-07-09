from __future__ import annotations

import argparse
from pathlib import Path

from .collector import run_update


def main() -> None:
    parser = argparse.ArgumentParser(description="Update the historical crypto Parquet archive.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    update = subparsers.add_parser("update", help="Repair recent data and backfill older history.")
    update.add_argument("--repo-root", type=Path, default=Path.cwd())
    update.add_argument("--config", type=Path, default=None)
    update.add_argument("--max-requests", type=int, default=None)

    args = parser.parse_args()
    if args.command == "update":
        summary = run_update(args.repo_root, config_path=args.config, max_requests=args.max_requests)
        print(
            "update complete: "
            f"requests={summary.requests_used} "
            f"rows_received={summary.rows_received} "
            f"rows_written={summary.rows_written}"
        )


if __name__ == "__main__":
    main()

