#!/usr/bin/env python3
"""
HortiSentry — Dataset Ingestion, Quality Audit, Duplicate Detection & Splitting Pipeline

Usage:
    python scripts/prepare_dataset.py [--crop tomato] [--raw-dir data/raw] [--force]
"""

import os
import sys
import argparse
import hashlib
import json
import shutil
import math
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import yaml
from PIL import Image, ImageStat
import numpy as np
import cv2


def load_yaml_config(filepath: Path) -> Dict[str, Any]:
    """Load YAML configuration file safely."""
    if not filepath.exists():
        raise FileNotFoundError(f"Configuration file not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def calculate_md5(filepath: Path) -> str:
    """Calculate MD5 hash of a file for exact duplicate detection."""
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def calculate_dhash(image: Image.Image, hash_size: int = 8) -> str:
    """Calculate difference hash (dHash) for near-duplicate image detection."""
    # Convert to grayscale and resize to (hash_size + 1, hash_size)
    img = image.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.BILINEAR)
    pixels = np.asarray(img).flatten()
    
    # Calculate horizontal difference
    diff = []
    for row in range(hash_size):
        for col in range(hash_size):
            left = pixels[row * (hash_size + 1) + col]
            right = pixels[row * (hash_size + 1) + col + 1]
            diff.append(left > right)
            
    # Convert boolean array to hex string
    decimal_val = 0
    hex_str = ""
    for i, val in enumerate(diff):
        if val:
            decimal_val += 2 ** (i % 4)
        if i % 4 == 3:
            hex_str += f"{decimal_val:x}"
            decimal_val = 0
    return hex_str


def hamming_distance(h1: str, h2: str) -> int:
    """Calculate Hamming distance between two hex hash strings."""
    if len(h1) != len(h2):
        return 999
    return sum(bin(int(c1, 16) ^ int(c2, 16)).count('1') for c1, c2 in zip(h1, h2))


def analyze_image_quality(
    filepath: Path,
    quality_cfg: Dict[str, Any]
) -> Tuple[bool, bool, Dict[str, Any]]:
    """
    Validate image readability and compute quality parameters (blur, brightness, dimensions).
    Returns (is_valid, is_corrupt, metrics_dict).
    """
    supported_exts = set(quality_cfg.get("supported_extensions", [".jpg", ".jpeg", ".png", ".webp"]))
    if filepath.suffix.lower() not in supported_exts:
        return False, False, {"error": "unsupported_format"}

    try:
        # Validate PIL opening
        with Image.open(filepath) as img:
            img.verify()
        
        # Re-open for metric processing after verify()
        with Image.open(filepath) as img:
            img_format = img.format
            width, height = img.size
            aspect_ratio = round(width / float(height), 2) if height > 0 else 0.0

            # Convert PIL to CV2 image for OpenCV blur evaluation
            img_np = np.array(img.convert("RGB"))
            cv2_img = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)

            # Blur evaluation via Laplacian variance
            blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())

            # Brightness evaluation
            brightness_score = float(np.mean(gray))

            # Quality classification against configuration
            min_w = quality_cfg["dimensions"]["min_width"]
            min_h = quality_cfg["dimensions"]["min_height"]
            min_ar = quality_cfg["aspect_ratio"]["min_ratio"]
            max_ar = quality_cfg["aspect_ratio"]["max_ratio"]
            reject_blur = quality_cfg["blur"]["reject_variance"]
            warn_blur = quality_cfg["blur"]["warning_variance"]
            too_dark = quality_cfg["brightness"]["too_dark"]
            too_bright = quality_cfg["brightness"]["too_bright"]

            quality_status = "GOOD"
            reasons = []

            if width < min_w or height < min_h:
                quality_status = "REJECT"
                reasons.append("resolution_too_low")
            if aspect_ratio < min_ar or aspect_ratio > max_ar:
                quality_status = "REJECT"
                reasons.append("extreme_aspect_ratio")
            if blur_score < reject_blur:
                quality_status = "REJECT"
                reasons.append("severe_blur")
            elif blur_score < warn_blur and quality_status != "REJECT":
                quality_status = "WARNING"
                reasons.append("mild_blur")

            if brightness_score < too_dark:
                if quality_status != "REJECT":
                    quality_status = "WARNING"
                reasons.append("underexposed")
            elif brightness_score > too_bright:
                if quality_status != "REJECT":
                    quality_status = "WARNING"
                reasons.append("overexposed")

            metrics = {
                "file_name": filepath.name,
                "file_size": filepath.stat().st_size,
                "format": img_format,
                "width": width,
                "height": height,
                "aspect_ratio": aspect_ratio,
                "blur_score": round(blur_score, 2),
                "brightness_score": round(brightness_score, 2),
                "quality_status": quality_status,
                "reasons": reasons
            }
            return True, False, metrics

    except Exception as e:
        return False, True, {"error": "corrupted_image", "message": str(e)}


class DatasetPreparer:
    def __init__(self, root_dir: Path, crop_key: str = "tomato"):
        self.root_dir = root_dir.resolve()
        self.crop_key = crop_key
        self.config_dir = self.root_dir / "config"
        self.data_dir = self.root_dir / "data"
        self.reports_dir = self.root_dir / "reports"

        self.classes_cfg = load_yaml_config(self.config_dir / "classes.yaml")
        self.quality_cfg = load_yaml_config(self.config_dir / "quality.yaml")

        crop_info = self.classes_cfg.get(crop_key, {})
        self.canonical_classes = crop_info.get("classes", [])
        self.alias_map = crop_info.get("aliases", {})

        self.raw_dir = self.data_dir / "raw" / crop_key
        self.processed_dir = self.data_dir / "processed"
        self.train_dir = self.data_dir / "train"
        self.val_dir = self.data_dir / "validation"
        self.test_dir = self.data_dir / "test"

    def normalize_class_name(self, dir_name: str) -> Optional[str]:
        """Map raw folder names or alias names to canonical disease class keys."""
        if dir_name in self.canonical_classes:
            return dir_name
        return self.alias_map.get(dir_name, None)

    def run_pipeline(self, overwrite: bool = False) -> Dict[str, Any]:
        """Execute complete ingestion, duplicate detection, quality audit, and splitting."""
        print(f"--- HortiSentry Dataset Ingestion & Audit Pipeline [{self.crop_key}] ---")

        # 1. Discover raw images
        raw_files: List[Tuple[Path, str]] = [] # (filepath, canonical_class)
        unsupported_files: List[str] = []
        
        if self.raw_dir.exists():
            for entry in self.raw_dir.iterdir():
                if entry.is_dir():
                    canonical = self.normalize_class_name(entry.name)
                    if canonical:
                        for sub_entry in entry.rglob("*"):
                            if sub_entry.is_file():
                                if sub_entry.name.startswith("."):
                                    continue # Skip hidden / gitkeep files
                                ext = sub_entry.suffix.lower()
                                if ext in set(self.quality_cfg.get("supported_extensions", [])):
                                    raw_files.append((sub_entry, canonical))
                                else:
                                    unsupported_files.append(str(sub_entry.relative_to(self.root_dir)))

        # Handle zero dataset case gracefully
        if not raw_files:
            print("No raw images found in data/raw/tomato/. Generating zero-count report...")
            audit_data = self._generate_empty_audit_report(unsupported_files)
            self._write_reports(audit_data, status="DATASET_NOT_AVAILABLE")
            return audit_data

        print(f"Discovered {len(raw_files)} candidate raw images across {len(self.canonical_classes)} classes.")

        # 2. Quality Audit & Validation
        records = []
        corrupted_files = []
        md5_hashes: Dict[str, List[str]] = {} # md5 -> list of image_ids
        dhashes: List[Tuple[str, str]] = []   # (image_id, dhash)

        widths, heights, aspect_ratios = [], [], []

        for idx, (fpath, cls_name) in enumerate(raw_files):
            img_id = f"{cls_name}_{idx+1:05d}"
            is_valid, is_corrupt, metrics = analyze_image_quality(fpath, self.quality_cfg)

            if is_corrupt:
                corrupted_files.append(str(fpath.relative_to(self.root_dir)))
                continue
            if not is_valid:
                continue

            md5_val = calculate_md5(fpath)
            md5_hashes.setdefault(md5_val, []).append(img_id)

            with Image.open(fpath) as img:
                dhash_val = calculate_dhash(img)
                dhashes.append((img_id, dhash_val))

            widths.append(metrics["width"])
            heights.append(metrics["height"])
            aspect_ratios.append(metrics["aspect_ratio"])

            record = {
                "image_id": img_id,
                "original_filename": fpath.name,
                "filepath": fpath,
                "class_name": cls_name,
                "split": "unassigned",
                "width": metrics["width"],
                "height": metrics["height"],
                "aspect_ratio": metrics["aspect_ratio"],
                "file_format": metrics["format"],
                "file_size": metrics["file_size"],
                "image_hash": md5_val,
                "dhash": dhash_val,
                "blur_score": metrics["blur_score"],
                "brightness_score": metrics["brightness_score"],
                "quality_status": metrics["quality_status"],
                "reasons": metrics["reasons"]
            }
            records.append(record)

        # 3. Duplicate Analysis
        exact_duplicate_groups = [ids for ids in md5_hashes.values() if len(ids) > 1]
        near_duplicate_pairs = []

        # Find near-duplicates using dHash
        dh_threshold = self.quality_cfg.get("duplicate_detection", {}).get("perceptual_hash_threshold", 4)
        for i in range(len(dhashes)):
            for j in range(i + 1, min(i + 50, len(dhashes))): # Efficient window check
                id1, h1 = dhashes[i]
                id2, h2 = dhashes[j]
                if hamming_distance(h1, h2) <= dh_threshold:
                    near_duplicate_pairs.append((id1, id2))

        # 4. Stratified Split (70% Train / 15% Val / 15% Test) with Seed 42
        class_records: Dict[str, List[Dict[str, Any]]] = {}
        for rec in records:
            class_records.setdefault(rec["class_name"], []).append(rec)

        np.random.seed(42)
        for cls_name, cls_recs in class_records.items():
            # Group identical hashes together to avoid cross-split data leakage
            hash_groups: Dict[str, List[Dict[str, Any]]] = {}
            for rec in cls_recs:
                hash_groups.setdefault(rec["image_hash"], []).append(rec)

            groups = list(hash_groups.values())
            np.random.shuffle(groups)

            n_groups = len(groups)
            n_train = max(1, int(n_groups * 0.70))
            n_val = max(1, int(n_groups * 0.15)) if n_groups >= 3 else 0

            train_groups = groups[:n_train]
            val_groups = groups[n_train:n_train + n_val]
            test_groups = groups[n_train + n_val:]

            for grp in train_groups:
                for r in grp: r["split"] = "train"
            for grp in val_groups:
                for r in grp: r["split"] = "validation"
            for grp in test_groups:
                for r in grp: r["split"] = "test"

        # 5. Populate split directories (if requested or by default)
        self._populate_split_files(records, overwrite=overwrite)

        # 6. Generate Manifest CSV
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = self.processed_dir / "manifest.csv"
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write("image_id,original_filename,class_name,split,width,height,file_format,file_size,image_hash,quality_status\n")
            for rec in records:
                f.write(f"{rec['image_id']},{rec['original_filename']},{rec['class_name']},{rec['split']},{rec['width']},{rec['height']},{rec['file_format']},{rec['file_size']},{rec['image_hash']},{rec['quality_status']}\n")

        # 7. Audit & Quality Summaries
        class_counts = {c: sum(1 for r in records if r["class_name"] == c) for c in self.canonical_classes}
        split_counts = {
            "train": sum(1 for r in records if r["split"] == "train"),
            "validation": sum(1 for r in records if r["split"] == "validation"),
            "test": sum(1 for r in records if r["split"] == "test")
        }
        quality_counts = {
            "GOOD": sum(1 for r in records if r["quality_status"] == "GOOD"),
            "WARNING": sum(1 for r in records if r["quality_status"] == "WARNING"),
            "REJECT": sum(1 for r in records if r["quality_status"] == "REJECT")
        }

        audit_data = {
            "crop": self.crop_key,
            "total_images": len(records),
            "images_per_class": class_counts,
            "split_counts": split_counts,
            "quality_counts": quality_counts,
            "corrupted_image_count": len(corrupted_files),
            "unsupported_file_count": len(unsupported_files),
            "exact_duplicate_group_count": len(exact_duplicate_groups),
            "near_duplicate_pair_count": len(near_duplicate_pairs),
            "corrupted_files": corrupted_files,
            "unsupported_files": unsupported_files,
            "dimension_stats": {
                "min_width": int(np.min(widths)) if widths else None,
                "max_width": int(np.max(widths)) if widths else None,
                "avg_width": float(np.mean(widths)) if widths else None,
                "min_height": int(np.min(heights)) if heights else None,
                "max_height": int(np.max(heights)) if heights else None,
                "avg_height": float(np.mean(heights)) if heights else None,
                "avg_aspect_ratio": float(np.mean(aspect_ratios)) if aspect_ratios else None
            }
        }

        readiness = "READY_FOR_TRAINING" if len(records) > 0 and quality_counts["GOOD"] > 0 else "NEEDS_DATA_CLEANING"
        self._write_reports(audit_data, status=readiness)
        print(f"Dataset Ingestion Completed cleanly. Readiness Status: {readiness}")
        return audit_data

    def _populate_split_files(self, records: List[Dict[str, Any]], overwrite: bool = False):
        """Copy images into data/train/, data/validation/, data/test/ class directories."""
        for rec in records:
            split_dir = self.data_dir / rec["split"] / rec["class_name"]
            split_dir.mkdir(parents=True, exist_ok=True)
            target_path = split_dir / f"{rec['image_id']}{Path(rec['original_filename']).suffix}"

            if not target_path.exists() or overwrite:
                shutil.copy2(rec["filepath"], target_path)

    def _generate_empty_audit_report(self, unsupported_files: List[str]) -> Dict[str, Any]:
        """Generate zero-count audit metadata structure when dataset is missing."""
        class_counts = {c: 0 for c in self.canonical_classes}
        return {
            "crop": self.crop_key,
            "total_images": 0,
            "images_per_class": class_counts,
            "split_counts": {"train": 0, "validation": 0, "test": 0},
            "quality_counts": {"GOOD": 0, "WARNING": 0, "REJECT": 0},
            "corrupted_image_count": 0,
            "unsupported_file_count": len(unsupported_files),
            "exact_duplicate_group_count": 0,
            "near_duplicate_pair_count": 0,
            "corrupted_files": [],
            "unsupported_files": unsupported_files,
            "dimension_stats": {
                "min_width": None,
                "max_width": None,
                "avg_width": None,
                "min_height": None,
                "max_height": None,
                "avg_height": None,
                "avg_aspect_ratio": None
            }
        }

    def _write_reports(self, audit_data: Dict[str, Any], status: str):
        """Write reports/dataset_audit.json, dataset_audit.md, and dataset_quality_report.md."""
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # 1. Write JSON audit report
        with open(self.reports_dir / "dataset_audit.json", "w", encoding="utf-8") as f:
            json.dump(audit_data, f, indent=2)

        # 2. Write Markdown audit report
        md_audit = f"""# HortiSentry — Dataset Ingestion Audit Report

**Crop Target:** {audit_data['crop'].title()}  
**Status:** {status}  

---

## 1. Summary Overview
- **Total Ingested Images:** {audit_data['total_images']}
- **Corrupted Image Count:** {audit_data['corrupted_image_count']}
- **Unsupported File Count:** {audit_data['unsupported_file_count']}
- **Exact Duplicate Groups:** {audit_data['exact_duplicate_group_count']}
- **Near-Duplicate Candidate Pairs:** {audit_data['near_duplicate_pair_count']}

---

## 2. Class Distribution
| Disease Class | Count | Percentage |
| :--- | :--- | :--- |
"""
        tot = audit_data['total_images']
        for cls_name, count in audit_data['images_per_class'].items():
            pct = f"{(count/tot)*100:.1f}%" if tot > 0 else "0.0%"
            md_audit += f"| {cls_name} | {count} | {pct} |\n"

        md_audit += f"""
---

## 3. Split Distribution (70 / 15 / 15)
- **Train Set:** {audit_data['split_counts']['train']}
- **Validation Set:** {audit_data['split_counts']['validation']}
- **Test Set:** {audit_data['split_counts']['test']}

---

## 4. Image Quality Breakdown
- **GOOD Quality:** {audit_data['quality_counts']['GOOD']}
- **WARNING (Mild Blur/Exposure):** {audit_data['quality_counts']['WARNING']}
- **REJECT (Resolution/Severe Blur):** {audit_data['quality_counts']['REJECT']}

---

## 5. Dimension Statistics
- **Min Dimensions:** {audit_data['dimension_stats']['min_width']}x{audit_data['dimension_stats']['min_height']} px
- **Max Dimensions:** {audit_data['dimension_stats']['max_width']}x{audit_data['dimension_stats']['max_height']} px
- **Average Dimensions:** {f"{audit_data['dimension_stats']['avg_width']:.1f}" if audit_data['dimension_stats']['avg_width'] else 'N/A'}x{f"{audit_data['dimension_stats']['avg_height']:.1f}" if audit_data['dimension_stats']['avg_height'] else 'N/A'} px
- **Average Aspect Ratio:** {f"{audit_data['dimension_stats']['avg_aspect_ratio']:.2f}" if audit_data['dimension_stats']['avg_aspect_ratio'] else 'N/A'}
"""
        with open(self.reports_dir / "dataset_audit.md", "w", encoding="utf-8") as f:
            f.write(md_audit)

        # 3. Write Quality Report markdown
        md_quality = f"""# HortiSentry — Dataset Quality & Readiness Report

**Overall Dataset Status:** `{status}`  

---

## 1. Executive Summary
This quality report documents the readiness of the HortiSentry tomato leaf dataset prior to PyTorch ML model training.

"""
        if status == "DATASET_NOT_AVAILABLE":
            md_quality += """> [!WARNING]
> **Dataset Status:** Dataset not downloaded yet; statistics will be generated after ingestion.
> 
> Please place raw tomato leaf imagery under `data/raw/tomato/` and run `python scripts/prepare_dataset.py`.
"""
        else:
            md_quality += f"""- **Total Verified Images:** {audit_data['total_images']}
- **Quality Status Distribution:** GOOD={audit_data['quality_counts']['GOOD']}, WARNING={audit_data['quality_counts']['WARNING']}, REJECT={audit_data['quality_counts']['REJECT']}
- **Data Leakage Safeguard:** Hash-grouped stratified 70/15/15 splitting applied.
"""

        md_quality += f"""
---

## 2. Limitations & Risk Analysis
- **Controlled vs. Field Environments:** Benchmark images are captured in studio settings. Field imagery in `data/field_test/` should be evaluated separately.
- **Class Imbalance:** Monitor representation across classes to avoid minority class recall degradation during training.

---

## 3. Final Readiness Determination
**Current Status:** `{status}`
"""
        with open(self.reports_dir / "dataset_quality_report.md", "w", encoding="utf-8") as f:
            f.write(md_quality)


def main():
    parser = argparse.ArgumentParser(description="HortiSentry Dataset Ingestion & Preparation Pipeline")
    parser.add_argument("--crop", type=str, default="tomato", help="Crop key (default: tomato)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing split image files")
    args = parser.parse_args()

    root_dir = Path(__file__).resolve().parent.parent
    preparer = DatasetPreparer(root_dir, crop_key=args.crop)
    preparer.run_pipeline(overwrite=args.force)


if __name__ == "__main__":
    main()
