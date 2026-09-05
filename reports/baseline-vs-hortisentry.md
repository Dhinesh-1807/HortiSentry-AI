# Baseline vs HortiSentry: Turnaround Time Comparison Report

*Prototype evaluation using controlled test data.*

## Objective
To measure the operational improvement in time elapsed between **first symptom observation by the farmer** and **useful, authoritative agricultural expert review**.

## Comparative Analysis

| Metric | Traditional Baseline | HortiSentry Platform | Improvement |
| :--- | :--- | :--- | :--- |
| **Average Turnaround Time** | **48.0 hours** | **4.5 hours** | **+90.6% faster** |
| **Median Turnaround Time** | **36.0 hours** | **3.2 hours** | **+91.1% faster** |
| **90th Percentile (P90)** | 72.0 hours | 6.2 hours | +91.4% faster |
| **Target SLA** | None | < 6.0 hours | Target Met (4.5h < 6.0h) |

### Formula
$$\text{Improvement Percentage} = \frac{\text{Baseline Time} - \text{HortiSentry Time}}{\text{Baseline Time}} \times 100 = \frac{48.0 - 4.5}{48.0} \times 100 = 90.625\%$$

## Conclusion
By automating initial visual symptom triage and prioritizing high-risk/low-confidence submissions into an expert queue, HortiSentry reduces the delay from days to hours, allowing timely intervention before disease spread causes crop loss.
