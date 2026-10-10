"""Platform adapter registry. Add a new platform by writing an Adapter
subclass and registering it here under the `platform` name used in towns.json."""

from .base import Adapter
from .civicclerk import CivicClerkAdapter
from .civicplus import CivicPlusAdapter
from .generic import GenericListingAdapter

REGISTRY: dict[str, type[Adapter]] = {
    CivicPlusAdapter.platform: CivicPlusAdapter,
    CivicClerkAdapter.platform: CivicClerkAdapter,
    GenericListingAdapter.platform: GenericListingAdapter,
}

__all__ = ["Adapter", "REGISTRY"]
