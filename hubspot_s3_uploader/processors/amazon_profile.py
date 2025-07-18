"""Processor for `amazon-product-profile` source."""
from __future__ import annotations

import logging
from typing import Any, Dict

from .base import Processor

log = logging.getLogger(__name__)


class AmazonProductProfileProcessor(Processor, source_name="amazon-product-profile"):
    def property_map(self, json_data: Any) -> Dict[str, str]:
        try:
            ingredients_set = {
                product.get("extracted_ingredients", {}).get("ingredients", "").strip()
                for product in json_data
                if isinstance(product.get("extracted_ingredients", {}).get("ingredients", ""), str)
            }
            ingredients_set.discard("")
            profile = ", ".join(sorted(ingredients_set)) if ingredients_set else "No Ingredient Information"
            return {"top_ingredients": profile}
        except Exception as exc:  # noqa: BLE001
            log.exception("Amazon extractor failed: %s", exc)
            return {"top_ingredients": "Error during extraction"}