"""Snapshot the handbook's document stable_ids and MITRE page IDs (FR-02-06).

READ ONLY: it lists file names under ../handbook/knowledge and never opens or changes the
handbook's content. Run from backend/: `uv run python evals/scripts/snapshot_ksor_refs.py`.
"""

import re
import subprocess
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[2]
HANDBOOK = BACKEND.parent.parent / "handbook"
OUT = BACKEND / "evals/data/reference"
MITRE_FILE = re.compile(r"^t(\d{4})(?:-(\d{3}))?-")


def main() -> None:
    knowledge = HANDBOOK / "knowledge"
    commit = subprocess.run(  # noqa: S603
        ["git", "-C", str(HANDBOOK), "log", "-1", "--format=%h %cs"],  # noqa: S607
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    header = f"# snapshot of ../handbook/knowledge file names — handbook commit {commit}\n"
    stable = sorted(
        "knowledge/" + p.relative_to(knowledge).with_suffix("").as_posix()
        for p in knowledge.rglob("*.md")
    )
    mitre = set()
    for p in (knowledge / "mitre").glob("t*.md"):
        m = MITRE_FILE.match(p.name)
        if m:
            mitre.add(f"T{m[1]}" + (f".{m[2]}" if m[2] else ""))
    (OUT / "ksor_stable_ids.txt").write_text(header + "\n".join(stable) + "\n", encoding="utf-8")
    (OUT / "ksor_mitre_ids.txt").write_text(
        header + "\n".join(sorted(mitre)) + "\n", encoding="utf-8"
    )
    print(f"stable_ids: {len(stable)} · MITRE ids: {len(mitre)} · handbook {commit}")


if __name__ == "__main__":
    main()
