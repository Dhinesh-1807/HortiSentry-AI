#!/usr/bin/env python3
"""
Automated Verification Script for HortiSentry Phase 10A Dataset Preparation.
Verifies all 22 acceptance criteria and asset integrity.
"""

import os
import glob
import csv
import json
import yaml
from pathlib import Path

def verify_phase10a():
    root = Path(__file__).resolve().parent.parent
    print("=== HortiSentry Phase 10A Automated Verification ===")
    
    # 1. Baseline Tomato Dataset Preservation
    raw_tomato = glob.glob(str(root / "data" / "raw" / "tomato" / "*" / "*"))
    train_imgs = glob.glob(str(root / "data" / "train" / "*" / "*"))
    val_imgs = glob.glob(str(root / "data" / "validation" / "*" / "*"))
    test_imgs = glob.glob(str(root / "data" / "test" / "*" / "*"))
    manifest_tomato = root / "data" / "processed" / "manifest.csv"
    ckpt_tomato = root / "ml" / "artifacts" / "tomato_v1.pt"
    
    assert len(raw_tomato) == 6271, f"Raw tomato count changed! Got {len(raw_tomato)}"
    assert len(train_imgs) == 4386, f"Train count changed! Got {len(train_imgs)}"
    assert len(val_imgs) == 938, f"Val count changed! Got {len(val_imgs)}"
    assert len(test_imgs) == 947, f"Test count changed! Got {len(test_imgs)}"
    assert manifest_tomato.exists(), "Tomato manifest.csv missing!"
    assert ckpt_tomato.exists() and ckpt_tomato.stat().st_size == 6223435, "tomato_v1.pt checkpoint altered!"
    print("1. Baseline Tomato Dataset & Checkpoint Preservation: VERIFIED (6271 total, 4386 train, 938 val, 947 test)")

    # 2. Config Files
    ds_yaml = root / "config" / "datasets.yaml"
    mc_yaml = root / "config" / "multi_crop_classes.yaml"
    assert ds_yaml.exists(), "datasets.yaml missing!"
    assert mc_yaml.exists(), "multi_crop_classes.yaml missing!"
    
    with open(ds_yaml, "r", encoding="utf-8") as f:
        ds_data = yaml.safe_load(f)
    assert "datasets" in ds_data and len(ds_data["datasets"]) >= 14, "datasets.yaml registry entries missing!"
    print("2. Dataset Source Registry & Normalization Configs: VERIFIED")

    # 3. Multi-Crop Raw Directory Structure
    raw_mc = root / "data" / "raw" / "multi_crop"
    expected_crops = ["apple", "blueberry", "cherry", "corn", "grape", "orange", "peach", "pepper", "potato", "raspberry", "soybean", "squash", "strawberry", "tomato"]
    for crop in expected_crops:
        assert (raw_mc / crop).exists(), f"Crop directory missing: {crop}"
    print(f"3. Raw Multi-Crop Directory Structure ({len(expected_crops)} crops): VERIFIED")

    # 4. Multi-Crop Processed Manifest
    mc_manifest = root / "data" / "processed" / "multi_crop_manifest.csv"
    assert mc_manifest.exists(), "multi_crop_manifest.csv missing!"
    with open(mc_manifest, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 755, f"Expected 755 manifest rows, got {len(rows)}"
    expected_cols = ["image_id", "dataset_id", "source", "crop", "original_label", "canonical_class", "split", "width", "height", "file_format", "file_size", "image_hash", "quality_status", "duplicate_group_id"]
    for col in expected_cols:
        assert col in rows[0], f"Missing manifest column: {col}"
    print(f"4. Multi-Crop Processed Manifest: VERIFIED ({len(rows)} records, all {len(expected_cols)} columns present)")

    # 5. Audit Reports & Visualizations
    reports_dir = root / "reports" / "phase10"
    viz_dir = reports_dir / "visualizations"
    
    assert (reports_dir / "dataset_source_inventory.md").exists(), "dataset_source_inventory.md missing!"
    assert (reports_dir / "class_distribution.csv").exists(), "class_distribution.csv missing!"
    assert (reports_dir / "class_distribution.md").exists(), "class_distribution.md missing!"
    assert (reports_dir / "multi_crop_dataset_audit.json").exists(), "multi_crop_dataset_audit.json missing!"
    assert (reports_dir / "multi_crop_dataset_audit.md").exists(), "multi_crop_dataset_audit.md missing!"
    assert (viz_dir / "class_distribution.png").exists(), "class_distribution.png missing!"
    assert (viz_dir / "quality_distribution.png").exists(), "quality_distribution.png missing!"
    assert (viz_dir / "sample_grid.png").exists(), "sample_grid.png missing!"
    print("5. Dataset Audit Reports & Visualizations: VERIFIED")

    # 6. Technical Documentation
    docs_file = root / "docs" / "multi_crop_dataset.md"
    assert docs_file.exists(), "docs/multi_crop_dataset.md missing!"
    print("6. Technical Documentation (docs/multi_crop_dataset.md): VERIFIED")

    print("\nALL PHASE 10A VERIFICATION CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    verify_phase10a()
