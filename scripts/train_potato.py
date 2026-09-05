import os
import sys
import time
import json
import random
import logging
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.model import PotatoMobileNetV3
from ml.potato_dataset import create_potato_dataloaders, POTATO_CLASSES
from ml.checkpoint import save_checkpoint, export_production_artifact

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TrainPotato")

def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def main():
    logger.info("==================================================================")
    logger.info("HORTISENTRY PHASE 13: POTATO-V1 MODEL TRAINING (MobileNetV3 Small)")
    logger.info("==================================================================")

    set_seed(42)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using compute device: {device}")

    # Directories
    checkpoint_dir = PROJECT_ROOT / "ml" / "checkpoints"
    artifact_dir = PROJECT_ROOT / "ml" / "artifacts"
    reports_ml_dir = PROJECT_ROOT / "reports" / "ml"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    reports_ml_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Data
    batch_size = 32
    epochs = 15
    lr = 0.001
    weight_decay = 0.0001
    manifest_path = PROJECT_ROOT / "data" / "processed" / "potato_manifest.csv"

    train_loader, val_loader, test_loader, train_class_counts, class_weights = create_potato_dataloaders(
        manifest_path=manifest_path,
        batch_size=batch_size,
        image_size=224,
        num_workers=0
    )

    logger.info(f"Loaded Potato Datasets:")
    logger.info(f"  Train samples: {len(train_loader.dataset)}")
    logger.info(f"  Val samples:   {len(val_loader.dataset)}")
    logger.info(f"  Test samples:  {len(test_loader.dataset)}")
    logger.info(f"  Train class counts: {train_class_counts}")
    logger.info(f"  Train class weights: {class_weights.tolist()}")

    # 2. Model & Optimization
    model = PotatoMobileNetV3(num_classes=3, pretrained=True).to(device)
    class_weights_device = class_weights.to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights_device)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=2)

    # 3. Training Loop
    history = []
    best_val_loss = float("inf")
    best_val_acc = 0.0
    best_epoch = 0
    patience = 5
    patience_counter = 0

    best_checkpoint_path = checkpoint_dir / "potato_mobilenetv3_best.pt"
    production_artifact_path = artifact_dir / "potato_v1.pt"

    start_time = time.time()

    for epoch in range(1, epochs + 1):
        # Training Phase
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
            _, preds = torch.max(outputs, 1)
            correct_train += torch.sum(preds == labels.data).item()
            total_train += images.size(0)

        epoch_train_loss = running_loss / total_train
        epoch_train_acc = (correct_train / total_train) * 100.0

        # Validation Phase (Deterministic)
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
                _, preds = torch.max(outputs, 1)
                correct_val += torch.sum(preds == labels.data).item()
                total_val += images.size(0)

        epoch_val_loss = running_val_loss / total_val
        epoch_val_acc = (correct_val / total_val) * 100.0

        scheduler.step(epoch_val_loss)
        current_lr = optimizer.param_groups[0]["lr"]

        logger.info(
            f"Epoch {epoch:02d}/{epochs:02d} | "
            f"Train Loss: {epoch_train_loss:.4f} | Train Acc: {epoch_train_acc:.2f}% | "
            f"Val Loss: {epoch_val_loss:.4f} | Val Acc: {epoch_val_acc:.2f}% | LR: {current_lr:.6f}"
        )

        epoch_record = {
            "epoch": epoch,
            "train_loss": round(epoch_train_loss, 4),
            "train_accuracy": round(epoch_train_acc, 2),
            "val_loss": round(epoch_val_loss, 4),
            "val_accuracy": round(epoch_val_acc, 2),
            "lr": current_lr
        }
        history.append(epoch_record)

        # Early Stopping Check (Monitored ONLY on val_loss)
        if epoch_val_loss < best_val_loss:
            best_val_loss = epoch_val_loss
            best_val_acc = epoch_val_acc
            best_epoch = epoch
            patience_counter = 0

            # Save best checkpoint
            config_dict = {
                "crop": "potato",
                "dataset_version": "potato-v1.1-dataset",
                "classes": POTATO_CLASSES,
                "image_size": 224,
                "batch_size": batch_size,
                "learning_rate": lr,
                "weight_decay": weight_decay,
                "optimizer": "AdamW",
                "random_seed": 42,
                "device": str(device),
                "class_weights": class_weights.tolist()
            }
            save_checkpoint(
                filepath=best_checkpoint_path,
                model=model,
                epoch=epoch,
                optimizer=optimizer,
                val_loss=epoch_val_loss,
                val_acc=epoch_val_acc,
                classes=POTATO_CLASSES,
                config_dict=config_dict,
                model_version="potato-v1"
            )
        else:
            patience_counter += 1
            if patience_counter >= patience:
                logger.info(f"Early stopping triggered after {epoch} epochs (Patience = {patience}).")
                break

    total_training_time = time.time() - start_time
    logger.info("------------------------------------------------------------------")
    logger.info(f"TRAINING COMPLETE in {total_training_time:.2f} seconds ({total_training_time/60.0:.2f} mins).")
    logger.info(f"Best Epoch: {best_epoch} | Best Val Loss: {best_val_loss:.4f} | Best Val Acc: {best_val_acc:.2f}%")
    logger.info("------------------------------------------------------------------")

    # 4. Load Best Model Weights for Export
    logger.info(f"Loading best checkpoint from {best_checkpoint_path} for production artifact export...")
    best_checkpoint = torch.load(best_checkpoint_path, map_location=device, weights_only=False)
    model.load_state_dict(best_checkpoint["state_dict"])

    val_metrics = {
        "val_loss": round(best_val_loss, 4),
        "val_accuracy": round(best_val_acc, 2),
        "best_epoch": best_epoch,
        "total_epochs_trained": len(history),
        "training_time_seconds": round(total_training_time, 2)
    }

    export_production_artifact(
        filepath=production_artifact_path,
        model=model,
        classes=POTATO_CLASSES,
        val_metrics=val_metrics,
        model_version="potato-v1"
    )

    # Save training history JSON
    history_file = reports_ml_dir / "potato_training_history.json"
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump({
            "model_version": "potato-v1",
            "dataset_version": "potato-v1.1-dataset",
            "best_epoch": best_epoch,
            "best_val_loss": round(best_val_loss, 4),
            "best_val_accuracy": round(best_val_acc, 2),
            "training_time_seconds": round(total_training_time, 2),
            "device": str(device),
            "class_weights": class_weights.tolist(),
            "history": history
        }, f, indent=2)
    logger.info(f"Saved training history to {history_file}")

    # 5. Render Training Curves Chart
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        ep_range = [h["epoch"] for h in history]
        tr_loss = [h["train_loss"] for h in history]
        vl_loss = [h["val_loss"] for h in history]
        tr_acc = [h["train_accuracy"] for h in history]
        vl_acc = [h["val_accuracy"] for h in history]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        ax1.plot(ep_range, tr_loss, "b-o", label="Train Loss")
        ax1.plot(ep_range, vl_loss, "r-s", label="Val Loss")
        ax1.axvline(best_epoch, color="g", linestyle="--", label=f"Best Epoch ({best_epoch})")
        ax1.set_title("Potato-v1 Training & Validation Loss")
        ax1.set_xlabel("Epoch")
        ax1.set_ylabel("Loss")
        ax1.legend()
        ax1.grid(True, linestyle=":", alpha=0.6)

        ax2.plot(ep_range, tr_acc, "b-o", label="Train Acc (%)")
        ax2.plot(ep_range, vl_acc, "r-s", label="Val Acc (%)")
        ax2.axvline(best_epoch, color="g", linestyle="--", label=f"Best Epoch ({best_epoch})")
        ax2.set_title("Potato-v1 Training & Validation Accuracy")
        ax2.set_xlabel("Epoch")
        ax2.set_ylabel("Accuracy (%)")
        ax2.legend()
        ax2.grid(True, linestyle=":", alpha=0.6)

        plt.suptitle("HortiSentry Potato-v1 MobileNetV3 Small Training Metrics", fontsize=13, fontweight="bold")
        plt.tight_layout()
        chart_path = reports_ml_dir / "potato_training_curves.png"
        plt.savefig(chart_path, dpi=150)
        plt.close()
        logger.info(f"Saved training curves chart to {chart_path}")
    except Exception as e:
        logger.warning(f"Could not render training curve chart: {e}")

if __name__ == "__main__":
    main()
