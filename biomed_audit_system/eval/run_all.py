"""
Run the full audit system over all fixtures and save each report as JSON, so the
deterministic scorer (`evaluate.py`) can grade them. Requires a live Gemini model.

Usage:
    python -m biomed_audit_system.eval.run_all FIXTURE_DIR [FIXTURE_DIR ...] [--out reports_dir]

Example:
    python -m biomed_audit_system.eval.run_all ../fhs_fixtures ../test_fixtures

Point FIXTURE_DIR at the folders holding the .R / .py fixtures. Reports are written
to eval/reports/<fixture>.json by default.
"""
import asyncio
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent


async def _run(fixture_dirs, out_dir: Path) -> None:
    from ..orchestrator import audit  # deferred: pulls in ADK

    out_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for d in fixture_dirs:
        files += sorted(Path(d).glob("*.R")) + sorted(Path(d).glob("*.py"))

    for path in files:
        code = path.read_text(encoding="utf-8")
        try:
            report = await audit(code, filename=str(path))
            (out_dir / (path.name + ".json")).write_text(
                report.model_dump_json(indent=2), encoding="utf-8"
            )
            n = sum(report.counts.values())
            print(f"  {path.name}: {n} findings -> {out_dir / (path.name + '.json')}")
        except Exception as exc:  # keep going; record the failure
            print(f"  {path.name}: ERROR {type(exc).__name__}: {exc}")


def main() -> None:
    args = [a for a in sys.argv[1:] if a != "--out"]
    out_dir = _HERE / "reports"
    if "--out" in sys.argv:
        i = sys.argv.index("--out")
        out_dir = Path(sys.argv[i + 1])
        args = [a for a in args if a != str(out_dir)]
    if not args:
        print("Usage: python -m biomed_audit_system.eval.run_all FIXTURE_DIR [...] [--out reports_dir]")
        sys.exit(1)
    asyncio.run(_run(args, out_dir))


if __name__ == "__main__":
    main()
