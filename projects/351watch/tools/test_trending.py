#!/usr/bin/env python3
"""Tests for trending.py: grouping, scoring order, headline templates, fallbacks, quotes, personalization.

    python3 projects/351watch/tools/test_trending.py        (or: python3 -m unittest discover -s projects/351watch/tools)

Standard library only. Builds small synthetic inputs, so the tests do not depend on the live data.
"""

import hashlib
import importlib.util
import os
import re
import sys
import unittest
from datetime import date, datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.dont_write_bytecode = True  # no __pycache__ next to the de-slop skill when its linter is loaded
import trending as T  # noqa: E402

TODAY = date(2026, 10, 12)
NOW = datetime(2026, 10, 12, 20, 0, tzinfo=timezone.utc)


def hit(town, board, board_key, meeting_date, topics, snippet, url, state="MA", first_seen="2026-10-11T12:00:00+00:00",
        source="agenda", title="Agenda"):
    hid = hashlib.sha1((url + "|" + snippet).encode()).hexdigest()[:12]
    return {"id": hid, "state": state, "town": town, "county": "Test", "board": board, "board_key": board_key,
            "meeting_date": meeting_date, "topics": topics, "snippet": snippet, "source_url": url,
            "document_title": title, "first_seen": first_seen, "source": source}


def inputs(hits, docs=None, coverage=None, history=None, tracker=None, ag=None, neighbors=None):
    """The dict load_inputs() returns, built in memory. docs: {url: text}."""
    rows = {}
    for url, text in (docs or {}).items():
        rows[url] = {"url": url, "text": text, "title": "Agenda"}
    hist = list(history or [])
    for h in hits:
        for t in h["topics"]:
            hist.append((h["state"], h["town"], t, T.parse_date(h["meeting_date"])))
    return {"hits_doc": {"generated": NOW.isoformat(), "window": {"start": "2026-06-14", "end": "2027-02-09"},
                         "hits": hits},
            "docs": rows, "history": hist, "coverage": coverage or {}, "tracker": tracker or [], "ag": ag or [],
            "neighbors": neighbors or {}}


def build(hits, **kw):
    return T.build(inputs(hits, **kw), TODAY, NOW)["stories"]


CARVER_TEXT = (
    "AGENDA 1. Call to order. Public Hearing Cont'd: 3. Federal Pond Solar, LLC, requesting a Special Permit and Site "
    "Plan Review pursuant to Section 290-3-1 of the Carver Zoning By Law, located at 104 Tremont Street in Carver, MA. "
    "Construction of ground-mounted solar and coupled BESS. Applicant has requested a continuance to October 27, 2026 "
    "Public Hearing: 4. Parallel Products Solar Energy, LLC. requesting a Special Permit and Site Plan Review pursuant "
    "to Section 290-3-6.3 of the Carver Zoning By Law, located at 235 Main Street in Carver, MA for the installation of "
    "a ground-mounted solar canopy system. 5. Adjourn")
NORTHAMPTON_TEXT = (
    "Northampton Public Hearings October 29, 2026 City Council Committee on Legislative Matters with Planning Board "
    "7:00 PM Proposed zoning ordinance amendments to establish definition of data centers and to impose a 365 day "
    "temporary moratorium on establishment of a data center by amending 350-2.0 and 350-5.2.")


class GroupingTests(unittest.TestCase):
    def test_same_llc_at_two_boards_is_one_story(self):
        pb = "https://x.gov/pb-1013"
        cc = "https://x.gov/cc-1014"
        docs = {
            pb: "AGENDA 1. Public Hearing: Somerset Energy Storage, LLC requesting a special permit for a battery "
                "energy storage system at 1606 Riverside Avenue. 2. Adjourn",
            cc: "AGENDA 1. Notice of Intent by Somerset Energy Storage, LLC for a battery energy storage system "
                "within the buffer zone. 2. Adjourn",
        }
        hits = [hit("Somerset", "Planning Board", "planning_board", "2026-10-13", ["battery_storage"],
                    "Somerset Energy Storage, LLC requesting a special permit for a battery energy storage system", pb),
                hit("Somerset", "Conservation Commission", "conservation_commission", "2026-10-14", ["battery_storage"],
                    "Somerset Energy Storage, LLC for a battery energy storage system within the buffer zone", cc)]
        stories = build(hits, docs=docs)
        self.assertEqual(len(stories), 1)
        self.assertEqual(len(stories[0]["hit_ids"]), 2)
        self.assertIn("2 town boards", stories[0]["reasons"])

    def test_same_address_is_one_story(self):
        pb = "https://x.gov/upton-pb"
        cc = "https://x.gov/upton-cc"
        docs = {pb: "7:35 169 South St – Public Hearing – Special Permit for a proposed Large-Scale Ground-Mounted "
                    "Solar Photovoltaic Installation 8:00 Adjourn",
                cc: "7:30 NOI - 169 South St Solar Field (Continued from Sept 23) 7:40 Adjourn"}
        hits = [hit("Upton", "Planning Board", "planning_board", "2026-10-13", ["solar"],
                    "Special Permit for a proposed Large-Scale Ground-Mounted Solar Photovoltaic Installation", pb),
                hit("Upton", "Conservation Commission", "conservation_commission", "2026-10-14", ["solar"],
                    "NOI - 169 South St Solar Field (Continued from Sept 23)", cc)]
        stories = build(hits, docs=docs)
        self.assertEqual(len(stories), 1)
        self.assertIn("169 South St", stories[0]["headline"])

    def test_same_town_topic_meeting_is_one_story(self):
        url = "https://x.gov/carver"
        hits = [hit("Carver", "Planning Board", "planning_board", "2026-10-13", ["solar"],
                    "Federal Pond Solar, LLC, requesting a Special Permit and Site Plan Review", url),
                hit("Carver", "Planning Board", "planning_board", "2026-10-13", ["solar"],
                    "Parallel Products Solar Energy, LLC. requesting a Special Permit and Site Plan Review", url)]
        stories = build(hits, docs={url: CARVER_TEXT})
        self.assertEqual(len(stories), 1)

    def test_different_topics_in_one_meeting_stay_apart(self):
        url = "https://x.gov/leyden"
        text = ("AGENDA 1. Review of consolidated local permitting process for proposed clean energy infrastructure "
                "facility (solar, wind, battery storage, etc.) 2. Dark sky bylaw 3. AI data center moratorium? 4. Adjourn")
        hits = [hit("Leyden", "Planning Board", "planning_board", "2026-10-14", ["moratorium", "data_center"],
                    "AI data center moratorium?", url),
                hit("Leyden", "Planning Board", "planning_board", "2026-10-14",
                    ["battery_storage", "solar", "clean_energy_siting"],
                    "consolidated local permitting process for proposed clean energy infrastructure facility", url)]
        stories = build(hits, docs={url: text})
        self.assertEqual(len(stories), 2)
        self.assertEqual(stories[0]["action"], "moratorium")

    def test_same_llc_in_two_towns_counts_both(self):
        a, b = "https://a.gov/1", "https://b.gov/1"
        docs = {a: "AGENDA 1. Public Hearing: Kestrel Ridge Storage, LLC requesting a special permit for a battery "
                   "energy storage system on the town line. 2. Adjourn",
                b: "AGENDA 1. Public Hearing: Kestrel Ridge Storage, LLC requesting a special permit for a battery "
                   "energy storage system access road. 2. Adjourn"}
        hits = [hit("Carver", "Planning Board", "planning_board", "2026-10-15", ["battery_storage"],
                    "Kestrel Ridge Storage, LLC requesting a special permit for a battery energy storage system on", a),
                hit("Plympton", "Zoning Board of Appeals", "zoning_board_of_appeals", "2026-10-16", ["battery_storage"],
                    "Kestrel Ridge Storage, LLC requesting a special permit for a battery energy storage system access", b)]
        stories = build(hits, docs=docs, neighbors={"MA:Carver": ["MA:Plympton"], "MA:Plympton": ["MA:Carver"]})
        self.assertEqual(len(stories), 1)
        self.assertEqual(stories[0]["towns"], ["MA:Carver", "MA:Plympton"])
        self.assertIn("Neighboring Plympton too", stories[0]["reasons"])
        apart = build(hits, docs=docs)  # without neighbor data the reason names the town
        self.assertIn("Also in Plympton", apart[0]["reasons"])

    def test_utility_name_does_not_join_towns(self):
        a, b = "https://a.gov/2", "https://b.gov/2"
        docs = {a: "AGENDA 1. Public Hearing: New England Power Company requesting a special permit for a battery "
                   "storage yard at the substation. 2. Adjourn",
                b: "AGENDA 1. Public Hearing: New England Power Company requesting a special permit for a battery "
                   "storage cabinet at the depot. 2. Adjourn"}
        hits = [hit("Berlin", "Planning Board", "planning_board", "2026-10-15", ["battery_storage"],
                    "New England Power Company requesting a special permit for a battery storage yard", a),
                hit("Lowell", "Planning Board", "planning_board", "2026-10-15", ["battery_storage"],
                    "New England Power Company requesting a special permit for a battery storage cabinet", b)]
        self.assertEqual(len(build(hits, docs=docs)), 2)


class ScoringTests(unittest.TestCase):
    def test_data_center_moratorium_outranks_solar_continuance(self):
        n = "https://x.gov/northampton"
        c = "https://x.gov/carver"
        hits = [hit("Northampton", "Planning Board", "planning_board", "2026-10-13", ["moratorium", "data_center"],
                    "impose a 365 day temporary moratorium on establishment of a data center", n),
                hit("Carver", "Planning Board", "planning_board", "2026-10-13", ["solar"],
                    "Federal Pond Solar, LLC, requesting a Special Permit and Site Plan Review", c)]
        stories = build(hits, docs={n: NORTHAMPTON_TEXT, c: CARVER_TEXT})
        self.assertEqual(stories[0]["town"], "Northampton")
        self.assertEqual(stories[1]["action"], "continuance")
        self.assertGreater(stories[0]["score"], 3 * stories[1]["score"])

    def test_sooner_meeting_ranks_higher(self):
        hits = [hit("Lakeville", "Planning Board", "planning_board", "2026-10-15", ["battery_storage"],
                    "Public hearing on a new Battery Energy Storage Systems zoning bylaw", "https://x.gov/a"),
                hit("Lenox", "Planning Board", "planning_board", "2026-11-21", ["battery_storage"],
                    "Public hearing on a new Battery Energy Storage Systems zoning bylaw", "https://x.gov/b")]
        stories = build(hits)
        self.assertEqual([s["town"] for s in stories], ["Lakeville", "Lenox"])
        self.assertIn("Hearing Oct 15", stories[0]["reasons"])  # a date; the page shows "in 3 days"

    def test_past_meetings_drop_off(self):
        hits = [hit("Lakeville", "Planning Board", "planning_board", "2026-10-01", ["battery_storage"],
                    "Public hearing on a new Battery Energy Storage Systems zoning bylaw", "https://x.gov/a")]
        self.assertEqual(build(hits), [])

    def test_minutes_alone_never_make_a_story(self):
        mins = ("Minutes of September 22. Councilor White made a motion to ordain. Councilor Cunningham inquired about "
                "the range for small, medium and large BESS. He questioned what kilowatt hour is safe.")
        m, hr = "https://x.gov/minutes", "https://x.gov/hearing"
        hits = [hit("Pittsfield", "City Council", "select_board", "2026-10-13", ["battery_storage"],
                    "Councilor Cunningham inquired about the range for small, medium and large BESS", m),
                hit("Lakeville", "Planning Board", "planning_board", "2026-10-22", ["battery_storage"],
                    "Public hearing on a new Battery Energy Storage Systems zoning bylaw", hr)]
        stories = build(hits, docs={m: mins})
        self.assertEqual([s["town"] for s in stories], ["Lakeville"])  # minutes only count toward other stories

    def test_first_in_town_needs_history(self):
        h = hit("Burrillville", "Town Council", "select_board", "2026-10-14", ["data_center"],
                "Consider and act on a petition to prohibit data centers; or take any other action thereon.",
                "https://x.gov/b")
        with_history = build([h], coverage={("MA", "Burrillville"): date(2026, 7, 1)})
        self.assertIn("First time this has come up in Burrillville", with_history[0]["reasons"])
        no_history = build([h], coverage={("MA", "Burrillville"): date(2026, 9, 1)})  # 43 days is too little
        self.assertFalse(any(r.startswith("First time") for r in no_history[0]["reasons"]))
        earlier = build([h], coverage={("MA", "Burrillville"): date(2026, 7, 1)},
                        history=[("MA", "Burrillville", "data_center", date(2026, 9, 1))])
        self.assertFalse(any(r.startswith("First time") for r in earlier[0]["reasons"]))

    def test_stated_scale_adds_points(self):
        big = hit("Saugus", "Board of Appeals", "zoning_board_of_appeals", "2026-10-15", ["40b_comprehensive_permit"],
                  "Public hearing on an application by 20 Bennett LLC for a comprehensive permit to build three "
                  "hundred (300) rental apartment units", "https://x.gov/s")
        small = hit("Sandwich", "Board of Appeals", "zoning_board_of_appeals", "2026-10-15", ["40b_comprehensive_permit"],
                    "Public hearing on an application by Elm Court LLC for a comprehensive permit to build a "
                    "duplex with affordable units", "https://x.gov/t")
        stories = build([big, small])
        self.assertEqual(stories[0]["town"], "Saugus")
        self.assertIn("300 units", stories[0]["reasons"])


class HeadlineTests(unittest.TestCase):
    def test_moratorium_hearing(self):
        url = "https://x.gov/n"
        s = build([hit("Northampton", "Planning Board", "planning_board", "2026-10-29", ["moratorium", "data_center"],
                       "impose a 365 day temporary moratorium on establishment of a data center", url)],
                  docs={url: NORTHAMPTON_TEXT})[0]
        self.assertEqual(s["headline"], "Northampton planners hold hearing on a 365-day data-center moratorium")
        self.assertEqual(s["dek"], "The Planning Board meets Thursday, Oct 29. The agenda lists a public hearing on "
                                   "a temporary moratorium on data centers.")
        self.assertIn("Moratorium hearing", s["reasons"])

    def test_named_project_hearing(self):
        url = "https://x.gov/carver"
        text = CARVER_TEXT.replace("Applicant has requested a continuance to October 27, 2026 ", "")
        s = build([hit("Carver", "Planning Board", "planning_board", "2026-10-13", ["solar"],
                       "Parallel Products Solar Energy, LLC. requesting a Special Permit and Site Plan Review", url)],
                  docs={url: text})[0]
        self.assertEqual(s["headline"], "Carver planners hear Parallel Products Solar Energy permit request")
        self.assertIn("special permit and site plan review", s["dek"])

    def test_continuance_names_the_applicant_and_date(self):
        url = "https://x.gov/carver"
        s = build([hit("Carver", "Planning Board", "planning_board", "2026-10-13", ["solar"],
                       "Federal Pond Solar, LLC, requesting a Special Permit and Site Plan Review", url)],
                  docs={url: CARVER_TEXT})[0]
        self.assertEqual(s["headline"], "Federal Pond Solar asks Carver planners for continuance to Oct 27")
        self.assertIn("Continuance requested", s["reasons"])

    def test_petition_to_prohibit(self):
        s = build([hit("Burrillville", "Town Council", "select_board", "2026-10-14", ["data_center"],
                       "Consider and act on a petition from Roberta Lacey for an amendment to the General Ordinances, "
                       "Chapter 30 Zoning to prohibit data centers; or take any other action thereon.",
                       "https://x.gov/b", state="RI")])[0]
        self.assertEqual(s["headline"], "Burrillville Town Council takes up petition to prohibit data centers")
        self.assertEqual(s["town_path"], "/ri/burrillville")

    def test_40b_units(self):
        s = build([hit("Saugus", "Board of Appeals", "zoning_board_of_appeals", "2026-10-15",
                       ["40b_comprehensive_permit"],
                       "Public hearing on an application by 20 Bennett LLC for a comprehensive permit to build three "
                       "hundred (300) rental apartment units", "https://x.gov/s")])[0]
        self.assertEqual(s["headline"], "Saugus zoning board hears 300-unit 40B rental plan")

    def test_town_meeting_article(self):
        url = "https://x.gov/harvard"
        text = ("ARTICLE 6: REPLACE SOLAR OVERLAY WITH NEW CLEAN ENERGY FACILITIES BYLAW To see if the Town will vote "
                "to amend the Protective Bylaw by inserting standards for Solar Photovoltaic Installations, Battery "
                "Energy Storage Systems, and Consolidated Local Permitting; or take any other action relative thereto.")
        s = build([hit("Harvard", "Town Meeting", "town_meeting", "2026-10-20",
                       ["battery_storage", "solar", "clean_energy_siting"],
                       "inserting standards for Solar Photovoltaic Installations, Battery Energy Storage Systems", url)],
                  docs={url: text})[0]
        self.assertEqual(s["headline"], "Harvard Town Meeting takes up solar and battery storage rules")
        self.assertTrue(s["dek"].startswith("Harvard's Town Meeting is Tuesday, Oct 20."))

    def test_headlines_avoid_dashes_and_stay_short(self):
        url = "https://x.gov/n"
        stories = build([hit("Northampton", "Planning Board", "planning_board", "2026-10-29",
                             ["moratorium", "data_center"],
                             "impose a 365 day temporary moratorium on establishment of a data center", url)],
                        docs={url: NORTHAMPTON_TEXT})
        for s in stories:
            self.assertLessEqual(len(s["headline"]), T.HEADLINE_MAX)
            self.assertNotRegex(s["headline"] + s["dek"], "[—–]")


class FallbackTests(unittest.TestCase):
    def test_bare_mention_without_text(self):
        s = build([hit("Holyoke", "Planning Board", "planning_board", "2026-10-13", ["battery_storage"],
                       "Short Term Rentals, ZC Tiny Homes, SPR BESS Agilitas, PH SP Fence Rafael",
                       "https://x.gov/h")])[0]
        self.assertEqual(s["headline"], "Battery storage item on Holyoke Planning Board agenda")
        self.assertEqual(s["dek"], "The Planning Board meets Tuesday, Oct 13. The agenda lists an item on battery storage.")

    def test_project_without_name_or_address(self):
        s = build([hit("Clay", "Zoning Board of Appeals", "zoning_board_of_appeals", "2026-10-14", ["battery_storage"],
                       "Public hearing on an area variance to reduce setbacks for the development of BESS equipment",
                       "https://x.gov/c", state="NY")])[0]
        self.assertEqual(s["headline"], "Clay zoning board hears variance request for a battery storage project")

    def test_long_names_fall_back_to_a_shorter_template(self):
        long_name = "Northeastern Massachusetts Regional Community Renewable Energy Cooperative Holdings"
        s = build([hit("Westborough", "Conservation Commission", "conservation_commission", "2026-10-14", ["solar"],
                       f"Public hearing: {long_name} LLC requesting a special permit for a ground-mounted solar array",
                       "https://x.gov/w")])[0]
        self.assertLessEqual(len(s["headline"]), T.HEADLINE_MAX)
        self.assertIn("Westborough Conservation Commission", s["headline"])

    def test_undated_fall_warrant(self):
        url = "https://x.gov/holliston"
        text = ("Commonwealth of Massachusetts. ARTICLE 12 To see if the Town will vote to amend the Zoning Bylaw by "
                "adding a Battery Energy Storage Systems section; or take any other action relative thereto.")
        s = build([hit("Holliston", "Town Meeting", "town_meeting", None, ["battery_storage"],
                       "adding a Battery Energy Storage Systems section", url,
                       title="October 2026 Town Meeting Warrant")], docs={url: text})[0]
        self.assertIsNone(s["meeting_date"])
        self.assertIn("gives no date", s["dek"])
        self.assertIn("Town Meeting date not in the warrant", s["reasons"])

    def test_warrant_date_is_read_from_the_warrant(self):
        d, hint = T.warrant_date("The inhabitants are to meet at the High School on Saturday, October 17, 2026 at "
                                 "9:00 AM for the Fall Annual Town Meeting.", "FINAL 2026 Fall Annual Town Meeting")
        self.assertEqual(d, date(2026, 10, 17))


class TextTests(unittest.TestCase):
    def test_quote_is_short_and_clean(self):
        text = ("AGENDA 5° oo006806d~CO0dU6lU(O e Public hearing for bylaw amendments: amending Section 4 Definitions "
                "to add Battery Energy Storage System and to set standards for battery energy storage in all districts, "
                "with setbacks, fencing, noise limits, decommissioning surety, fire department review and annual "
                "inspection of every system larger than seventy kilowatt hours, as shown on the plan on file.")
        q = T.pick_quote(text, [T.SUBJECT_RE["battery_storage"]], T.BYLAW_RE, "")
        self.assertLessEqual(len(q), 201)
        self.assertNotIn("~", q)
        self.assertIn("Battery", q)

    def test_unit_count_is_the_total(self):
        item = ("a four (4)-story elevator building offering a total of 116 rental units, including 87 units priced at "
                "market and 29 units income restricted")
        self.assertEqual(T.extract_scale(item)[0][1], "116 units")
        item = "three hundred (300) rental apartment units (25% of which (75 units) will be affordable)"
        self.assertEqual([s[1] for s in T.extract_scale(item)], ["300 units"])

    def test_articles_and_durations(self):
        self.assertEqual(T.with_article("one-year moratorium"), "a one-year moratorium")
        self.assertEqual(T.with_article("87-unit plan"), "an 87-unit plan")
        self.assertEqual(T.with_article("18-month moratorium"), "an 18-month moratorium")
        self.assertEqual(T.extract_duration("a Twelve (12) Month Moratorium on data centers"), "12-month")
        self.assertEqual(T.extract_duration("impose a 365 day temporary moratorium"), "365-day")

    def test_address_skips_offices_and_meeting_rooms(self):
        item = ("filed by High Street Solar 1, LLC, 55 Technology Drive, Suite 102, Lowell, MA 01851, for the property "
                "located at 0 High Street in Rochester. Meeting at Town Hall, 1 Constitution Way.")
        self.assertEqual(T.extract_address(item, "Rochester")[0], "0 High Street")

    def test_names_skip_lawyers_and_owners(self):
        item = ("Petitioner, On Commons LLC C/O, Blatman, Bobrowski, Haverty & Silverstein, LLC is requesting a "
                "Comprehensive Permit")
        self.assertEqual([n[0] for n in T.extract_names(item, "Mashpee")], ["On Commons"])


class PersonalizationTests(unittest.TestCase):
    def test_formula(self):
        stories = [
            {"id": "a", "score": 20.0, "state": "MA", "town": "Pittsfield", "towns": ["MA:Pittsfield"],
             "topics": ["data_center"]},
            {"id": "b", "score": 8.0, "state": "MA", "town": "Carver", "towns": ["MA:Carver"], "topics": ["solar"]},
            {"id": "c", "score": 6.0, "state": "MA", "town": "Plympton", "towns": ["MA:Plympton"],
             "topics": ["battery_storage"]},
        ]
        neighbors = {"MA:Carver": ["MA:Plympton", "MA:Wareham"], "MA:Plympton": ["MA:Carver"]}
        out = T.personalize(stories, ["MA:Carver"], neighbors, ["battery_storage"])
        got = {s["id"]: s["personal_score"] for s in out}
        self.assertEqual(got["b"], 24.0)    # 8 x (1 + 2) x 1
        self.assertEqual(got["c"], 18.0)    # 6 x (1 + 1) x 1.5
        self.assertEqual(got["a"], 20.0)    # unchanged
        self.assertEqual([s["id"] for s in out], ["b", "a", "c"])


class OutputTests(unittest.TestCase):
    def test_schema(self):
        url = "https://x.gov/n"
        out = T.build(inputs([hit("Northampton", "Planning Board", "planning_board", "2026-10-29",
                                  ["moratorium", "data_center"],
                                  "impose a 365 day temporary moratorium on establishment of a data center", url)],
                             docs={url: NORTHAMPTON_TEXT}), TODAY, NOW)
        self.assertEqual(set(out), {"generated", "window", "personalize", "stories"})
        s = out["stories"][0]
        for key in ("id", "score", "headline", "dek", "quote", "reasons", "topics", "state", "town", "county", "towns",
                    "board", "meeting_date", "days_until", "first_seen", "is_new", "source_url", "town_path", "hit_ids"):
            self.assertIn(key, s)
        self.assertEqual(s["days_until"], 17)
        self.assertTrue(s["is_new"])


def load_linter():
    path = os.path.join(PROJECT, "..", "..", ".claude", "skills", "de-slop", "scripts", "slop_lint.py")
    if not os.path.exists(path):
        return None
    spec = importlib.util.spec_from_file_location("slop_lint", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


READER_BANNED = re.compile(r"\bpacket\b|\bmention|\bflagged\b|\bmatched\b|\bhits?\b|\btracker\b|first seen|"
                           r"\btoday\b|\btomorrow\b", re.I)
REASON_BANNED = re.compile(r"\b(?:Mon|Tues|Wednes|Thurs|Fri|Satur|Sun)day\b|\bitem\b")  # dates, not days; no topic echo


class CopyLintTests(unittest.TestCase):
    """Every template, filled with sample words, passes the de-slop linter's word rules."""

    def test_templates_are_clean(self):
        lint = load_linter()
        if lint is None:
            self.skipTest("slop_lint.py not found")
        samples = [
            hit("Northampton", "Planning Board", "planning_board", "2026-10-29", ["moratorium", "data_center"],
                "Public hearing to impose a 365 day temporary moratorium on data centers", "https://x.gov/1"),
            hit("Leyden", "Planning Board", "planning_board", "2026-10-14", ["moratorium", "data_center"],
                "6. AI data center moratorium?", "https://x.gov/2"),
            hit("South Hadley", "Planning Board", "planning_board", "2026-10-26", ["data_center"],
                "public hearing on amendments to the Zoning Bylaw to prohibit the construction of data centers",
                "https://x.gov/3"),
            hit("Geneva", "Town Board", "select_board", "2026-10-13", ["battery_storage"],
                "RESOLUTION NO. 68-2026 Adopting Local Law No. 5 of 2026, Battery Energy Storage Systems.",
                "https://x.gov/4", state="NY"),
            hit("Egremont", "Planning Board", "planning_board", "2026-10-16", ["battery_storage"],
                "Battery Energy Storage System Draft Bylaw", "https://x.gov/5"),
            hit("Weston", "Planning Board", "planning_board", "2026-10-21", ["zoning_amendment"],
                "public hearing on a petition to rezone a 28-acre portion of 300 Wellesley St from SR to MF",
                "https://x.gov/6"),
            hit("Beverly", "Zoning Board of Appeals", "zoning_board_of_appeals", "2026-10-28", ["wireless_telecom"],
                "public hearing on a Special Permit to permit a wireless communications facility with a monopole 124 "
                "feet in height at 12 Tozer Road", "https://x.gov/7"),
            hit("Mattapoisett", "Select Board", "select_board", "2026-10-13", ["clean_energy_siting"],
                "Vote to approve the DOER Consolidated Permit Application Process", "https://x.gov/8"),
            hit("Millbury", "Board of Selectmen", "select_board", "2026-10-13", ["solar"],
                "Millbury Landfill Solar - Lease Amendment and Notice of Lease", "https://x.gov/9"),
            hit("Swansea", "Conservation Commission (wetlands filing)", "conservation_commission", "2026-10-05",
                ["wetlands_filing", "battery_storage"],
                "NOI, Old Warren Road Development II, LLC: Build 4.9 MW-AC battery energy storage system.",
                "https://x.gov/10", source="massdep_wetlands"),
            hit("Lexington", "Planning Board", "planning_board", "2026-10-21", ["zoning_amendment"],
                "The Public Hearing on Zoning Bylaw Amendments for October 21, 2026, has been CANCELLED",
                "https://x.gov/11"),
        ]
        out = T.build(inputs(samples), TODAY, NOW)
        lines = []
        for s in out["stories"]:
            lines += [s["headline"], s["dek"]] + s["reasons"]
        self.assertGreaterEqual(len(out["stories"]), 10)
        hits = []
        for line in lines:
            for rid, _cat, _w, pat, _msg in lint.RULES:
                if rid in ("arrow", "emoji", "middot-meta"):
                    continue
                if re.search(pat, line, re.I):
                    hits.append((rid, line))
        self.assertEqual(hits, [])

    def test_no_system_words_or_relative_days(self):
        """Readers never see 'packet', 'mentions', 'hits', 'tracker' or 'tomorrow'; reasons give dates."""
        url = "https://x.gov/n"
        samples = [
            hit("Northampton", "Planning Board", "planning_board", "2026-10-13", ["moratorium", "data_center"],
                "Public hearing to impose a 365 day temporary moratorium on data centers", url),
            hit("Holyoke", "Planning Board", "planning_board", "2026-10-12", ["battery_storage"],
                "Short Term Rentals, ZC Tiny Homes, SPR BESS Agilitas, PH SP Fence Rafael", "https://x.gov/h"),
            hit("Westfield", "City Council", "select_board", "2026-10-15", ["battery_storage"],
                "public hearing to consider a petition to adopt zoning regulations for battery storage",
                "https://x.gov/w"),
            hit("Pittsfield", "City Council", "select_board", "2026-10-13", ["battery_storage"],
                "Councilor Cunningham inquired about the range for small, medium and large BESS. He said no.",
                "https://x.gov/p"),
        ]
        tracker = [{"town": "Westfield", "topic": "Battery storage", "action": "Moratorium", "status": "Expired"}]
        out = T.build(inputs(samples, tracker=tracker), TODAY, NOW)
        westfield = next(s for s in out["stories"] if s["town"] == "Westfield")
        self.assertIn("Town has an earlier vote on this", westfield["reasons"])
        for s in out["stories"]:
            for line in [s["headline"], s["dek"]] + s["reasons"]:
                self.assertNotRegex(line, READER_BANNED)
            for r in s["reasons"]:
                self.assertNotRegex(r, REASON_BANNED)


if __name__ == "__main__":
    unittest.main()
