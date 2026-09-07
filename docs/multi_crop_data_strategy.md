# HortiSentry Multi-Crop Data Strategy & AI Provider Roadmap

## Executive Overview
This document details the multi-crop data expansion strategy and AI provider transition roadmap for HortiSentry.

While Phase 10A established a multi-crop benchmark dataset of **755 registered images across 13 non-tomato crops**, HortiSentry explicitly refrains from training supervised ML classification models on small benchmark sets. Instead, HortiSentry employs an **AI Provider Three-State Architecture** that guarantees accurate, evidence-backed disease observations regardless of dedicated model availability.

---

## 1. Why 755 Benchmark Images are NOT Used for Supervised Model Training

1. **Overfitting & Poor Generalization:** Supervised deep neural networks (e.g. MobileNetV3, ResNet) trained on fewer than 100 images per class exhibit severe memorization and fail when presented with unseen field foliage.
2. **Studio-to-Field Domain Gap:** Benchmark datasets (such as PlantVillage) consist primarily of leaves excised and photographed against monochromatic studio backgrounds. Models trained exclusively on studio images fail in natural field environments under ambient sunlight and complex canopy backgrounds.
3. **Class Imbalance & Single-Class Crops:** Several target crops currently contain only healthy foliage samples or single disease classes. Supervised multi-class classifiers cannot be constructed without representative disease and healthy classes.

---

## 2. Dataset Readiness Targets for Future Supervised Training

To qualify a crop for dedicated PyTorch model training (GREEN Tier), the dataset must satisfy the following engineering targets:

- **Minimum Sample Volume:** $\ge 500$ high-quality images per class (ideal target: $1000+$ images/class).
- **Source Diversity:** Images must originate from at least **2 independent agricultural institutions/datasets** to prevent source bias.
- **Field Representation:** At least **30% of training imagery** must feature natural field conditions (ambient light, complex backgrounds).
- **Zero Cross-Split Leakage:** Exact MD5 duplicates and near-duplicate dHash pairs must be isolated within the same split (Train, Validation, or Test).

---

## 3. AI Provider Three-State Architecture

HortiSentry handles crop observations seamlessly across three operational states:

```
                  ┌──────────────────────────────────────────────┐
                  │ Crop Disease Observation Request Submitted   │
                  └──────────────────────┬───────────────────────┘
                                         │
                         Is Dedicated Model Available?
                                         │
                      ┌──────────────────┴──────────────────┐
                      │ YES                                 │ NO
                      ▼                                     ▼
        ┌───────────────────────────┐         ┌───────────────────────────┐
        │   STATE A: Dedicated ML   │         │   STATE B: Multimodal     │
        │   Classifier (PyTorch)    │         │   Visual Assessment +     │
        │   (e.g., tomato-v1)       │         │   AI Evidence Engine      │
        └─────────────┬─────────────┘         └─────────────┬─────────────┘
                      │                                     │
                      └──────────────────┬──────────────────┘
                                         │
                                         ▼
                      ┌─────────────────────────────────────┐
                      │   AI Evidence Review Delivered     │
                      │   (With Transparency & Confidence)  │
                      └─────────────────────────────────────┘
```

### State A: Dedicated Trained Model (PyTorch Provider)
- **Applicability:** Crops meeting GREEN Tier readiness with verified high-accuracy models (e.g. Tomato with `tomato-v1`, MobileNetV3 Small, 99.37% test accuracy).
- **Inference Mode:** Fast local tensor inference yielding disease class probabilities, confidence scores, and literature recommendations.

### State B: Multimodal Visual Assessment + AI Evidence Review Engine
- **Applicability:** Crops in YELLOW or RED tiers where supervised ML models are not yet trained (e.g. Potato, Pepper, Apple, Grape, Corn, Peach, etc.).
- **Inference Mode:** Multimodal visual symptom analysis identifies leaf spot patterns, chlorosis, lesions, and necrosis. The **AI Evidence Review Engine** queries trusted agricultural repositories (TNAU, ICAR, FAO, University Extension) to deliver differential diagnoses, confidence ratings, and diagnostic evidence.

### State C: Unsupported / Insufficient Evidence
- **Applicability:** Observations with severe image corruption, non-plant imagery, or unidentifiable visual features.
- **Inference Mode:** Triggers automated guidance requesting clearer close-up foliage photographs under natural light.

---

## 4. Dataset Versioning Policy

- **`multi-crop-v1.0-benchmark`**: The initial 755-image integration & audit dataset.
- **`multi-crop-v1.1`**: Planned expanded dataset incorporating field-captured imagery from PlantDoc, TNAU, and ICAR repositories (Phase 11).
- **Immutable Provenance:** Dataset manifests are immutable and versioned. Existing versions are never silently overwritten or mutated.
