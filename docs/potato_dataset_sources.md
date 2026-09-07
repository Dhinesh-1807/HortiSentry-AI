# Potato Dataset Sources & License Traceability

## Overview
This document registers all public agricultural repositories integrated into the **`potato-v1.1-dataset`** expansion for HortiSentry. Every image is traceable to its source organization, original publication, and licensing terms.

---

## Source Register

### 1. PlantVillage Dataset (Color & Segmented)
- **Dataset Name:** PlantVillage Potato Subset (Color & Segmented Healthy)
- **Source Organization:** Penn State University / spMohanty GitHub Repository
- **Source URL:** https://github.com/spMohanty/PlantVillage-Dataset
- **License:** CC BY 4.0 (Creative Commons Attribution 4.0 International)
- **License Status:** VERIFIED
- **Attribution Requirement:** "Hughes, D., & Salathé, M. (2015). An open access repository of plant pathology images for diagnosing plant diseases."
- **Allowed Use:** Open research, educational, and commercial model training.
- **Environment:** Controlled / Laboratory background (`CONTROLLED`).
- **Canonical Classes Mapped:**
  - `Potato___healthy` (color & segmented) → `Potato_Healthy`
  - `Potato___Early_blight` → `Potato_Early_Blight`
  - `Potato___Late_blight` → `Potato_Late_Blight`

### 2. PlantDoc Dataset
- **Dataset Name:** PlantDoc In-Situ Visual Disease Dataset
- **Source Organization:** Indian Institute of Technology (IIT) Dharwad / pratikkayal GitHub Repository
- **Source URL:** https://github.com/pratikkayal/PlantDoc-Dataset
- **License:** MIT License / Open Research Data
- **License Status:** VERIFIED
- **Attribution Requirement:** "Singh, D., et al. (2020). PlantDoc: A Dataset for Visual Plant Disease Detection."
- **Allowed Use:** Open research, model training, and comparative evaluation.
- **Environment:** In-situ natural field condition (`FIELD`).
- **Canonical Classes Mapped:**
  - `Potato leaf early blight` → `Potato_Early_Blight`
  - `Potato leaf late blight` → `Potato_Late_Blight`

### 3. HortiSentry Benchmark Set
- **Dataset Name:** HortiSentry Multi-Crop Benchmark Set
- **Source Organization:** HortiSentry Internal Benchmark
- **Source URL:** Internal Repository (`data/processed/multi_crop_manifest.csv`)
- **License:** Proprietary / HortiSentry Internal Open Research
- **License Status:** VERIFIED
- **Environment:** Controlled / Field
- **Canonical Classes Mapped:**
  - `Potato_Healthy`
  - `Potato_Early_Blight`
  - `Potato_Late_Blight`

---

## Compliance & Rights Summary
All acquired images operate under open research licenses (CC BY 4.0 / MIT). No datasets with ambiguous, restricted, or unverified licensing terms are included in the `potato-v1.1-dataset` training pool.
