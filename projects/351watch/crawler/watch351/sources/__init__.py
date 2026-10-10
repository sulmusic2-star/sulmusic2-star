"""Second data sources for 351 Watch (state filings that do not come from town agendas).

Each module is runnable on its own (``python3 -m watch351.sources.<name>``) and writes
its outputs under ``data/sources/``. Hits use the shape of ``data/hits_current.json``
(see ARCHITECTURE.md) so the daily engine can merge them.

* ``massdep`` -- MassDEP Wetlands Protection Act filings (NOI, buffer zone, ANRAD) from
  the EEA Data Portal's public Data Lake API.
"""
