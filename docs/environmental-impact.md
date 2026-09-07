# HortiSentry — Environmental Impact & Sustainability Assessment

## Potential Positive Environmental Impacts
1. **Early Targeted Disease Containment:** Early observation of disease outbreaks (e.g. Late Blight) allows farmers to isolate affected areas early, potentially reducing crop loss.
2. **Preventing Over-application of Chemicals:** By providing expert review before intervention, farmers avoid indiscriminate broad-spectrum chemical spraying caused by misdiagnosis.

## Potential Negative Operational Footprint & Mitigation
1. **Model Training & Cloud Compute Energy:** Deep neural networks consume electrical power during training.  
   *Mitigation:* Use lightweight architectures (MobileNetV3 / EfficientNet-B0) with small parameter footprints and transfer learning to minimize GPU training time.
2. **Data Storage & Network Transmission:** Transferring high-resolution photos consumes network bandwidth and storage space.  
   *Mitigation:* Client-side image resizing and lossy compression before upload to optimize file payload size.
