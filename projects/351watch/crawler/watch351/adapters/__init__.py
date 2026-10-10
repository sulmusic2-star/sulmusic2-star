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
