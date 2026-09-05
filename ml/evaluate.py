import os
import sys
import time
import json
import logging
from pathlib import Path
import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.config import MLConfig
from ml.utils import get_device
from ml.transforms import get_eval_transforms
from ml.dataset import TomatoDataset
from ml.model import TomatoMobileNetV3
from ml.checkpoint import load_checkpoint
from ml.metrics import calculate_classification_metrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ml.evaluate")

def plot_confusion_matrix(cm: np.ndarray, class_names: list, output_path: Path):
    """Plot raw and normalized confusion matrices side by side to PNG."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # 1. Raw Counts Confusion Matrix
    im1 = ax1.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    ax1.set_title("Raw Counts Confusion Matrix", fontsize=12, fontweight="bold")
    fig.colorbar(im1, ax=ax1)
    tick_marks = np.arange(len(class_names))
    ax1.set_xticks(tick_marks)
    ax1.set_xticklabels(class_names, rotation=45, ha="right")
    ax1.set_yticks(tick_marks)
    ax1.set_yticklabels(class_names)

    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax1.text(j, i, format(cm[i, j], "d"),
                     ha="center", va="center",
                     color="white" if cm[i, j] > thresh else "black", fontweight="bold")

    ax1.set_ylabel("True Label", fontweight="bold")
    ax1.set_xlabel("Predicted Label", fontweight="bold")

    # 2. Normalized Percentage Confusion Matrix
    cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
    im2 = ax2.imshow(cm_norm, interpolation="nearest", cmap=plt.cm.Greens)
    ax2.set_title("Normalized Confusion Matrix (%)", fontsize=12, fontweight="bold")
    fig.colorbar(im2, ax=ax2)
    ax2.set_xticks(tick_marks)
    ax2.set_xticklabels(class_names, rotation=45, ha="right")
    ax2.set_yticks(tick_marks)
    ax2.set_yticklabels(class_names)

    for i in range(cm_norm.shape[0]):
        for j in range(cm_norm.shape[1]):
            ax2.text(j, i, f"{cm_norm[i, j]*100:.1f}%",
                     ha="center", va="center",
                     color="white" if cm_norm[i, j] > 0.5 else "black", fontweight="bold")

    ax2.set_ylabel("True Label", fontweight="bold")
    ax2.set_xlabel("Predicted Label", fontweight="bold")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Saved confusion matrix chart to {output_path}")

def run_evaluation(artifact_path: Path = None):
    logger.info("--- HortiSentry Real Model Evaluation on Untouched Test Set ---")

    cfg = MLConfig()
    device = get_device()

    if artifact_path is None:
        artifact_path = PROJECT_ROOT / "ml" / "artifacts" / "tomato_v1.pt"
        if not artifact_path.exists():
            artifact_path = PROJECT_ROOT / "ml" / "checkpoints" / "tomato_mobilenetv3_best.pt"

    logger.info(f"Loading model checkpoint from {artifact_path}")
    checkpoint = load_checkpoint(artifact_path, map_location="cpu")

    classes = checkpoint.get("classes", cfg.classes)
    num_classes = len(classes)

    # Reconstruct Model
    model = TomatoMobileNetV3(num_classes=num_classes, pretrained=False).to(device)
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()

    # Load Untouched Test Dataset
    eval_transform = get_eval_transforms(cfg.image_size)
    test_dir = PROJECT_ROOT / "data" / "test"
    test_ds = TomatoDataset(test_dir, classes=classes, transform=eval_transform, exclude_reject=False)
    test_loader = torch.utils.data.DataLoader(test_ds, batch_size=1, shuffle=False)

    logger.info(f"Evaluating {len(test_ds)} untouched test samples...")

    y_true = []
    y_pred = []
    inference_times_ms = []

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            
            start_t = time.time()
            outputs = model(images)
            probs = torch.softmax(outputs, dim=1)
            _, preds = torch.max(outputs, 1)
            elapsed_ms = (time.time() - start_t) * 1000.0

            inference_times_ms.append(elapsed_ms)
            y_true.append(labels.item())
            y_pred.append(preds.item())

    # Compute Classification Metrics
    metrics = calculate_classification_metrics(y_true, y_pred, classes)
    
    avg_inference_ms = round(float(np.mean(inference_times_ms)), 2)
    median_inference_ms = round(float(np.median(inference_times_ms)), 2)
    
    timing_info = {
        "device": str(device),
        "total_test_samples": len(test_ds),
        "avg_inference_time_ms": avg_inference_ms,
        "median_inference_time_ms": median_inference_ms,
        "throughput_images_per_sec": round(1000.0 / avg_inference_ms, 2) if avg_inference_ms > 0 else 0
    }
    metrics["inference_timing"] = timing_info

    logger.info("=== UNTOUCHED TEST SET PERFORMANCE METRICS ===")
    logger.info(f"Test Accuracy: {metrics['accuracy']*100:.2f}%")
    logger.info(f"Macro F1 Score: {metrics['macro']['f1_score']:.4f}")
    logger.info(f"Weighted F1 Score: {metrics['weighted']['f1_score']:.4f}")
    logger.info(f"Average Inference Speed: {avg_inference_ms} ms / image on {device}")

    # Output JSON Metrics Reports
    reports_dir = PROJECT_ROOT / "reports" / "ml"
    reports_dir.mkdir(parents=True, exist_ok=True)

    with open(reports_dir / "test_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    with open(reports_dir / "classification_report.json", "w", encoding="utf-8") as f:
        json.dump({
            "accuracy": metrics["accuracy"],
            "macro_avg": metrics["macro"],
            "weighted_avg": metrics["weighted"],
            "per_class": metrics["per_class"]
        }, f, indent=2)

    # Plot Confusion Matrix
    cm = np.array(metrics["confusion_matrix"])
    plot_confusion_matrix(cm, classes, reports_dir / "confusion_matrix.png")

    logger.info("--- Evaluation Completed Successfully ---")
    return metrics

if __name__ == "__main__":
    run_evaluation()
