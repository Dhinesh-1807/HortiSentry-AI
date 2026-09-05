import os
import sys
import csv
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("VerifyPhase12B")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def verify_phase12b():
    logger.info("==================================================================")
    logger.info("HORTISENTRY PHASE 12B VERIFICATION SUITE")
    logger.info("==================================================================")

    passed_checks = 0
    total_checks = 10

    # Check 1: Tomato Baseline Preservation
    logger.info("\nCheck 1: Verifying Tomato Baseline Lock...")
    tomato_manifest = PROJECT_ROOT / "data" / "processed" / "manifest.csv"
    assert tomato_manifest.exists(), "Tomato manifest.csv missing!"
    with open(tomato_manifest, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        assert len(rows) == 6271, f"Expected 6271 tomato rows, got {len(rows)}"
        splits = {}
        for r in rows:
            splits[r["split"]] = splits.get(r["split"], 0) + 1
        assert splits.get("train") == 4386
        assert splits.get("validation") == 938
        assert splits.get("test") == 947
    logger.info("✅ Check 1 Passed: Tomato baseline locked (6,271 images: 4386/938/947).")
    passed_checks += 1

    # Check 2: Model Artifact Lock (No Training)
    logger.info("\nCheck 2: Verifying Model Artifact Lock...")
    tomato_model = PROJECT_ROOT / "ml" / "artifacts" / "tomato_v1.pt"
    assert tomato_model.exists(), "tomato_v1.pt artifact missing!"
    potato_model = PROJECT_ROOT / "ml" / "artifacts" / "potato_v1.pt"
    assert not potato_model.exists(), "ERROR: potato_v1.pt exists! Model training was executed prematurely!"
    logger.info("✅ Check 2 Passed: tomato_v1.pt untouched and no potato_v1.pt model trained.")
    passed_checks += 1

    # Check 3: Potato Manifest Version potato-v1.1-dataset
    logger.info("\nCheck 3: Verifying potato_manifest.csv Version...")
    potato_manifest = PROJECT_ROOT / "data" / "processed" / "potato_manifest.csv"
    assert potato_manifest.exists(), "potato_manifest.csv missing!"
    with open(potato_manifest, encoding="utf-8") as f:
        pot_rows = list(csv.DictReader(f))
        assert len(pot_rows) >= 2000, f"Expected >= 2000 images, got {len(pot_rows)}"
        dataset_ids = set(r["dataset_id"] for r in pot_rows)
        assert "potato-v1.1-dataset" in dataset_ids, "Dataset ID potato-v1.1-dataset missing in manifest!"
    logger.info(f"✅ Check 3 Passed: Manifest updated to potato-v1.1-dataset ({len(pot_rows)} total images).")
    passed_checks += 1

    # Check 4: Healthy Class Expansion (>= 300 images)
    logger.info("\nCheck 4: Verifying Healthy Class Expansion (>= 300)...")
    healthy_count = sum(1 for r in pot_rows if r["canonical_class"] == "Potato_Healthy")
    assert healthy_count >= 300, f"Expected >= 300 healthy images, got {healthy_count}"
    logger.info(f"✅ Check 4 Passed: Potato_Healthy count is {healthy_count} (>= 300 target satisfied).")
    passed_checks += 1

    # Check 5: Zero Cross-Split Leakage Audit
    logger.info("\nCheck 5: Auditing Cross-Split Duplicate Leakage...")
    group_to_splits = {}
    for r in pot_rows:
        grp = r["duplicate_group_id"]
        if grp not in group_to_splits:
            group_to_splits[grp] = set()
        group_to_splits[grp].add(r["split"])

    leakage_count = sum(1 for grp, splits in group_to_splits.items() if len(splits) > 1)
    assert leakage_count == 0, f"Cross-split leakage detected in {leakage_count} groups!"
    logger.info("✅ Check 5 Passed: 0 cross-split duplicate leakage verified.")
    passed_checks += 1

    # Check 6: Phase 12B Reports Verification
    logger.info("\nCheck 6: Verifying Required Phase 12B Reports...")
    required_reports = [
        PROJECT_ROOT / "reports" / "phase12b" / "potato_class_distribution.csv",
        PROJECT_ROOT / "reports" / "phase12b" / "potato_class_distribution.md",
        PROJECT_ROOT / "reports" / "phase12b" / "potato_source_distribution.md",
        PROJECT_ROOT / "reports" / "phase12b" / "potato_environment_audit.md",
        PROJECT_ROOT / "reports" / "phase12b" / "potato_leakage_audit.md",
        PROJECT_ROOT / "reports" / "phase12b" / "potato_dataset_audit.json",
        PROJECT_ROOT / "reports" / "phase12b" / "potato_dataset_audit.md",
        PROJECT_ROOT / "reports" / "phase12b" / "potato_training_gate.md",
        PROJECT_ROOT / "reports" / "phase12b" / "phase12b_completion_report.md"
    ]
    for rep in required_reports:
        assert rep.exists(), f"Missing report: {rep}"
    logger.info("✅ Check 6 Passed: All 9 required Phase 12B report files present.")
    passed_checks += 1

    # Check 7: Documentation Verification
    logger.info("\nCheck 7: Verifying Documentation Updates...")
    docs = [
        PROJECT_ROOT / "docs" / "potato_dataset_sources.md",
        PROJECT_ROOT / "docs" / "potato_dataset.md"
    ]
    for d in docs:
        assert d.exists(), f"Missing doc file: {d}"
        content = d.read_text(encoding="utf-8")
        assert "potato-v1.1-dataset" in content, f"Doc {d.name} missing reference to potato-v1.1-dataset"
    logger.info("✅ Check 7 Passed: Documentation updated with potato-v1.1-dataset details.")
    passed_checks += 1

    # Check 8: Visualizations Verification
    logger.info("\nCheck 8: Verifying Visual Charts...")
    vis_dir = PROJECT_ROOT / "reports" / "phase12b" / "visualizations"
    assert vis_dir.exists(), "Visualizations directory missing!"
    charts = list(vis_dir.glob("*.png"))
    assert len(charts) >= 4, f"Expected at least 4 charts, got {len(charts)}"
    logger.info(f"✅ Check 8 Passed: {len(charts)} visual charts present in reports/phase12b/visualizations/.")
    passed_checks += 1

    # Check 9: Training Gate Status Evaluation
    logger.info("\nCheck 9: Verifying Training Gate Status...")
    gate_file = PROJECT_ROOT / "reports" / "phase12b" / "potato_training_gate.md"
    content = gate_file.read_text(encoding="utf-8")
    assert "TRAINING_READY" in content, "Gate status is not TRAINING_READY!"
    assert "GREEN" in content, "Gate readiness is not GREEN!"
    logger.info("✅ Check 9 Passed: Training gate evaluated to TRAINING_READY (GREEN).")
    passed_checks += 1

    # Check 10: Environment Representation (Field vs Controlled)
    logger.info("\nCheck 10: Verifying Environment Representation...")
    env_types = set(r["environment"] for r in pot_rows)
    assert "FIELD" in env_types and "CONTROLLED" in env_types, f"Missing environment types: {env_types}"
    logger.info("✅ Check 10 Passed: Both FIELD and CONTROLLED environment representations verified.")
    passed_checks += 1

    logger.info("\n==================================================================")
    logger.info(f"PHASE 12B VERIFICATION COMPLETE: {passed_checks}/{total_checks} CHECKS PASSED (100%)")
    logger.info("==================================================================")

if __name__ == "__main__":
    verify_phase12b()
