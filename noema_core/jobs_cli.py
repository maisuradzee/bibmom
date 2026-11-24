"""Command-line interface for NOEMA's durable job ledger."""
from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .jobs import DEFAULT_DB_PATH, JobQueue


def _database_path(value: str | None) -> Path:
    if value:
        return Path(value).expanduser()
    configured = os.environ.get("NOEMA_JOBS_DB")
    return Path(configured).expanduser() if configured else DEFAULT_DB_PATH


def _print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NOEMA durable job queue")
    parser.add_argument("--db", help="SQLite database path (default: ~/.noema/noema-jobs.sqlite3)")
    commands = parser.add_subparsers(dest="command", required=True)

    enqueue = commands.add_parser("enqueue", help="enqueue an allowlisted task type")
    enqueue.add_argument("--type", required=True, dest="job_type")
    enqueue.add_argument("--payload", required=True, help="JSON object payload")
    enqueue.add_argument("--idempotency-key")
    enqueue.add_argument("--max-attempts", type=int, default=3)

    listing = commands.add_parser("list", help="list recent jobs without exposing payloads")
    listing.add_argument("--status", action="append", dest="statuses")
    listing.add_argument("--limit", type=int, default=50)

    status = commands.add_parser("status", help="show one job without its payload")
    status.add_argument("job_id")

    commands.add_parser("verify", help="verify SQLite and audit-log integrity")

    args = parser.parse_args(argv)
    queue = JobQueue(_database_path(args.db))

    if args.command == "enqueue":
        try:
            payload = json.loads(args.payload)
        except json.JSONDecodeError as exc:
            parser.error(f"--payload is not valid JSON: {exc}")
        if not isinstance(payload, dict):
            parser.error("--payload must decode to a JSON object")
        job = queue.enqueue(
            args.job_type,
            payload,
            idempotency_key=args.idempotency_key,
            max_attempts=args.max_attempts,
            actor="cli",
        )
        _print_json({
            "job_id": job.job_id,
            "job_type": job.job_type,
            "status": job.status,
            "attempts": job.attempts,
            "max_attempts": job.max_attempts,
        })
        return 0

    if args.command == "list":
        _print_json([
            {
                "job_id": job.job_id,
                "job_type": job.job_type,
                "status": job.status,
                "attempts": job.attempts,
                "max_attempts": job.max_attempts,
                "created_at": job.created_at,
                "last_error": job.last_error,
            }
            for job in queue.list_jobs(statuses=args.statuses, limit=args.limit)
        ])
        return 0

    if args.command == "status":
        job = queue.get(args.job_id)
        _print_json({
            "job_id": job.job_id,
            "job_type": job.job_type,
            "status": job.status,
            "attempts": job.attempts,
            "max_attempts": job.max_attempts,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
            "last_error": job.last_error,
            "result": job.result,
        })
        return 0

    if args.command == "verify":
        result = queue.integrity_check()
        _print_json(result)
        return 0 if result["valid"] else 2

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
