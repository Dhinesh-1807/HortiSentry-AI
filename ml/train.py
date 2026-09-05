import os
import sys
import time
import json
import logging
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import ReduceLROnPlateau
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.config import MLConfig
from ml.utils import set_seed, get_device
from ml.transforms import get_train_transforms, get_eval_transforms
from ml.dataset import create_dataloaders
from ml.model import TomatoMobileNetV3
from ml.checkpoint import save_checkpoint, export_production_artifact
from ml.metrics import calculate_classification_metrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ml.train")

def compute_class_weights(train_class_counts: dict, classes: list, device: torch.device) -> torch.Tensor:
    """
    Calculate class weights strictly from the training distribution only.
    Formula: weight_c = N_total / (num_classes * N_c)
    """
    total_samples = sum(train_class_counts.values())
    num_classes = len(classes)
    weights = []
    
    logger.info("Computing CLASS_WEIGHTED_LOSS parameters from training set:")
    for cls_name in classes:
        count = train_class_counts.get(cls_name, 0)
        if count > 0:
            w = total_samples / (num_classes * count)
        else:
            w = 1.0
        weights.append(w)
        logger.info(f"  - {cls_name}: Count = {count}, Computed Weight = {w:.4f}")

    weights_tensor = torch.tensor(weights, dtype=torch.float32).to(device)
    return weights_tensor

def plot_training_curves(history: dict, output_path: Path):
    """Plot and save loss & accuracy training curves to PNG."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    epochs = range(1, len(history["train_loss"]) + 1)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Loss subplot
    ax1.plot(epochs, history["train_loss"], "b-o", label="Training Loss", linewidth=2)
    ax1.plot(epochs, history["val_loss"], "r-s", label="Validation Loss", linewidth=2)
    ax1.set_title("Training & Validation Loss", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("CrossEntropy Loss")
    ax1.grid(True, linestyle="--", alpha=0.6)
    ax1.legend()

    # Accuracy subplot
    ax2.plot(epochs, history["train_acc"], "b-o", label="Training Accuracy", linewidth=2)
    ax2.plot(epochs, history["val_acc"], "r-s", label="Validation Accuracy", linewidth=2)
    ax2.set_title("Training & Validation Accuracy (%)", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Accuracy (%)")
    ax2.grid(True, linestyle="--", alpha=0.6)
    ax2.legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Saved training curves chart to {output_path}")

def run_training():
    logger.info("--- HortiSentry Real PyTorch Model Training ---")

    cfg = MLConfig()
    set_seed(cfg.random_seed)
    device = get_device()

    data_root = PROJECT_ROOT / "data"
    manifest_path = data_root / "processed" / "manifest.csv"

    # 1. Transforms & DataLoaders
    train_transform = get_train_transforms(cfg.image_size)
    eval_transform = get_eval_transforms(cfg.image_size)

    train_loader, val_loader, test_loader, train_counts = create_dataloaders(
        data_root=data_root,
        classes=cfg.classes,
        train_transform=train_transform,
        eval_transform=eval_transform,
        batch_size=cfg.batch_size,
        manifest_path=manifest_path
    )

    logger.info(f"Training dataset size: {len(train_loader.dataset)} samples (1 REJECT image excluded).")
    logger.info(f"Validation dataset size: {len(val_loader.dataset)} samples.")
    logger.info(f"Test dataset size: {len(test_loader.dataset)} samples (Untouched during training).")

    # 2. Compute Class Weighted Loss
    class_weights = compute_class_weights(train_counts, cfg.classes, device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)

    # 3. Initialize Model
    model = TomatoMobileNetV3(
        num_classes=cfg.num_classes,
        pretrained=cfg.pretrained,
        freeze_features=False
    ).to(device)

    # 4. Optimizer & LR Scheduler
    optimizer = optim.AdamW(model.parameters(), lr=cfg.learning_rate, weight_decay=cfg.weight_decay)
    scheduler = ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=2)

    # 5. Training Loop Setup
    checkpoint_dir = PROJECT_ROOT / "ml" / "checkpoints"
    best_model_path = checkpoint_dir / "tomato_mobilenetv3_best.pt"
    
    best_val_loss = float("inf")
    best_val_acc = 0.0
    best_epoch = 0
    patience_counter = 0

    history = {
        "epochs": [],
        "train_loss": [],
        "train_acc": [],
        "val_loss": [],
        "val_acc": [],
        "learning_rate": [],
        "epoch_duration_sec": []
    }

    start_training_time = time.time()

    # 6. Epoch Training & Validation Execution
    for epoch in range(1, cfg.epochs + 1):
        epoch_start = time.time()
        
        # --- Training Phase ---
        model.train()
        running_loss = 0.0
        correct_train = 0
        total_train = 0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, predicted = torch.max(outputs, 1)
            total_train += labels.size(0)
            correct_train += (predicted == labels).sum().item()

        epoch_train_loss = running_loss / total_train
        epoch_train_acc = (correct_train / total_train) * 100.0

        # --- Validation Phase ---
        model.eval()
        running_val_loss = 0.0
        correct_val = 0
        total_val = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)

                running_val_loss += loss.item() * images.size(0)
                _, predicted = torch.max(outputs, 1)
                total_val += labels.size(0)
                correct_val += (predicted == labels).sum().item()

        epoch_val_loss = running_val_loss / total_val
        epoch_val_acc = (correct_val / total_val) * 100.0
        epoch_duration = round(time.time() - epoch_start, 2)

        current_lr = optimizer.param_groups[0]["lr"]
        scheduler.step(epoch_val_loss)

        # Log epoch summary
        logger.info(
            f"Epoch [{epoch}/{cfg.epochs}] - "
            f"Train Loss: {epoch_train_loss:.4f}, Train Acc: {epoch_train_acc:.2f}% | "
            f"Val Loss: {epoch_val_loss:.4f}, Val Acc: {epoch_val_acc:.2f}% | "
            f"LR: {current_lr:.6f} ({epoch_duration}s)"
        )

        # Record history
        history["epochs"].append(epoch)
        history["train_loss"].append(round(epoch_train_loss, 4))
        history["train_acc"].append(round(epoch_train_acc, 2))
        history["val_loss"].append(round(epoch_val_loss, 4))
        history["val_acc"].append(round(epoch_val_acc, 2))
        history["learning_rate"].append(current_lr)
        history["epoch_duration_sec"].append(epoch_duration)

        # Checkpointing & Early Stopping Logic
        if epoch_val_loss < best_val_loss:
            best_val_loss = epoch_val_loss
            best_val_acc = epoch_val_acc
            best_epoch = epoch
            patience_counter = 0

            save_checkpoint(
                filepath=best_model_path,
                model=model,
                epoch=epoch,
                optimizer=optimizer,
                val_loss=epoch_val_loss,
                val_acc=epoch_val_acc,
                classes=cfg.classes,
                config_dict=cfg._data,
                model_version="tomato-v1"
            )
        else:
            patience_counter += 1
            logger.info(f"Validation loss did not improve. Early stopping patience: {patience_counter}/{cfg.early_stopping_patience}")
            if cfg.early_stopping_enabled and patience_counter >= cfg.early_stopping_patience:
                logger.info(f"Early stopping triggered at Epoch {epoch}!")
                break

    total_training_duration = round(time.time() - start_training_time, 2)
    logger.info(f"Training finished in {total_training_duration}s. Best Epoch: {best_epoch} (Val Loss: {best_val_loss:.4f}, Val Acc: {best_val_acc:.2f}%)")

    # 7. Save Reports & Export Artifacts
    reports_dir = PROJECT_ROOT / "reports" / "ml"
    reports_dir.mkdir(parents=True, exist_ok=True)

    with open(reports_dir / "training_history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    plot_training_curves(history, reports_dir / "training_curves.png")

    # Load best checkpoint to export production artifact
    best_ckpt = torch.load(best_model_path, weights_only=False)
    model.load_state_dict(best_ckpt["state_dict"])
    
    artifact_path = PROJECT_ROOT / "ml" / "artifacts" / "tomato_v1.pt"
    export_production_artifact(
        filepath=artifact_path,
        model=model,
        classes=cfg.classes,
        val_metrics={
            "best_epoch": best_epoch,
            "best_val_loss": round(best_val_loss, 4),
            "best_val_acc": round(best_val_acc, 2),
            "total_training_duration_sec": total_training_duration
        },
        model_version="tomato-v1"
    )

    logger.info("--- Training Completed Successfully ---")
    return history

if __name__ == "__main__":
    run_training()
