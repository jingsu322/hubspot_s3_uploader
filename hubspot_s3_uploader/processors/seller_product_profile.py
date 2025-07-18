"""Processor for `seller-product-profile` source."""
from __future__ import annotations

import logging
from typing import Any, Dict, Set

from .base import Processor

log = logging.getLogger(__name__)


class SellerProductProfileProcessor(Processor, source_name="seller-product-profile"):
    _INVALID = {"Pass", "Not a product page", "Not a product", "failed"}

    def property_map(self, json_data: Any) -> Dict[str, str]:
        ingredients: Set[str] = set()
        try:
            for product in json_data:
                raw = (
                    product.get("product_details", {}).get("ingredients")
                    or product.get("product_name", "").strip()
                )
                if raw in self._INVALID:
                    continue
                if isinstance(raw, list):
                    ingredients.update(i.strip() for i in raw if isinstance(i, str))
                elif isinstance(raw, str):
                    ingredients.add(raw.strip())
            profile = ", ".join(sorted(ingredients)) if ingredients else "No Ingredient Information"
            return {"top_ingredients": profile}
        except Exception as exc:  # noqa: BLE001
            log.exception("Seller extractor failed: %s", exc)
            return {"top_ingredients": "Error during extraction"}