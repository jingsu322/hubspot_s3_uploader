import logging
from datetime import datetime
from typing import Dict, List, Any, Set, Union

from dateutil import parser

logger = logging.getLogger(__name__)

def extract_product_profile(json_data: Union[List[Dict[str, Any]], Dict[str, Any]],
                            file_id: str,
                            source: str) -> str:
    """
    Extract product profile
    """
    try:
        product_names: List[str] = []
        ingredients_set: Set[str] = set()

        for product in (json_data if isinstance(json_data, list) else [json_data]):
            # buyer
            if source == "buyer":
                pname = product.get("product_name", "").strip()
                if pname and pname not in ["Pass", "Not a product page", "Not a product", "failed"]:
                    product_names.append(pname)
                    ingredients = product.get("product_details", {}).get("ingredients", [])
                    if isinstance(ingredients, list):
                        for ing in ingredients:
                            if isinstance(ing, str):
                                ingredients_set.add(ing.strip())

            # seller
            elif source == "seller":
                raw = product.get("product_details", {}).get("ingredients", [])
                ingredients = raw if raw else product.get("product_name", "").strip()
                if ingredients in ["Pass", "Not a product page", "Not a product", "failed"]:
                    continue
                if isinstance(ingredients, list):
                    for ing in ingredients:
                        if isinstance(ing, str):
                            ingredients_set.add(ing.strip())
                elif isinstance(ingredients, str):
                    ingredients_set.add(ingredients.strip())

            # amazon
            elif source == "amazon":
                ingredients = product.get("extracted_ingredients", {}).get("ingredients", {})
                if isinstance(ingredients, str):
                    ingredients_set.add(ingredients.strip())

            else:
                logger.warning("Invalid source %s in %s", source, file_id)

        if ingredients_set:
            return ", ".join(sorted(ingredients_set))
        if product_names:
            return "No Ingredient Information, " + ", ".join(product_names)
        return "No Ingredient Information"

    except Exception as e:  # noqa: BLE001
        logger.error("Error processing %s: %s", file_id, e)
        return "Error during extraction"

def build_lookup_dict(ws) -> Dict[str, str]:
    """
    Notebook: lookup_update sheet ➜ {Record ID: YYYY-MM-DD}
    """
    values = ws.get_all_values()
    if len(values) < 2:
        return {}

    header = values[0]
    try:
        rid_idx = header.index("Record ID")
        ds_idx  = header.index("Date Scraped")
    except ValueError as e:  # noqa: BLE001
        logger.error("Expected columns not found in %s: %s", ws.title, e)
        return {}

    mapping: Dict[str, str] = {}
    for row in values[1:]:
        rid  = row[rid_idx].strip()
        date_raw = row[ds_idx].strip()
        if rid and date_raw:
            try:
                mapping[rid] = datetime.strptime(date_raw, "%m-%d-%Y").strftime("%Y-%m-%d")
            except Exception:  # noqa: BLE001
                try:
                    mapping[rid] = parser.parse(date_raw).date().isoformat()
                except Exception as e:
                    logger.warning("Failed to parse date for %s: %s (%s)", rid, date_raw, e)

    return mapping