"""
Parser test plan Markdown → dict per TC ID.
Dipakai pdf_report.py untuk mengisi kolom Pre-step, Step, Expected Result.
"""

from __future__ import annotations
import re
from pathlib import Path


def _parse_table_rows(md: str) -> list[dict[str, str]]:
    rows = []
    in_table = False
    headers: list[str] = []
    for line in md.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            in_table = False
            headers = []
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not headers:
            headers = [h.lower().replace(" ", "_") for h in cells]
            in_table = True
            continue
        if re.match(r"^[-| ]+$", line):
            continue
        if in_table and headers:
            rows.append(dict(zip(headers, cells)))
    return rows


def load_all_test_plans(root: str = "test-plan") -> dict[str, dict]:
    """Return {tc_id: row_dict} from all *.md files under root."""
    result: dict[str, dict] = {}
    for md_file in Path(root).rglob("*.md"):
        try:
            text = md_file.read_text(encoding="utf-8")
        except Exception:
            continue
        for row in _parse_table_rows(text):
            tc_id = row.get("test_case_id", "").strip()
            if tc_id:
                result[tc_id] = row
    return result
