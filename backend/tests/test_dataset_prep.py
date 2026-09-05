import os
import pytest
from pathlib import Path
from PIL import Image
import numpy as np
import json
import csv

# Import dataset preparation modules
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from scripts.prepare_dataset import (
    DatasetPreparer,
    analyze_image_quality,
    calculate_md5,
    calculate_dhash,
    hamming_distance,
    load_yaml_config
)


@pytest.fixture
def temp_dataset_env(tmp_path):
    """Fixture providing a temporary isolated project structure."""
    root_dir = tmp_path / "hortisentry"
    root_dir.mkdir()

    # Create config files
    config_dir = root_dir / "config"
    config_dir.mkdir()
    
    classes_content = """
tomato:
  key: "tomato"
  classes:
    - "Healthy"
    - "Early_Blight"
    - "Late_Blight"
    - "Septoria_Leaf_Spot"
  aliases:
    "healthy": "Healthy"
    "Early_blight": "Early_Blight"
    "Leaf_Spot": "Septoria_Leaf_Spot"
"""
    with open(config_dir / "classes.yaml", "w", encoding="utf-8") as f:
        f.write(classes_content)

    quality_content = """
supported_extensions: [".jpg", ".jpeg", ".png", ".webp"]
dimensions:
  min_width: 32
  min_height: 32
  recommended_width: 224
  recommended_height: 224
aspect_ratio:
  min_ratio: 0.33
  max_ratio: 3.00
blur:
  reject_variance: 5.0
  warning_variance: 20.0
brightness:
  too_dark: 10.0
  too_bright: 245.0
duplicate_detection:
  perceptual_hash_threshold: 4
"""
    with open(config_dir / "quality.yaml", "w", encoding="utf-8") as f:
        f.write(quality_content)

    # Create data subdirectories
    raw_dir = root_dir / "data" / "raw" / "tomato"
    for cls_name in ["Healthy", "Early_Blight", "Late_Blight", "Septoria_Leaf_Spot"]:
        (raw_dir / cls_name).mkdir(parents=True, exist_ok=True)

    return root_dir


def create_synthetic_image(filepath: Path, width=64, height=64, color=(0, 200, 50)):
    """Helper to generate a valid PIL JPEG image fixture."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    arr = np.full((height, width, 3), color, dtype=np.uint8)
    # Add random texture to prevent 0 blur variance
    noise = np.random.randint(0, 50, (height, width, 3), dtype=np.uint8)
    img_np = np.clip(arr + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(img_np)
    img.save(filepath, format="JPEG")


def test_valid_image_detection(temp_dataset_env):
    cfg = load_yaml_config(temp_dataset_env / "config" / "quality.yaml")
    img_path = temp_dataset_env / "test_valid.jpg"
    create_synthetic_image(img_path)

    is_valid, is_corrupt, metrics = analyze_image_quality(img_path, cfg)
    assert is_valid is True
    assert is_corrupt is False
    assert metrics["quality_status"] in ["GOOD", "WARNING"]
    assert metrics["width"] == 64
    assert metrics["height"] == 64


def test_corrupted_image_detection(temp_dataset_env):
    cfg = load_yaml_config(temp_dataset_env / "config" / "quality.yaml")
    corrupt_path = temp_dataset_env / "test_corrupt.jpg"
    with open(corrupt_path, "wb") as f:
        f.write(b"NOT_AN_IMAGE_HEADER_CORRUPTED_BYTES_123456789")

    is_valid, is_corrupt, metrics = analyze_image_quality(corrupt_path, cfg)
    assert is_valid is False
    assert is_corrupt is True
    assert metrics["error"] == "corrupted_image"


def test_unsupported_file_detection(temp_dataset_env):
    cfg = load_yaml_config(temp_dataset_env / "config" / "quality.yaml")
    txt_path = temp_dataset_env / "notes.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("Some text file content")

    is_valid, is_corrupt, metrics = analyze_image_quality(txt_path, cfg)
    assert is_valid is False
    assert is_corrupt is False
    assert metrics["error"] == "unsupported_format"


def test_class_alias_mapping(temp_dataset_env):
    preparer = DatasetPreparer(temp_dataset_env, crop_key="tomato")
    assert preparer.normalize_class_name("Healthy") == "Healthy"
    assert preparer.normalize_class_name("healthy") == "Healthy"
    assert preparer.normalize_class_name("Early_blight") == "Early_Blight"
    assert preparer.normalize_class_name("Leaf_Spot") == "Septoria_Leaf_Spot"
    assert preparer.normalize_class_name("UnknownClass") is None


def test_duplicate_detection(temp_dataset_env):
    img1 = temp_dataset_env / "img1.jpg"
    img2 = temp_dataset_env / "img2.jpg"
    create_synthetic_image(img1)
    create_synthetic_image(img2)

    # Force identical image content
    with open(img1, "rb") as f1, open(img2, "wb") as f2:
        f2.write(f1.read())

    h1 = calculate_md5(img1)
    h2 = calculate_md5(img2)
    assert h1 == h2

    with Image.open(img1) as i1, Image.open(img2) as i2:
        dh1 = calculate_dhash(i1)
        dh2 = calculate_dhash(i2)
        assert dh1 == dh2
        assert hamming_distance(dh1, dh2) == 0


def test_missing_dataset_handling(temp_dataset_env):
    preparer = DatasetPreparer(temp_dataset_env, crop_key="tomato")
    audit_data = preparer.run_pipeline()

    assert audit_data["total_images"] == 0
    assert audit_data["crop"] == "tomato"
    assert (temp_dataset_env / "reports" / "dataset_audit.json").exists()
    assert (temp_dataset_env / "reports" / "dataset_quality_report.md").exists()

    with open(temp_dataset_env / "reports" / "dataset_quality_report.md", "r", encoding="utf-8") as f:
        content = f.read()
        assert "DATASET_NOT_AVAILABLE" in content
        assert "Dataset not downloaded yet" in content


def test_reproducible_splitting_and_manifest(temp_dataset_env):
    raw_dir = temp_dataset_env / "data" / "raw" / "tomato"

    # Populate synthetic dataset (10 images per class)
    classes = ["Healthy", "Early_Blight", "Late_Blight", "Septoria_Leaf_Spot"]
    for cls_name in classes:
        cls_dir = raw_dir / cls_name
        for i in range(10):
            create_synthetic_image(cls_dir / f"leaf_{i}.jpg", color=(i*20, 150, 80))

    preparer = DatasetPreparer(temp_dataset_env, crop_key="tomato")
    audit_data = preparer.run_pipeline(overwrite=True)

    assert audit_data["total_images"] == 40
    assert audit_data["split_counts"]["train"] > 0
    assert audit_data["split_counts"]["validation"] > 0
    assert audit_data["split_counts"]["test"] > 0
    assert audit_data["split_counts"]["train"] + audit_data["split_counts"]["validation"] + audit_data["split_counts"]["test"] == 40

    manifest_file = temp_dataset_env / "data" / "processed" / "manifest.csv"
    assert manifest_file.exists()

    with open(manifest_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 40
        for r in rows:
            assert r["split"] in ["train", "validation", "test"]
            assert r["class_name"] in classes
            assert int(r["width"]) == 64
