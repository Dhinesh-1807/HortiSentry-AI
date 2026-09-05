import os
import sys
import csv
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.transforms import get_train_transforms, get_eval_transforms

logger = logging.getLogger(__name__)

POTATO_CLASSES = ["Potato_Healthy", "Potato_Early_Blight", "Potato_Late_Blight"]
CLASS_TO_IDX = {cls_name: i for i, cls_name in enumerate(POTATO_CLASSES)}
IDX_TO_CLASS = {i: cls_name for i, cls_name in enumerate(POTATO_CLASSES)}

class PotatoDataset(Dataset):
    """
    PyTorch Dataset for HortiSentry Potato Disease Leaf Images.
    Loads images deterministically from data/processed/potato_manifest.csv (potato-v1.1-dataset).
    """

    def __init__(
        self,
        manifest_path: Path,
        split: str = "train",
        transform=None,
        exclude_reject: bool = True
    ):
        self.manifest_path = Path(manifest_path)
        self.split = split
        self.transform = transform
        self.samples: List[Tuple[Path, int, str, str]] = [] # (file_path, label_idx, source, environment)
        self.excluded_count = 0
        self.classes = POTATO_CLASSES
        self.class_to_idx = CLASS_TO_IDX

        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Potato manifest CSV not found at {self.manifest_path}")

        with open(self.manifest_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Check dataset version
                if row.get("dataset_id") != "potato-v1.1-dataset":
                    logger.warning(f"Unexpected dataset_id '{row.get('dataset_id')}' in manifest.")

                # Filter by split
                if row.get("split") != split:
                    continue

                # Filter rejected quality
                if exclude_reject and row.get("quality_status") == "REJECT":
                    self.excluded_count += 1
                    continue

                cls_name = row.get("canonical_class")
                if cls_name not in CLASS_TO_IDX:
                    logger.warning(f"Unknown canonical class '{cls_name}' in row.")
                    continue

                label_idx = CLASS_TO_IDX[cls_name]

                # Resolve file path
                # Path stored in manifest is relative to project root or raw directory
                rel_path = row.get("file_path", "")
                if rel_path:
                    file_path = PROJECT_ROOT / rel_path
                else:
                    file_path = PROJECT_ROOT / "data" / "raw" / "multi_crop" / "potato" / cls_name / f"{row.get('image_id')}.jpg"

                # Verify file existence
                if not file_path.exists():
                    # Fallback check under POTATO_RAW_DIR
                    alt_path = PROJECT_ROOT / "data" / "raw" / "multi_crop" / "potato" / cls_name / Path(rel_path).name
                    if alt_path.exists():
                        file_path = alt_path
                    else:
                        logger.error(f"Missing file for record {row.get('image_id')}: {file_path}")
                        continue

                source = row.get("source", "UNKNOWN")
                env = row.get("environment", "CONTROLLED")
                self.samples.append((file_path, label_idx, source, env))

        logger.info(f"Loaded PotatoDataset split '{split}': {len(self.samples)} samples (Excluded REJECTs: {self.excluded_count})")

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        img_path, label_idx, _, _ = self.samples[idx]
        try:
            with Image.open(img_path) as img:
                image = img.convert("RGB")
        except Exception as e:
            logger.error(f"Error loading image {img_path}: {e}")
            image = Image.new("RGB", (224, 224), color=0)

        if self.transform:
            image = self.transform(image)

        return image, label_idx


def create_potato_dataloaders(
    manifest_path: Optional[Path] = None,
    batch_size: int = 32,
    image_size: int = 224,
    num_workers: int = 0
) -> Tuple[DataLoader, DataLoader, DataLoader, Dict[str, int], torch.Tensor]:
    """
    Construct PyTorch DataLoaders for Train, Validation, and Test splits from potato_manifest.csv.
    Calculates class weights strictly from the Training split.
    
    Returns:
        (train_loader, val_loader, test_loader, train_class_counts, class_weights_tensor)
    """
    if manifest_path is None:
        manifest_path = PROJECT_ROOT / "data" / "processed" / "potato_manifest.csv"

    train_tf = get_train_transforms(image_size=image_size)
    eval_tf = get_eval_transforms(image_size=image_size)

    train_ds = PotatoDataset(manifest_path, split="train", transform=train_tf, exclude_reject=True)
    val_ds = PotatoDataset(manifest_path, split="validation", transform=eval_tf, exclude_reject=False)
    test_ds = PotatoDataset(manifest_path, split="test", transform=eval_tf, exclude_reject=False)

    # Calculate class counts strictly from the training dataset for loss weighting
    train_class_counts = {cls_name: 0 for cls_name in POTATO_CLASSES}
    for _, label_idx, _, _ in train_ds.samples:
        cls_name = POTATO_CLASSES[label_idx]
        train_class_counts[cls_name] += 1

    total_train = len(train_ds)
    num_classes = len(POTATO_CLASSES)
    
    # Inverse class frequency weights: W_c = N_total / (N_classes * N_c)
    weights = []
    for cls_name in POTATO_CLASSES:
        count = train_class_counts[cls_name]
        w = total_train / (num_classes * count) if count > 0 else 1.0
        weights.append(w)

    class_weights_tensor = torch.tensor(weights, dtype=torch.float32)

    train_loader = DataLoader(
        train_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers, pin_memory=True
    )
    val_loader = DataLoader(
        val_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=True
    )
    test_loader = DataLoader(
        test_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=True
    )

    return train_loader, val_loader, test_loader, train_class_counts, class_weights_tensor
