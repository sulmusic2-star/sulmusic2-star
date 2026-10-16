#!/usr/bin/env python3
"""A warrant's meeting day comes from its own first lines, and hits about something else are dropped.

    python3 tools/test_dates.py
"""
import os
import sys
import unittest
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "crawler"))
from watch351.dates import warrant_date  # noqa: E402
from watch351.keywords import find_hits, off_subject  # noqa: E402


class WarrantDateTests(unittest.TestCase):
    def test_weekday_month_day_year(self):
        self.assertEqual(warrant_date("TOWN OF PLYMOUTH FALL ANNUAL TOWN MEETING WARRANT Saturday, October 17, 2026 To the"),
                         date(2026, 10, 17))
        self.assertEqual(warrant_date("SPECIAL TOWN MEETING MONDAY, OCTOBER 19, 2026 7:00 PM"), date(2026, 10, 19))
        self.assertEqual(warrant_date("Tues., Oct. 13, 2026 at 7 pm"), date(2026, 10, 13))

    def test_ordinal_day_of_month(self):
        self.assertEqual(warrant_date("to meet on Monday, the Nineteenth day of October, 2026, at 7:00 p.m."), date(2026, 10, 19))
        self.assertEqual(warrant_date("on Monday, the 19th day of October, 2026"), date(2026, 10, 19))

    def test_a_bare_date_is_not_the_meeting(self):
        self.assertIsNone(warrant_date("Fiscal year beginning July 1, 2026. Article 1: budget."))
        self.assertIsNone(warrant_date(None))

    def test_the_weekday_must_match(self):
        self.assertIsNone(warrant_date("SPECIAL TOWN MEETING Monday, October 20, 2026"))  # Oct 20, 2026 is a Tuesday
        self.assertEqual(warrant_date("SPECIAL TOWN MEETING Tuesday, October 20, 2026"), date(2026, 10, 20))

    def test_only_the_top_of_the_document_counts(self):
        text = "x" * 5000 + " Saturday, October 17, 2026"
        self.assertIsNone(warrant_date(text))


class OffSubjectTests(unittest.TestCase):
    def test_general_ordinance_amendment_without_zoning_words(self):
        h = {"topics": ["zoning_amendment"],
             "snippet": "City Council Action Request – General Ordinance Amendment Amend General Ordinances to include E-Bike Regulations and Use"}
        self.assertTrue(off_subject(h))

    def test_zoning_ordinance_amendment_stays(self):
        h = {"topics": ["zoning_amendment"],
             "snippet": "Review and Revise Zoning Ordinance Pertaining to Signs 1. General Ordinance Amendment Ch. 8, Article V, Signs"}
        self.assertFalse(off_subject(h))

    def test_matcher_skips_ordinance_amendments_with_no_zoning_nearby(self):
        text = ("1. Council Order 2026-078: General Ordinance Amendment Prohibiting Use of Traffic Cameras for Traffic "
                "Enforcement. 2. Minutes of the last meeting. 3. Adjourn.")
        self.assertEqual([h.topics for h in find_hits(text)], [])
        text2 = "7. Zoning Bylaw Amendment: Article 12, Accessory Dwelling Units in the Residential district. Public hearing."
        self.assertIn("zoning_amendment", [t for h in find_hits(text2) for t in h.topics])

    def test_pole_petition_and_pfas_moratorium(self):
        self.assertTrue(off_subject({"topics": ["moratorium"], "snippet": "Moratorium on PFAS testing fees, discussion"}))
        self.assertTrue(off_subject({"topics": ["solar"], "snippet": "Eversource pole petition, 2 poles on Solar Lane; conduit"}))
        self.assertFalse(off_subject({"topics": ["solar"], "snippet": "Eversource pole petition for the solar farm interconnection, 3 poles"}))


if __name__ == "__main__":
    unittest.main()
