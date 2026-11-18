"""
Jalankan manual untuk re-generate PDF tanpa ulang test:
    python -m utils.pdf_report reports/<DD-MM-YYYY_HH.MM>/results.json
"""

from __future__ import annotations
import json
import os
import sys
import math
from datetime import datetime
from pathlib import Path
from typing import Any

from fpdf import FPDF, XPos, YPos

# ---------------------------------------------------------------------------
# Brand colors SGS (dari /_next/static/css/395cd51044a14000.css)
# ---------------------------------------------------------------------------
C_RED = (193, 6, 19)       # #c10613 — primary brand
C_RED_DARK = (139, 0, 0)   # darker red for section accents
C_OLIVE = (58, 63, 43)     # #3a3f2b — dark olive
C_GREEN = (8, 41, 24)      # #082918 — deep brand green
C_BG = (250, 248, 246)     # #faf8f6 — warm off-white background
C_WHITE = (255, 255, 255)
C_BLACK = (0, 0, 0)
C_GRAY_LIGHT = (230, 228, 225)
C_GRAY_MID = (180, 176, 170)
C_GRAY_TEXT = (90, 85, 80)

# Status colors
C_PASS = (34, 139, 34)
C_FLAKY = (255, 165, 0)
C_FAIL = (193, 6, 19)
C_ERROR = (128, 0, 128)
C_SKIP = (140, 140, 140)

STATUS_COLOR = {
    "passed": C_PASS,
    "flaky": C_FLAKY,
    "failed": C_FAIL,
    "error": C_ERROR,
    "skipped": C_SKIP,
}

STATUS_LABEL = {
    "passed": "Pass",
    "flaky": "Pass",
    "failed": "Fail",
    "error": "Error",
    "skipped": "Hold",
}

PRIORITY_COLOR = {
    "1 - high": C_FAIL,
    "high": C_FAIL,
    "2 - medium": C_FLAKY,
    "medium": C_FLAKY,
    "3 - low": C_PASS,
    "low": C_PASS,
}


# ---------------------------------------------------------------------------
# Unicode sanitizer (Helvetica hanya support Latin-1)
# ---------------------------------------------------------------------------

_UNICODE_MAP = {
    "’": "'", "‘": "'", "“": '"', "”": '"',
    "–": "-", "—": "--", "…": "...",
    "→": "->", "←": "<-", "•": "*",
    "●": "*",   # ●
    "■": "#",   # ■
    "▶": ">",   # ▶
    "✔": "v",   # ✓
    "✘": "x",   # ✗
}


def _safe(text: str) -> str:
    """Ganti karakter Unicode umum lalu strip sisanya ke Latin-1."""
    if not isinstance(text, str):
        text = str(text)
    for src, dst in _UNICODE_MAP.items():
        text = text.replace(src, dst)
    # Strip emoji dan karakter non-Latin-1 lainnya
    return text.encode("latin-1", errors="ignore").decode("latin-1")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rgb(color: tuple) -> dict:
    return {"r": color[0], "g": color[1], "b": color[2]}


def _duration_str(secs: float) -> str:
    if secs < 60:
        return f"{secs:.1f} detik"
    return f"{secs / 60:.1f} menit"


def _pass_rate(results: list[dict]) -> float:
    executed = [r for r in results if r["status"] != "skipped"]
    if not executed:
        return 0.0
    ok = [r for r in executed if r["status"] in ("passed", "flaky")]
    return len(ok) / len(executed) * 100


def _counts(results: list[dict]) -> dict:
    c: dict[str, int] = {s: 0 for s in ("passed", "flaky", "failed", "error", "skipped")}
    for r in results:
        c[r["status"]] = c.get(r["status"], 0) + 1
    return c


def _feature_summary(results: list[dict]) -> list[dict]:
    groups: dict[str, list] = {}
    for r in results:
        key = f"{r.get('platform', 'web').title()} › {r.get('feature', '').replace('/', ' / ').title()}"
        groups.setdefault(key, []).append(r)
    rows = []
    for label, items in sorted(groups.items()):
        c = _counts(items)
        total = len(items)
        ok = c["passed"] + c["flaky"]
        rate = ok / (total - c["skipped"]) * 100 if (total - c["skipped"]) > 0 else 0
        rows.append({
            "label": label,
            "total": total,
            "passed": c["passed"],
            "flaky": c["flaky"],
            "failed": c["failed"],
            "error": c["error"],
            "skipped": c["skipped"],
            "rate": rate,
        })
    return rows


# ---------------------------------------------------------------------------
# FPDF subclass
# ---------------------------------------------------------------------------

class SGSReport(FPDF):
    PROJECT = "SGS DEV"
    FONT = "Helvetica"

    def __init__(self, meta: dict):
        super().__init__(orientation="L", unit="mm", format="A4")
        self.meta = meta
        self.set_auto_page_break(auto=True, margin=12)
        self.set_margins(12, 12, 12)

    # -- unicode-safe wrappers --

    def cell(self, w=0, h=0, txt="", **kwargs):
        return super().cell(w, h, _safe(txt), **kwargs)

    def multi_cell(self, w, h, txt="", **kwargs):
        return super().multi_cell(w, h, _safe(txt), **kwargs)

    # -- helpers --

    def _set_fill(self, color: tuple):
        self.set_fill_color(*color)

    def _set_text(self, color: tuple):
        self.set_text_color(*color)

    def _set_draw(self, color: tuple):
        self.set_draw_color(*color)

    def _logo_mark(self, x: float, y: float, r: float = 8):
        """Draw SGS logo image, fallback to circle mark if file missing."""
        import os
        logo_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data", "assets", "logo.png"
        )
        if os.path.exists(logo_path):
            # logo rasio ~3.78:1 (4460×1178), tampilkan dengan tinggi r*2
            logo_h = r * 2
            logo_w = logo_h * 3.78
            self.image(logo_path, x=x, y=y, w=logo_w, h=logo_h)
        else:
            # fallback: circle primitif
            self._set_fill(C_RED)
            self.ellipse(x, y, r * 2, r * 2, style="F")
            self.set_xy(x - 1, y + r * 0.42)
            self._set_text(C_WHITE)
            self.set_font(self.FONT, "B", int(r * 1.3))
            self.cell(r * 2 + 2, r * 0.9, "SGS", align="C",
                      new_x=XPos.RIGHT, new_y=YPos.TOP)
            self._set_text(C_BLACK)

    def section_badge(self, number: int, title: str):
        self._set_fill(C_RED)
        self._set_text(C_WHITE)
        self.set_font(self.FONT, "B", 10)
        self.cell(7, 7, str(number), border=0, align="C", fill=True,
                  new_x=XPos.RIGHT, new_y=YPos.TOP)
        self._set_text(C_BLACK)
        self.set_font(self.FONT, "B", 13)
        self.cell(0, 7, f"  {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def status_chip(self, status: str, w: float = 20, h: float = 5):
        color = STATUS_COLOR.get(status, C_GRAY_MID)
        label = STATUS_LABEL.get(status, status.title())
        self._set_fill(color)
        self._set_text(C_WHITE)
        self.set_font(self.FONT, "B", 7)
        self.cell(w, h, label, border=0, align="C", fill=True,
                  new_x=XPos.RIGHT, new_y=YPos.TOP)
        self._set_text(C_BLACK)

    def priority_chip(self, priority: str, w: float = 22, h: float = 5):
        color = PRIORITY_COLOR.get(priority.lower(), C_GRAY_MID)
        self._set_fill(color)
        self._set_text(C_WHITE)
        self.set_font(self.FONT, "B", 7)
        self.cell(w, h, priority, border=0, align="C", fill=True,
                  new_x=XPos.RIGHT, new_y=YPos.TOP)
        self._set_text(C_BLACK)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font(self.FONT, "", 7)
        self._set_text(C_GRAY_TEXT)
        project = self.meta.get("project", self.PROJECT)
        ts = self.meta.get("timestamp", "")
        self.cell(0, 5, f"[SGS] {project} · Automation Test Report · {ts}",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self._set_draw(C_GRAY_LIGHT)
        self.set_line_width(0.2)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self._set_text(C_BLACK)

    def footer(self):
        self.set_y(-10)
        self.set_font(self.FONT, "", 7)
        self._set_text(C_GRAY_TEXT)
        self.cell(0, 5, f"Halaman {self.page_no()}", align="R",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self._set_text(C_BLACK)

    # -- cover --

    def cover(self, results: list[dict]):
        self.add_page()
        pw = self.w - self.l_margin - self.r_margin
        meta = self.meta
        counts = _counts(results)
        rate = _pass_rate(results)
        total = len(results)

        # ── Full-width header bar (C_OLIVE dark background) ──────────────────
        BAR_H = 32
        self._set_fill(C_OLIVE)
        self.rect(0, 0, self.w, BAR_H, style="F")

        # Thin red accent stripe at bottom of header bar
        self._set_fill(C_RED)
        self.rect(0, BAR_H - 2, self.w, 2, style="F")

        # Logo image + subtitle
        LOGO_X = self.l_margin + 2
        LOGO_Y = 8
        LOGO_H = 12   # tinggi logo mm
        LOGO_W = LOGO_H * 3.78  # ~45mm
        self._logo_mark(LOGO_X, LOGO_Y, r=LOGO_H / 2)

        self.set_xy(LOGO_X, LOGO_Y + LOGO_H + 1)
        self._set_text(C_GRAY_LIGHT)
        self.set_font(self.FONT, "", 7)
        self.cell(LOGO_W + 4, 4, "QA Automation · QBIT",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Date info — small text, right-aligned, below logo subtitle
        ts = meta.get("timestamp", "").replace("_", " ")
        env_text = meta.get("environment", "development").upper()
        self._set_text(C_GRAY_LIGHT)
        self.set_font(self.FONT, "", 7)
        self.set_xy(self.l_margin, LOGO_Y + LOGO_H + 6)
        self.cell(0, 4, f"Dijalankan  {ts}  ·  {env_text}", align="R",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self._set_text(C_BLACK)

        # ── Title section ─────────────────────────────────────────────────────
        self.set_xy(self.l_margin, BAR_H + 4)
        self._set_text(C_RED)
        self.set_font(self.FONT, "B", 22)
        self.cell(0, 10, "Automation Test Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self._set_text(C_GRAY_TEXT)
        self.set_font(self.FONT, "", 10)
        env = meta.get("environment", "development")
        self.cell(0, 5, f"{meta.get('project', self.PROJECT)} · Environment {env}",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self._set_text(C_BLACK)
        self.ln(3)

        # ── Stat cards ────────────────────────────────────────────────────────
        y_cards = self.get_y()
        card_w = pw / 4
        card_h = 22       # tinggi tiap stat card kanan
        GAP = 3           # jarak antar baris kanan
        STRIPE_H = 3      # tinggi stripe warna di atas card

        # pass_card_h harus sama dengan 2 baris kanan + gap
        pass_card_w = card_w * 1.5
        pass_card_h = card_h * 2 + GAP   # = 47mm

        # Offset absolut konten dalam pass rate card (relatif ke y_cards)
        PR_LABEL = STRIPE_H + 2          # = 5   → label "PASS RATE"
        PR_NUM   = STRIPE_H + 10         # = 13  → angka besar %
        PR_SUB   = STRIPE_H + 24         # = 27  → "X dari Y lulus"
        PR_BAR   = STRIPE_H + 30         # = 33  → progress bar
        PR_LEG   = STRIPE_H + 36         # = 39  → legend dots

        def stat_card(x, y, label, value, color):
            self._set_fill(C_WHITE)
            self._set_draw(C_GRAY_LIGHT)
            self.set_line_width(0.5)
            self.rect(x, y, card_w - 2, card_h, style="FD")
            # Colored top stripe
            self._set_fill(color)
            self.rect(x, y, card_w - 2, STRIPE_H, style="F")
            # Dot + label
            self._set_fill(color)
            self.ellipse(x + 3, y + STRIPE_H + 3, 2.5, 2.5, style="F")
            self.set_xy(x + 7, y + STRIPE_H + 2)
            self._set_text(C_GRAY_TEXT)
            self.set_font(self.FONT, "", 7)
            self.cell(card_w - 10, 5, label, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            # Value number
            self.set_xy(x + 3, y + STRIPE_H + 8)
            self._set_text(C_BLACK)
            self.set_font(self.FONT, "B", 16)
            self.cell(card_w - 6, 9, str(value), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self._set_text(C_BLACK)

        # ── Pass rate card ────────────────────────────────────────────────────
        pass_color = C_FAIL if counts["failed"] > 0 else C_PASS
        self._set_fill(C_WHITE)
        self._set_draw(C_GRAY_LIGHT)
        self.set_line_width(0.5)
        self.rect(self.l_margin, y_cards, pass_card_w - 2, pass_card_h, style="FD")
        # Top stripe
        self._set_fill(pass_color)
        self.rect(self.l_margin, y_cards, pass_card_w - 2, STRIPE_H, style="F")

        # Dot + "PASS RATE" label
        self._set_fill(pass_color)
        self.ellipse(self.l_margin + 3, y_cards + PR_LABEL + 1, 2.5, 2.5, style="F")
        self.set_xy(self.l_margin + 7, y_cards + PR_LABEL)
        self._set_text(C_GRAY_TEXT)
        self.set_font(self.FONT, "", 7)
        self.cell(pass_card_w - 40, 5, "PASS RATE",
                  new_x=XPos.RIGHT, new_y=YPos.TOP)

        # FAILED badge (right side, same row as label)
        if counts["failed"] > 0:
            badge_x = self.l_margin + pass_card_w - 2 - 28
            self._set_fill(C_FAIL)
            self.rect(badge_x, y_cards + PR_LABEL, 26, 5, style="F")
            self.set_xy(badge_x, y_cards + PR_LABEL)
            self._set_text(C_WHITE)
            self.set_font(self.FONT, "B", 7)
            self.cell(26, 5, f"FAILED {counts['failed']}", align="C",
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self._set_text(C_BLACK)

        # Rate number (font 24, h=11 → ends at PR_NUM+11=24)
        self.set_xy(self.l_margin + 3, y_cards + PR_NUM)
        self._set_text(C_BLACK)
        self.set_font(self.FONT, "B", 24)
        self.cell(pass_card_w - 6, 11, f"{rate:.1f}%",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Sub-text (starts at PR_SUB=27, h=4 → ends at 31)
        executed = total - counts["skipped"]
        ok = counts["passed"] + counts["flaky"]
        self.set_xy(self.l_margin + 3, y_cards + PR_SUB)
        self._set_text(C_GRAY_TEXT)
        self.set_font(self.FONT, "", 7)
        self.cell(pass_card_w - 6, 4,
                  f"{ok} dari {executed} test yang dieksekusi lulus",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self._set_text(C_BLACK)

        # Progress bar (starts at PR_BAR=33, h=3 → ends at 36)
        bar_w = pass_card_w - 10
        bar_h = 3
        segments = [
            (counts["passed"], C_PASS),
            (counts["flaky"], C_FLAKY),
            (counts["failed"], C_FAIL),
            (counts["skipped"], C_SKIP),
        ]
        self._set_fill(C_GRAY_LIGHT)
        self.rect(self.l_margin + 3, y_cards + PR_BAR, bar_w, bar_h, style="F")
        bx = self.l_margin + 3
        for cnt, color in segments:
            if executed > 0 and cnt > 0:
                w = bar_w * cnt / max(executed, 1)
                self._set_fill(color)
                self.rect(bx, y_cards + PR_BAR, w, bar_h, style="F")
                bx += w

        # Legend (starts at PR_LEG=39, h=4 → ends at 43 < pass_card_h=47)
        self.set_xy(self.l_margin + 3, y_cards + PR_LEG)
        legend_items = [
            ("Passed", C_PASS, counts["passed"]),
            ("Flaky", C_FLAKY, counts["flaky"]),
            ("Failed", C_FAIL, counts["failed"]),
            ("Skipped", C_SKIP, counts["skipped"]),
        ]
        for lab, color, cnt in legend_items:
            self._set_fill(color)
            self.ellipse(self.get_x(), self.get_y() + 1, 2.5, 2.5, style="F")
            self.set_x(self.get_x() + 3.5)
            self._set_text(C_GRAY_TEXT)
            self.set_font(self.FONT, "", 7)
            self.cell(22, 4, f"{lab} {cnt}", new_x=XPos.RIGHT, new_y=YPos.TOP)
            self._set_text(C_BLACK)

        # ── Right stat cards (3×2 grid) ───────────────────────────────────────
        cx = self.l_margin + pass_card_w
        stat_items = [
            ("TOTAL TEST", total, C_GRAY_MID),
            ("PASSED",  counts["passed"],  C_PASS),
            ("FLAKY",   counts["flaky"],   C_FLAKY),
            ("FAILED",  counts["failed"],  C_FAIL),
            ("ERROR",   counts["error"],   C_ERROR),
            ("SKIPPED", counts["skipped"], C_SKIP),
        ]
        row2_y = y_cards + card_h + GAP
        positions = [
            (cx,              y_cards), (cx + card_w,     y_cards), (cx + card_w * 2, y_cards),
            (cx,              row2_y),  (cx + card_w,     row2_y),  (cx + card_w * 2, row2_y),
        ]
        for (sx, sy), (lab, val, col) in zip(positions, stat_items):
            stat_card(sx, sy, lab, val, col)

        self.set_y(y_cards + pass_card_h + 6)

        # Meta table
        meta_rows = [
            ("PROJECT", meta.get("project", self.PROJECT),
             "ENVIRONMENT", meta.get("environment", "development")),
            ("CMS", meta.get("cms_url", "https://sgs-cms-dev.qode.biz.id"),
             "BROWSER", "Chromium (Playwright), viewport 1280×720"),
            ("WEB", meta.get("web_url", "https://sgs-web-dev.qode.biz.id"),
             "DURASI", _duration_str(meta.get("duration_s", 0))),
            ("WAKTU EKSEKUSI",
             f"{meta.get('started', '')} s/d {meta.get('finished', '')}",
             "TESTER", meta.get("tester", os.environ.get("USERNAME", "-"))),
            ("PERINTAH", meta.get("command", "pytest"),
             "JUMLAH BUG",
             f"{sum(1 for r in results if r['status'] == 'failed')} temuan (detail di bagian 3 & 4)"),
        ]
        col_w = [30, pw / 2 - 32, 30, pw / 2 - 32]
        for row in meta_rows:
            self._set_text(C_GRAY_TEXT)
            self.set_font(self.FONT, "", 7)
            x0 = self.l_margin
            for i, cell_text in enumerate(row):
                self.set_x(x0 + sum(col_w[:i]))
                if i % 2 == 0:
                    self.cell(col_w[i], 5, cell_text.upper(),
                              new_x=XPos.RIGHT, new_y=YPos.TOP)
                else:
                    self._set_text(C_BLACK)
                    self.set_font(self.FONT, "", 8)
                    self.cell(col_w[i], 5, cell_text,
                              new_x=XPos.RIGHT, new_y=YPos.TOP)
                    self._set_text(C_GRAY_TEXT)
                    self.set_font(self.FONT, "", 7)
            self.ln(5)
        self._set_text(C_BLACK)
        self.ln(2)

        # Feature summary table
        self.section_badge(1, "Ringkasan per Fitur")
        self._feature_table(results)

    def _feature_table(self, results: list[dict]):
        rows = _feature_summary(results)
        col_w = {"label": 90, "total": 15, "passed": 15, "flaky": 15,
                 "failed": 15, "error": 15, "skipped": 15, "rate": 30}
        # Header
        self._set_fill(C_OLIVE)
        self._set_text(C_WHITE)
        self.set_font(self.FONT, "B", 7)
        headers = ["PLATFORM › FITUR", "TOTAL", "PASSED", "FLAKY",
                   "FAILED", "ERROR", "SKIPPED", "PASS RATE"]
        for h, key in zip(headers, col_w.keys()):
            self.cell(col_w[key], 6, h, border=0, align="L" if key == "label" else "C",
                      fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.ln(6)
        self._set_text(C_BLACK)

        for row in rows:
            self._set_fill(C_BG if rows.index(row) % 2 == 0 else C_WHITE)
            self.set_font(self.FONT, "B", 7)
            # label
            self.cell(col_w["label"], 6, row["label"], border=0, fill=True,
                      new_x=XPos.RIGHT, new_y=YPos.TOP)
            self.set_font(self.FONT, "", 7)
            for key in ("total", "passed", "flaky", "failed", "error", "skipped"):
                val = row[key]
                if key == "failed" and val > 0:
                    self._set_text(C_FAIL)
                elif key == "flaky" and val > 0:
                    self._set_text(C_FLAKY)
                else:
                    self._set_text(C_GRAY_TEXT if val == 0 else C_BLACK)
                self.cell(col_w[key], 6, str(val), border=0, align="C",
                          fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
                self._set_text(C_BLACK)
            # rate bar + text
            rate = row["rate"]
            bar_total = col_w["rate"] - 12
            rate_x = self.get_x()
            rate_y = self.get_y()
            self._set_fill(C_PASS)
            self.rect(rate_x, rate_y + 1.5, bar_total * rate / 100, 3, style="F")
            if row["failed"] > 0:
                fail_start = bar_total * (row["passed"] + row["flaky"]) / max(row["total"] - row["skipped"], 1)
                self._set_fill(C_FAIL)
                self.rect(rate_x + fail_start, rate_y + 1.5,
                          bar_total * row["failed"] / max(row["total"] - row["skipped"], 1), 3, style="F")
            self.set_xy(rate_x + bar_total + 1, rate_y)
            self._set_text(C_BLACK)
            self.set_font(self.FONT, "", 7)
            self.cell(11, 6, f"{rate:.0f}%", align="R",
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Bug summary
        bugs = [r for r in results if r["status"] == "failed"]
        if bugs:
            self.ln(2)
            self.set_font(self.FONT, "B", 7)
            self._set_text(C_GRAY_TEXT)
            self.cell(0, 5, "Bug per priority: ", new_x=XPos.RIGHT, new_y=YPos.TOP)
            from data.bug_context import BUG_CONTEXT
            for status_label, color in [("2 - Medium", C_FLAKY), ("3 - Low", C_PASS)]:
                self._set_fill(color)
                self.ellipse(self.get_x(), self.get_y() + 1, 2, 2, style="F")
                self.set_x(self.get_x() + 3)
                self._set_text(C_GRAY_TEXT)
                self.set_font(self.FONT, "", 7)
                self.cell(18, 5, f"{status_label} {len(bugs)}",
                          new_x=XPos.RIGHT, new_y=YPos.TOP)
            self._set_text(C_BLACK)
            self.ln(5)

    def legend_page(self):
        """Halaman 2: Penjelasan visual tiap status chip."""
        self.add_page()
        pw = self.w - self.l_margin - self.r_margin

        self._set_text(C_GRAY_TEXT)
        self.set_font(self.FONT, "", 8)
        self.cell(0, 5, "Keterangan status yang digunakan di laporan ini:",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self._set_text(C_BLACK)
        self.ln(4)

        legend_items = [
            ("passed",  "Pass",    C_PASS,
             "Sesuai expected result."),
            ("flaky",   "Flaky",   C_FLAKY,
             "Gagal lalu lulus saat diulang otomatis. Dihitung lulus, bukan bug."),
            ("failed",  "Fail",    C_FAIL,
             "Tidak sesuai expected walau sudah diulang. Masuk Bug Report."),
            ("error",   "Error",   C_ERROR,
             "Test gagal di tahap persiapan (setup/teardown)."),
            ("skipped", "Skipped", C_SKIP,
             "Sengaja tidak dijalankan (alasan di bagian 5)."),
        ]

        chip_w = 28
        row_h = 10
        for status, label, color, desc in legend_items:
            x0 = self.l_margin
            y0 = self.get_y()
            # Chip (filled pill)
            self._set_fill(color)
            self._set_draw(color)
            self.rect(x0, y0, chip_w, row_h, style="F")
            self._set_text(C_WHITE)
            self.set_font(self.FONT, "B", 8)
            self.set_xy(x0, y0)
            self.cell(chip_w, row_h, label, align="C",
                      new_x=XPos.RIGHT, new_y=YPos.TOP)
            # Description
            self._set_text(C_BLACK)
            self.set_font(self.FONT, "", 9)
            self.set_xy(x0 + chip_w + 5, y0 + 1)
            self.cell(pw - chip_w - 5, row_h - 2, desc,
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(3)

        self._set_text(C_BLACK)

    def test_case_pages(self, results: list[dict], test_plans: dict):
        self.add_page()
        self.section_badge(2, "Test Case Result")
        self._set_text(C_GRAY_TEXT)
        self.set_font(self.FONT, "", 7)
        self.multi_cell(
            0, 4,
            "Format mengikuti template Test Case tim (onboard/report-bug.md). "
            "Status: Pass (termasuk flaky) · Fail · Hold (di-skip). Baris merah = Fail (masuk Bug Report).",
            new_x=XPos.LMARGIN, new_y=YPos.NEXT,
        )
        self._set_text(C_BLACK)
        self.ln(2)

        # Group by platform/feature
        groups: dict[str, list] = {}
        for r in results:
            key = f"{r.get('platform', 'web').title()} › {r.get('feature', '').replace('/', ' / ').title()}"
            groups.setdefault(key, []).append(r)

        for group_label, items in sorted(groups.items()):
            ok = sum(1 for i in items if i["status"] in ("passed", "flaky"))
            fail = sum(1 for i in items if i["status"] == "failed")
            self.set_font(self.FONT, "B", 9)
            self._set_text(C_BLACK)
            self.cell(0, 6, f"{group_label}  ", new_x=XPos.RIGHT, new_y=YPos.TOP)
            self._set_text(C_GRAY_TEXT)
            self.set_font(self.FONT, "", 7)
            suffix = f"({ok} Passed"
            if fail:
                suffix += f" · {fail} Failed"
            suffix += ")"
            self.cell(0, 6, suffix, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self._set_text(C_BLACK)
            self._tc_table(items, test_plans)
            self.ln(3)

    def _tc_table(self, items: list[dict], test_plans: dict):
        pw = self.w - self.l_margin - self.r_margin
        col = {
            "tc_id": 22, "features": 16, "sub": 16, "desc": 38,
            "steps": 50, "expected": 40, "type": 14, "priority": 16,
            "status": 14, "tester": 14, "date": 20, "remark": 0,
        }
        col["remark"] = pw - sum(v for k, v in col.items() if k != "remark")

        headers = ["TEST ID", "FEATURES", "SUB FEATURES", "DESCRIPTION",
                   "STEP TO REPRODUCE", "EXPECTED RESULT", "TYPE", "PRIORITY",
                   "STATUS", "TESTER", "TEST DATE", "REMARK"]

        self._set_fill(C_OLIVE)
        self._set_text(C_WHITE)
        self.set_font(self.FONT, "B", 6)
        for h, key in zip(headers, col.keys()):
            self.cell(col[key], 5, h, border=0, fill=True, align="C",
                      new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.ln(5)
        self._set_text(C_BLACK)

        for item in items:
            # Highlight failed rows
            is_fail = item["status"] == "failed"
            self._set_fill((255, 240, 240) if is_fail else (C_BG if items.index(item) % 2 == 0 else C_WHITE))

            doc = item.get("doc", "")
            tc_id = doc.split(":")[0].strip() if ":" in doc else ""
            title = doc.split(":", 1)[1].strip() if ":" in doc else doc

            # Look up test plan row
            tp = test_plans.get(tc_id, {})
            steps_text = tp.get("test_steps", tp.get("step_to_reproduce", "")).replace("<br>", "\n")
            expected_text = tp.get("expected_result", "")
            tc_type = tp.get("test_type", tp.get("type", ""))
            priority = tp.get("priority", "")

            remark = item.get("message", "")
            if item["status"] == "flaky" and not remark:
                remark = "Flaky — lulus setelah diulang"

            ts = self.meta.get("timestamp", "").replace("_", " ")
            date_str = ts.split(" ")[0] if ts else ""
            tester = self.meta.get("tester", os.environ.get("USERNAME", "-"))

            row_h = 5
            self.set_font(self.FONT, "", 6)
            fill = True
            for key, text in [
                ("tc_id", tc_id), ("features", item.get("feature", "").split("/")[-2] if "/" in item.get("feature", "") else ""),
                ("sub", item.get("feature", "").split("/")[-1]),
                ("desc", title), ("steps", steps_text), ("expected", expected_text),
                ("type", tc_type), ("priority", priority),
            ]:
                self.multi_cell(col[key], row_h, text, border=0, fill=fill,
                                new_x=XPos.RIGHT, new_y=YPos.TOP, max_line_height=row_h)
                fill = False

            # Status chip inline
            x0 = self.get_x()
            y0 = self.get_y()
            self.status_chip(item["status"], col["status"], row_h)
            self.set_xy(x0 + col["status"], y0)

            for key, text in [("tester", tester), ("date", date_str), ("remark", remark)]:
                self.multi_cell(col[key], row_h, text, border=0,
                                new_x=XPos.RIGHT, new_y=YPos.TOP, max_line_height=row_h)

            self.ln(row_h)
            self._set_text(C_BLACK)

    def bug_list_page(self, results: list[dict]):
        bugs = [r for r in results if r["status"] == "failed"]
        if not bugs:
            return
        self.add_page()
        self.section_badge(3, "Daftar Bug")
        self._set_text(C_GRAY_TEXT)
        self.set_font(self.FONT, "", 7)
        self.cell(0, 4, "Format mengikuti template Bug Report tim (onboard/report-bug.md). Kolom Assigned to diisi PM.",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self._set_text(C_BLACK)
        self.ln(2)

        pw = self.w - self.l_margin - self.r_margin
        col = {"id": 16, "date": 20, "platform": 18, "menu": 30, "condition": 65,
               "raised": 14, "priority": 20, "evidence": 20, "type": 14,
               "assigned": 18, "status": 16, "remarks": 0}
        col["remarks"] = pw - sum(v for k, v in col.items() if k != "remarks")

        headers = ["ID", "DATE", "PLATFORM", "MENU/ITEM", "CONDITION / STATE",
                   "RAISED BY", "PRIORITY", "EVIDENCE", "TYPE", "ASSIGNED TO", "STATUS", "REMARKS"]

        self._set_fill(C_OLIVE)
        self._set_text(C_WHITE)
        self.set_font(self.FONT, "B", 6)
        for h, key in zip(headers, col.keys()):
            self.cell(col[key], 5, h, border=0, fill=True, align="C",
                      new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.ln(5)
        self._set_text(C_BLACK)

        ts = self.meta.get("timestamp", "").replace("_", " ")
        date_str = ts.split(" ")[0] if ts else ""
        tester = self.meta.get("tester", os.environ.get("USERNAME", "-"))

        for i, bug in enumerate(bugs):
            bug_id = f"BUG-{i + 1:03d}"
            doc = bug.get("doc", "")
            tc_id = doc.split(":")[0].strip() if ":" in doc else ""
            title = doc.split(":", 1)[1].strip() if ":" in doc else doc
            platform = bug.get("platform", "web").title()
            feature = bug.get("feature", "").replace("/", " › ").title()
            message = bug.get("message", "")[:120]

            from data.bug_context import BUG_CONTEXT
            ctx = BUG_CONTEXT.get(tc_id, {})
            priority = ctx.get("severity", "2 - Medium")
            has_ss = bool(bug.get("screenshot"))
            evidence = "Screenshot (lihat detail)" if has_ss else "-"

            self._set_fill(C_BG if i % 2 == 0 else C_WHITE)
            self.set_font(self.FONT, "B", 6)
            row_h = 5
            fill = True
            for key, text in [
                ("id", bug_id), ("date", date_str), ("platform", platform),
                ("menu", feature), ("condition", f"{title}\n{tc_id}"),
                ("raised", tester),
            ]:
                self.multi_cell(col[key], row_h, text, border=0, fill=fill,
                                new_x=XPos.RIGHT, new_y=YPos.TOP, max_line_height=row_h)
                self.set_font(self.FONT, "", 6)
                fill = False

            # Priority chip
            self.priority_chip(priority, col["priority"], row_h)

            for key, text in [("evidence", evidence), ("type", "1 - Bug"),
                               ("assigned", ""), ("status", "1 - Raised"),
                               ("remarks", f"Test case {tc_id}")]:
                self.multi_cell(col[key], row_h, text, border=0,
                                new_x=XPos.RIGHT, new_y=YPos.TOP, max_line_height=row_h)
            self.ln(row_h)
            self._set_text(C_BLACK)

    def bug_detail_pages(self, results: list[dict], test_plans: dict):
        bugs = [r for r in results if r["status"] == "failed"]
        if not bugs:
            return

        self.add_page()
        self.section_badge(4, f"Detail Bug ({len(bugs)} temuan)")

        ts = self.meta.get("timestamp", "").replace("_", " ")
        tester = self.meta.get("tester", os.environ.get("USERNAME", "-"))
        env = self.meta.get("environment", "development")
        cms_url = self.meta.get("cms_url", "https://sgs-cms-dev.qode.biz.id")
        web_url = self.meta.get("web_url", "https://sgs-web-dev.qode.biz.id")

        from data.bug_context import BUG_CONTEXT
        pw = self.w - self.l_margin - self.r_margin

        for i, bug in enumerate(bugs):
            if i > 0:
                self.add_page()
            bug_id = f"BUG-{i + 1:03d}"
            doc = bug.get("doc", "")
            tc_id = doc.split(":")[0].strip() if ":" in doc else ""
            title = doc.split(":", 1)[1].strip() if ":" in doc else doc
            platform = bug.get("platform", "web").title()
            feature = bug.get("feature", "").replace("/", " › ").title()
            message = bug.get("message", "")

            ctx = BUG_CONTEXT.get(tc_id, {})
            priority = ctx.get("severity", "2 - Medium")
            tp = test_plans.get(tc_id, {})

            # Bug card header
            self._set_fill(C_BG)
            self._set_draw(C_GRAY_LIGHT)
            self.set_line_width(0.3)
            card_y = self.get_y()
            self.rect(self.l_margin, card_y, pw, 10, style="FD")
            # BUG ID badge
            self._set_fill(C_OLIVE)
            self.rect(self.l_margin, card_y, 20, 10, style="F")
            self.set_xy(self.l_margin, card_y)
            self._set_text(C_WHITE)
            self.set_font(self.FONT, "B", 8)
            self.cell(20, 10, bug_id, border=0, align="C",
                      new_x=XPos.RIGHT, new_y=YPos.TOP)
            self._set_text(C_BLACK)
            self.set_font(self.FONT, "B", 10)
            self.cell(pw - 50, 10, f"  {title}",
                      new_x=XPos.RIGHT, new_y=YPos.TOP)
            self.priority_chip(priority, 30, 10)
            self.ln(10)

            # Metadata row
            self._set_text(C_GRAY_TEXT)
            self.set_font(self.FONT, "", 7)
            meta_line = (
                f"TEST CASE {tc_id} · {title}   "
                f"MENU {platform} · {feature}   "
                f"TYPE 1 - Bug   "
                f"TANGGAL {ts} · {env}   "
                f"RAISED BY {tester}"
            )
            self.multi_cell(0, 4, meta_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self._set_text(C_BLACK)
            self.ln(2)

            # Pre-step, Step, Actual, Expected, Impact
            left_w = pw * 0.55
            right_w = pw * 0.43

            pre_step = tp.get("pre_conditions", tp.get("preconditions", ""))
            if not pre_step:
                pre_step = f"CMS: {cms_url}\nWeb: {web_url}\nSudah login di CMS."
            steps = tp.get("test_steps", tp.get("step_to_reproduce", "")).replace("<br>", "\n")
            expected = ctx.get("expected", tp.get("expected_result", ""))
            actual = ctx.get("actual", message)
            impact = ctx.get("impact", "")

            def detail_row(label: str, text: str, color=None):
                self._set_text(C_GRAY_TEXT)
                self.set_font(self.FONT, "", 7)
                self.cell(28, 5, label.upper(), new_x=XPos.RIGHT, new_y=YPos.TOP)
                if color:
                    self._set_fill(color)
                    self._set_text(C_BLACK if color == (255, 240, 240) else C_BLACK)
                    self.set_font(self.FONT, "", 8)
                    self.multi_cell(left_w - 30, 5, text, border=0, fill=True,
                                    new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                else:
                    self._set_text(C_BLACK)
                    self.set_font(self.FONT, "", 8)
                    self.multi_cell(left_w - 30, 5, text,
                                    new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                self._set_text(C_BLACK)

            detail_row("PRE-STEP", pre_step)
            detail_row("STEP", steps)
            detail_row("ACTUAL RESULT", actual, (255, 240, 240))
            detail_row("EXPECTED RESULT", expected, (240, 255, 240))
            if impact:
                detail_row("IMPACT", impact, (255, 255, 220))

            # Right column: screenshot + meta
            right_x = self.l_margin + left_w + 4
            self.set_xy(right_x, card_y + 12)
            ss_path = bug.get("screenshot", "")
            if ss_path and Path(ss_path).exists():
                try:
                    self.image(ss_path, x=right_x, w=right_w, h=55)
                    self.set_xy(right_x, self.get_y() + 2)
                except Exception:
                    pass
            self._set_text(C_GRAY_TEXT)
            self.set_font(self.FONT, "", 6)
            feature_path = bug.get("feature", "").strip("/")
            tp_path = f"test-plan/{feature_path}/test-{feature_path.split('/')[-1]}.md" if feature_path else "-"
            meta_right = [
                ("URL SAAT GAGAL", bug.get("url", "-")),
                ("VERIFIKASI", f"Gagal {bug.get('attempts', 2)}x berturut-turut (diulang otomatis)"),
                ("TEST SCRIPT", bug.get("nodeid", "-")),
                ("TEST PLAN", tp_path),
                ("LOG ERROR", bug.get("log", "-")),
            ]
            for lab, val in meta_right:
                self.set_x(right_x)
                self.set_font(self.FONT, "B", 6)
                self._set_text(C_GRAY_TEXT)
                self.cell(28, 4, lab, new_x=XPos.RIGHT, new_y=YPos.TOP)
                self.set_font(self.FONT, "", 6)
                self._set_text(C_BLACK)
                self.multi_cell(right_w - 30, 4, val,
                                new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self._set_text(C_BLACK)

    def skipped_page(self, results: list[dict]):
        skipped = [r for r in results if r["status"] == "skipped"]
        if not skipped:
            return
        self.add_page()
        self.section_badge(5, "Test yang Di-skip")
        self._set_text(C_GRAY_TEXT)
        self.set_font(self.FONT, "", 7)
        self.cell(0, 4, "Sengaja tidak dijalankan — alasan tercantum di kolom Alasan.",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self._set_text(C_BLACK)
        self.ln(2)

        pw = self.w - self.l_margin - self.r_margin
        self._set_fill(C_OLIVE)
        self._set_text(C_WHITE)
        self.set_font(self.FONT, "B", 7)
        for h, w in [("TC ID", 35), ("TITLE", 90), ("STATUS", 20), ("ALASAN", pw - 150)]:
            self.cell(w, 5, h, border=0, fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.ln(5)
        self._set_text(C_BLACK)

        for item in skipped:
            doc = item.get("doc", "")
            tc_id = doc.split(":")[0].strip() if ":" in doc else ""
            title = doc.split(":", 1)[1].strip() if ":" in doc else doc
            reason = item.get("message", "")
            self._set_fill(C_BG)
            self.set_font(self.FONT, "", 7)
            self.cell(35, 5, tc_id, border=0, fill=True,
                      new_x=XPos.RIGHT, new_y=YPos.TOP)
            self.cell(90, 5, title, border=0, fill=True,
                      new_x=XPos.RIGHT, new_y=YPos.TOP)
            self.status_chip("skipped", 20, 5)
            self.multi_cell(pw - 150, 5, reason, border=0,
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT, max_line_height=5)
            self._set_text(C_BLACK)

    def flaky_page(self, results: list[dict]):
        flaky = [r for r in results if r["status"] == "flaky"]
        if not flaky:
            return
        self.add_page()
        self.section_badge(6, "Test Flaky (lulus setelah diulang)")
        self._set_text(C_GRAY_TEXT)
        self.set_font(self.FONT, "", 7)
        self.multi_cell(
            0, 4,
            "Gagal di percobaan pertama lalu lulus saat dijalankan ulang otomatis, tidak dihitung bug. "
            "Kalau test yang sama sering flaky, laporkan sebagai isu performa / stabilitas server dev.",
            new_x=XPos.LMARGIN, new_y=YPos.NEXT,
        )
        self._set_text(C_BLACK)
        self.ln(2)

        pw = self.w - self.l_margin - self.r_margin
        self._set_fill(C_OLIVE)
        self._set_text(C_WHITE)
        self.set_font(self.FONT, "B", 7)
        for h, w in [("TC ID", 35), ("TITLE", 90), ("PERCOBAAN", 20), ("ERROR PERCOBAAN PERTAMA", pw - 150)]:
            self.cell(w, 5, h, border=0, fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.ln(5)
        self._set_text(C_BLACK)

        for item in flaky:
            doc = item.get("doc", "")
            tc_id = doc.split(":")[0].strip() if ":" in doc else ""
            title = doc.split(":", 1)[1].strip() if ":" in doc else doc
            first_error = item.get("first_error", item.get("message", ""))[:300]
            attempts = item.get("attempts", 2)
            self._set_fill(C_BG)
            self.set_font(self.FONT, "", 7)
            self.cell(35, 5, tc_id, border=0, fill=True,
                      new_x=XPos.RIGHT, new_y=YPos.TOP)
            self.cell(90, 5, title, border=0, fill=True,
                      new_x=XPos.RIGHT, new_y=YPos.TOP)
            self.cell(20, 5, f"{attempts}x", border=0, fill=True, align="C",
                      new_x=XPos.RIGHT, new_y=YPos.TOP)
            self.set_font(self.FONT, "", 6)
            self.multi_cell(pw - 150, 5, first_error, border=0,
                            new_x=XPos.LMARGIN, new_y=YPos.NEXT, max_line_height=5)
            self._set_text(C_BLACK)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def generate(results_path: str) -> str:
    results_file = Path(results_path)
    with open(results_file, encoding="utf-8") as f:
        data = json.load(f)

    meta = data.get("meta", {})
    results = data.get("results", [])

    from utils.test_plan import load_all_test_plans
    test_plans = load_all_test_plans()

    pdf = SGSReport(meta)
    pdf.set_title(f"SGS Automation Test Report — {meta.get('timestamp', '')}")
    pdf.set_author("QBIT")

    pdf.cover(results)
    pdf.legend_page()
    pdf.test_case_pages(results, test_plans)
    pdf.bug_list_page(results)
    pdf.bug_detail_pages(results, test_plans)
    pdf.skipped_page(results)
    pdf.flaky_page(results)

    out_dir = results_file.parent
    ts = meta.get("timestamp", datetime.now().strftime("%d-%m-%Y_%H.%M"))
    project_slug = meta.get("project", "SGS").replace(" ", "-")
    out_path = out_dir / f"{project_slug}-Test-Report_{ts}.pdf"
    pdf.output(str(out_path))
    print(f"[pdf] Report saved → {out_path}")
    return str(out_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m utils.pdf_report reports/<timestamp>/results.json")
        sys.exit(1)
    generate(sys.argv[1])
