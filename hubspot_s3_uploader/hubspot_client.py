"""Minimal HubSpot CRM v3 wrapper – PATCH company properties."""
from __future__ import annotations

import logging
from typing import Dict

import requests

from . import config

log = logging.getLogger(__name__)

_BASE = "https://api.hubapi.com"
_HEADERS = {
    "Authorization": f"Bearer {config.HUBSPOT_PRIVATE_APP_TOKEN}",
    "Content-Type": "application/json",
}


def update_company_properties(hs_object_id: str, properties: Dict[str, str]) -> None:
    """PATCH properties on a Company object.

    Args:
        hs_object_id: HubSpot company ID (string to keep edge‑cases safe).
        properties: {internal_property_name: value}
    """
    url = f"{_BASE}/crm/v3/objects/companies/{hs_object_id}"
    resp = requests.patch(url, headers=_HEADERS, json={"properties": properties}, timeout=30)
    if resp.status_code // 100 != 2:
        log.error("HubSpot error %s – %s", resp.status_code, resp.text)
        resp.raise_for_status()
    log.info("✓ HubSpot company %s updated: %s", hs_object_id, list(properties.keys()))