"""
conftest.py — fixtures dan hooks global untuk pytest SGS DEV.
"""

from __future__ import annotations
import json
import os
import time
from datetime import datetime
from pathlib import Path

import pytest
from playwright.sync_api import Browser, BrowserContext, Page

from data.config import CMS_BASE_URL, WEB_BASE_URL
from utils.playwright_helpers import login_cms

# ---------------------------------------------------------------------------
# Session-level result tracking
# ---------------------------------------------------------------------------

_results: list[dict] = []
_session_start: float = time.time()
_session_meta: dict = {}

# Track first failures for flaky detection: nodeid -> first_error message
_first_errors: dict[str, str] = {}
# Track attempt count: nodeid -> int
_attempt_counts: dict[str, int] = {}

# Progress file (set saat session start)
_progress_path: Path | None = None
_total_collected: int = 0
_done_count: int = 0


# ---------------------------------------------------------------------------
# Progress file hooks
# ---------------------------------------------------------------------------

def pytest_collection_finish(session):
    """Catat total TC yang dikumpulkan dan buat progress.txt awal."""
    global _progress_path, _total_collected
    _total_collected = len(session.items)

    ts = datetime.now().strftime("%d-%m-%Y_%H.%M")
    report_dir = Path("reports") / ts
    report_dir.mkdir(parents=True, exist_ok=True)
    _progress_path = report_dir / "progress.txt"

    with _progress_path.open("w", encoding="utf-8") as f:
        f.write(f"SGS DEV — Test Progress\n")
        f.write(f"Started : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Total TC: {_total_collected}\n")
        f.write("-" * 60 + "\n")

    print(f"\n[progress] {_progress_path}")


def pytest_runtest_logreport(report):
    """Tulis baris progress ke file setiap TC selesai (fase call saja)."""
    global _done_count
    if report.when != "call" or _progress_path is None:
        return
    # Lewati intermediate rerun (outcome == "rerun") — bukan hasil final
    if report.outcome not in ("passed", "failed", "skipped"):
        return

    _done_count += 1

    if report.passed:
        status = "PASSED "
        icon = "[+]"
    elif report.failed:
        status = "FAILED "
        icon = "[!]"
    else:
        status = "SKIPPED"
        icon = "[-]"

    # Bersihkan nodeid jadi lebih pendek: test-scripts/login/test_login.py::test_foo[chromium]
    short_id = report.nodeid.replace("\\", "/")

    pct = int(_done_count / max(_total_collected, 1) * 100)
    line = (
        f"{icon} {_done_count:>3}/{_total_collected}  ({pct:>3}%)  "
        f"{status}  {short_id}\n"
    )

    with _progress_path.open("a", encoding="utf-8") as f:
        f.write(line)


# ---------------------------------------------------------------------------
# Browser context defaults
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 1280, "height": 720}}


# ---------------------------------------------------------------------------
# Page fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def page(browser: Browser, base_url: str):
    """Generic page at CMS base URL — gunakan untuk test login/dashboard."""
    context: BrowserContext = browser.new_context(base_url=base_url)
    p: Page = context.new_page()
    yield p
    p.close()
    context.close()


@pytest.fixture
def cms_page(browser: Browser):
    """Page yang sudah login ke CMS SGS — gunakan untuk test CRUD."""
    context: BrowserContext = browser.new_context(base_url=CMS_BASE_URL)
    p: Page = context.new_page()
    login_cms(p)
    yield p
    p.close()
    context.close()


@pytest.fixture
def web_page(browser: Browser):
    """Page di web SGS — gunakan bersama cms_page untuk cross-check."""
    context: BrowserContext = browser.new_context(base_url=WEB_BASE_URL)
    p: Page = context.new_page()
    p.goto(WEB_BASE_URL)
    yield p
    p.close()
    context.close()


@pytest.fixture
def cms_web_pages(browser: Browser):
    """
    Tuple (cms_page, web_page) dalam browser session yang sama.
    Gunakan untuk test cross-check: data dibuat di CMS lalu diverifikasi di web.
    Teardown: close kedua context setelah test.
    """
    cms_ctx: BrowserContext = browser.new_context(base_url=CMS_BASE_URL)
    web_ctx: BrowserContext = browser.new_context(base_url=WEB_BASE_URL)
    cms_p: Page = cms_ctx.new_page()
    web_p: Page = web_ctx.new_page()
    login_cms(cms_p)
    web_p.goto(WEB_BASE_URL)
    yield cms_p, web_p
    cms_p.close()
    cms_ctx.close()
    web_p.close()
    web_ctx.close()


# ---------------------------------------------------------------------------
# Screenshot on failure + result tracking
# ---------------------------------------------------------------------------

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    nodeid: str = item.nodeid
    feature_path = "/".join(item.fspath.relto(item.session.fspath).replace("\\", "/").split("/")[1:-1])
    platform = "cms" if any(m.name == "cms" for m in item.iter_markers()) else "web"

    # Determine doc string (TC ID + title)
    doc = (item.function.__doc__ or "").strip().splitlines()[0] if item.function.__doc__ else nodeid.split("::")[-1]

    # Screenshot path setup
    feature_name = Path(str(item.fspath)).parent.name
    timestamp = datetime.now().strftime("%d-%m-%Y_%H.%M")
    bug_dir = Path("bug") / feature_name / timestamp

    screenshot_path = ""
    log_text = ""

    if report.failed:
        # Grab page (try all page-like fixtures)
        page_obj: Page | None = None
        for key in ("page", "cms_page", "web_page"):
            page_obj = item.funcargs.get(key)
            if page_obj is not None:
                break
        if page_obj is None:
            cms_web = item.funcargs.get("cms_web_pages")
            if cms_web:
                page_obj = cms_web[0]

        if page_obj:
            bug_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = str(bug_dir / "screenshot.png")
            try:
                page_obj.screenshot(path=screenshot_path)
            except Exception:
                screenshot_path = ""

        log_text = str(report.longrepr)
        log_path = bug_dir / "error.log"
        bug_dir.mkdir(parents=True, exist_ok=True)
        log_path.write_text(log_text, encoding="utf-8")

        # Store first error for flaky detection
        if nodeid not in _first_errors:
            _first_errors[nodeid] = log_text[:500]

    # Attempt counting
    _attempt_counts[nodeid] = _attempt_counts.get(nodeid, 0) + 1

    # Determine final status
    if report.passed:
        if _attempt_counts.get(nodeid, 1) > 1 and nodeid in _first_errors:
            status = "flaky"
        else:
            status = "passed"
    elif report.failed:
        status = "failed"
    else:
        status = "skipped"

    # Update or append result
    existing = next((r for r in _results if r["nodeid"] == nodeid), None)
    result_entry = {
        "nodeid": nodeid,
        "doc": doc,
        "feature": feature_path,
        "platform": platform,
        "params": str(item.callspec.params) if hasattr(item, "callspec") else "",
        "status": status,
        "message": log_text[:300] if status == "failed" else "",
        "duration": report.duration,
        "attempts": _attempt_counts.get(nodeid, 1),
        "screenshot": screenshot_path,
        "log": str(bug_dir / "error.log") if log_text else "",
        "first_error": _first_errors.get(nodeid, ""),
        "url": "",
    }

    if existing:
        existing.update(result_entry)
    else:
        _results.append(result_entry)


# ---------------------------------------------------------------------------
# Session finish → results.json + PDF
# ---------------------------------------------------------------------------

def pytest_sessionfinish(session, exitstatus):
    if not _results:
        return

    # Pakai folder yang sama dengan progress.txt jika sudah dibuat
    if _progress_path is not None:
        report_dir = _progress_path.parent
        ts = report_dir.name
    else:
        ts = datetime.now().strftime("%d-%m-%Y_%H.%M")
        report_dir = Path("reports") / ts
    report_dir.mkdir(parents=True, exist_ok=True)

    # Tulis baris penutup di progress.txt
    if _progress_path is not None:
        counts = {"passed": 0, "failed": 0, "skipped": 0, "flaky": 0, "error": 0}
        for r in _results:
            counts[r.get("status", "skipped")] = counts.get(r.get("status", "skipped"), 0) + 1
        with _progress_path.open("a", encoding="utf-8") as f:
            f.write("-" * 60 + "\n")
            f.write(f"Finished: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(
                f"Summary : {counts['passed']} passed  {counts['flaky']} flaky  "
                f"{counts['failed']} failed  {counts['skipped']} skipped\n"
            )

    duration_s = time.time() - _session_start
    started = datetime.fromtimestamp(_session_start).strftime("%d/%m/%Y %H:%M")
    finished = datetime.now().strftime("%d/%m/%Y %H:%M")

    meta = {
        "project": "SGS DEV",
        "environment": "development",
        "timestamp": ts,
        "started": started,
        "finished": finished,
        "duration_s": round(duration_s, 1),
        "cms_url": CMS_BASE_URL,
        "web_url": WEB_BASE_URL,
        "command": "pytest " + " ".join(session.config.invocation_params.args),
        "tester": os.environ.get("USERNAME", os.environ.get("USER", "-")),
    }

    output = {"meta": meta, "results": _results}
    results_path = report_dir / "results.json"
    results_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[report] results.json → {results_path}")

    try:
        from utils.pdf_report import generate
        pdf_path = generate(str(results_path))
        print(f"[report] PDF report → {pdf_path}")
    except Exception as e:
        print(f"[report] PDF generation failed: {e}")
