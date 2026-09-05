# HortiSentry AI Evidence Review Specification

## Phrasing & Non-Definitive Language
To ensure responsible AI usage in agricultural decision support, AI Reviews use non-definitive phrasing:
- *"The uploaded image and symptoms are visually consistent with [Disease Name]."*
- For low confidence ($< 0.70$): *"The available visual and evidence signals are insufficient for definitive identification. Expert verification recommended."*

## Safety Guardrails & Non-Chemical Prioritization
- **No Unbacked Chemicals**: Never invents pesticide names or exact chemical dosages.
- **IPM Cultural Practices**: Recommends field sanitation, infected debris removal, canopy airflow management, and crop rotation.
- **Explicit Disclaimer**: Adds *"Specific chemical treatment guidance could not be verified from the available trusted sources. Consult local extension officers for approved chemical applications."*

## Confidence Metric Formula
$$\text{Overall Confidence} = 0.40 \cdot \text{VisionConfidence} + 0.60 \cdot \text{EvidenceConfidence}$$
