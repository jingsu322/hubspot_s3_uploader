import logging
import time
from typing import Dict, Any

import requests
from requests.exceptions import HTTPError

from .config import HUBSPOT_TOKEN

logger = logging.getLogger(__name__)

def update_company(hs_object_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
    url = f"https://api.hubapi.com/crm/v3/objects/companies/{hs_object_id}"
    headers = {"Authorization": f"Bearer {HUBSPOT_TOKEN}", "Content-Type": "application/json"}
    response = requests.patch(url, headers=headers, json={"properties": properties}, timeout=30)

    try:
        response.raise_for_status()
        return response.json()
    except HTTPError as e:
        logger.error("HubSpot update failed for %s – %s", hs_object_id, e.response.text)
        raise
    finally:
        time.sleep(1)