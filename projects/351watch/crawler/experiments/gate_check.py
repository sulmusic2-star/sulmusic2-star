#!/usr/bin/env python3
"""Check that production does not pick up anything under test: the gated states (VT and CT for the Wave 1
state feeds; MI, VA, MD and OH were promoted on 2026-11-03), the Wave 1 New York towns (data/test/wave1/config/towns_ny.json, outside the
data/towns_*.json glob) and the Wave 1 state-feed outputs (data/test/wave1/sources/, never data/sources/).

    python3 experiments/gate_check.py
"""
import subprocess
import sys
from collections import Counter
from pathlib import Path

CRAWLER = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CRAWLER))

from watch351 import current, daily  # noqa: E402
from watch351.sources import state_feeds  # noqa: E402

DATA = CRAWLER.parent / "data"
WAVE1_CONFIG = DATA / "test" / "wave1" / "config"
WAVE2_CONFIG = DATA / "test" / "wave2" / "config"
ok = True


def check(cond: bool, label: str) -> None:
    global ok
    ok &= bool(cond)
    print(("  ok    " if cond else "  FAIL  ") + label)


gated = current.gated_states(DATA)
print("gated towns files:", sorted(gated))
default_rows = daily.select_towns(DATA, None, None)
states = Counter(r["state"] for r in default_rows)
print("default daily selection (no --states):", dict(states))
check(not (set(states) & gated), "no gated state in the default daily selection")
check(dict(states) == {"MA": 243, "NY": 92, "RI": 39, "VA": 108, "MD": 30, "MI": 101, "OH": 33},
      "default selection is MA 243, NY 92, RI 39 (NY: 33 pilot + 22 promoted from wave 1 on 2026-11-02 + 5 from the "
      "2026-11-03 follow-up + 26 towns and 6 county boards from wave 2), VA 108, MD 30, MI 101, OH 33 (promoted 2026-11-03)")
doc = current.build(DATA, archive=False)
print("production hits_current build: states", doc["states"], "towns_monitored", doc["towns_monitored"])
check(not (set(doc["states"]) & gated), "no gated state in a production hits_current build")
check(not any(h.get("source") in ("vt_act250", "ct_siting_council") for h in doc["hits"]),
      "no Wave 1 state-feed hit in a production build")
check(not list((DATA / "sources").glob("vt_*")) and not list((DATA / "sources").glob("ct_*")),
      "data/sources/ holds no Wave 1 state-feed output")
explicit = Counter(r["state"] for r in daily.select_towns(DATA, {"MI", "VA"}, None))
print("explicit --states MI,VA selection:", dict(explicit))
check(set(explicit) == {"MI", "VA"} if gated >= {"MI", "VA"} else True, "--states MI,VA selects MI and VA")
check({"VT", "CT"} <= gated, "data/towns_vt.json and data/towns_ct.json are gated")
# Wave 1 New York towns: their own config directory, gated, never in the production NY selection
w1 = current.load_towns(WAVE1_CONFIG, include_gated={"NY"}) if (WAVE1_CONFIG / "towns_ny.json").exists() else []
prod_ny = {r["town"] for r in default_rows if r["state"] == "NY"}
check(not list(DATA.glob("towns_ny_*.json")), "no extra data/towns_ny_*.json (wave 1 NY stays outside the glob)")
check(not ({r["town"] for r in w1} & prod_ny), f"none of the {len(w1)} wave 1 NY towns is in the production NY selection")
check("NY" in current.gated_states(WAVE1_CONFIG) if (WAVE1_CONFIG / "towns_ny.json").exists() else True,
      "the wave 1 NY config is gated")
# Wave 2 New York rows (data/test/wave2/config/towns_ny.json): the same gate
w2_file = WAVE2_CONFIG / "towns_ny.json"
w2 = current.load_towns(WAVE2_CONFIG, include_gated={"NY"}) if w2_file.exists() else []
promoted_w2 = {r["town"] for r in default_rows if r["state"] == "NY" and str(r.get("promoted_from", "")).startswith("wave2")}
check(not ({r["town"] for r in w2} & prod_ny - promoted_w2),
      f"none of the {len(w2)} wave 2 NY rows is in the production NY selection, except the {len(promoted_w2)} promoted "
      "from it with promoted_from = wave2 or wave2_counties")
check("NY" in current.gated_states(WAVE2_CONFIG) if w2_file.exists() else True, "the wave 2 NY config is gated")
# naming a gated state without --output-dir must be refused (exit 2) before any request
for argv, label in ((["--states", "VT"], "VT"),
                    (["--data-dir", str(WAVE1_CONFIG), "--states", "NY"], "wave 1 NY"),
                    (["--data-dir", str(WAVE2_CONFIG), "--states", "NY"], "wave 2 NY")):
    proc = subprocess.run([sys.executable, "-m", "watch351.daily", *argv, "--no-network-docs"],
                          cwd=CRAWLER, capture_output=True, text=True, timeout=120)
    print(f"daily {' '.join(argv)} (no --output-dir): exit", proc.returncode, "|", proc.stderr.strip()[-120:])
    # a gated config whose rows have all been promoted or marked not automated is refused earlier still
    check(proc.returncode == 2 and ("not part of the production run" in proc.stderr or "no automated towns selected" in proc.stderr),
          f"{label} without --output-dir is refused before any request")
# the state-feed modules refuse to write where production reads
for d in (DATA, DATA / "sources"):
    try:
        state_feeds.check_out_dir(d)
        refused = False
    except SystemExit:
        refused = True
    check(refused, f"state feeds refuse --out-dir {d.relative_to(CRAWLER.parent)}")
# Virginia, Maryland, Michigan and Ohio were promoted on 2026-11-03: their towns files are no longer gated
check(not ({"VA", "MD", "MI", "OH"} & gated), "data/towns_va.json, towns_md.json, towns_mi.json and towns_oh.json are not gated")
gl = Counter(r["state"] for r in daily.select_towns(DATA, {"MI", "OH"}, None))
print("explicit --states MI,OH selection:", dict(gl))
check(set(gl) == {"MI", "OH"} if gated >= {"MI", "OH"} else True, "--states MI,OH selects MI and OH only")
print("GATE OK" if ok else "GATE FAILED")
sys.exit(0 if ok else 1)
