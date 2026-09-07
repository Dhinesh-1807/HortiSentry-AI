# HortiSentry — User Guide & Demonstration Manual

**Tagline:** See Early. Act Smart. Protect Crops.  

---

## 1. Farmer Role User Guide

### Step 1: Accessing the Home Dashboard
1. Open web browser and navigate to `http://localhost:5173`.
2. Notice the prominent Responsible AI disclaimer: *"Decision Support, Not Diagnostic Certification"*.

### Step 2: Creating a New Observation
1. Click **"New Observation"** in the navigation header.
2. Select your crop: **Tomato**.
3. Choose your crop growth stage (e.g. `Fruiting` or `Vegetative`).

### Step 3: Leaf Photo Upload & Image Quality Pre-Check
1. Click **"Upload Leaf Image"** or tap to capture photo on mobile devices.
2. The instant image quality pre-check evaluates blur and exposure.
3. If image quality passes, a green *"Quality Passed"* badge will appear.

### Step 4: Selecting Symptoms & Location
1. Check observed symptoms (e.g. `Yellow spots`, `Leaf curling`).
2. Enter your location (Village, District, State) and optional farm notes.
3. Click **"Submit Observation"**.

### Step 5: Viewing AI Observation Results & Escalation
1. View instant AI observation analysis:
   - **Predicted Disease** (e.g. `Healthy`, `Early Blight`, `Late Blight`, `Septoria Leaf Spot`).
   - **Confidence Percentage** (e.g. `99.98%`).
   - **Mode Badge** (`REAL MODEL`).
2. If AI confidence is below $70\%$, the system automatically displays: *"AI confidence is low. Expert review recommended."* and queues the case for expert human review.
3. Track observation status anytime under **"Observation History"**.

---

## 2. Agricultural Expert Role User Guide

### Step 1: Opening the Expert Dashboard
1. Navigate to `http://localhost:5173/expert`.
2. View key KPI cards: **Pending Reviews**, **Under Review**, **Completed Cases**, and **Needs Info**.

### Step 2: Inspecting an Escalated Review Case
1. Click on any pending observation from the review queue.
2. View high-resolution leaf photo, crop stage, farmer location, symptoms, and the original AI prediction.

### Step 3: Submitting Expert Resolution
1. To confirm or override the diagnosis:
   - Select authoritative disease class (e.g., `Early_Blight`).
   - Add expert advisory notes for the farmer.
   - Click **"Complete Review"**.
2. To request clearer imagery or more details:
   - Click **"Request More Information"**.
   - Type information request notes and submit.

---

## 3. Demonstration Workflow for Project Viva

1. **Step A:** Open Farmer UI (`http://localhost:5173`) and submit `data/test/Healthy/Healthy_01005.JPG`.
2. **Step B:** Show instant real PyTorch inference output (`Healthy`, 99.98% confidence).
3. **Step C:** Click **"Request Expert Review"** to manually escalate the case.
4. **Step D:** Switch to Expert Dashboard (`http://localhost:5173/expert`) and open the escalated case.
5. **Step E:** Complete expert review with an authoritative diagnosis override (`Early Blight`).
6. **Step F:** Return to Farmer UI and verify status updated to `COMPLETED`, showing the preserved original AI prediction alongside the expert override decision.
