# Potato-v1 Model Card (HortiSentry System)

## Model Details
- **Model Name:** `potato-v1`
- **Model Type:** Convolutional Neural Network (Transfer Learning)
- **Base Architecture:** MobileNetV3 Small (`mobilenet_v3_small`)
- **Framework:** PyTorch 2.x
- **Developer:** HortiSentry AI Engineering Team
- **Artifact Path:** `ml/artifacts/potato_v1.pt`
- **SHA-256 Checksum:** `24344f482356...`
- **Artifact Size:** 5.86 MB

## Intended Use
- **Primary Function:** AI-assisted visual observation and classification of potato leaf foliage images.
- **Target Audience:** Farmers, agricultural extension officers, and HortiSentry review queue agronomists.
- **Out of Scope:** Mandatory diagnostic certification without human escalation; non-foliage plant parts (tubers, roots).

## Classification Schema
1. `Potato_Healthy` — Healthy potato leaf tissue.
2. `Potato_Early_Blight` — Foliage infected by *Alternaria solani*.
3. `Potato_Late_Blight` — Foliage infected by *Phytophthora infestans*.

## Training Data & Splits
- **Dataset:** `potato-v1.1-dataset` (2,543 total images)
- **Train Split:** 1,796 images (70%)
- **Validation Split:** 368 images (15%)
- **Test Split:** 379 images (15%)
- **Data Augmentations:** RandomResizedCrop(224), RandomHorizontalFlip(0.5), RandomRotation(15 deg), ColorJitter(0.1, 0.1).

## Performance Summary
- **Test Accuracy:** 96.83%
- **Macro F1 Score:** 0.9733
- **Weighted F1 Score:** 0.9683
- **Healthy Class F1:** 0.9895 (100% recall)
- **Inference Latency:** 10.04 ms (CPU)

## Safety & Responsible AI Policy
- **Confidence Threshold:** 0.70 (`CONFIDENCE_THRESHOLD = 0.70`)
- **Escalation Trigger:** Any prediction with confidence $< 0.70$ generates `needs_expert_review: true`.
- **Terminology:** Product reports label outputs as `"AI-Assisted Agricultural Decision Support"`.
