import pytest
from PIL import Image
from app.services.crop_service import CropConfigLoader
from app.ml.vision_provider import VisualSymptomAnalyzerProvider, PyTorchTomatoVisionProvider
from app.evidence.source_registry import TrustedSourceRegistry
from app.evidence.search import AgriculturalSearchEngine
from app.evidence.retrieval import EvidenceRetrievalService
from app.evidence.ranking import EvidenceRanker
from app.evidence.review_generator import AIReviewGenerator
from app.evidence.service import EvidenceEngineService

def test_crop_catalogue_32_crops():
    crops = CropConfigLoader.get_supported_crops()
    assert len(crops) >= 32
    
    categories = set(c["category"] for c in crops)
    assert "vegetables" in categories
    assert "fruits" in categories
    assert "spices_plantation" in categories

def test_trusted_source_registry():
    sources = TrustedSourceRegistry.get_all_sources()
    assert len(sources) >= 5
    tier1 = [s for s in sources if s.authority_tier == 1]
    assert len(tier1) >= 3

def test_evidence_search_and_ranking():
    raw_evidence = EvidenceRetrievalService.retrieve_evidence(
        crop="tomato",
        disease_candidate="Early Blight",
        symptoms=["Yellow spots", "Brown spots"]
    )
    assert len(raw_evidence) > 0
    ranked = EvidenceRanker.rank_evidence(raw_evidence)
    assert ranked[0].relevance_score >= ranked[-1].relevance_score

def test_visual_symptom_analyzer():
    provider = VisualSymptomAnalyzerProvider()
    img = Image.new("RGB", (224, 224), (80, 140, 80))
    res = provider.analyze_image(img, crop_key="chilli", user_symptoms=["Upward leaf curling"])
    assert res.crop_key == "chilli"
    assert res.provider_type == "visual_assessment"
    assert res.model_version == "visual-assessment-v1"
    assert len(res.visible_symptoms) > 0

def test_evidence_engine_service_generation():
    img = Image.new("RGB", (224, 224), (100, 150, 100))
    review = EvidenceEngineService.generate_ai_evidence_review(
        image=img,
        crop="brinjal",
        user_symptoms=["Little leaves", "Bushy growth"]
    )
    assert review.primary_candidate is not None
    assert len(review.sources_used) > 0
    assert review.overall_confidence > 0.0
    assert "Specific chemical treatment guidance could not be verified" in review.recommended_immediate_actions[-1]
