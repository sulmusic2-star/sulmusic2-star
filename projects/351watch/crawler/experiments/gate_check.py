#!/usr/bin/env python3
"""Check that the production daily run does not pick up gated states (MI, VA under test).

    python3 experiments/gate_check.py
"""
import subprocess
import sys
from collections import Counter
from pathlib import Path

CRAWLER = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CRAWLER))

from watch351 import current, daily  # noqa: E402

DATA = CRAWLER.parent / "data"
ok = True
gated = current.gated_states(DATA)
print("gated towns files:", sorted(gated))
default_rows = daily.select_towns(DATA, None, None)
states = Counter(r["state"] for r in default_rows)
print("default daily selection (no --states):", dict(states))
ok &= not (set(states) & gated)
doc = current.build(DATA, archive=False)
print("production hits_current build: states", doc["states"], "towns_monitored", doc["towns_monitored"])
ok &= not (set(doc["states"]) & gated)
explicit = Counter(r["state"] for r in daily.select_towns(DATA, {"MI", "VA"}, None))
print("explicit --states MI,VA selection:", dict(explicit))
ok &= set(explicit) == {"MI", "VA"} if gated >= {"MI", "VA"} else True
# naming a gated state without --output-dir must be refused (exit 2) before any request
proc = subprocess.run([sys.executable, "-m", "watch351.daily", "--states", "VA", "--no-network-docs"],
                      cwd=CRAWLER, capture_output=True, text=True, timeout=120)
print("daily --states VA (no --output-dir): exit", proc.returncode, "|", proc.stderr.strip()[-160:])
ok &= proc.returncode == 2 and "not part of the production run" in proc.stderr
print("GATE OK" if ok else "GATE FAILED")
sys.exit(0 if ok else 1)
