"""Command-line tools for NOEMA's durable queue and backup operations."""
from __future__ import annotations

import argparse
import json
import os
import sys
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


def _snapshot_to_json(snapshot: Any) -> dict[str, Any]:
    return {
        "path": snapshot.path,
        "sha256": snapshot.sha256,
        "byte_length": snapshot.byte_length,
        "job_count": snapshot.job_count,
        "audit_event_count": snapshot.audit_event_count,
        "audit_last_hash": snapshot.audit_last_hash,
        "created_at": snapshot.created_at,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NOEMA durable queue operations")
    parser.add_argument(
        "--db",
        help="SQLite database path (default: NOEMA_JOBS_DB or ~/.noema/noema-jobs.sqlite3)",
    )
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

    commands.add_parser("verify", help="verify SQLite, foreign keys, payload/result and audit integrity")

    metrics = commands.add_parser("metrics", help="show queue status counts and integrity")
    metrics.add_argument("--json", action="store_true", help="print JSON (default)")

    backup = commands.add_parser("backup", help="create a verified online SQLite backup")
    backup.add_argument("--output", required=True, help="new backup path; existing files are never overwritten")

    restore = commands.add_parser("restore", help="restore a verified backup into a new database path")
    restore.add_argument("--source", required=True, help="verified backup file")
    restore.add_argument("--destination", required=True, help="new database path; it must not already exist")

    args = parser.parse_args(argv)

    try:
        if args.command == "restore":
            snapshot = JobQueue.restore_from_backup(
                args.source,
                args.destination,
            )
            _print_json({"restored": True, **_snapshot_to_json(snapshot)})
            return 0

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
            })
            return 0

        if args.command == "verify":
            result = queue.integrity_check()
            _print_json(result)
            return 0 if result["valid"] else 2

        if args.command == "metrics":
            _print_json({
                "database": str(queue.db_path),
                "queue_counts": queue.count_jobs_by_status(),
                "integrity": queue.integrity_check(),
            })
            return 0

        if args.command == "backup":
            snapshot = queue.backup_to(args.output)
            _print_json({"backup_created": True, **_snapshot_to_json(snapshot)})
            return 0

        parser.error(f"Unsupported command: {args.command}")
    except Exception as exc:
        print(f"NOEMA operation failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
