from __future__ import annotations

import argparse
import sys


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="cronos", description="Cronos CLI")
    p.add_argument("--log-level", default="INFO", help="Log level")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("collect", help="Run collection for all collectors")
    sub.add_parser("serve", help="Start the API server")
    sub.add_parser("migrate", help="Run database migrations")
    sub.add_parser("seed-demo", help="Seed the database with demo data")
    sub.add_parser("rollup", help="Build daily rollups")
    sub.add_parser("prune", help="Prune old data according to retention")
    sub.add_parser("scheduler", help="Start the background scheduler")
    return p


def collect(args: argparse.Namespace | None = None) -> None:
    from cronos.collector.discovery import discover_collectors
    from cronos.collector.registry import registry
    from cronos.config import load_collectors_config
    from cronos.logging_config import setup_logging
    from cronos.persistence.db import get_engine

    setup_logging(getattr(args, "log_level", "INFO") if args else "INFO")
    engine = get_engine()
    cfg = load_collectors_config()
    discover_collectors()

    for entry in cfg.get("collectors", []):
        cid = entry["id"]
        if entry.get("enabled", True) and cid in registry:
            print(f"Running collector: {cid}")
            collector_cls = registry[cid]
            collector = collector_cls()
            import asyncio
            asyncio.run(collector.collect(entry.get("config", {}), engine))
        else:
            print(f"Skipping collector: {cid} (not found or disabled)")


def serve(args: argparse.Namespace | None = None) -> None:
    import uvicorn

    from cronos.logging_config import setup_logging

    setup_logging(getattr(args, "log_level", "INFO") if args else "INFO")
    uvicorn.run("cronos.api.main:app", host="127.0.0.1", port=8000, reload=False)


def migrate(args: argparse.Namespace | None = None) -> None:
    from alembic.config import CommandLine

    from cronos.logging_config import setup_logging

    setup_logging(getattr(args, "log_level", "INFO") if args else "INFO")
    CommandLine().main(argv=["--raiseerr", "upgrade", "head"])


def seed_demo(args: argparse.Namespace | None = None) -> None:
    from cronos.demo.generator import generate_demo_data
    from cronos.logging_config import setup_logging
    from cronos.persistence.db import get_engine

    setup_logging(getattr(args, "log_level", "INFO") if args else "INFO")
    engine = get_engine()
    generate_demo_data(engine)
    print("Demo data seeded.")


def rollup(args: argparse.Namespace | None = None) -> None:
    from cronos.logging_config import setup_logging
    from cronos.persistence.repositories import build_rollups

    setup_logging(getattr(args, "log_level", "INFO") if args else "INFO")
    from cronos.persistence.db import get_engine
    engine = get_engine()
    build_rollups(engine)
    print("Rollups built.")


def prune(args: argparse.Namespace | None = None) -> None:
    from cronos.logging_config import setup_logging
    from cronos.persistence.repositories import prune_data

    setup_logging(getattr(args, "log_level", "INFO") if args else "INFO")
    from cronos.persistence.db import get_engine
    engine = get_engine()
    prune_data(engine)
    print("Data pruned.")


def scheduler(args: argparse.Namespace | None = None) -> None:
    from cronos.logging_config import setup_logging
    from cronos.scheduler.engine import run_scheduler

    setup_logging(getattr(args, "log_level", "INFO") if args else "INFO")
    run_scheduler()


def main() -> None:
    p = _parser()
    args = p.parse_args()
    commands = {
        "collect": collect,
        "serve": serve,
        "migrate": migrate,
        "seed-demo": seed_demo,
        "rollup": rollup,
        "prune": prune,
        "scheduler": scheduler,
    }
    fn = commands.get(args.command)
    if fn:
        fn(args)
    else:
        p.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
