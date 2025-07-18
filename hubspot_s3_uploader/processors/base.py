"""Abstract base‑class + registry for source‑specific processors."""
from __future__ import annotations

import abc
from typing import Dict, Any


class Processor(abc.ABC):
    """Convert raw JSON → {"top_ingredients": "…"}."""

    # Registry of subclasses: {source_name: cls}
    _registry: dict[str, "Processor"] = {}

    def __init_subclass__(cls, /, source_name: str, **kwargs):
        super().__init_subclass__(**kwargs)
        Processor._registry[source_name] = cls

    @classmethod
    def for_source(cls, source: str) -> "Processor":
        try:
            proc_cls = cls._registry[source]
        except KeyError as exc:
            raise ValueError(f"No processor for source '{source}'") from exc
        return proc_cls()

    # ------------------------------------------------------------------
    @abc.abstractmethod
    def property_map(self, json_data: Any) -> Dict[str, str]:
        """Return dict ready for HubSpot PATCH (top_ingredients only)."""