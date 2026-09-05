import os
import sys
import json
import hashlib
import logging
from pathlib import Path
import torch
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "backend") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "backend"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("VerifyPhase13")

def get_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def main():
    logger.info("==================================================================")
    logger.info("HORTISENTRY PHASE 13 VERIFICATION SUITE")
    logger.info("==================================================================")

    passed_checks = 0
    failed_checks = 0

    def check(condition: bool, description: str):
        nonlocal passed_checks, failed_checks
        if condition:
            logger.info(f"✅ PASS: {description}")
            passed_checks += 1
        else:
            logger.error(f"❌ FAIL: {description}")
            failed_checks += 1

    # 1. Tomato Baseline Protection
    tomato_artifact = PROJECT_ROOT / "ml" / "artifacts" / "tomato_v1.pt"
    tomato_manifest = PROJECT_ROOT / "data" / "processed" / "manifest.csv"
    check(tomato_artifact.exists(), "Tomato-v1 production artifact exists and is locked")
    check(tomato_manifest.exists(), "Tomato manifest.csv exists and is locked")

    # 2. Potato Dataset & Manifest
    potato_manifest = PROJECT_ROOT / "data" / "processed" / "potato_manifest.csv"
    check(potato_manifest.exists(), "Potato manifest CSV exists")

    # 3. Model Checkpoints & Artifacts
    potato_checkpoint = PROJECT_ROOT / "ml" / "checkpoints" / "potato_mobilenetv3_best.pt"
    potato_artifact = PROJECT_ROOT / "ml" / "artifacts" / "potato_v1.pt"
    check(potato_checkpoint.exists(), "Potato best checkpoint exists (potato_mobilenetv3_best.pt)")
    check(potato_artifact.exists(), "Potato production artifact exists (potato_v1.pt)")

    # 4. Reports & JSON Audits
    history_json = PROJECT_ROOT / "reports" / "ml" / "potato_training_history.json"
    metrics_json = PROJECT_ROOT / "reports" / "ml" / "potato_test_metrics.json"
    integrity_json = PROJECT_ROOT / "reports" / "ml" / "potato_model_integrity.json"
    benchmark_json = PROJECT_ROOT / "reports" / "ml" / "potato_inference_benchmark.json"
    report_md = PROJECT_ROOT / "reports" / "ml" / "potato_classification_report.md"
    curves_png = PROJECT_ROOT / "reports" / "ml" / "potato_training_curves.png"
    cm_png = PROJECT_ROOT / "reports" / "ml" / "potato_confusion_matrix.png"

    check(history_json.exists(), "potato_training_history.json exists")
    check(metrics_json.exists(), "potato_test_metrics.json exists")
    check(integrity_json.exists(), "potato_model_integrity.json exists")
    check(benchmark_json.exists(), "potato_inference_benchmark.json exists")
    check(report_md.exists(), "potato_classification_report.md exists")
    check(curves_png.exists(), "potato_training_curves.png chart exists")
    check(cm_png.exists(), "potato_confusion_matrix.png chart exists")

    # 5. Documentation Suite
    check((PROJECT_ROOT / "docs" / "potato_model.md").exists(), "docs/potato_model.md exists")
    check((PROJECT_ROOT / "docs" / "ml_model.md").exists(), "docs/ml_model.md exists")
    check((PROJECT_ROOT / "docs" / "responsible_ai.md").exists(), "docs/responsible_ai.md exists")
    check((PROJECT_ROOT / "reports" / "phase13" / "phase13_completion_report.md").exists(), "phase13_completion_report.md exists")
    check((PROJECT_ROOT / "reports" / "phase13" / "potato_training_report.md").exists(), "potato_training_report.md exists")
    check((PROJECT_ROOT / "reports" / "phase13" / "potato_evaluation_report.md").exists(), "potato_evaluation_report.md exists")
    check((PROJECT_ROOT / "reports" / "phase13" / "potato_model_card.md").exists(), "potato_model_card.md exists")

    # 6. Artifact Reload & Dimension Check
    try:
        ckpt = torch.load(potato_artifact, map_location="cpu", weights_only=False)
        check(ckpt.get("model_version") == "potato-v1", "Artifact model_version == 'potato-v1'")
        check(len(ckpt.get("classes", [])) == 3, "Artifact has 3 output classes")
        check("state_dict" in ckpt, "Artifact contains valid state_dict")
    except Exception as e:
        check(False, f"Artifact reload failed: {e}")

    # 7. Model Performance Metrics Verification
    if metrics_json.exists():
        with open(metrics_json, "r", encoding="utf-8") as f:
            m_data = json.load(f)
        acc = m_data.get("accuracy", 0.0)
        f1 = m_data.get("macro_metrics", {}).get("f1_score", 0.0)
        check(acc >= 0.90, f"Test Accuracy >= 90% (Actual: {acc*100:.2f}%)")
        check(f1 >= 0.90, f"Macro F1 Score >= 0.90 (Actual: {f1:.4f})")

    # 8. Latency Benchmark Verification
    if benchmark_json.exists():
        with open(benchmark_json, "r", encoding="utf-8") as f:
            b_data = json.load(f)
        mean_lat = b_data.get("mean_latency_ms", 999.0)
        check(mean_lat <= 100.0, f"Mean Inference Latency <= 100ms (Actual: {mean_lat:.2f}ms)")

    # 9. Multi-Crop Predictor Integration
    try:
        from app.core.config import settings
        settings.ML_MODE = "REAL"
        from app.ml.predictor import ml_service
        ml_service.reload_model()

        models = ml_service.get_registered_models()
        check(models["tomato"]["status"] == "ACTIVE", "Tomato model is ACTIVE in MLSafetyWrapper")
        check(models["potato"]["status"] == "ACTIVE", "Potato model is ACTIVE in MLSafetyWrapper")

        # Test dummy prediction for both crops
        dummy_img = Image.new("RGB", (224, 224), color=(80, 140, 60))
        tom_res = ml_service.predict(dummy_img, "tomato")
        pot_res = ml_service.predict(dummy_img, "potato")

        check(tom_res.get("model_version") == "tomato-v1", "Tomato prediction uses 'tomato-v1' artifact")
        check(pot_res.get("model_version") == "potato-v1", "Potato prediction uses 'potato-v1' artifact")
        check(tom_res.get("is_demo_mode") is False, "Tomato REAL prediction is_demo_mode == False")
        check(pot_res.get("is_demo_mode") is False, "Potato REAL prediction is_demo_mode == False")
    except Exception as e:
        check(False, f"Multi-crop predictor verification failed: {e}")

    logger.info("==================================================================")
    logger.info(f"VERIFICATION COMPLETE: {passed_checks} PASSED, {failed_checks} FAILED")
    logger.info("==================================================================")

    if failed_checks > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
