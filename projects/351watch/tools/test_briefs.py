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
        bad = {**GOOD, "what": "The permit is for NextGrid Energy, a 4.9 MW solar array."}
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

    def test_a_history_date_of_an_agenda_without_items_passes_through_the_tool(self):
        pass  # covered in ToolTests.test_storage_and_verifier_write_verified (the search doc dated 2026-09-29)

    def test_line_length_and_ids(self):
        bad = {**GOOD, "line": "x" * 91}
        self.assertTrue(any("91 characters" in f for f in B.verify(bad, TEXT, {"2026-09-29"})))
        bad = {**GOOD, "id": "nope"}
        self.assertTrue(any("12-hex" in f for f in B.verify(bad, TEXT, {"2026-09-29"})))

    def test_no_text_fails(self):
        self.assertIn("no agenda text for this document in data/search", B.verify(GOOD, "", set()))


class ToleranceTests(unittest.TestCase):
    """What counts as the same thing written another way."""

    def ok(self, brief, text=TEXT, dates=("2026-09-29",), year=2026):
        self.assertEqual(B.verify(brief, text, set(dates), year), [])

    def test_street_abbreviations_both_ways(self):
        self.ok({**GOOD, "where": "104 Tremont St", "line": "Federal Pond Solar hearing, 104 Tremont St, moves to Oct 27"})
        self.ok({**GOOD, "where": "104 Tremont St."})
        text = TEXT.replace("104 Tremont Street", "104 Tremont St.").replace("235 Main Street", "235 Main Ave")
        self.ok({**GOOD, "where": "104 Tremont Street"}, text)
        self.ok({**GOOD, "where": "235 Main Avenue"}, text)
        self.ok({**GOOD, "where": "235 Main Ave."}, text)
        self.assertTrue(any(f.startswith("where:") for f in B.verify({**GOOD, "where": "104 Tremont Road"}, TEXT, {"2026-09-29"}, 2026)))

    def test_history_dates_from_any_document_we_hold(self):
        self.ok({**GOOD, "history": "The Planning Board also met on Sep 15 and Aug 4, 2026."}, dates=("2026-09-29", "2026-09-15", "2026-08-04"))
        self.assertTrue(any("history" in f for f in B.verify({**GOOD, "history": "Also on the Sep 15 agenda."}, TEXT, {"2026-09-29"}, 2026)))

    def test_can_speak_rests_on_a_standing_item_anywhere(self):
        far = "PRIVILEGE OF THE FLOOR: residents may address the board. " + "Item. " * 400 + TEXT.replace("Public Hearing Cont’d:", "Old business:")
        self.ok({**GOOD, "can_speak": True}, far)
        for cue in ("Citizens' time", "Public participation", "Comments from the public", "Public input", "Open forum"):
            self.ok({**GOOD, "can_speak": True}, cue + ". " + far)

    def test_more_action_cues(self):
        res = TEXT + " RESOLUTION 70-2026: Endorsing the solar array at 104 Tremont Street. The council shall act on it tonight."
        self.ok({**GOOD, "action": "vote", "quote": "Endorsing the solar array at 104 Tremont Street"}, res)
        self.ok({**GOOD, "action": "discussion", "quote": "Endorsing the solar array at 104 Tremont Street"},
                res + " Listening session, informational only.")
        ext = TEXT + " 6. Meadow Solar 1, LLC: request for extension of its special permit at 223 Meadow Street."
        self.ok({**GOOD, "action": "extension", "quote": "request for extension of its special permit"}, ext)
        self.assertTrue(any("extension" in f for f in B.verify({**GOOD, "action": "extension"}, TEXT, {"2026-09-29"}, 2026)))

    def test_number_forms(self):
        text = TEXT + " A 45 ft pole; a 28.251 acres lot; US-made panels; $1,660,000 bond; a 15 minute limit."
        self.ok({**GOOD, "size": "45-foot pole on 28.251-acre lot"}, text)
        self.ok({**GOOD, "size": "45' pole"}, text)
        self.ok({**GOOD, "what": "U.S.-made panels and a $1.66 million bond are listed; a 15-minute limit applies."},
                text.replace("$1,660,000", "$1.66 million"))
        self.ok({**GOOD, "size": "1,660,000 dollars"}, text)
        self.assertTrue(any("46" in f for f in B.verify({**GOOD, "size": "46-foot pole"}, text, {"2026-09-29"}, 2026)))

    def test_weekday_names_count_when_right_for_the_date(self):
        self.ok({**GOOD, "next": "The hearing continues Tue Oct 27."})
        self.ok({**GOOD, "next": "The hearing continues Tuesday, October 27, 2026."})
        self.assertTrue(any("Wed" in f for f in B.verify({**GOOD, "next": "The hearing continues Wed Oct 27."}, TEXT, {"2026-09-29"}, 2026)))

    def test_sentence_initial_and_ordinary_capitals_are_not_facts(self):
        self.ok({**GOOD, "what": "Nothing else is listed. This item is the only one. No vote is listed. Applicant asked to continue."})

    def test_asides_about_our_records_or_copy_fail(self):
        for text in ("The filing was made in July (per our records).", "The rest of the article is cut off in our copy.",
                     "Old Warren Rd Development LLC (Pedro Rodriguez, as the agenda spells it) filed."):
            fails = B.verify({**GOOD, "what": text}, TEXT, {"2026-09-29"}, 2026)
            self.assertTrue(any("say what the agenda says" in f for f in fails), (text, fails))
        fails = B.verify({**GOOD, "how_to_speak": "Public hearing; no rules stated."}, TEXT, {"2026-09-29"}, 2026)
        self.assertTrue(any("no rules stated" in f for f in fails), fails)
        self.ok({**GOOD, "what": "Town Meeting decides later; the Town Clerk posts the result. Both steps are routine."})
        self.assertTrue(any("Acme" in f for f in B.verify({**GOOD, "what": "The plan is from Acme Partners."}, TEXT, {"2026-09-29"}, 2026)))

    def test_bodies_and_state_law_from_our_records(self):
        self.ok({**GOOD, "next": "The Planning Board sends it to the Select Board; the Attorney General reviews a bylaw after Town Meeting."})
        self.ok({**GOOD, "next": "Under Massachusetts state law a town may regulate but not ban solar."})
        self.assertTrue(any("Massachusetts" in f for f in B.verify({**GOOD, "next": "Towns in Massachusetts do this."}, TEXT, {"2026-09-29"}, 2026)))

    def test_two_digit_years(self):
        text = TEXT + " Approved 10/19/21. See the '21 decision and the FY27 budget."
        self.ok({**GOOD, "what": "Approved in 2021 under the FY2027 budget; the 2021 decision stands."}, text)
        self.assertTrue(any("2019" in f for f in B.verify({**GOOD, "what": "Approved in 2019."}, text, {"2026-09-29"}, 2026)))

    def test_board_abbreviations_and_stage_words(self):
        text = TEXT.replace("CARVER PLANNING BOARD", "CARVER ZBA and SELECTBOARD")
        self.ok({**GOOD, "next": "The Zoning Board of Appeals and the Select Board take it up Oct 27."}, text)
        self.ok({**GOOD, "line": "Postponed: Federal Pond Solar hearing moves to Oct 27"})
        self.ok({**GOOD, "line": "Hearing: Federal Pond Solar, 104 Tremont St (Vote Oct 27)"})


class ToolTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="briefs-")
        os.makedirs(os.path.join(self.dir, "search", "MA"))
        with open(os.path.join(self.dir, "search", "MA", "2026-10.jsonl"), "w") as f:
            f.write(json.dumps({"id": "abc", "url": URL, "state": "MA", "town": "Carver", "board_key": "planning_board",
                                "meeting_date": "2026-10-13", "text": TEXT}) + "\n")
            # an earlier agenda with no flagged item: its date may still be named in `history`
            f.write(json.dumps({"id": "abd", "url": URL + "?prev", "state": "MA", "town": "Carver", "board_key": "planning_board",
                                "meeting_date": "2026-09-29", "text": "Planning Board agenda. 1. Minutes. 2. Adjourn."}) + "\n")
        other = {**HIT, "id": "0000000000aa", "meeting_date": "2026-10-01", "source_url": URL + "?x"}
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

    def test_unknown_hit_is_skipped_not_failed(self):
        # an item dropped as off the subject or archived: the brief stays unused, and the run does not fail
        path = B.append_brief(self.dir, {**GOOD, "id": "ffffffffffff"}, "MA", None)
        self.assertEqual(verify_briefs.main(["--data", self.dir, "--quiet"]), 0)
        self.assertIs(B.read_rows(path)[0][1]["verified"], False)
        self.assertEqual(B.load_briefs(self.dir, verified_only=True), {})


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
        self.assertIn(f'>{GOOD["line"]}</a></span>', html.replace("’", "’"))  # the headline links to the meeting page
        self.assertIn('</a></span><span class="stage moved">Asked to move</span></p>', html)  # the status sits beside it
        self.assertIn('<p class="brief-what">Federal Pond Solar wants a special permit', html)
        self.assertNotIn("104 Tremont Street", html, "a list leaves the facts line to the meeting's own page")
        full = self.build.meeting_html(ctx, m, show_town=False, full=True)
        self.assertIn("104 Tremont Street", full)  # the facts line on the meeting page: where, size, who
        self.assertIn("4.9 MW on 22 acres", full)
        self.assertIn('<span class="stage moved">Asked to move</span>', html)  # the applicant asked; the board hasn't agreed yet
        self.assertNotIn("Agenda wording", html, "lists carry no agenda text")
        self.assertNotIn("Copy citation", html)
        self.assertNotIn(self.build.SPEAK_TEXT, html, "a postponed hearing gets no speak line")
        full = self.build.meeting_html(ctx, m, show_town=False, full=True)
        self.assertIn("<summary>Agenda wording</summary>", full)
        self.assertIn(GOOD["quote"], full)
        self.assertIn(GOOD["next"], full)
        self.assertNotIn("requesting a Special Permit and Site Plan Review", full.split("Agenda wording")[0])
        self.assertIn("Read Oct 10, 2026", self.build.citation(ctx, m, next(iter(m["lines"].values()))))

    def test_postponement_names_the_new_day_when_the_brief_has_one(self):
        self.assertEqual(self.build.brief_stage(GOOD), "Asks to postpone")  # GOOD's next: the applicant asked
        moved = {**GOOD, "next": "The company asked to postpone to Tue Oct 27, 2026, 6:30 pm, Town Hall Meeting Room #1."}
        self.assertEqual(self.build.brief_stage(moved), "Asks to postpone to Tue Oct 27")
        self.assertEqual(self.build.brief_stage({**GOOD, "next": "The hearing continues Tue Oct 27."}), "Postponed to Tue Oct 27")
        self.assertEqual(self.build.brief_stage({**GOOD, "next": "The hearing was continued to Tue Oct 27."}), "Postponed to Tue Oct 27")
        self.assertEqual(self.build.brief_stage({**GOOD, "action": "hearing"}), "Hearing")
        self.assertEqual(self.build.brief_stage({**GOOD, "action": "adopted"}), "Final vote")

    def test_speak_line_only_for_a_live_hearing(self):
        self.build.BRIEFS[HIT["id"]] = {**GOOD, "verified": True, "action": "hearing"}
        ctx, m = self.meeting(HIT)
        self.assertEqual(self.build.speak_line(m), self.build.SPEAK_TEXT)
        html = self.build.meeting_html(ctx, m, show_town=False)
        # a list prints the agenda's own rule, keyed "Speaking:", once and above the items; never the generic stamp
        self.assertNotIn(self.build.SPEAK_SHORT[self.build.SPEAK_TEXT], html)
        rule = self.build.speak_rule(m)
        if rule:
            self.assertEqual(html.count("<b>Speaking:</b>"), 1)
            self.assertLess(html.index("<b>Speaking:</b>"), html.index('<ul class="lines">'))
        self.build.BRIEFS[HIT["id"]] = {**GOOD, "verified": True, "action": "continued"}
        ctx, m = self.meeting(HIT)
        self.assertEqual(self.build.speak_line(m), "")

    def test_without_a_brief_the_rules_line_stays(self):
        ctx, m = self.meeting(HIT)
        html = self.build.meeting_html(ctx, m, show_town=False, full=True)
        self.assertIn("<summary>Agenda wording</summary>", html)
        self.assertIn("Federal Pond Solar", html)

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
        self.assertEqual(self.build.BRIEF_STAGE["continued"], "Postponed")


if __name__ == "__main__":
    unittest.main()
