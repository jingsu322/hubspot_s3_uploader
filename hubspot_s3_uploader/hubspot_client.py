import requests
from .config import HUBSPOT_TOKEN


def update_company(hs_object_id, properties):
    url = f"https://api.hubapi.com/crm/v3/objects/companies/{hs_object_id}"
    headers = {
        'Authorization': f'Bearer {HUBSPOT_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {'properties': properties}
    resp = requests.patch(url, headers=headers, json=data)
    resp.raise_for_status()
    return resp.json()