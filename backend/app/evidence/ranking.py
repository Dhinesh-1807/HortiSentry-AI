import logging
from typing import List
from app.evidence.models import RetrievedEvidence
from app.evidence.source_registry import TrustedSourceRegistry

logger = logging.getLogger(__name__)

class EvidenceRanker:
    """Ranks retrieved evidence items based on source authority, crop relevance, and symptom match."""

    @classmethod
    def rank_evidence(cls, evidence_items: List[RetrievedEvidence]) -> List[RetrievedEvidence]:
        ranked = []
        for ev in evidence_items:
            tier_weight = TrustedSourceRegistry.get_tier_weight(ev.authority_tier)
            
            # Weighted overall score formula:
            # 40% Tier weight + 30% Crop relevance + 20% Disease relevance + 10% Symptom match
            score = (
                0.40 * tier_weight +
                0.30 * ev.crop_relevance +
                0.20 * ev.disease_relevance +
                0.10 * ev.symptom_relevance
            )
            ev.relevance_score = round(min(1.0, score), 4)
            ranked.append(ev)

        # Sort descending by relevance score
        ranked.sort(key=lambda x: x.relevance_score, reverse=True)
        return ranked
