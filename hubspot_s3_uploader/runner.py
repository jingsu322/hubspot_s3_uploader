import logging
import time
from .config import PREFIXES, HUBSPOT_DELAY
from .aws_client import list_json_keys, read_json, move_key
from .extractor import extract_product_profile
from .sheets_client import prod_ws, buyer_ws, seller_ws, build_lookup_dict
from .hubspot_client import update_company

logging.basicConfig(level=logging.INFO)

def main():
    date_buyer = build_lookup_dict(buyer_ws)
    date_seller = build_lookup_dict(seller_ws)

    headers = prod_ws.row_values(1)
    col_map = {h: i+1 for i, h in enumerate(headers)}
    data = prod_ws.get_all_records()
    row_index = {str(r['record_id']): i+2 for i, r in enumerate(data)}

    for source, prefix in PREFIXES.items():
        for key in list_json_keys(prefix):
            file_id = key.rsplit('/', 1)[-1].rsplit('.', 1)[0]
            raw = read_json(key)
            profile = extract_product_profile(raw, file_id, source)

            if source == 'buyer':
                last_date = date_buyer.get(file_id)
            elif source == 'seller':
                last_date = date_seller.get(file_id)
            else:
                items = json.loads(raw) if isinstance(raw, (bytes, str)) else raw
                last_date = None
                for item in items if isinstance(items, list) else [items]:
                    upd = item.get('updated_at') or item.get('data', {}).get('updated_at')
                    if upd:
                        last_date = parser.parse(upd).date().isoformat()
                        break

            try:
                update_company(file_id, {'top_ingredients': profile, 'last_scraped_date': last_date})
                status = 'done'
            except Exception as e:
                logging.error(f"HubSpot update failed for {file_id}: {e}")
                status = 'error'

            time.sleep(HUBSPOT_DELAY)

            dest = 's3-hubspot/done/' if status == 'done' else 's3-hubspot/error/'
            move_key(key, dest)

            row = row_index.get(file_id)
            if row:
                prod_ws.update_cell(row, col_map['last_scraped_date'], last_date)
                prod_ws.update_cell(row, col_map['status'], status)
            else:
                new = [''] * len(headers)
                new[col_map['source'] - 1] = f"{source}-{prefix.split('/')[0]}"
                new[col_map['target'] - 1] = 's3-hubspot'
                new[col_map['record_id'] - 1] = file_id
                new[col_map['last_scraped_date'] - 1] = last_date
                new[col_map['status'] - 1] = status
                prod_ws.append_row(new)

    logging.info("ETL run complete.")

if __name__ == '__main__':
    main()