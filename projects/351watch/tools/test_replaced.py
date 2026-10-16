#!/usr/bin/env python3
"""A town re-posts an agenda under a new file: the old document is marked replaced, its items keep
their ids and point at the new file, and items the new file dropped go away.

    python3 tools/test_replaced.py
"""
import os
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "crawler"))
from watch351.state import DocIndex  # noqa: E402

OLD = "https://www.carverma.gov/AgendaCenter/ViewFile/Agenda/_10202026-628"
NEW = "https://www.carverma.gov/AgendaCenter/ViewFile/Agenda/_10202026-631"
TODAY = date(2026, 10, 17)


def rec(url, first_seen, hits, **extra):
    return {"url": url, "state": "MA", "town": "Carver", "board": "Select Board", "board_key": "select_board",
            "meeting_date": "2026-10-20", "first_seen": first_seen, "last_seen_in_listing": first_seen[:10],
            "status": "ok", "kw": "x", "text_source": "pdf", "title": "10/20/26 Agenda",
            "hits": [{"topics": ["solar"], "snippet": s} for s in hits], **extra}


class ReplacedTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.index = DocIndex(Path(self.tmp.name))
        self.index.put(rec(OLD, "2026-10-16T11:00:00+00:00", ["Purchase of solar credits, item 6", "Temporary event parking"]))
        self.index.put(rec(NEW, "2026-10-17T11:00:00+00:00", ["Purchase of solar credits, item 6", "Solar canopy at the school"]))

    def tearDown(self):
        self.tmp.cleanup()

    def test_old_file_gone_from_listing_is_replaced(self):
        listed = {("select_board", "2026-10-20"): {NEW}}
        retired = self.index.retire_replaced("MA", "Carver", listed, TODAY)
        self.assertEqual([r["url"] for r in retired], [OLD])
        old = self.index.get(OLD)
        self.assertEqual((old["status"], old["replaced_by"], old["status_before"]), ("replaced", NEW, "ok"))
        hits = {h["snippet"]: h for h in self.index.current_hits()}
        # the item both files carry keeps the old file's identity but links to the new file
        self.assertEqual(hits["Purchase of solar credits, item 6"]["source_url"], OLD)
        self.assertEqual(hits["Purchase of solar credits, item 6"]["doc_url"], NEW)
        # the item the new file dropped is gone; the new file's new item is there under its own file
        self.assertNotIn("Temporary event parking", hits)
        self.assertEqual(hits["Solar canopy at the school"]["source_url"], NEW)
        self.assertNotIn("doc_url", hits["Solar canopy at the school"])

    def test_both_files_listed_means_nothing_replaced(self):
        listed = {("select_board", "2026-10-20"): {OLD, NEW}}
        self.assertEqual(self.index.retire_replaced("MA", "Carver", listed, TODAY), [])
        self.assertEqual(self.index.get(OLD)["status"], "ok")

    def test_old_meetings_are_left_alone(self):
        self.index.put(rec("https://example.org/old", "2026-08-01T11:00:00+00:00", ["x"], meeting_date="2026-08-05"))
        listed = {("select_board", "2026-08-05"): {"https://example.org/other"}}
        self.assertEqual(self.index.retire_replaced("MA", "Carver", listed, TODAY), [])

    def test_listed_again_is_current_again(self):
        self.index.retire_replaced("MA", "Carver", {("select_board", "2026-10-20"): {NEW}}, TODAY)
        self.index.touch(OLD, TODAY)
        old = self.index.get(OLD)
        self.assertEqual(old["status"], "ok")
        self.assertNotIn("replaced_by", old)

    def test_replaced_twice_links_to_the_last_file(self):
        third = "https://www.carverma.gov/AgendaCenter/ViewFile/Agenda/_10202026-632"
        self.index.retire_replaced("MA", "Carver", {("select_board", "2026-10-20"): {NEW}}, TODAY)
        self.index.put(rec(third, "2026-10-18T11:00:00+00:00", ["Purchase of solar credits, item 6"]))
        self.index.retire_replaced("MA", "Carver", {("select_board", "2026-10-20"): {third}}, date(2026, 10, 18))
        hits = {h["snippet"]: h for h in self.index.current_hits()}
        # the item all three files carry keeps the first file's identity and links to the third
        self.assertEqual(hits["Purchase of solar credits, item 6"]["source_url"], OLD)
        self.assertEqual(hits["Purchase of solar credits, item 6"]["doc_url"], third)
        # the second file's own item, dropped by the third, is gone
        self.assertNotIn("Solar canopy at the school", hits)

    def test_replacement_not_read_yet_keeps_everything_with_the_live_link(self):
        unread = "https://www.carverma.gov/AgendaCenter/ViewFile/Agenda/_10202026-640"
        self.index.retire_replaced("MA", "Carver", {("select_board", "2026-10-20"): {unread}}, TODAY)
        # OLD is replaced by a file the index hasn't read (fetch failed); NEW is now also "not listed"
        hits = {h["snippet"]: h for h in self.index.current_hits()}
        self.assertEqual(hits["Temporary event parking"]["doc_url"], unread)
        self.assertEqual(hits["Purchase of solar credits, item 6"]["source_url"], OLD)


if __name__ == "__main__":
    unittest.main()
