#!/usr/bin/env python3
"""Tests for written briefs: the verifier (briefs.py, tools/verify_briefs.py) and how build.py renders one.

    python3 projects/351watch/tools/test_briefs.py

Standard library only. Builds a small data directory in a temp folder, so the tests do not depend on
the live data.
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import briefs as B  # noqa: E402
import verify_briefs  # noqa: E402

URL = "https://www.carverma.gov/AgendaCenter/ViewFile/Agenda/_10132026-616"
TEXT = ("CARVER PLANNING BOARD AGENDA Tuesday, October 13, 2026 6:30 PM Carver Town Hall, Meeting Room #1. "
        "Public Hearing Cont’d: 3. Federal Pond Solar, LLC, requesting a Special Permit and Site Plan Review "
        "pursuant to Section 290-3-1 of the Carver Zoning By Law, located at 104 Tremont Street in Carver, MA, "
        "for a 4.9 MW ground-mounted solar array and coupled BESS on 22 acres. Applicant has requested a "
        "continuance to October 27, 2026. 4. Parallel Products Solar Energy, LLC. requesting a Special Permit "
        "located at 235 Main Street. 5. Adjourn")
HIT = {"id": "7bdece78956c", "state": "MA", "town": "Carver", "county": "Plymouth", "board": "Planning Board",
       "board_key": "planning_board", "meeting_date": "2026-10-13", "topics": ["battery_storage", "solar"],
       "snippet": "Federal Pond Solar, LLC, requesting a Special Permit and Site Plan Review",
       "source_url": URL, "document_title": "October 13, 2026 - PB Agenda", "first_seen": "2026-10-10T14:41:35+00:00",
       "source": "agenda"}
GOOD = {"id": "7bdece78956c", "what": "Federal Pond Solar wants a special permit for a 4.9 MW solar array with battery storage.",
        "where": "104 Tremont Street", "size": "4.9 MW on 22 acres", "who": "Federal Pond Solar, LLC",
        "action": "continued", "next": "The applicant asked to continue the hearing to October 27.",
        "history": "Also on the Sept 29 agenda.", "can_speak": True,
        "line": "Federal Pond Solar’s 4.9 MW solar and battery permit: hearing continued to Oct 27",
        "quote": "Applicant has requested a continuance to October 27, 2026.", "source_url": URL,
        "written_at": "2026-10-12T21:00:00+00:00", "writer": "test"}


class VerifyTests(unittest.TestCase):
    def test_a_good_brief_passes(self):
        self.assertEqual(B.verify(GOOD, TEXT, {"2026-09-29", "2026-10-13"}), [])

    def test_an_invented_number_fails(self):
        bad = {**GOOD, "size": "9.9 MW on 22 acres"}
        fails = B.verify(bad, TEXT, {"2026-09-29"})
        self.assertTrue(any(f.startswith("size:") and "9.9" in f for f in fails), fails)
        bad = {**GOOD, "line": "Federal Pond Solar’s 12 MW solar permit: hearing continued to Oct 27"}
        self.assertTrue(any("12" in f for f in B.verify(bad, TEXT, {"2026-09-29"})))

    def test_a_wrong_quote_fails(self):
        bad = {**GOOD, "quote": "Applicant has requested a continuance to November 3, 2026."}
        self.assertIn("quote is not in the agenda word for word", B.verify(bad, TEXT, {"2026-09-29"}))

    def test_a_quote_survives_whitespace_and_curly_quotes(self):
        ok = {**GOOD, "quote": "Public Hearing Cont'd:  3. Federal Pond Solar, LLC, requesting a Special Permit"}
        self.assertEqual(B.verify(ok, TEXT, {"2026-09-29"}), [])
        joined = {**GOOD, "quote": "Federal Pond Solar, LLC, requesting a Special Permit … Applicant has requested a continuance"}
        self.assertEqual(B.verify(joined, TEXT, {"2026-09-29"}), [])

    def test_an_invented_name_or_address_fails(self):
        bad = {**GOOD, "who": "Acme Solar Partners"}
        self.assertTrue(any(f.startswith("who:") for f in B.verify(bad, TEXT, {"2026-09-29"})))
        bad = {**GOOD, "where": "104 Tremont Street, Plympton"}
        self.assertTrue(any(f.startswith("where:") and "plympton" in f.lower() for f in B.verify(bad, TEXT, {"2026-09-29"})))
        bad = {**GOOD, "what": "NextGrid Energy wants a special permit for a 4.9 MW solar array."}
        self.assertTrue(any("nextgrid" in f.lower() for f in B.verify(bad, TEXT, {"2026-09-29"})))

    def test_action_needs_its_cue(self):
        bad = {**GOOD, "action": "withdrawn"}
        self.assertTrue(any("withdrawn" in f for f in B.verify(bad, TEXT, {"2026-09-29"})))
        bad = {**GOOD, "action": "mentioned"}
        self.assertTrue(any("not one of" in f for f in B.verify(bad, TEXT, {"2026-09-29"})))

    def test_can_speak_needs_a_hearing_or_public_comment(self):
        text = TEXT.replace("Public Hearing Cont’d:", "Old business:")
        bad = {**GOOD, "can_speak": True}
        self.assertTrue(any("can_speak" in f for f in B.verify(bad, text, {"2026-09-29"})))
        self.assertEqual(B.verify({**GOOD, "can_speak": None}, text, {"2026-09-29"}), [])

    def test_history_dates_must_be_ours(self):
        fails = B.verify(GOOD, TEXT, {"2026-10-13"})
        self.assertTrue(any("history" in f and "9/29" in f for f in fails), fails)

    def test_line_length_and_ids(self):
        bad = {**GOOD, "line": "x" * 91}
        self.assertTrue(any("91 characters" in f for f in B.verify(bad, TEXT, {"2026-09-29"})))
        bad = {**GOOD, "id": "nope"}
        self.assertTrue(any("12-hex" in f for f in B.verify(bad, TEXT, {"2026-09-29"})))

    def test_no_text_fails(self):
        self.assertIn("no agenda text for this document in data/search", B.verify(GOOD, "", set()))


class ToolTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="briefs-")
        os.makedirs(os.path.join(self.dir, "search", "MA"))
        with open(os.path.join(self.dir, "search", "MA", "2026-10.jsonl"), "w") as f:
            f.write(json.dumps({"id": "abc", "url": URL, "state": "MA", "town": "Carver", "board_key": "planning_board",
                                "meeting_date": "2026-10-13", "text": TEXT}) + "\n")
        other = {**HIT, "id": "0000000000aa", "meeting_date": "2026-09-29", "source_url": URL + "?x"}
        with open(os.path.join(self.dir, "hits_current.json"), "w") as f:
            json.dump({"generated": "2026-10-12T13:00:00+00:00", "window": {"start": "2026-06-14", "end": "2027-02-09"},
                       "hits": [HIT, other]}, f)

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_storage_and_verifier_write_verified(self):
        path = B.append_brief(self.dir, {**GOOD, "verified": True}, "MA", "2026-10-13")
        self.assertTrue(path.endswith(os.path.join("briefs", "MA", "2026-10.jsonl")))
        rows = B.read_rows(path)
        self.assertNotIn("verified", rows[0][1], "only the verifier sets verified")
        B.append_brief(self.dir, {**GOOD, "quote": "not in the agenda", "written_at": "2026-10-12T22:00:00+00:00"}, "MA", "2026-10-13")
        # the latest row for an id wins
        self.assertEqual(B.load_briefs(self.dir)["7bdece78956c"]["quote"], "not in the agenda")
        code = verify_briefs.main(["--data", self.dir, "--quiet"])
        self.assertEqual(code, 1)
        rows = [r for _, r in B.read_rows(path)]
        self.assertNotIn("verified", rows[0], "a superseded row is left as it was")
        self.assertIs(rows[1]["verified"], False)
        self.assertEqual(B.load_briefs(self.dir, verified_only=True), {})
        # a good row written later passes and is the one loaded
        B.append_brief(self.dir, {**GOOD, "written_at": "2026-10-12T23:00:00+00:00"}, "MA", "2026-10-13")
        self.assertEqual(verify_briefs.main(["--data", self.dir, "--quiet"]), 0)
        self.assertIs(B.load_briefs(self.dir, verified_only=True)["7bdece78956c"]["verified"], True)

    def test_check_mode_writes_nothing(self):
        path = B.append_brief(self.dir, {**GOOD, "size": "99 MW"}, "MA", "2026-10-13")
        self.assertEqual(verify_briefs.main(["--data", self.dir, "--check", "--quiet"]), 1)
        self.assertNotIn("verified", B.read_rows(path)[0][1])

    def test_unknown_hit_fails(self):
        B.append_brief(self.dir, {**GOOD, "id": "ffffffffffff"}, "MA", None)
        self.assertEqual(verify_briefs.main(["--data", self.dir, "--quiet"]), 1)


class RenderTests(unittest.TestCase):
    """build.py shows a verified brief as the item's heading, its facts and the exact wording."""

    def setUp(self):
        import build  # noqa: F401  (imports trending; no side effects at import)
        self.build = build
        build.BRIEFS.clear()
        build.ANALYSIS.clear()

    def tearDown(self):
        self.build.BRIEFS.clear()

    def meeting(self, hit):
        ctx = SimpleNamespace(today="2026-10-12", town_by_id={}, headers={}, is_new=lambda h: False,
                              known_posting=lambda *a: False)
        return ctx, self.build.group_meetings(ctx, [hit])[0]

    def test_brief_replaces_the_rules_based_line(self):
        self.build.BRIEFS[HIT["id"]] = {**GOOD, "verified": True}
        ctx, m = self.meeting(HIT)
        html = self.build.meeting_html(ctx, m, show_town=False)
        self.assertIn(f'<p class="line-say">{GOOD["line"]}</p>', html.replace("’", "’"))
        self.assertIn('<p class="brief-what">Federal Pond Solar wants a special permit', html)
        for label in ("Where", "Size", "Who", "Next", "Earlier", "Can I speak?"):
            self.assertIn(f"<dt>{label}</dt>", html)
        self.assertIn("<dd>104 Tremont Street</dd>", html)
        self.assertIn("<summary>Exact agenda wording</summary>", html)
        self.assertIn(GOOD["quote"], html)
        self.assertNotIn("requesting a Special Permit and Site Plan Review", html.split("Exact agenda wording")[0])
        self.assertIn("Retrieved Oct 10, 2026", html)

    def test_without_a_brief_the_rules_line_stays(self):
        ctx, m = self.meeting(HIT)
        html = self.build.meeting_html(ctx, m, show_town=False)
        self.assertNotIn("Exact agenda wording", html)
        self.assertIn("Show the agenda text", html)

    def test_brief_stays_first_and_whole_in_a_meeting(self):
        self.build.BRIEFS[HIT["id"]] = {**GOOD, "verified": True}
        other = {**HIT, "id": "0000000000bb", "topics": ["solar"],
                 "snippet": "Federal Pond Solar, LLC, requesting a Special Permit and Site Plan Review for solar"}
        ctx, m = self.meeting(other)
        ctx, m = ctx, self.build.group_meetings(ctx, [other, HIT])[0]
        first = next(iter(m["lines"].values()))
        self.assertEqual(first["kind"], "brief")

    def test_labels_live_in_one_dict(self):
        self.assertEqual(list(self.build.BRIEF_LABELS)[:2], ["what", "where"])
        html = self.build.brief_facts_html({"where": "Main St", "can_speak": False})
        self.assertIn("<dt>Where</dt><dd>Main St</dd>", html)
        self.assertIn(self.build.BRIEF_SPEAK[False], html)
        self.assertNotIn("<dt>Size</dt>", html)


if __name__ == "__main__":
    unittest.main()
