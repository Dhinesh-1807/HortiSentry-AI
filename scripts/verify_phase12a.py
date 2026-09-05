import os
import sys
import csv
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("VerifyPhase12A")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def verify_phase12a():
    logger.info("==================================================================")
    logger.info("HORTISENTRY PHASE 12A VERIFICATION SUITE")
    logger.info("==================================================================")

    passed_checks = 0
    total_checks = 10

    # Check 1: Tomato Manifest Preservation
    logger.info("\nCheck 1: Verifying Tomato Dataset Baseline...")
    tomato_manifest = PROJECT_ROOT / "data" / "processed" / "manifest.csv"
    assert tomato_manifest.exists(), "Tomato manifest.csv missing!"
    with open(tomato_manifest, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 6271, f"Expected 6271 tomato rows, got {len(rows)}"
        splits = {}
        for r in rows:
            s = r["split"]
            splits[s] = splits.get(s, 0) + 1
        assert splits.get("train") == 4386, f"Expected 4386 train, got {splits.get('train')}"
        assert splits.get("validation") == 938, f"Expected 938 val, got {splits.get('validation')}"
        assert splits.get("test") == 947, f"Expected 947 test, got {splits.get('test')}"
    logger.info("✅ Check 1 Passed: Tomato dataset manifest locked (6,271 images: 4386/938/947).")
    passed_checks += 1

    # Check 2: Tomato Model Artifact Lock
    logger.info("\nCheck 2: Verifying tomato_v1.pt Model Artifact...")
    tomato_model = PROJECT_ROOT / "ml" / "artifacts" / "tomato_v1.pt"
    assert tomato_model.exists(), "tomato_v1.pt artifact missing!"
    potato_model = PROJECT_ROOT / "ml" / "artifacts" / "potato_v1.pt"
    assert not potato_model.exists(), "ERROR: potato_v1.pt exists! Model training was incorrectly executed!"
    logger.info("✅ Check 2 Passed: tomato_v1.pt untouched and no potato_v1.pt trained.")
    passed_checks += 1

    # Check 3: Potato Benchmark Preservation
    logger.info("\nCheck 3: Verifying Potato Benchmark Preservation...")
    multi_crop_manifest = PROJECT_ROOT / "data" / "processed" / "multi_crop_manifest.csv"
    assert multi_crop_manifest.exists(), "multi_crop_manifest.csv missing!"
    with open(multi_crop_manifest, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        potato_bench = [r for r in reader if r.get("crop") == "potato"]
        assert len(potato_bench) == 80, f"Expected 80 potato benchmark images, got {len(potato_bench)}"
    logger.info("✅ Check 3 Passed: 80 original Potato benchmark images preserved.")
    passed_checks += 1

    # Check 4: Potato Dataset Raw Structure
    logger.info("\nCheck 4: Verifying Potato Raw Directory Structure...")
    potato_raw = PROJECT_ROOT / "data" / "raw" / "multi_crop" / "potato"
    expected_classes = ["Potato_Healthy", "Potato_Early_Blight", "Potato_Late_Blight"]
    for c in expected_classes:
        cdir = potato_raw / c
        assert cdir.exists(), f"Missing directory: {cdir}"
        imgs = list(cdir.glob("*.jpg")) + list(cdir.glob("*.JPG")) + list(cdir.glob("*.png")) + list(cdir.glob("*.webp"))
        assert len(imgs) > 0, f"Directory {c} is empty!"
    logger.info("✅ Check 4 Passed: All 3 canonical Potato class directories present and populated.")
    passed_checks += 1

    # Check 5: Potato Manifest Integrity
    logger.info("\nCheck 5: Verifying data/processed/potato_manifest.csv...")
    potato_manifest = PROJECT_ROOT / "data" / "processed" / "potato_manifest.csv"
    assert potato_manifest.exists(), "potato_manifest.csv missing!"
    with open(potato_manifest, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        pot_rows = list(reader)
        assert len(pot_rows) >= 1000, f"Expected at least 1000 potato images, got {len(pot_rows)}"
        for r in pot_rows:
            assert r["canonical_class"] in expected_classes, f"Invalid canonical class: {r['canonical_class']}"
            assert r["split"] in ["train", "validation", "test"], f"Invalid split: {r['split']}"
            assert r["quality_status"] in ["GOOD", "WARNING", "REJECT"], f"Invalid quality: {r['quality_status']}"
    logger.info(f"✅ Check 5 Passed: potato_manifest.csv verified with {len(pot_rows)} traceable records.")
    passed_checks += 1

    # Check 6: Zero Cross-Split Leakage
    logger.info("\nCheck 6: Auditing Cross-Split Leakage...")
    group_to_splits = {}
    with open(potato_manifest, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            grp = r["duplicate_group_id"]
            if grp not in group_to_splits:
                group_to_splits[grp] = set()
            group_to_splits[grp].add(r["split"])

    leakage_count = sum(1 for grp, splits in group_to_splits.items() if len(splits) > 1)
    assert leakage_count == 0, f"Cross-split leakage detected in {leakage_count} duplicate groups!"
    logger.info("✅ Check 6 Passed: 0 cross-split leakage verified across all duplicate groups.")
    passed_checks += 1

    # Check 7: Required Audit Reports Exist
    logger.info("\nCheck 7: Verifying Required Phase 12 Reports...")
    required_reports = [
        PROJECT_ROOT / "reports" / "phase12" / "potato_class_distribution.csv",
        PROJECT_ROOT / "reports" / "phase12" / "potato_class_distribution.md",
        PROJECT_ROOT / "reports" / "phase12" / "potato_source_distribution.md",
        PROJECT_ROOT / "reports" / "phase12" / "potato_environment_audit.md",
        PROJECT_ROOT / "reports" / "phase12" / "potato_dataset_audit.json",
        PROJECT_ROOT / "reports" / "phase12" / "potato_dataset_audit.md",
        PROJECT_ROOT / "reports" / "phase12" / "potato_training_gate.md"
    ]
    for rep in required_reports:
        assert rep.exists(), f"Missing report: {rep}"
    logger.info("✅ Check 7 Passed: All 7 required audit report files present.")
    passed_checks += 1

    # Check 8: Documentation Files Exist
    logger.info("\nCheck 8: Verifying Documentation Files...")
    docs = [
        PROJECT_ROOT / "docs" / "potato_dataset_sources.md",
        PROJECT_ROOT / "docs" / "potato_dataset.md"
    ]
    for d in docs:
        assert d.exists(), f"Missing documentation file: {d}"
    logger.info("✅ Check 8 Passed: Both docs/potato_dataset_sources.md and docs/potato_dataset.md present.")
    passed_checks += 1

    # Check 9: Visualizations Generated
    logger.info("\nCheck 9: Verifying Visual Charts...")
    vis_dir = PROJECT_ROOT / "reports" / "phase12" / "visualizations"
    assert vis_dir.exists(), "Visualizations directory missing!"
    charts = list(vis_dir.glob("*.png"))
    assert len(charts) >= 4, f"Expected at least 4 visual charts, got {len(charts)}"
    logger.info(f"✅ Check 9 Passed: {len(charts)} visual charts generated in reports/phase12/visualizations/.")
    passed_checks += 1

    # Check 10: Training Gate Decision
    logger.info("\nCheck 10: Verifying Training Gate Decision...")
    gate_file = PROJECT_ROOT / "reports" / "phase12" / "potato_training_gate.md"
    content = gate_file.read_text(encoding="utf-8")
    assert "TRAINING_READY" in content or "DATA_EXPANSION_REQUIRED" in content, "Invalid training gate status!"
    logger.info("✅ Check 10 Passed: Training gate decision formalized.")
    passed_checks += 1

    logger.info("\n==================================================================")
    logger.info(f"PHASE 12A VERIFICATION COMPLETE: {passed_checks}/{total_checks} CHECKS PASSED (100%)")
    logger.info("==================================================================")

if __name__ == "__main__":
    verify_phase12a()
