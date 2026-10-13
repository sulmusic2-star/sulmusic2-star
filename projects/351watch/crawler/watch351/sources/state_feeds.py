"""Shared helpers for state siting feeds (Vermont Act 250, Connecticut Siting Council).

These sources do not come from town agendas: a state body lists projects (Act 250 District
Commissions) or petitions and dockets (the Connecticut Siting Council), and each listed matter
becomes an *item* filed under its host town. Items that are siting-relevant also become hits in
the shape of data/hits_current.json (ARCHITECTURE.md), so a town page can show them next to its
agenda items.

Gating. Both sources are under test (Wave 1, 2026-10). Their outputs go to data/test/wave1/sources/
and never to data/sources/ (which current.build() merges into production): `check_out_dir` refuses
an output directory inside data/sources or data/ itself while GATED is true. ops/daily.sh does not
run them.

Personal data. Applicants that are private individuals are stored as "[individual]" (the MassDEP
source's rule); for organizations, a contact person's name that the source glues in front of the
organization ("Ryan Gumbart Town of Weathersfield") is stripped where it can be recognized
(`organization`), and the item keeps only the organization.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]          # projects/351watch
DATA = ROOT / "data"
WAVE1 = DATA / "test" / "wave1"
DEFAULT_OUT = WAVE1 / "sources"
GATED = True
INDIVIDUAL = "[individual]"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def check_out_dir(out_dir: Path) -> None:
    """Refuse to write a gated source's output where production reads it (data/sources/, data/)."""
    out = Path(out_dir).resolve()
    if GATED and (out == DATA.resolve() or out == (DATA / "sources").resolve()
                  or (DATA / "sources").resolve() in out.parents):
        raise SystemExit(f"{out}: this source is gated (Wave 1 test). Write to data/test/wave1/sources "
                         f"(the default); data/sources/*_hits.json is merged into production.")


def hit_id(source_url: str, snippet: str) -> str:
    return hashlib.sha1(f"{source_url}|{snippet}".encode("utf-8")).hexdigest()[:12]


def clean(s: str | None) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("\xa0", " ")).strip()


# ------------------------------------------------------------------------------------ applicants
ORG_RX = re.compile(
    r"\bL\.?\s?L\.?\s?C\b|\bL\.?\s?L\.?\s?P\b|\bINC\b|\bINCORPORATED\b|\bCORP|\bCO\.|\bCOMPANY\b|\bCOMPANIES\b|"
    r"\bTRUST\b|\bTRUSTEES?\b|\bL\.?P\.?$|\bLTD\b|\bPARTNERS|\bASSOC|\bTOWN\b|\bCITY\b|\bVILLAGE\b|\bCOUNTY\b|"
    r"\bSTATE\b|\bDEPARTMENT\b|\bDEPT\b|\bAGENCY\b|\bAUTHORITY\b|\bCOMMISSION\b|\bBOARD\b|\bDISTRICT\b|"
    r"\bUNIVERSITY\b|\bCOLLEGE\b|\bSCHOOL|\bACADEMY\b|\bCHURCH\b|\bPARISH\b|\bDIOCESE\b|\bCLUB\b|\bSOCIETY\b|"
    r"\bFOUNDATION\b|\bINSTITUTE\b|\bHOSPITAL\b|\bCENTER\b|\bENERGY\b|\bSOLAR\b|\bPOWER\b|\bELECTRIC\b|\bUTILIT|"
    r"\bRENEWABLE|\bSTORAGE\b|\bDEVELOPMENT\b|\bREALTY\b|\bREAL\s+ESTATE\b|\bPROPERT|\bHOMES\b|\bHOUSING\b|"
    r"\bBUILDERS?\b|\bCONSTRUCTION\b|\bCONTRACT|\bENGINEER|\bGROUP\b|\bHOLDINGS?\b|\bMANAGEMENT\b|\bENTERPRISES?\b|"
    r"\bINDUSTR|\bSERVICES?\b|\bFARMS?\b|\bESTATES?\b|\bCONSERVATION\b|\bLAND\b|\bVENTURES?\b|\bCAPITAL\b|\bBANK\b|"
    r"\bASSOCIATION\b|\bCONDOMINIUM|\bCOOPERATIVE\b|\bCO-?OP\b|\bRESORT\b|\bMOUNTAIN\b|\bSKI\b|\bHOTELS?\b|\bINN\b|"
    r"\bSYSTEMS?\b|\bTECHNOLOG|\bPARTNERSHIP\b|\bTOWERS?\b|\bWIRELESS\b|\bCOMMUNICATIONS?\b|\bCELLCO\b|\bVERIZON\b|"
    r"\bAT&T\b|\bT-MOBILE\b|\bSTORES?\b|\bMARKET\b|\bAIRPORT\b|\bRAIL|\bQUARR|\bGRAVEL\b|\bSAND\b|\bAGGREGATE|"
    r"\bMATERIALS\b|\bPAVING\b|\bASPHALT\b|\bCONCRETE\b|\bEXCAVATING\b|\bTRUCKING\b|\bMOTORS\b|\bAUTO\b|\bDAIRY\b|"
    r"\bORCHARDS?\b|\bVINEYARD|\bBREW|\bDISTILL|\bLUMBER\b|\bMILLS?\b|\bMANUFACTUR|\bFUEL|\bOIL\b|\bPROPANE\b|"
    r"\bMEDICAL\b|\bHEALTH\b|\bCAMP\b|\bGOLF\b|\bCOUNTRY\s+CLUB\b|\bCEMETERY\b|\bFIRE\b|\bLIBRARY\b|\bMUSEUM\b|"
    r"\bOF\s+VERMONT\b|\bVERMONT\s+(?:AGENCY|DEPARTMENT|STATE|AGENCY)|\bVTRANS\b|\bAOT\b|\bUSA\b|\bU\.S\.|\bFEDERAL\b",
    re.I)

# Common given names (US), used only to recognize a contact person glued in front of an organization
# ("Brian Donahue Green Mountain Valley School"). An organization that itself starts with such a word
# ("Grace Church") is protected by requiring a second, surname-like token and an organization marker
# after it.
_GIVEN = set("""
aaron adam adrian al alan albert alex alexander alexandra alice alicia allen allison amanda amber amy andrea andrew
andy angela ann anna anne annie anthony april arthur ashley audrey austin barbara barry ben benjamin beth betsy
betty beverly bill billy bob bobby bonnie brad bradley brandon brenda brendan brett brian bridget brittany bruce bryan
caitlin cameron carl carla carol caroline carolyn carrie casey catherine cathy chad charles charlie cheryl chris
christian christina christine christopher chuck cindy claire clark colin connie corey craig crystal curtis cynthia
dale dan dana daniel danielle darren dave david dawn dean deb debbie deborah debra denise dennis derek diana diane
dick don donald donna doris dorothy doug douglas drew dustin dylan earl ed eddie edward eileen elaine eleanor elizabeth
ellen emily emma eric erica erik erin ethan eugene evan evelyn frances francis frank fred frederick gabriel gail gary
gene george gerald glen glenn gloria gordon grace graham greg gregory hannah harold harry heather helen henry holly
howard ian jack jackie jacob jacqueline james jamie jan jane janet janice jason jay jean jeff jeffrey jen jennifer
jenny jeremy jerry jesse jessica jill jim jimmy jo joan joann joanne jodi joe joel john johnny jon jonathan jordan
joseph josh joshua joyce juan judith judy julia julie justin kara karen kari karl kate katherine kathleen kathryn kathy
katie kay keith kelly ken kenneth kerry kevin kim kimberly kirk kris kristen kristin kurt kyle larry laura lauren
laurie lawrence lee leo leonard leslie linda lindsay lisa liz lori louis lucy luke lynn madeline marc marcia margaret
maria marie marilyn mario marjorie mark marsha martha martin mary matt matthew maureen megan melanie melissa michael
michele michelle mike mitchell molly monica nancy natalie nathan neil nicholas nick nicole noah norman pam pamela pat
patricia patrick paul paula peggy penny peter phil philip phillip rachel ralph randy ray raymond rebecca regina rene
rich richard rick rob robert robin rod roger ron ronald rose ross roy russell ruth ryan sally sam samantha samuel sandra
sandy sara sarah scott sean seth sharon shawn sheila shelley stacey stacy stan stanley stephanie stephen steve steven
sue susan suzanne tammy tara ted teresa terri terry theresa thomas tim timothy tina todd tom tommy tony tracy travis
trevor troy tyler valerie vanessa victor victoria vincent virginia walter wayne wendy will william willie zachary
""".split())
_INITIAL = re.compile(r"^[A-Z]\.?$")


def _person_prefix_len(tokens: list[str]) -> int:
    """How many leading tokens are a person's name ("Brian Donahue", "Ken R. Nolan"), 0 if none."""
    if len(tokens) < 3 or tokens[0].lower().strip(".,") not in _GIVEN:
        return 0
    i = 1
    if _INITIAL.match(tokens[i]):
        i += 1
    if i >= len(tokens) or not re.match(r"^[A-Z][a-zA-Z'\-]+,?$", tokens[i]):
        return 0
    return i + 1


def _common_suffix(a: list[str], b: list[str]) -> list[str]:
    out = []
    for x, y in zip(reversed(a), reversed(b)):
        if x.lower() != y.lower():
            break
        out.append(x)
    return list(reversed(out))


def organization(name: str, others: list[str] | None = None) -> str:
    """The organization in a source's applicant string, or INDIVIDUAL for a private person.

    "Ryan Gumbart Town of Weathersfield" -> "Town of Weathersfield"; "Glenn Cummings 22 Corporate Drive,
    LLC" -> "22 Corporate Drive, LLC"; "Woodstock Resort Corporation" -> unchanged; "David & Lucy Bryant"
    -> "[individual]". `others` are the other participant strings on the same record (landowner, primary
    contact): an organization they share with a different person in front ("Ankur Patel Giri Montpelier
    Inc" / "Ashish Sangani Giri Montpelier Inc") is taken as the common suffix."""
    name = clean(name).strip(";, ")
    if not name:
        return ""
    if re.fullmatch(r"[A-Z][A-Z&\-]{2,7}", name):          # an acronym: "VTEL", "VELCO", "VPPSA"
        return name
    # a person's estate-planning trust ("Katharine D. Stockman Revocable Trust") is a private individual
    if re.search(r"\b(?:revocable|irrevocable|living|family)\s+trust\b", name, re.I):
        return INDIVIDUAL
    if not ORG_RX.search(name):
        return INDIVIDUAL
    m = re.search(r"\b(?:Town|City|Village|County|State)\s+of\s+\w", name)
    if m and m.start() > 0:
        return name[m.start():]
    toks = name.split()
    for o in others or []:
        o = clean(o).strip(";, ")
        if not o or o.lower() == name.lower():
            continue
        suf = _common_suffix(toks, o.split())
        if 1 < len(suf) < len(toks) and ORG_RX.search(" ".join(suf)):
            return " ".join(suf)
    k = _person_prefix_len(toks)
    if k and ORG_RX.search(" ".join(toks[k:])):
        return " ".join(toks[k:])
    return name


def organizations(field: str, others: list[str] | None = None) -> list[str]:
    """Every applicant in a ';'-separated field, as organizations or INDIVIDUAL (deduplicated)."""
    out = []
    for part in (field or "").split(";"):
        org = organization(part, others)
        if org and org not in out:
            out.append(org)
    return out


# ------------------------------------------------------------------------------------- towns
def load_state_towns(st: str, data_dir: Path = DATA) -> list[dict]:
    """Rows of data/towns_<st>.json (gated files are read here on purpose: this is the source's own
    town list, not the production selection)."""
    p = data_dir / f"towns_{st.lower()}.json"
    if not p.exists():
        return []
    doc = json.loads(p.read_text())
    return [t for t in doc.get("towns", []) if isinstance(t, dict) and t.get("town")]


def norm_key(name: str) -> str:
    n = clean(name).lower().replace("&", "and")
    n = re.sub(r"^(?:town|city|village)\s+of\s+", "", n)
    n = re.sub(r",\s*(?:town|city|village)\s+of$", "", n)
    n = re.sub(r"\bst\.?\s", "saint ", n)
    n = re.sub(r"\bmt\.?\s", "mount ", n)
    return re.sub(r"[^a-z0-9]+", " ", n).strip()


# ---------------------------------------------------------------------------------- ledger / output
def load_json(path: Path, default):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return default


def write_json(path: Path, obj) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n")
    tmp.replace(path)


def first_seen(ledger: dict, key: str, ts: str) -> str:
    """First time this item (or this version of it) was seen; kept across runs in the source's ledger."""
    return ledger.setdefault(key, ts)


def snippet_of(*parts: str, limit: int = 240) -> str:
    s = clean(" ".join(p for p in parts if p))
    if len(s) > limit:
        s = s[:limit - 1].rsplit(" ", 1)[0].rstrip(" ,;:-") + "…"
    return s


def iso(d: date | None) -> str | None:
    return d.isoformat() if d else None
