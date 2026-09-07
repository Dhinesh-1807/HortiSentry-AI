# HortiSentry Multi-Crop Dataset System — Technical Documentation

## Executive Overview
The **HortiSentry Multi-Crop Dataset System** provides a structured, traceable, and audited data pipeline for expanding HortiSentry from a single-crop tomato classifier to a 14-crop horticultural observation platform.

The system ensures complete data auditability, preserves raw source labels, normalizes disease taxonomies, detects exact and perceptual duplicates, prevents data leakage between splits, and strictly isolates field evaluation datasets.

---

## 1. Baseline Dataset Protection & Isolation
To maintain system integrity, Phase 10A enforces strict isolation between baseline assets and multi-crop additions:

| Asset | Path | Isolation Status |
| :--- | :--- | :--- |
| **Tomato Raw Images** | `data/raw/tomato/` | **100% Preserved & Unmodified** (6,271 images) |
| **Tomato Processed Manifest** | `data/processed/manifest.csv` | **100% Preserved & Unmodified** |
| **Tomato Train/Val/Test** | `data/train/`, `data/validation/`, `data/test/` | **100% Preserved & Unmodified** |
| **Tomato Model Checkpoint** | `ml/artifacts/tomato_v1.pt` | **100% Preserved & Unmodified** |
| **Multi-Crop Raw Images** | `data/raw/multi_crop/<crop>/` | **Isolated Subdirectory** |
| **Multi-Crop Manifest** | `data/processed/multi_crop_manifest.csv` | **Isolated Multi-Crop Manifest** |

---

## 2. Dataset Sources & Licensing Provenance
Registered sources in `config/datasets.yaml`:

| Source ID | Dataset Name | Organization | License | Provenance URL |
| :--- | :--- | :--- | :--- | :--- |
| `plantvillage` | PlantVillage Dataset | Penn State / EPFL | CC BY 4.0 | `github.com/spMohanty/PlantVillage-Dataset` |
| `plantdoc` | PlantDoc Dataset | IIT Bombay | CC BY 4.0 | `github.com/pratikkayal/PlantDoc-Dataset` |
| `tnau_agritech` | TNAU AgriTech Portal | Tamil Nadu Agricultural Univ. | Open Educational | `agritech.tnau.ac.in` |
| `icar_datasets` | ICAR Open Repositories | ICAR Govt of India | Public Govt Access | `icar.gov.in` |

---

## 3. Label Normalization & Taxonomy Schema
Configured in `config/multi_crop_classes.yaml`:

```yaml
class_mappings:
  - crop: "potato"
    canonical_class: "Potato_Early_Blight"
    original_label: "Potato___Early_blight"
    disease_type: "fungal"
```

### Taxonomy Rules
1. **Preservation:** Raw labels (`original_label`) are never deleted or overwritten.
2. **Standardization:** `canonical_class` uses standardized English CamelCase naming (`<Crop>_<DiseaseName>`).
3. **Biological Categorization:** Each class is mapped to a disease category: `fungal`, `bacterial`, `viral`, `pest`, `physiological`, `healthy`, or `unknown`.

---

## 4. Image Quality Validation Pipeline

All images undergo multi-factor quality inspection prior to manifest registration:

| Metric | Target / Rule | Action |
| :--- | :--- | :--- |
| **Format** | JPG, JPEG, PNG, WEBP | Unrecognized formats marked `unsupported_format` |
| **Resolution** | Min $224 \times 224$ pixels | Images below minimum marked `REJECT` |
| **Aspect Ratio** | $0.5 \le \text{Aspect Ratio} \le 2.0$ | Extreme aspect ratios marked `REJECT` |
| **Blur Score** | OpenCV Laplacian Variance $< 20.0$ | Severe blur marked `REJECT`; $< 100.0$ marked `WARNING` |
| **Exposure** | Grayscale Mean $< 30.0$ or $> 220.0$ | Over/underexposed images marked `WARNING` |

---

## 5. Duplicate Detection & Data Leakage Prevention

### Exact Duplicate Detection (MD5)
- Computes 128-bit MD5 hashes for all files.
- Identical hashes are assigned a unified `duplicate_group_id` (`DUP_XXXX`) in `multi_crop_manifest.csv`.

### Perceptual Duplicate Detection (dHash)
- Resizes grayscale images to $9 \times 8$ pixels to calculate horizontal difference hashes (dHash).
- Identifies near-duplicate pairs matching Hamming distance $\le 4$.

### Leakage Prevention in Splitting
- Stratified splitting applies a deterministic seed (`42`).
- Images sharing the same MD5 hash are forced into the **same split** (Train, Validation, or Test) to prevent cross-split data leakage.

---

## 6. Field Test Isolation Policy
- Imagery in `data/field_test/` is strictly reserved for post-training field accuracy benchmarks.
- Field test images are **never** included in training, validation, or multi-crop manifests.

---

## 7. Known Dataset Limitations
1. **Studio vs. Field Domain Gap:** PlantVillage images are captured in controlled studio environments against monochromatic backgrounds.
2. **Class Imbalance:** Representation varies across crops; minority classes should be monitored during future model training.
3. **No Training Claim:** Phase 10A is strictly restricted to data preparation. No ML model performance metrics are claimed.
