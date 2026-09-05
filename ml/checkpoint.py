import torch
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

def save_checkpoint(
    filepath: Path,
    model: torch.nn.Module,
    epoch: int,
    optimizer: torch.optim.Optimizer,
    val_loss: float,
    val_acc: float,
    classes: List[str],
    config_dict: Dict[str, Any],
    model_version: str = "tomato-v1"
) -> None:
    """Save training checkpoint to disk."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    state = {
        "model_version": model_version,
        "epoch": epoch,
        "state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict() if optimizer else None,
        "val_loss": val_loss,
        "val_acc": val_acc,
        "classes": classes,
        "class_to_idx": {cls_name: i for i, cls_name in enumerate(classes)},
        "config": config_dict,
        "image_size": config_dict.get("image_size", 224),
        "mean": [0.485, 0.456, 0.406],
        "std": [0.229, 0.224, 0.225]
    }
    torch.save(state, filepath)
    logger.info(f"Saved checkpoint to {filepath} (Epoch {epoch}, Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%)")

def export_production_artifact(
    filepath: Path,
    model: torch.nn.Module,
    classes: List[str],
    val_metrics: Dict[str, float],
    test_metrics: Optional[Dict[str, float]] = None,
    model_version: str = "tomato-v1"
) -> None:
    """Export lightweight production model artifact for inference backend."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    artifact = {
        "model_version": model_version,
        "architecture": "mobilenet_v3_small",
        "state_dict": model.state_dict(),
        "classes": classes,
        "class_to_idx": {cls_name: i for i, cls_name in enumerate(classes)},
        "image_size": 224,
        "mean": [0.485, 0.456, 0.406],
        "std": [0.229, 0.224, 0.225],
        "val_metrics": val_metrics,
        "test_metrics": test_metrics or {}
    }
    torch.save(artifact, filepath)
    logger.info(f"Exported production artifact to {filepath} (Version: {model_version})")

def load_checkpoint(filepath: Path, map_location: str = "cpu") -> Dict[str, Any]:
    """Load model checkpoint or artifact dictionary from disk."""
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Checkpoint file not found: {filepath}")
    return torch.load(filepath, map_location=map_location, weights_only=False)
