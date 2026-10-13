"""Platform adapter registry. Add a new platform by writing an Adapter
subclass and registering it here under the `platform` name used in towns.json."""

from .base import Adapter
from .civicclerk import CivicClerkAdapter
from .civicplus import CivicPlusAdapter
from .generic import GenericListingAdapter
from .legistar import LegistarAdapter

REGISTRY: dict[str, type[Adapter]] = {
    CivicPlusAdapter.platform: CivicPlusAdapter,
    CivicClerkAdapter.platform: CivicClerkAdapter,
    GenericListingAdapter.platform: GenericListingAdapter,
    LegistarAdapter.platform: LegistarAdapter,
}

__all__ = ["Adapter", "REGISTRY"]
from .ri_sos import RISOSAdapter; REGISTRY[RISOSAdapter.platform] = RISOSAdapter  # RI Secretary of State Open Meetings portal
from .generic_ny import GenericNYAdapter; from .escribe import EscribeAdapter; REGISTRY.update({GenericNYAdapter.platform: GenericNYAdapter, EscribeAdapter.platform: EscribeAdapter})  # NY pilot: hand listings with month pages / compact dates; eSCRIBE portals
from .agenda_page import AgendaPageAdapter; REGISTRY[AgendaPageAdapter.platform] = AgendaPageAdapter  # MI/VA test: general agenda-page reader (WordPress, Revize, CivicPlus documents, Municode Meetings, plain pages)
from .cmm_compass import CMMCompassAdapter; REGISTRY[CMMCompassAdapter.platform] = CMMCompassAdapter  # Wave 1 NY: Compass Web Development CMM agenda embeds (Clymer, Ellery, Angelica)
