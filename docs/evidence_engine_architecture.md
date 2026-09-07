# HortiSentry AI Evidence Review Engine — Architecture & Technical Reference

## Executive Summary
The **HortiSentry AI Evidence Review Engine** transitions the platform from a manual expert-dependent review bottleneck to a scalable, evidence-backed AI observation system. By integrating authoritative agricultural research sources (ICAR, TNAU, FAO, EPPO, PPQS) into the dynamic observation pipeline, HortiSentry delivers grounded, transparent, and probabilistic disease reviews to farmers while preserving human expert escalation for high-risk or uncertain cases.

---

## 1. System Architecture

```
                  ┌──────────────────────────────┐
                  │    Farmer Image Upload       │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │    Image Quality & Vision    │
                  │   Analysis (MobileNetV3 /    │
                  │   Visual Symptom Analyzer)   │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │   Search Query Generator     │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │     Evidence Cache (TTL)     │
                  └──────┬────────────────┬──────┘
             Cache Hit   │                │ Cache Miss
                         ▼                ▼
            ┌──────────────────┐  ┌──────────────────┐
            │ Cached Evidence  │  │ Search Provider  │
            └────────┬─────────┘  │  (Local / Web)   │
                     │            └────────┬─────────┘
                     │                     │
                     └──────────┬──────────┘
                                │
                                ▼
                  ┌──────────────────────────────┐
                  │ Source Ranker (Tier Weight + │
                  │     Relevance Score)         │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │ Fact Extraction (IPM First)  │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │ Grounded Review Generator &  │
                  │  Escalation Decision Engine  │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │  AI-Assisted Review & Source │
                  │  Attribution Cards Display   │
                  └──────────────────────────────┘
```

---

## 2. Key Components

### 2.1 Source Registry (`backend/app/evidence/source_registry.py`)
Establishes a 3-tier hierarchy of authoritative agricultural institutions:
- **Tier 1 (Weight: 1.00):** ICAR (Indian Council of Agricultural Research), TNAU Agritech Portal, FAO (Food & Agriculture Organization), EPPO, PPQS India.
- **Tier 2 (Weight: 0.85):** CABI PlantwisePlus, State Agricultural Universities (SAUs), KVK Extension Portals.
- **Tier 3 (Weight: 0.70):** Peer-reviewed agricultural extension articles and verified advisory bulletins.

### 2.2 Search Provider Abstraction (`backend/app/evidence/search_provider.py`)
Provides a pluggable `AgriculturalSearchProvider` interface with automatic fallback:
- **LocalKnowledgeSearchProvider:** Built-in verified agricultural database covering ICAR/TNAU advisories for 32 horticultural crops.
- **ConfigurableWebSearchProvider:** Extensible HTTP client for live web search integration.
- **Graceful Fallback:** If an external search provider fails or is unreachable, the system gracefully degrades to local knowledge without application failure.

### 2.3 Transparent Ranking Formula (`backend/app/evidence/ranking.py`)
Retrieved evidence is ranked using an explicit weighted scoring formula:
$$S = w_{\text{tier}} \times \left(0.40 \cdot R_{\text{crop}} + 0.40 \cdot R_{\text{disease}} + 0.20 \cdot R_{\text{symptom}}\right)$$
Where:
- $w_{\text{tier}}$: Authority weight derived from institution tier (1.00, 0.85, 0.70).
- $R_{\text{crop}}$: Match relevance with requested crop species.
- $R_{\text{disease}}$: Match relevance with vision candidate disease.
- $R_{\text{symptom}}$: Match relevance with reported foliage symptoms.

### 2.4 Evidence Caching (`backend/app/evidence/cache.py`)
- In-memory TTL cache (default 3600 seconds) keyed by MD5 hash of `crop:disease:symptoms`.
- Reduces latency and protects external API quotas.

### 2.5 Grounded Review Generator & Safety Guardrails (`backend/app/evidence/review_generator.py`)
- **Strict Grounding:** AI reviews are synthesized *exclusively* from retrieved facts.
- **IPM Priority:** Emphasizes cultural, mechanical, and biological Integrated Pest Management practices.
- **No-Hallucination Disclaimer:** Avoids chemical dosage recommendations; appends explicit extension officer consultation notices.
- **Probabilistic Terminology:** Uses language such as *"visually consistent with"* and *"suggests potential risk"*.
- **Escalation Rules:** Automatically flags cases for human expert review when:
  1. Overall confidence $< 0.70$.
  2. Evidence sources conflict (`evidence_is_mixed = True`).
  3. Estimated disease severity is `HIGH`.
  4. Image quality issues are detected.

---

## 3. Database Schema Integration

The backend persists AI evidence reviews alongside baseline predictions:
- `ai_reviews`: Stores summary, confidence breakdown, severity, conflict notes, and provider metadata.
- `review_evidence`: Stores individual cited evidence items, including source name, URL, authority tier, and relevance score.
- `expert_reviews` & `escalations`: Maintained for human expert escalation and auditability.
