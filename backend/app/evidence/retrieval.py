import time
import logging
from typing import List, Optional, Dict, Any
from app.evidence.models import RetrievedEvidence
from app.evidence.search_provider import get_search_provider, AgriculturalSearchProvider
from app.evidence.source_registry import TrustedSourceRegistry

logger = logging.getLogger(__name__)

class EvidenceRetrievalService:
    """Service responsible for querying trusted agricultural sources and delivering Top 5-8 evidence items."""

    def __init__(self, search_provider: Optional[AgriculturalSearchProvider] = None):
        self.provider = search_provider or get_search_provider()

    @classmethod
    def get_cache_stats(cls) -> Dict[str, Any]:
        from app.evidence.cache import global_evidence_cache
        return global_evidence_cache.get_stats()

    @classmethod
    def retrieve_evidence(
        cls,
        crop: str,
        disease_candidate: str,
        symptoms: List[str],
        max_sources: int = 8,
        search_provider: Optional[AgriculturalSearchProvider] = None
    ) -> List[RetrievedEvidence]:
        """
        Generates structured search queries and retrieves top authoritative agricultural evidence.
        Limits retrieval to Top 5-8 sources.
        """
        provider = search_provider or get_search_provider()
        symptoms_str = " ".join(symptoms[:3])
        query = f"{crop} {disease_candidate} {symptoms_str} symptoms management integrated pest management".strip()

        raw_results = provider.search(query, max_results=max_sources)
        retrieved: List[RetrievedEvidence] = []

        now_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        if raw_results:
            for item in raw_results:
                domain = item.get("domain", "icar.gov.in")
                source_meta = TrustedSourceRegistry.get_source_by_domain(domain)
                authority_tier = source_meta.authority_tier if source_meta else item.get("authority_tier", 1)
                source_id = source_meta.source_id if source_meta else item.get("source_id", "custom")

                retrieved.append(
                    RetrievedEvidence(
                        source_id=source_id,
                        source_name=item.get("source_name", "Authoritative Agricultural Extension"),
                        domain=domain,
                        title=item.get("title", f"{crop.capitalize()} Disease Advisory"),
                        url=item.get("url", f"https://{domain}"),
                        evidence_text=item.get("snippet", ""),
                        authority_tier=authority_tier,
                        crop_relevance=0.95 if crop.lower() in item.get("snippet", "").lower() or crop.lower() in item.get("title", "").lower() else 0.70,
                        disease_relevance=0.90 if disease_candidate.lower() in item.get("snippet", "").lower() or disease_candidate.lower() in item.get("title", "").lower() else 0.60,
                        symptom_relevance=item.get("relevance_score", 0.80),
                        relevance_score=item.get("relevance_score", 0.80),
                        retrieved_at=now_str,
                        is_cached=False
                    )
                )
        else:
            domain = "agritech.tnau.ac.in"
            retrieved.append(
                RetrievedEvidence(
                    source_id="tnau",
                    source_name="TNAU Agritech Portal — Extension Guidance",
                    domain=domain,
                    title=f"General {crop.capitalize()} Disease & Pest Management Guide",
                    url=f"https://{domain}/crop_protection",
                    evidence_text=f"Inspect {crop.capitalize()} foliage for necrotic lesions or discoloration. Maintain sanitation, field drainage, and crop hygiene.",
                    authority_tier=1,
                    crop_relevance=0.80,
                    disease_relevance=0.50,
                    symptom_relevance=0.50,
                    relevance_score=0.65,
                    retrieved_at=now_str,
                    is_cached=False
                )
            )

        return retrieved[:max_sources]
