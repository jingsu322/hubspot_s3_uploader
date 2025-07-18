"""Processor for `buyer-product-profile` source."""
from __future__ import annotations

import logging
from typing import Any, List, Set, Dict

from .base import Processor

log = logging.getLogger(__name__)


class BuyerProductProfileProcessor(Processor, source_name="buyer-product-profile"):
    _INVALID = {"Pass", "Not a product page", "Not a product", "failed"}

    # ------------------------------------------------------------------
    def property_map(self, json_data: Any) -> Dict[str, str]:
        product_names: List[str] = []
        ingredients: Set[str] = set()
        try:
            for product in json_data:
                pname = product.get("product_name", "").strip()
                if pname and pname not in self._INVALID:
                    product_names.append(pname)
                    ing_list = product.get("product_details", {}).get("ingredients", [])
                    if isinstance(ing_list, list):
                        ingredients.update(i.strip() for i in ing_list if isinstance(i, str))
            # Build final string
            if ingredients:
                profile = ", ".join(sorted(ingredients))
            else:
                profile = "No Ingredient Information" + (
                    ", " + ", ".join(product_names) if product_names else ""
                )
            return {"top_ingredients": profile}
        except Exception as exc:  # noqa: BLE001
            log.exception("Buyer extractor failed: %s", exc)
            return {"top_ingredients": "Error during extraction"}