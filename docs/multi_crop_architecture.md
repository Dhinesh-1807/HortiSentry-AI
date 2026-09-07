# HortiSentry Multi-Crop Platform Architecture

## Executive Overview
HortiSentry Phase 10 scales the system from a single-crop (Tomato) PyTorch disease classifier to an extensible 32-crop horticultural platform. The system leverages a dual-provider vision abstraction layer:
1. **Dedicated PyTorch Vision Model (`tomato-v1`)**: Highly accurate trained MobileNetV3 Small classifier for Tomato leaf diseases (99.37% test accuracy).
2. **Visual Symptom Analyzer Provider (`visual_assessment`)**: Generalizable multimodal AI vision analyzer operating across 31 additional horticultural crops (Vegetables, Fruits, Spices & Plantation).

## Architecture Diagram

```mermaid
flowchart TD
    Farmer[Farmer Observation UI] --> CropSelect[32-Crop Catalogue Selection]
    CropSelect --> VisionRouter[Vision Provider Abstraction Router]
    
    VisionRouter -->|crop == 'tomato'| PyTorchModel[PyTorch tomato-v1 MobileNetV3 Small]
    VisionRouter -->|crop != 'tomato'| VisualAnalyzer[Visual Symptom Analyzer Engine]
    
    PyTorchModel --> VisionResult[Vision Analysis Result]
    VisualAnalyzer --> VisionResult
    
    VisionResult --> EvidenceEngine[AI Evidence Engine]
    
    subgraph AI Evidence Engine
        EvidenceEngine --> Search[Structured Query Engine]
        Search --> SourceRegistry[Trusted Source Registry ICAR / TNAU / FAO / EPPO]
        SourceRegistry --> Retrieval[Evidence Retrieval Service & Cache]
        Retrieval --> Ranker[Multi-Factor Evidence Ranker 40% Tier, 30% Crop, 20% Disease, 10% Symptom]
        Ranker --> Extractor[Fact Extractor & Source Citation]
        Extractor --> ReviewGen[AI Review Generator with IPM Guardrails]
    end
    
    ReviewGen --> AIReview[AI Evidence Review Output]
    AIReview --> EscalationCheck{Escalation Trigger Check}
    EscalationCheck -->|Low Conf / Mixed Evidence| ExpertQueue[Human Expert Escalation Queue]
    EscalationCheck -->|High Confidence| FarmerUI[Farmer AI Review Detail Screen]
```

## Crop Categories
- **Vegetables (10 crops)**: Tomato, Chilli, Brinjal, Potato, Onion, Garlic, Okra, Cabbage, Cauliflower, Cucumber.
- **Fruits (12 crops)**: Mango, Banana, Papaya, Citrus, Grapes, Guava, Pomegranate, Apple, Watermelon, Pineapple, Sapota, Strawberry.
- **Spices & Plantation (10 crops)**: Ginger, Turmeric, Black Pepper, Cardamom, Clove, Cinnamon, Coconut, Arecanut, Cashew, Coffee.
