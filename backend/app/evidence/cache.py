import time
import hashlib
import logging
from typing import List, Dict, Tuple, Any, Optional
from app.evidence.models import RetrievedEvidence

logger = logging.getLogger(__name__)

class EvidenceCache:
    """In-memory TTL cache for agricultural evidence retrieval to optimize latency and external API cost."""

    def __init__(self, ttl_seconds: int = 3600):
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Tuple[float, List[RetrievedEvidence]]] = {}

    def _generate_key(self, crop: str, disease_candidate: str, symptoms: List[str], location_district: str = "") -> str:
        symptom_str = ",".join(sorted([s.lower() for s in symptoms]))
        raw_key = f"{crop.lower()}:{disease_candidate.lower()}:{symptom_str}:{location_district.lower()}"
        return hashlib.md5(raw_key.encode("utf-8")).hexdigest()

    def get(self, crop: str, disease_candidate: str, symptoms: List[str], location_district: str = "") -> Optional[List[RetrievedEvidence]]:
        key = self._generate_key(crop, disease_candidate, symptoms, location_district)
        if key in self._cache:
            created_at, items = self._cache[key]
            if time.time() - created_at < self.ttl_seconds:
                logger.info(f"Cache hit for crop '{crop}' candidate '{disease_candidate}'. Returning {len(items)} cached items.")
                # Mark as cached
                cached_items = []
                for item in items:
                    item_copy = item.model_copy()
                    item_copy.is_cached = True
                    cached_items.append(item_copy)
                return cached_items
            else:
                logger.info(f"Cache entry expired for key {key}. Evicting.")
                del self._cache[key]
        return None

    def set(self, crop: str, disease_candidate: str, symptoms: List[str], items: List[RetrievedEvidence], location_district: str = ""):
        key = self._generate_key(crop, disease_candidate, symptoms, location_district)
        self._cache[key] = (time.time(), items)

    def clear(self):
        self._cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        valid_entries = sum(1 for created_at, _ in self._cache.values() if time.time() - created_at < self.ttl_seconds)
        return {
            "total_cached_keys": len(self._cache),
            "valid_cached_keys": valid_entries,
            "ttl_seconds": self.ttl_seconds
        }

# Global Singleton Instance
global_evidence_cache = EvidenceCache(ttl_seconds=3600)
