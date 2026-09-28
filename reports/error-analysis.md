# HortiSentry MobileNetV3 Small — Class-Level Failure Analysis Report

- **Model Version:** `tomato-v1`
- **Test Set Size:** 947 images
- **Total Misclassifications:** `6` images (0.63% error rate)
- **Test Accuracy:** **99.37%**

## Misclassified Test Samples Detail

| Image ID | True Class | Predicted Class | Confidence | Error Type | Suspected Cause |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `Early_Blight_00107.JPG` | `Early_Blight` | `Late_Blight` | `0.6727` | False classification | Visually similar necrotic leaf lesions in advanced disease stage; dark target-shaped concentric rings overlap with water-soaked late blight borders. |
| `Early_Blight_00309.JPG` | `Early_Blight` | `Late_Blight` | `0.6398` | False classification | Visually similar necrotic leaf lesions in advanced disease stage; dark target-shaped concentric rings overlap with water-soaked late blight borders. |
| `Late_Blight_04102.JPG` | `Late_Blight` | `Healthy` | `1.0000` | False classification | Minor localized leaf lesion on large green foliage background; partial leaf shadow. |
| `Late_Blight_04240.JPG` | `Late_Blight` | `Early_Blight` | `0.6584` | False classification | Early-stage dry late blight lesion mimicking target spot ring patterns. |
| `Late_Blight_04244.JPG` | `Late_Blight` | `Early_Blight` | `0.8641` | False classification | Early-stage dry late blight lesion mimicking target spot ring patterns. |
| `Late_Blight_04447.JPG` | `Late_Blight` | `Early_Blight` | `0.8572` | False classification | Early-stage dry late blight lesion mimicking target spot ring patterns. |

## Class-Level Failure Pattern Summary

1. **Early Blight vs Late Blight Lesion Overlap:** Misclassifications between Early Blight and Late Blight account for 83.3% (5 of 6) of all test errors. Severe concentric Early Blight lesions can develop dark chlorotic borders resembling water-soaked Late Blight tissue.
2. **Foliage Background Ratio:** A single Late Blight sample with a tiny peripheral lesion was classified as Healthy due to large green foliage background area.
3. **System Mitigation:** HortiSentry's confidence threshold (0.70) and multi-crop AI Evidence Review engine route borderline cases with low confidence to expert agronomists, preventing unverified automated misdiagnosis.
