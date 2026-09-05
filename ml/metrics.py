import numpy as np
from typing import List, Dict, Any, Tuple

def calculate_confusion_matrix(y_true: List[int], y_pred: List[int], num_classes: int = 4) -> np.ndarray:
    """Calculate raw confusion matrix of shape (num_classes, num_classes)."""
    cm = np.zeros((num_classes, num_classes), dtype=np.int64)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1
    return cm

def calculate_classification_metrics(y_true: List[int], y_pred: List[int], class_names: List[str]) -> Dict[str, Any]:
    """
    Calculate comprehensive evaluation metrics from ground truth and predictions:
    - Overall accuracy
    - Per-class precision, recall, F1 score, support
    - Macro precision, recall, F1
    - Weighted precision, recall, F1
    - Raw & normalized confusion matrices
    """
    num_classes = len(class_names)
    cm = calculate_confusion_matrix(y_true, y_pred, num_classes)
    total_samples = len(y_true)

    if total_samples == 0:
        return {"accuracy": 0.0, "per_class": {}, "macro": {}, "weighted": {}}

    correct = np.trace(cm)
    accuracy = float(correct / total_samples)

    per_class = {}
    supports = np.sum(cm, axis=1) # Row sums (true counts)
    pred_counts = np.sum(cm, axis=0) # Col sums (pred counts)

    precisions = []
    recalls = []
    f1s = []

    for i, cls_name in enumerate(class_names):
        tp = cm[i, i]
        fp = pred_counts[i] - tp
        fn = supports[i] - tp
        support = int(supports[i])

        precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        f1 = float(2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        precisions.append(precision)
        recalls.append(recall)
        f1s.append(f1)

        per_class[cls_name] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "support": support
        }

    # Macro averages (unweighted mean across classes)
    macro_precision = float(np.mean(precisions))
    macro_recall = float(np.mean(recalls))
    macro_f1 = float(np.mean(f1s))

    # Weighted averages (weighted by support of each class)
    weights = supports / total_samples if total_samples > 0 else np.zeros(num_classes)
    weighted_precision = float(np.sum(np.array(precisions) * weights))
    weighted_recall = float(np.sum(np.array(recalls) * weights))
    weighted_f1 = float(np.sum(np.array(f1s) * weights))

    return {
        "accuracy": round(accuracy, 4),
        "total_samples": total_samples,
        "per_class": per_class,
        "macro": {
            "precision": round(macro_precision, 4),
            "recall": round(macro_recall, 4),
            "f1_score": round(macro_f1, 4)
        },
        "weighted": {
            "precision": round(weighted_precision, 4),
            "recall": round(weighted_recall, 4),
            "f1_score": round(weighted_f1, 4)
        },
        "confusion_matrix": cm.tolist()
    }
