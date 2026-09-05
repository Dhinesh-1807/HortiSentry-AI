import pytest
from unittest.mock import MagicMock
from app.evidence.source_registry import TrustedSourceRegistry
from app.evidence.search_provider import LocalKnowledgeSearchProvider, ConfigurableWebSearchProvider
from app.evidence.retrieval import EvidenceRetrievalService
from app.evidence.ranking import EvidenceRanker
from app.evidence.extraction import EvidenceExtractor
from app.evidence.cache import EvidenceCache
from app.evidence.review_generator import AIReviewGenerator
from app.evidence.service import EvidenceEngineService
from app.ml.vision_provider import VisionAnalysisResult

def test_source_registry():
    sources = TrustedSourceRegistry.get_all_sources()
    assert len(sources) >= 5
    icar = TrustedSourceRegistry.get_source_by_id("icar")
    assert icar is not None
    assert icar.authority_tier == 1
    assert icar.domain == "icar.gov.in"

    tnau = TrustedSourceRegistry.get_source_by_domain("agritech.tnau.ac.in")
    assert tnau is not None
    assert tnau.authority_tier == 1

def test_local_search_provider():
    provider = LocalKnowledgeSearchProvider()
    assert provider.health_check() is True

    results = provider.search("tomato early blight concentric rings", max_results=5)
    assert len(results) > 0
    assert any("Early Blight" in r["title"] or "TNAU" in r["source_name"] for r in results)

def test_ranking_and_relevance():
    retrieval_svc = EvidenceRetrievalService()
    raw_ev = retrieval_svc.retrieve_evidence("tomato", "Early Blight", ["concentric ring spots"])
    assert len(raw_ev) > 0

    ranked = EvidenceRanker.rank_evidence(raw_ev)
    assert len(ranked) == len(raw_ev)
    assert ranked[0].relevance_score >= ranked[-1].relevance_score

def test_fact_extraction():
    retrieval_svc = EvidenceRetrievalService()
    raw_ev = retrieval_svc.retrieve_evidence("tomato", "Early Blight", ["concentric ring spots"])
    ranked = EvidenceRanker.rank_evidence(raw_ev)
    facts = EvidenceExtractor.extract_facts(ranked)
    assert "symptoms" in facts or "management" in facts

def test_ai_review_generator_grounding_and_confidence():
    vision_res = VisionAnalysisResult(
        crop_key="tomato",
        provider_type="trained_model",
        model_version="tomato-v1",
        predicted_class="Early Blight",
        confidence=0.92,
        visual_confidence=0.92,
        visible_symptoms=["concentric spots", "yellow halo"],
        disease_candidates=[
            {"class": "Early Blight", "visual_confidence": 0.92},
            {"class": "Late Blight", "visual_confidence": 0.08}
        ]
    )

    retrieval_svc = EvidenceRetrievalService()
    raw_ev = retrieval_svc.retrieve_evidence("tomato", "Early Blight", ["concentric spots"])
    ranked = EvidenceRanker.rank_evidence(raw_ev)

    review = AIReviewGenerator.generate_review("tomato", vision_res, ranked)
    assert review.primary_candidate == "Early Blight"
    assert review.vision_confidence == 0.92
    assert review.overall_confidence > 0.70
    assert review.escalation_recommended is False
    # Check no hallucination disclaimer present
    assert any("could not be verified" in act for act in review.recommended_immediate_actions)

def test_conflict_detection_and_escalation():
    vision_res = VisionAnalysisResult(
        crop_key="potato",
        provider_type="visual_assessment",
        model_version="visual-assessment-v1",
        predicted_class="Late Blight",
        confidence=0.55,  # Low confidence
        visual_confidence=0.55,
        visible_symptoms=["water soaked lesions"],
        disease_candidates=[
            {"class": "Late Blight", "visual_confidence": 0.55},
            {"class": "Early Blight", "visual_confidence": 0.45}
        ]
    )

    retrieval_svc = EvidenceRetrievalService()
    raw_ev = retrieval_svc.retrieve_evidence("potato", "Late Blight", ["water soaked lesions"])
    ranked = EvidenceRanker.rank_evidence(raw_ev)

    review = AIReviewGenerator.generate_review("potato", vision_res, ranked)
    # Low confidence must trigger escalation
    assert review.escalation_recommended is True

def test_evidence_cache():
    cache = EvidenceCache(ttl_seconds=10)
    cache.clear()

    retrieval_svc = EvidenceRetrievalService()
    items = retrieval_svc.retrieve_evidence("tomato", "Early Blight", ["spot"])

    cache.set("tomato", "Early Blight", ["spot"], items)
    cached_get = cache.get("tomato", "Early Blight", ["spot"])
    assert cached_get is not None
    assert len(cached_get) == len(items)
    assert cached_get[0].is_cached is True
