# HortiSentry AI Evidence Engine Documentation

## Core Design Principles
The HortiSentry AI Evidence Engine provides non-hallucinatory, evidence-backed decision support for horticultural disease observations.

## Workflow Pipeline
1. **Query Construction**: Generates targeted query strings prioritizing domain filters (e.g. `site:agritech.tnau.ac.in`, `site:icar.gov.in`).
2. **Evidence Retrieval & Caching**: Queries the structured search engine and caches retrieved evidence items for 1 hour to ensure responsive, low-latency performance.
3. **Multi-Factor Ranking Formula**:
   $$\text{Score} = 0.40 \cdot \text{TierWeight} + 0.30 \cdot \text{CropRelevance} + 0.20 \cdot \text{DiseaseRelevance} + 0.10 \cdot \text{SymptomRelevance}$$
   - Tier 1 Sources (ICAR, TNAU, FAO, EPPO, PPQS): Weight 1.00
   - Tier 2 Sources (CABI, IIHR, CPRI, Universities): Weight 0.80 - 0.85
   - Tier 3 Sources (Extension Services): Weight 0.70
4. **Fact Extraction & Source Attribution**: Parses symptoms, IPM cultural management practices, prevention strategies, and monitoring guidance while preserving explicit source links.
5. **AI Review Generation**: Synthesizes the final review output with IPM prioritization and conflict warnings.
