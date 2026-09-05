import logging
from typing import List, Dict, Any
from app.evidence.models import RetrievedEvidence, ExtractedFact

logger = logging.getLogger(__name__)

class EvidenceExtractor:
    """Extracts structured facts from top-ranked evidence while preserving source attribution."""

    @classmethod
    def extract_facts(cls, ranked_evidence: List[RetrievedEvidence]) -> Dict[str, List[ExtractedFact]]:
        facts: Dict[str, List[ExtractedFact]] = {
            "symptoms": [],
            "management": [],
            "prevention": [],
            "monitoring": []
        }

        for ev in ranked_evidence:
            text = ev.evidence_text
            # Basic parsing of text blocks
            parts = text.split(". ")
            for p in parts:
                p_str = p.strip()
                if not p_str:
                    continue

                if "symptom" in p_str.lower() or "lesion" in p_str.lower() or "spot" in p_str.lower():
                    facts["symptoms"].append(
                        ExtractedFact(
                            fact_type="symptoms",
                            content=p_str,
                            source_name=ev.source_name,
                            source_url=ev.url
                        )
                    )
                elif "remove" in p_str.lower() or "destroy" in p_str.lower() or "prune" in p_str.lower() or "drain" in p_str.lower():
                    facts["management"].append(
                        ExtractedFact(
                            fact_type="management",
                            content=p_str,
                            source_name=ev.source_name,
                            source_url=ev.url
                        )
                    )
                elif "rotate" in p_str.lower() or "seed" in p_str.lower() or "resistant" in p_str.lower() or "clean" in p_str.lower():
                    facts["prevention"].append(
                        ExtractedFact(
                            fact_type="prevention",
                            content=p_str,
                            source_name=ev.source_name,
                            source_url=ev.url
                        )
                    )
                else:
                    facts["monitoring"].append(
                        ExtractedFact(
                            fact_type="monitoring",
                            content=p_str,
                            source_name=ev.source_name,
                            source_url=ev.url
                        )
                    )

        return facts
