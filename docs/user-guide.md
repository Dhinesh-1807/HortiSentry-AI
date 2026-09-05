# HortiSentry — User Guide

**Tagline:** See Early. Act Smart. Protect Crops.  

---

## 1. Farmer Mobile Workflow Guide

### 1.1 Accessing HortiSentry Home
Navigate to `http://localhost:5173/`. The Farmer Home page presents the brand hero banner, system health status, recent observations, and the primary action button: **[ Report Crop Disease ]**.

### 1.2 Submitting a Crop Observation (6-Step Wizard)

1. **Step 1 — Select Target Crop:** Select the crop being observed (e.g., **Tomato**). Future crops like Chilli, Brinjal, and Potato will be supported in upcoming releases.
2. **Step 2 — Image Upload & Capture:** Upload a clear, well-lit photo of the affected leaf (supports JPG, JPEG, PNG, WEBP; max 10 MB limit). The system displays image preview, filename, and pixel dimensions.
3. **Step 3 — Select Symptoms:** Select visual symptoms from interactive chips (e.g., *Yellow spots*, *Brown spots*, *Dark lesions*, *Leaf curling*, *White patches*, *Holes*, *Wilting*, *Discoloration*, *Drying*).
4. **Step 4 — Select Crop Growth Stage:** Choose the growth stage (*Seedling*, *Vegetative*, *Flowering*, *Fruiting*, *Harvest*).
5. **Step 5 — Regional Location & Field Notes:** Enter non-identifying regional location (*Village*, *District*, *State*). Optionally provide field notes and symptom observed date/time.
6. **Step 6 — Review & Submit:** Inspect summary card and click **[ Submit Observation ]**.

### 1.3 Understanding AI Observation Results
Upon submission, HortiSentry displays the AI-assisted observation:
- **Predicted Condition & Confidence Percentage:** Displays AI top predicted class and confidence bar (e.g., `87%`).
- **DEMO MODE Indicator:** Displays a prominent DEMO MODE badge when running in prototype mode.
- **Image Quality Rating:** Indicates whether the image quality is *Good* or *Needs Attention* (e.g. blur or exposure warning).
- **Responsible AI Disclaimer:** Reminds farmers that AI output is an observation aid, not a guaranteed diagnosis.

### 1.4 Requesting Expert Review
If AI confidence is low (<70%) or image quality is poor, the observation is automatically queued for expert review. Farmers can also click **[ Request Expert Review ]** at any time.

---

## 2. Expert & Cooperative Reviewer Dashboard Guide

### 2.1 Workspace Overview (`/expert`)
Agricultural experts access the dashboard at `http://localhost:5173/expert`. The dashboard provides:
- **KPI Metrics:** Total Observations, Pending Reviews, Low Confidence Cases (<70%), Completed Reviews, and Escalation Counts.
- **Priority Queue Preview:** Quick access to unreviewed cases requiring triage.

### 2.2 Review Queue Triage (`/expert/reviews`)
- **Data Table / Card Stack:** Filter cases by Status (*Pending*, *Under Review*, *Needs Info*), Confidence Level (*Below 70%*), or Escalation Reason (*Low Confidence*, *Poor Image Quality*, *Manual Farmer Request*).
- **Case Search:** Instant search by Case ID, Crop, or Prediction.

### 2.3 Case Inspection & Ground-Truth Diagnosis (`/expert/reviews/:id`)
1. **High-Res Photo Viewer:** Inspect leaf photo with zoom controls and automated blur/exposure diagnostic scores.
2. **AI Inference Breakdown:** View top 3 probability distribution, model version (`tomato-v1`), and `DEMO MODE` tag.
3. **Expert Decision Panel:**
   - **Validate AI Prediction:** One-click validation if expert agrees with AI.
   - **Correct AI Prediction:** Select correct classification from dropdown (e.g., *Healthy*, *Early Blight*, *Late Blight*, *Leaf Spot*).
   - **Expert Notes:** Enter pathological reasoning and protective advice for the farmer.
   - **Complete Review:** Submits diagnosis, updating status to `COMPLETED`. Both original AI prediction and ground-truth expert classification are stored separately for evaluation.
4. **Request Additional Info:** Opens dialog to specify required follow-up images or details from the farmer.

### 2.4 Audit Log & History (`/expert/history`)
Provides a complete audit trail of completed reviews, displaying original AI prediction vs. expert diagnosis.
