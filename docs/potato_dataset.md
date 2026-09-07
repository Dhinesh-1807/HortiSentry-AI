# HortiSentry Potato Dataset (`potato-v1.1-dataset`) Technical Reference

## Executive Summary
The **`potato-v1.1-dataset`** is the updated multi-crop expansion dataset prepared for training HortiSentry's upcoming `potato-v1` vision classifier. It combines laboratory-controlled images with real-world field images across 3 canonical disease classes: `Potato_Healthy`, `Potato_Early_Blight`, and `Potato_Late_Blight`.

---

## 1. Dataset Overview & Composition

| Feature | Details |
| :--- | :--- |
| **Dataset Version** | `potato-v1.1-dataset` |
| **Total Images** | 2,543 images |
| **Healthy Image Count** | 334 images ($\ge 300$ target satisfied) |
| **Canonical Classes** | `Potato_Healthy`, `Potato_Early_Blight`, `Potato_Late_Blight` |
| **Source Repositories** | PlantVillage (Color & Segmented), PlantDoc, HortiSentry Benchmark |
| **Environment Mix** | 95.9% Controlled (Laboratory), 4.1% Field (In-Situ) |
| **Split Strategy** | 70% Train, 15% Validation, 15% Test (Group-Aware Hash Allocation) |

---

## 2. Canonical Class Mapping

| Original Source Label | Canonical Class | Disease Name & Pathogen |
| :--- | :--- | :--- |
| `Potato___healthy` (color & segmented) | `Potato_Healthy` | Solanum tuberosum (Healthy Leaf) |
| `Potato___Early_blight` | `Potato_Early_Blight` | Alternaria solani |
| `Potato___Late_blight` | `Potato_Late_Blight` | Phytophthora infestans |
| `Potato leaf early blight` | `Potato_Early_Blight` | Alternaria solani (Field condition) |
| `Potato leaf late blight` | `Potato_Late_Blight` | Phytophthora infestans (Field condition) |

---

## 3. Data Hygiene & Quality Pipeline
- **Quality Audit:** Every image is verified for readability, resolution ($\ge 50\times 50$), and file format (JPG/PNG/WEBP).
- **Duplicate & Leakage Prevention:** Perceptual hash and MD5 hash clustering (`duplicate_group_id`). All duplicate group members are assigned to the exact same split, guaranteeing zero cross-split leakage.
- **Traceability:** Unified tracking via `data/processed/potato_manifest.csv`.

---

## 4. Training Readiness & Gate Status
- **Class Imbalance:** 3.5:1 ratio (Early Blight vs Healthy).
- **Gate Decision:** `TRAINING_READY` (`GREEN` status).
- **Model Training:** **NOT EXECUTED in Phase 12B**. Model training is authorized for future Phase 13.
