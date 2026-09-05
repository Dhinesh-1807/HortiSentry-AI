# HortiSentry — REST API Documentation

**Base API URL:** `http://localhost:8000/api`  
**Interactive Swagger Docs:** `http://localhost:8000/docs`  
**OpenAPI Specification:** `http://localhost:8000/openapi.json`  

---

## 1. Core System Endpoints

### `GET /api/health`
- **Purpose:** System health check, database connectivity, and ML mode status.
- **Request Parameters:** None
- **Response (200 OK):**
  ```json
  {
    "status": "healthy",
    "database": "connected",
    "ml_mode": "REAL",
    "timestamp": "2026-09-02T22:30:00.000Z"
  }
  ```

### `GET /api/model-status`
- **Purpose:** Active ML model status, architecture, and class configuration.
- **Response (200 OK):**
  ```json
  {
    "status": "active",
    "version": "tomato-v1",
    "architecture": "MobileNetV3 Small",
    "classes": ["Healthy", "Early_Blight", "Late_Blight", "Septoria_Leaf_Spot"],
    "is_demo_mode": false,
    "confidence_threshold": 0.70
  }
  ```

### `GET /api/crops`
- **Purpose:** Supported crops, growth stages, and selectable symptoms.
- **Response (200 OK):**
  ```json
  [
    {
      "id": "tomato",
      "display_name": "Tomato",
      "scientific_name": "Solanum lycopersicum",
      "stages": ["SEEDLING", "VEGETATIVE", "FLOWERING", "FRUITING", "HARVEST"],
      "symptoms": ["Yellow spots", "Brown spots", "Dark lesions", "Leaf curling", "White patches", "Holes", "Wilting", "Discoloration", "Drying", "Other"]
    }
  ]
  ```

---

## 2. ML Inference & Observation Endpoints

### `POST /api/predict`
- **Purpose:** Direct computer vision inference on uploaded leaf image without creating observation record.
- **Content-Type:** `multipart/form-data`
- **Payload:** `file` (Image binary)
- **Response (200 OK):**
  ```json
  {
    "predicted_class": "Healthy",
    "confidence": 0.9998,
    "top_predictions": [
      { "class": "Healthy", "confidence": 0.9998 },
      { "class": "Late_Blight", "confidence": 0.0002 }
    ],
    "model_version": "tomato-v1",
    "inference_time_ms": 30.73,
    "is_demo_mode": false,
    "needs_expert_review": false
  }
  ```

### `POST /api/observations`
- **Purpose:** Submit farmer crop observation with leaf photo, symptoms, stage, and location.
- **Content-Type:** `multipart/form-data`
- **Form Fields:** `crop_id`, `crop_stage`, `symptoms`, `village`, `district`, `state`, `notes`
- **File:** `file` (Image binary)
- **Response (201 Created):** Returns observation details, image quality result, AI prediction, and assigned status.

### `GET /api/observations`
- **Purpose:** List observations with optional status filtering.
- **Response (200 OK):** Array of observation summary objects.

### `GET /api/observations/{id}`
- **Purpose:** Retrieve complete observation case details, AI prediction breakdown, and expert review status.

### `POST /api/observations/{id}/escalate`
- **Purpose:** Manually trigger expert escalation for an existing observation case.
- **Payload:** `{"reason_notes": "Farmer requested expert review"}`

---

## 3. Expert Review Endpoints

### `GET /api/expert/dashboard/stats`
- **Purpose:** Metrics overview for expert dashboard (Pending, Under Review, Completed, Needs Info, Average Latency).

### `GET /api/expert/reviews`
- **Purpose:** Retrieve queued expert review cases.

### `GET /api/expert/reviews/{id}`
- **Purpose:** Retrieve full inspection detail for a single expert review case.

### `POST /api/expert/reviews/{id}/complete`
- **Purpose:** Submit authoritative expert diagnosis and resolution notes.
- **Payload:** `{"expert_prediction": "Early_Blight", "expert_notes": "Concentric rings verified."}`

### `POST /api/expert/reviews/{id}/request-info`
- **Purpose:** Request additional imagery or notes from the submitting farmer.
- **Payload:** `{"info_note": "Please upload a clearer close-up photo of lower leaves."}`
