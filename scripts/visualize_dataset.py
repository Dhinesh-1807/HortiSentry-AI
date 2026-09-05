#!/usr/bin/env python3
"""
HortiSentry — Dataset Visualization Script

Usage:
    python scripts/visualize_dataset.py
"""

import sys
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg") # Non-interactive backend
import matplotlib.pyplot as plt
from PIL import Image


def visualize_dataset(root_dir: Path):
    reports_dir = root_dir / "reports"
    audit_json = reports_dir / "dataset_audit.json"
    manifest_csv = root_dir / "data" / "processed" / "manifest.csv"

    if not audit_json.exists() or not manifest_csv.exists():
        print("No dataset available for visualization.")
        return

    with open(audit_json, "r", encoding="utf-8") as f:
        audit_data = json.load(f)

    tot_images = audit_data.get("total_images", 0)
    if tot_images == 0:
        print("No dataset available for visualization.")
        return

    print("Generating dataset visualization charts...")
    reports_dir.mkdir(parents=True, exist_ok=True)

    # 1. Class Distribution Bar Chart
    classes = list(audit_data["images_per_class"].keys())
    counts = [audit_data["images_per_class"][c] for c in classes]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(classes, counts, color=["#10b981", "#f59e0b", "#ef4444", "#8b5cf6"])
    plt.title("HortiSentry Tomato Disease Class Distribution", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Disease Class", fontweight="bold", labelpad=8)
    plt.ylabel("Number of Leaf Images", fontweight="bold", labelpad=8)
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + max(counts) * 0.01,
            f"{height}",
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=9
        )

    plt.tight_layout()
    plt.savefig(reports_dir / "class_distribution.png", dpi=200)
    plt.close()
    print(f"Generated: {reports_dir / 'class_distribution.png'}")

    # 2. Sample Image Grid (if images exist in train directories)
    train_dir = root_dir / "data" / "train"
    sample_images = []

    for cls_name in classes:
        cls_folder = train_dir / cls_name
        if cls_folder.exists():
            for f in cls_folder.iterdir():
                if f.is_file() and not f.name.startswith("."):
                    sample_images.append((cls_name, f))
                    break

    if sample_images:
        fig, axes = plt.subplots(1, len(sample_images), figsize=(3 * len(sample_images), 3.5))
        if len(sample_images) == 1:
            axes = [axes]

        for ax, (cls_name, img_path) in zip(axes, sample_images):
            try:
                img = Image.open(img_path)
                ax.imshow(img)
                ax.set_title(cls_name.replace("_", " "), fontsize=10, fontweight="bold")
                ax.axis("off")
            except Exception as e:
                ax.set_title(f"Error loading {cls_name}")
                ax.axis("off")

        plt.suptitle("HortiSentry Class Sample Leaf Imagery", fontsize=12, fontweight="bold", y=0.98)
        plt.tight_layout()
        plt.savefig(reports_dir / "sample_grid.png", dpi=200)
        plt.close()
        print(f"Generated: {reports_dir / 'sample_grid.png'}")

    print("Dataset visualization completed.")


def main():
    root_dir = Path(__file__).resolve().parent.parent
    visualize_dataset(root_dir)


if __name__ == "__main__":
    main()
