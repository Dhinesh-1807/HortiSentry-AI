import os
import sys
import time
import json
import hashlib
import logging
from pathlib import Path
import numpy as np
import torch
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.model import PotatoMobileNetV3
from ml.potato_dataset import PotatoDataset, POTATO_CLASSES, create_potato_dataloaders
from ml.checkpoint import load_checkpoint
from ml.transforms import get_eval_transforms

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("EvaluatePotato")

def get_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def compute_metrics(y_true, y_pred, num_classes=3):
    total = len(y_true)
    correct = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp)
    acc = correct / total if total > 0 else 0.0

    cm = np.zeros((num_classes, num_classes), dtype=int)
    for yt, yp in zip(y_true, y_pred):
        cm[yt][yp] += 1

    per_class_p = []
    per_class_r = []
    per_class_f1 = []
    supports = []

    for c in range(num_classes):
        tp = cm[c][c]
        fp = sum(cm[r][c] for r in range(num_classes) if r != c)
        fn = sum(cm[c][col] for col in range(num_classes) if col != c)
        sup = sum(cm[c][col] for col in range(num_classes))

        p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * p * r) / (p + r) if (p + r) > 0 else 0.0

        per_class_p.append(p)
        per_class_r.append(r)
        per_class_f1.append(f1)
        supports.append(sup)

    macro_p = float(np.mean(per_class_p))
    macro_r = float(np.mean(per_class_r))
    macro_f1 = float(np.mean(per_class_f1))

    weighted_p = sum(p * s for p, s in zip(per_class_p, supports)) / total if total > 0 else 0.0
    weighted_r = sum(r * s for r, s in zip(per_class_r, supports)) / total if total > 0 else 0.0
    weighted_f1 = sum(f1 * s for f1, s in zip(per_class_f1, supports)) / total if total > 0 else 0.0

    return {
        "accuracy": acc,
        "macro_precision": macro_p,
        "macro_recall": macro_r,
        "macro_f1": macro_f1,
        "weighted_precision": weighted_p,
        "weighted_recall": weighted_r,
        "weighted_f1": weighted_f1,
        "per_class_p": per_class_p,
        "per_class_r": per_class_r,
        "per_class_f1": per_class_f1,
        "supports": supports,
        "confusion_matrix": cm
    }

def main():
    logger.info("==================================================================")
    logger.info("HORTISENTRY PHASE 13: POTATO-V1 MODEL TEST EVALUATION & AUDIT")
    logger.info("==================================================================")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Evaluation compute device: {device}")

    artifact_path = PROJECT_ROOT / "ml" / "artifacts" / "potato_v1.pt"
    manifest_path = PROJECT_ROOT / "data" / "processed" / "potato_manifest.csv"
    reports_ml_dir = PROJECT_ROOT / "reports" / "ml"
    reports_ml_dir.mkdir(parents=True, exist_ok=True)

    if not artifact_path.exists():
        logger.error(f"Production artifact not found at {artifact_path}")
        sys.exit(1)

    # ------------------------------------------------------------------
    # 1. Reload Model & Verify Artifact Integrity
    # ------------------------------------------------------------------
    logger.info("Step 1: Auditing Artifact Integrity & File Signatures...")
    checkpoint = load_checkpoint(artifact_path, map_location="cpu")
    
    file_size_bytes = artifact_path.stat().st_size
    file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
    sha256_checksum = get_sha256(artifact_path)

    classes = checkpoint.get("classes", POTATO_CLASSES)
    model_version = checkpoint.get("model_version", "potato-v1")
    image_size = checkpoint.get("image_size", 224)

    model = PotatoMobileNetV3(num_classes=len(classes), pretrained=False)
    model.load_state_dict(checkpoint["state_dict"])
    model.to(device)
    model.eval()

    # Dry-run forward pass to verify output shape
    dummy_input = torch.randn(1, 3, image_size, image_size).to(device)
    with torch.no_grad():
        dummy_output = model(dummy_input)
    
    assert dummy_output.shape == (1, 3), f"Expected shape (1, 3), got {dummy_output.shape}"
    logger.info(f"✅ Verified model artifact: {model_version}, {len(classes)} output classes, SHA-256: {sha256_checksum[:12]}...")

    integrity_report = {
        "artifact_path": str(artifact_path.relative_to(PROJECT_ROOT)),
        "model_version": model_version,
        "architecture": checkpoint.get("architecture", "mobilenet_v3_small"),
        "dataset_version": "potato-v1.1-dataset",
        "num_classes": len(classes),
        "classes": classes,
        "class_to_idx": checkpoint.get("class_to_idx", {}),
        "output_dimension": dummy_output.shape[1],
        "image_size": image_size,
        "file_size_bytes": file_size_bytes,
        "file_size_mb": file_size_mb,
        "sha256": sha256_checksum,
        "reload_test": "PASSED",
        "normalization": {
            "mean": checkpoint.get("mean", [0.485, 0.456, 0.406]),
            "std": checkpoint.get("std", [0.229, 0.224, 0.225])
        }
    }
    with open(reports_ml_dir / "potato_model_integrity.json", "w", encoding="utf-8") as f:
        json.dump(integrity_report, f, indent=2)

    # ------------------------------------------------------------------
    # 2. Test Set Evaluation (Untouched Test Set Images)
    # ------------------------------------------------------------------
    logger.info("Step 2: Evaluating Model ONCE on Untouched Test Set...")
    eval_tf = get_eval_transforms(image_size=image_size)
    test_ds = PotatoDataset(manifest_path, split="test", transform=eval_tf, exclude_reject=False)

    y_true = []
    y_pred = []
    y_probs = []
    sources = []
    environments = []

    start_eval = time.time()
    with torch.no_grad():
        for i in range(len(test_ds)):
            file_path, label_idx, source, env = test_ds.samples[i]
            img_tensor, label = test_ds[i]
            img_tensor = img_tensor.unsqueeze(0).to(device)

            output = model(img_tensor)
            prob = torch.softmax(output, dim=1).squeeze(0)

            pred_class_idx = torch.argmax(prob).item()

            y_true.append(label)
            y_pred.append(pred_class_idx)
            y_probs.append(prob.cpu().numpy().tolist())
            sources.append(source)
            environments.append(env)

    total_eval_time = time.time() - start_eval

    # Metrics Calculation
    res = compute_metrics(y_true, y_pred, num_classes=3)
    acc = res["accuracy"]
    macro_p = res["macro_precision"]
    macro_r = res["macro_recall"]
    macro_f1 = res["macro_f1"]
    weighted_p = res["weighted_precision"]
    weighted_r = res["weighted_recall"]
    weighted_f1 = res["weighted_f1"]
    cm = res["confusion_matrix"]

    per_class_metrics = {}
    for idx, cls_name in enumerate(POTATO_CLASSES):
        per_class_metrics[cls_name] = {
            "precision": round(float(res["per_class_p"][idx]), 4),
            "recall": round(float(res["per_class_r"][idx]), 4),
            "f1_score": round(float(res["per_class_f1"][idx]), 4),
            "support": int(res["supports"][idx])
        }

    test_metrics = {
        "model_version": model_version,
        "dataset_version": "potato-v1.1-dataset",
        "test_samples": len(y_true),
        "accuracy": round(float(acc), 4),
        "accuracy_percentage": round(float(acc) * 100.0, 2),
        "macro_metrics": {
            "precision": round(float(macro_p), 4),
            "recall": round(float(macro_r), 4),
            "f1_score": round(float(macro_f1), 4)
        },
        "weighted_metrics": {
            "precision": round(float(weighted_p), 4),
            "recall": round(float(weighted_r), 4),
            "f1_score": round(float(weighted_f1), 4)
        },
        "per_class": per_class_metrics,
        "confusion_matrix": cm.tolist()
    }

    with open(reports_ml_dir / "potato_test_metrics.json", "w", encoding="utf-8") as f:
        json.dump(test_metrics, f, indent=2)

    logger.info(f"Test Accuracy: {acc*100:.2f}% | Macro F1: {macro_f1:.4f} | Weighted F1: {weighted_f1:.4f}")

    # ------------------------------------------------------------------
    # 3. Controlled vs Field Subset Evaluation
    # ------------------------------------------------------------------
    logger.info("Step 3: Auditing Controlled vs Field Performance...")
    field_indices = [i for i, env in enumerate(environments) if env == "FIELD"]
    controlled_indices = [i for i, env in enumerate(environments) if env == "CONTROLLED"]

    field_eval = {}
    if field_indices:
        field_y_true = [y_true[i] for i in field_indices]
        field_y_pred = [y_pred[i] for i in field_indices]
        field_res = compute_metrics(field_y_true, field_y_pred, num_classes=3)
        field_eval = {
            "samples": len(field_indices),
            "accuracy": round(float(field_res["accuracy"]), 4),
            "accuracy_percentage": round(float(field_res["accuracy"]) * 100.0, 2),
            "macro_f1": round(float(field_res["macro_f1"]), 4),
            "status": "IN_SITU_FIELD_EVALUATED"
        }
    else:
        field_eval = {"samples": 0, "status": "Independent field validation not established."}

    ctrl_y_true = [y_true[i] for i in controlled_indices]
    ctrl_y_pred = [y_pred[i] for i in controlled_indices]
    ctrl_res = compute_metrics(ctrl_y_true, ctrl_y_pred, num_classes=3)

    controlled_eval = {
        "samples": len(controlled_indices),
        "accuracy": round(float(ctrl_res["accuracy"]), 4),
        "accuracy_percentage": round(float(ctrl_res["accuracy"]) * 100.0, 2),
        "macro_f1": round(float(ctrl_res["macro_f1"]), 4)
    }

    # ------------------------------------------------------------------
    # 4. Generate Classification Report & Confusion Matrix Analysis (.md)
    # ------------------------------------------------------------------
    report_md_path = reports_ml_dir / "potato_classification_report.md"
    with open(report_md_path, "w", encoding="utf-8") as f:
        f.write("# HortiSentry Potato-v1 Test Set Classification Report\n\n")
        f.write(f"**Model Version:** `{model_version}`  \n")
        f.write(f"**Dataset Version:** `potato-v1.1-dataset`  \n")
        f.write(f"**Test Set Size:** {len(y_true)} images  \n\n")

        f.write("## Overall Metrics Summary\n\n")
        f.write("| Metric | Score | Percentage |\n")
        f.write("| :--- | :---: | :---: |\n")
        f.write(f"| **Test Accuracy** | {acc:.4f} | **{acc*100:.2f}%** |\n")
        f.write(f"| **Macro Precision** | {macro_p:.4f} | {macro_p*100:.2f}% |\n")
        f.write(f"| **Macro Recall** | {macro_r:.4f} | {macro_r*100:.2f}% |\n")
        f.write(f"| **Macro F1 Score** | {macro_f1:.4f} | **{macro_f1*100:.2f}%** |\n")
        f.write(f"| **Weighted Precision** | {weighted_p:.4f} | {weighted_p*100:.2f}% |\n")
        f.write(f"| **Weighted Recall** | {weighted_r:.4f} | {weighted_r*100:.2f}% |\n")
        f.write(f"| **Weighted F1 Score** | {weighted_f1:.4f} | {weighted_f1*100:.2f}% |\n\n")

        f.write("## Per-Class Performance Breakdown\n\n")
        f.write("| Canonical Class | Support | Precision | Recall | F1-Score |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: |\n")
        for cls_name in POTATO_CLASSES:
            m = per_class_metrics[cls_name]
            f.write(f"| `{cls_name}` | {m['support']} | {m['precision']:.4f} | {m['recall']:.4f} | **{m['f1_score']:.4f}** |\n")

        f.write("\n## Environment Subset Performance (Controlled vs Field)\n\n")
        f.write("| Environment Split | Support | Accuracy | Macro F1 | Status |\n")
        f.write("| :--- | :---: | :---: | :---: | :--- |\n")
        f.write(f"| `CONTROLLED` (Laboratory) | {controlled_eval['samples']} | {controlled_eval['accuracy_percentage']}% | {controlled_eval['macro_f1']:.4f} | Baseline Benchmark |\n")
        if field_indices:
            f.write(f"| `FIELD` (In-Situ) | {field_eval['samples']} | {field_eval['accuracy_percentage']}% | {field_eval['macro_f1']:.4f} | In-situ Field Subset |\n\n")
        else:
            f.write(f"| `FIELD` (In-Situ) | 0 | N/A | N/A | Independent field validation not established. |\n\n")

        f.write("## Confusion Matrix & Error Analysis\n\n")
        f.write("| True \\ Predicted | Potato_Healthy | Potato_Early_Blight | Potato_Late_Blight |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        for idx, cls_name in enumerate(POTATO_CLASSES):
            row_str = " | ".join(str(cm[idx][j]) for j in range(3))
            f.write(f"| `{cls_name}` | {row_str} |\n")

        f.write("\n### Observed Confusion Matrix Observations:\n")
        f.write(f"- **Healthy $\\rightarrow$ Early Blight:** {cm[0][1]} misclassifications.\n")
        f.write(f"- **Healthy $\\rightarrow$ Late Blight:** {cm[0][2]} misclassifications.\n")
        f.write(f"- **Early Blight $\\rightarrow$ Late Blight:** {cm[1][2]} misclassifications.\n")
        f.write(f"- **Late Blight $\\rightarrow$ Early Blight:** {cm[2][1]} misclassifications.\n\n")

    logger.info(f"Saved classification report to {report_md_path}")

    # Render Confusion Matrix Chart
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(6, 5))
        cax = ax.matshow(cm, cmap="Blues")
        fig.colorbar(cax)

        labels = ["Healthy", "Early Blight", "Late Blight"]
        ax.set_xticks([0, 1, 2])
        ax.set_yticks([0, 1, 2])
        ax.set_xticklabels(labels)
        ax.set_yticklabels(labels)

        for i in range(3):
            for j in range(3):
                ax.text(j, i, str(cm[i, j]), ha="center", va="center", color="black" if cm[i, j] < (cm.max()/2) else "white", fontsize=12, fontweight="bold")

        plt.title("Potato-v1 Confusion Matrix (Test Set)", fontsize=12, fontweight="bold", pad=20)
        plt.xlabel("Predicted Label")
        plt.ylabel("True Label")
        plt.tight_layout()
        cm_chart_path = reports_ml_dir / "potato_confusion_matrix.png"
        plt.savefig(cm_chart_path, dpi=150)
        plt.close()
        logger.info(f"Saved confusion matrix chart to {cm_chart_path}")
    except Exception as e:
        logger.warning(f"Could not render confusion matrix chart: {e}")

    # ------------------------------------------------------------------
    # 5. Latency Benchmark Execution (100 Test Samples)
    # ------------------------------------------------------------------
    logger.info("Step 5: Executing Inference Latency Benchmark (100 passes)...")
    benchmark_samples = min(100, len(test_ds))
    latencies_ms = []

    model.eval()
    with torch.no_grad():
        # Warmup
        dummy = torch.randn(1, 3, image_size, image_size).to(device)
        for _ in range(10):
            _ = model(dummy)

        for i in range(benchmark_samples):
            img_tensor, _ = test_ds[i]
            img_tensor = img_tensor.unsqueeze(0).to(device)

            t0 = time.time()
            _ = model(img_tensor)
            elapsed_ms = (time.time() - t0) * 1000.0
            latencies_ms.append(elapsed_ms)

    mean_lat = float(np.mean(latencies_ms))
    med_lat = float(np.median(latencies_ms))
    min_lat = float(np.min(latencies_ms))
    max_lat = float(np.max(latencies_ms))

    benchmark_report = {
        "model_version": model_version,
        "device": str(device),
        "benchmark_samples": benchmark_samples,
        "mean_latency_ms": round(mean_lat, 2),
        "median_latency_ms": round(med_lat, 2),
        "min_latency_ms": round(min_lat, 2),
        "max_latency_ms": round(max_lat, 2),
        "throughput_images_per_sec": round(1000.0 / mean_lat, 2) if mean_lat > 0 else 0.0
    }

    with open(reports_ml_dir / "potato_inference_benchmark.json", "w", encoding="utf-8") as f:
        json.dump(benchmark_report, f, indent=2)

    logger.info(f"Inference Latency: Mean {mean_lat:.2f}ms | Median {med_lat:.2f}ms | Throughput {1000.0/mean_lat:.1f} img/s")
    logger.info("==================================================================")
    logger.info("POTATO-V1 EVALUATION & AUDIT COMPLETE.")
    logger.info("==================================================================")

if __name__ == "__main__":
    main()
