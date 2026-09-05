import os
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import csv
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
import logging

logger = logging.getLogger(__name__)

class TomatoDataset(Dataset):
    """
    PyTorch Dataset for HortiSentry Tomato Disease Leaf Images.
    Loads images from structured split directories or manifest CSV.
    Strictly excludes images with quality_status == 'REJECT' from training.
    """

    def __init__(
        self,
        split_dir: Path,
        classes: List[str],
        transform=None,
        manifest_path: Optional[Path] = None,
        exclude_reject: bool = True
    ):
        self.split_dir = Path(split_dir)
        self.classes = classes
        self.class_to_idx = {cls_name: i for i, cls_name in enumerate(classes)}
        self.transform = transform
        self.samples: List[Tuple[Path, int]] = []
        self.excluded_count = 0

        # Load rejected image IDs or hashes from manifest.csv if present
        rejected_filenames = set()
        if manifest_path and manifest_path.exists() and exclude_reject:
            with open(manifest_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("quality_status") == "REJECT":
                        rejected_filenames.add(row.get("original_filename"))

        # Scan split directory for class subfolders
        valid_exts = {".jpg", ".jpeg", ".png", ".webp"}
        for cls_name in classes:
            cls_folder = self.split_dir / cls_name
            if not cls_folder.exists():
                logger.warning(f"Class directory not found: {cls_folder}")
                continue
            
            label = self.class_to_idx[cls_name]
            for root, _, files in os.walk(cls_folder):
                for f in files:
                    ext = Path(f).suffix.lower()
                    if ext in valid_exts and not f.startswith("."):
                        file_path = Path(root) / f
                        if exclude_reject and (f in rejected_filenames or file_path.name in rejected_filenames):
                            self.excluded_count += 1
                            logger.info(f"Excluded REJECT image from dataset split {self.split_dir.name}: {f}")
                            continue
                        self.samples.append((file_path, label))

        logger.info(f"Loaded {len(self.samples)} samples from {self.split_dir} (Excluded REJECTs: {self.excluded_count})")

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        img_path, label = self.samples[idx]
        try:
            with Image.open(img_path) as img:
                image = img.convert("RGB")
        except Exception as e:
            logger.error(f"Error loading image {img_path}: {e}")
            # Fallback to zero tensor if corrupted image encountered unexpectedly
            image = Image.new("RGB", (224, 224), color=0)

        if self.transform:
            image = self.transform(image)

        return image, label


def create_dataloaders(
    data_root: Path,
    classes: List[str],
    train_transform,
    eval_transform,
    batch_size: int = 32,
    num_workers: int = 0,
    manifest_path: Optional[Path] = None
) -> Tuple[DataLoader, DataLoader, DataLoader, Dict[str, int]]:
    """
    Construct PyTorch DataLoaders for Train, Validation, and Test splits.
    Returns: (train_loader, val_loader, test_loader, train_class_counts)
    """
    data_root = Path(data_root)
    if manifest_path is None:
        manifest_path = data_root / "processed" / "manifest.csv"

    train_ds = TomatoDataset(
        data_root / "train",
        classes=classes,
        transform=train_transform,
        manifest_path=manifest_path,
        exclude_reject=True
    )
    val_ds = TomatoDataset(
        data_root / "validation",
        classes=classes,
        transform=eval_transform,
        manifest_path=manifest_path,
        exclude_reject=False
    )
    test_ds = TomatoDataset(
        data_root / "test",
        classes=classes,
        transform=eval_transform,
        manifest_path=manifest_path,
        exclude_reject=False
    )

    # Calculate class counts strictly from the training dataset for loss weighting
    train_class_counts = {cls_name: 0 for cls_name in classes}
    for _, label_idx in train_ds.samples:
        cls_name = classes[label_idx]
        train_class_counts[cls_name] += 1

    train_loader = DataLoader(
        train_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers, pin_memory=True
    )
    val_loader = DataLoader(
        val_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=True
    )
    test_loader = DataLoader(
        test_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=True
    )

    return train_loader, val_loader, test_loader, train_class_counts
