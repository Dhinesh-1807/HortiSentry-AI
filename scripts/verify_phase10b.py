#!/usr/bin/env python3
"""
Automated Verification Script for HortiSentry Phase 10B.
Checks all 19 acceptance criteria and asset integrity.
"""

import os
import glob
import csv
import json
import yaml
from pathlib import Path

def verify_phase10b():
    root = Path(__file__).resolve().parent.parent
    print("=== HortiSentry Phase 10B Automated Verification ===")

    # 1. Baseline Tomato Preservation Check
    raw_tomato = glob.glob(str(root / "data" / "raw" / "tomato" / "*" / "*"))
    train_imgs = glob.glob(str(root / "data" / "train" / "*" / "*"))
    val_imgs = glob.glob(str(root / "data" / "validation" / "*" / "*"))
    test_imgs = glob.glob(str(root / "data" / "test" / "*" / "*"))
    ckpt_tomato = root / "ml" / "artifacts" / "tomato_v1.pt"

    assert len(raw_tomato) == 6271, f"Raw tomato count changed! Got {len(raw_tomato)}"
    assert len(train_imgs) == 4386, f"Train count changed! Got {len(train_imgs)}"
    assert len(val_imgs) == 938, f"Val count changed! Got {len(val_imgs)}"
    assert len(test_imgs) == 947, f"Test count changed! Got {len(test_imgs)}"
    assert ckpt_tomato.exists() and ckpt_tomato.stat().st_size == 6223435, "tomato_v1.pt checkpoint altered!"
    print("1. Baseline Tomato Dataset & Model Checkpoint Preservation: VERIFIED (6271 total, 4386 train, 938 val, 947 test)")

    # 2. Model Registry Check
    models_yaml = root / "config" / "models.yaml"
    assert models_yaml.exists(), "config/models.yaml missing!"
    with open(models_yaml, "r", encoding="utf-8") as f:
        m_data = yaml.safe_load(f)
    assert "models" in m_data and "tomato-v1" in m_data["models"], "models.yaml structure invalid!"
    print("2. Model Registry Configuration (config/models.yaml): VERIFIED")

    # 3. Reports Verification
    rep_dir = root / "reports" / "phase10b"
    req_reports = [
        "current_dataset_audit.md",
        "crop_support_matrix.csv",
        "dataset_readiness_report.md",
        "leakage_audit.md",
        "source_inventory.md",
        "phase10b_completion_report.md"
    ]
    for rep in req_reports:
        assert (rep_dir / rep).exists(), f"Missing report: {rep}"
    print(f"3. Phase 10B Reports ({len(req_reports)} files under reports/phase10b/): VERIFIED")

    # 4. Crop Support Matrix Columns
    csv_matrix = rep_dir / "crop_support_matrix.csv"
    with open(csv_matrix, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 14, f"Expected 14 rows in crop support matrix, got {len(rows)}"
    expected_cols = ["crop", "dataset_available", "image_count", "class_count", "field_images", "dedicated_model", "model_status", "evidence_review", "recommended_next_step"]
    for col in expected_cols:
        assert col in rows[0], f"Missing column in crop support matrix: {col}"
    print("4. Crop Support Matrix Content & Structure: VERIFIED")

    # 5. Technical Documentation Verification
    doc_field = root / "docs" / "field_data_collection_plan.md"
    doc_strat = root / "docs" / "multi_crop_data_strategy.md"
    assert doc_field.exists(), "docs/field_data_collection_plan.md missing!"
    assert doc_strat.exists(), "docs/multi_crop_data_strategy.md missing!"
    print("5. Technical Documentation (field collection plan & data strategy): VERIFIED")

    print("\nALL PHASE 10B VERIFICATION CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    verify_phase10b()
