# HortiSentry Field Data Collection Plan & Privacy Framework

## Executive Purpose
This document specifies the protocols, metadata schema, and privacy standards for acquiring real-world field imagery across horticultural crops. The primary goal is to reduce the **studio-to-field domain gap** by capturing visual symptoms under ambient sunlight, variable weather, complex canopy backgrounds, and natural field conditions.

---

## 1. Field Imagery Metadata Schema

Every field-acquired image must record the following standardized metadata fields:

| Field Name | Type | Description / Accepted Values | Example |
| :--- | :--- | :--- | :--- |
| `image_id` | String | Unique identifier | `field_potato_00104` |
| `crop` | String | Target crop name | `potato` |
| `canonical_class` | String | Standardized class | `Potato_Early_Blight` |
| `growth_stage` | String | Plant growth stage (`Seedling`, `Vegetative`, `Flowering`, `Fruiting`, `Harvest`) | `Vegetative` |
| `plant_part` | String | Affected organ (`Foliage`, `Stem`, `Fruit`, `Tuber`, `Flower`) | `Foliage` |
| `region_state` | String | State/Province broad region | `Tamil Nadu` |
| `region_district` | String | District/County broad region | `Coimbatore` |
| `environment` | String | `FIELD` (controlled studio prohibited) | `FIELD` |
| `lighting_condition` | String | `Direct Sunlight`, `Shaded Canopy`, `Cloudy Ambient` | `Direct Sunlight` |
| `camera_distance` | String | `Macro Detail (<10cm)`, `Close-up (10-30cm)`, `Canopy (30-100cm)` | `Close-up (10-30cm)` |
| `capture_date` | String | Date of capture (`YYYY-MM-DD`) | `2026-09-04` |

---

## 2. Privacy & Ethics Safeguards

To comply with global data protection standards (GDPR, India DPDP Act):

1. **No Personally Identifiable Information (PII):** Farmer names, phone numbers, email addresses, or owner identities must **never** be stored in the dataset or manifest.
2. **No Precise GPS Coordinates:** Micro-location coordinates (latitude/longitude) are strictly stripped to protect farm privacy. Only broad administrative regions (State / District) are retained.
3. **Facial Anonymization:** Any background faces or identifying human features must be blurred or cropped prior to ingest.

---

## 3. Recommended Field Sampling Protocol

### Image Distance & Angle Diversity
- **Macro Detail:** Close-up of individual spots, lesions, or fungal fruiting bodies.
- **Whole Leaf View:** Entire leaf blade showing symptom distribution across veins and margins.
- **Canopy Context:** Upper/middle canopy view illustrating severity and spread across foliage.

### Lighting & Exposure Variations
- Capture samples under early morning light, direct midday sun, and overcast skies to build illumination invariance into future ML models.
