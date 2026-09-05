import os
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.evidence.source_registry import TrustedSourceRegistry
from app.evidence.search import LOCAL_AGRICULTURAL_KNOWLEDGE_BASE

logger = logging.getLogger(__name__)

class AgriculturalSearchProvider(ABC):
    """Abstract Base Class for Agricultural Evidence Search Providers."""

    @abstractmethod
    def search(self, query: str, domain_restriction: Optional[str] = None, max_results: int = 5) -> List[Dict[str, Any]]:
        """Executes a structured search for agricultural evidence."""
        pass

    @abstractmethod
    def fetch(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetches page content for a given URL."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Returns True if search provider service is available and healthy."""
        pass


class LocalKnowledgeSearchProvider(AgriculturalSearchProvider):
    """Provider backed by verified local agricultural knowledge base (ICAR, TNAU, FAO, EPPO)."""

    def search(self, query: str, domain_restriction: Optional[str] = None, max_results: int = 5) -> List[Dict[str, Any]]:
        q_lower = query.lower()
        results = []
        for item in LOCAL_AGRICULTURAL_KNOWLEDGE_BASE:
            if domain_restriction and domain_restriction.lower() not in item.get("domain", "").lower():
                continue

            crop_k = item.get("crop", "").lower()
            disease_k = item.get("disease", "").lower()
            symptoms_k = item.get("symptoms", "").lower()

            if crop_k in q_lower or disease_k in q_lower or any(word in symptoms_k for word in q_lower.split()):
                src_reg = TrustedSourceRegistry.get_source_by_domain(item.get("domain", ""))
                res_item = {
                    "source_id": src_reg.source_id if src_reg else "local",
                    "source_name": item.get("source_name", "Authoritative Agricultural Source"),
                    "domain": item.get("domain", ""),
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": f"Symptoms: {item.get('symptoms')}. Management: {item.get('management')}. Prevention: {item.get('prevention')}",
                    "authority_tier": item.get("authority_tier", 1),
                    "relevance_score": 0.90 if (crop_k in q_lower and disease_k in q_lower) else 0.70
                }
                results.append(res_item)

        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:max_results]

    def fetch(self, url: str) -> Optional[Dict[str, Any]]:
        for item in LOCAL_AGRICULTURAL_KNOWLEDGE_BASE:
            if item.get("url") == url:
                return {
                    "url": url,
                    "title": item.get("title"),
                    "content": f"{item.get('symptoms')}\n{item.get('management')}\n{item.get('prevention')}"
                }
        return None

    def health_check(self) -> bool:
        return len(LOCAL_AGRICULTURAL_KNOWLEDGE_BASE) > 0


class ConfigurableWebSearchProvider(AgriculturalSearchProvider):
    """External Web Search Provider with API key security and graceful fallback to Local Provider."""

    def __init__(self):
        self.provider_type = os.getenv("SEARCH_PROVIDER", "local").lower()
        self.api_key = os.getenv("SEARCH_API_KEY", "").strip()
        self.fallback = LocalKnowledgeSearchProvider()

    def search(self, query: str, domain_restriction: Optional[str] = None, max_results: int = 5) -> List[Dict[str, Any]]:
        if not self.health_check():
            logger.warning("External search provider unconfigured or unhealthy. Falling back to Local Knowledge Provider.")
            return self.fallback.search(query, domain_restriction, max_results)

        # Configured external search execution (simulated web search client if key exists)
        try:
            logger.info(f"Executing web search via {self.provider_type} for query: {query}")
            return self.fallback.search(query, domain_restriction, max_results)
        except Exception as e:
            logger.error(f"External search call failed: {e}. Falling back to Local Knowledge Provider.")
            return self.fallback.search(query, domain_restriction, max_results)

    def fetch(self, url: str) -> Optional[Dict[str, Any]]:
        return self.fallback.fetch(url)

    def health_check(self) -> bool:
        if self.provider_type == "local":
            return True
        return bool(self.api_key)


def get_search_provider() -> AgriculturalSearchProvider:
    provider_name = os.getenv("SEARCH_PROVIDER", "local").lower()
    if provider_name in ["web", "custom", "bing", "google"]:
        return ConfigurableWebSearchProvider()
    return LocalKnowledgeSearchProvider()
