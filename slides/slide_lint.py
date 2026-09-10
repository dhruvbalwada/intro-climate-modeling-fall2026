#!/usr/bin/env python3
"""Heuristic overflow lint for revealjs qmd decks.

Estimates each slide's content 'height units' and flags likely bleeders.
Budget: ~13 units normal, ~17 with {.smaller}. Not pixel-perfect — eyeball
remains the final check — but catches nearly all real overflows.

Usage: python3 slide_lint.py week01.qmd [more.qmd ...]   (expands includes)
"""
import re, sys, pathlib

BUDGET, BUDGET_SMALLER = 13.0, 17.0


def expand(path):
    src = pathlib.Path(path).read_text()
    def repl(m):
        inc = pathlib.Path(path).parent / m.group(1)
        return expand(inc) if inc.exists() else ""
    return re.sub(r"\{\{<\s*include\s+(\S+)\s*>\}\}", repl, src)


def lint(path):
    body = expand(path)
    body = re.sub(r"^---\n.*?\n---\n", "", body, flags=re.S)          # yaml
    body = re.sub(r"::: \{\.notes\}.*?\n:::", "", body, flags=re.S)   # speaker notes
    body = re.sub(r"::: \{\.db-comment\}.*?\n:::", "", body, flags=re.S) # review notes
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)                # comments
    slides = re.split(r"\n(?=#{1,2} )", body)
    problems = []
    for sl in slides:
        lines = sl.strip().splitlines()
        if not lines or not lines[0].startswith("#"):
            continue
        head = lines[0]
        if head.startswith("# "):      # section divider — near-empty by design
            continue
        units, title = 0.0, re.sub(r"\{.*?\}", "", head.lstrip("# ")).strip()
        in_columns = False
        for ln in lines[1:]:
            t = ln.strip()
            if t.startswith(":::: {.columns"): in_columns = True
            elif t == "::::": in_columns = False
            if not t or t in (":::", "::::") or t.startswith((":::: {", "::: {")):
                continue
            if t == ". . .":
                continue
            if t.startswith("!["):
                hpx = re.search(r'height="?(\d+)px', t)
                base = (int(hpx.group(1)) / 55.0) if hpx else 6.0     # ~55px per line-unit
                units += base * (0.5 if in_columns else 1.0)          # side-by-side images share a row
            elif t.startswith("|"):
                units += 1.3                       # table row
            elif t.startswith(("$$",)):
                units += 2.0
            elif t.startswith(("-", "*", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.")):
                units += 1.0 + max(0, (len(t) - 90) / 90)   # long bullets wrap
            elif t.startswith(">"):
                units += 1.2
            else:
                units += 1.0 + max(0, (len(t) - 100) / 100)
        budget = BUDGET_SMALLER if ".smaller" in head else BUDGET
        if units > budget:
            problems.append((title, units, budget))
    return problems


if __name__ == "__main__":
    bad = False
    for f in sys.argv[1:]:
        for title, u, b in lint(f):
            bad = True
            print(f"  OVERFLOW RISK  [{f}] '{title}'  ~{u:.1f} units (budget {b:.0f})")
    print("lint: FAIL" if bad else "lint: all slides within budget ✅")
    sys.exit(1 if bad else 0)
