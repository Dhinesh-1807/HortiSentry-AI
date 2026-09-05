import os
from pathlib import Path
import yaml
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent

class MLConfig:
    """Loader and container for ML pipeline settings from config/ml.yaml."""

    def __init__(self, config_path: Path = None):
        if config_path is None:
            config_path = PROJECT_ROOT / "config" / "ml.yaml"
        self.config_path = config_path
        self._data = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            raise FileNotFoundError(f"ML configuration file not found at {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @property
    def crop(self) -> str:
        return self._data.get("crop", "tomato")

    @property
    def classes(self) -> List[str]:
        return self._data.get("classes", ["Healthy", "Early_Blight", "Late_Blight", "Septoria_Leaf_Spot"])

    @property
    def num_classes(self) -> int:
        return len(self.classes)

    @property
    def image_size(self) -> int:
        return self._data.get("image_size", 224)

    @property
    def architecture(self) -> str:
        return self._data.get("model", {}).get("architecture", "mobilenet_v3_small")

    @property
    def pretrained(self) -> bool:
        return self._data.get("model", {}).get("pretrained", True)

    @property
    def batch_size(self) -> int:
        return self._data.get("training", {}).get("batch_size", 32)

    @property
    def epochs(self) -> int:
        return self._data.get("training", {}).get("epochs", 10)

    @property
    def learning_rate(self) -> float:
        return float(self._data.get("training", {}).get("learning_rate", 0.001))

    @property
    def weight_decay(self) -> float:
        return float(self._data.get("training", {}).get("weight_decay", 0.0001))

    @property
    def random_seed(self) -> int:
        return int(self._data.get("training", {}).get("random_seed", 42))

    @property
    def early_stopping_enabled(self) -> bool:
        return self._data.get("early_stopping", {}).get("enabled", True)

    @property
    def early_stopping_patience(self) -> int:
        return self._data.get("early_stopping", {}).get("patience", 3)

    @property
    def imbalance_strategy(self) -> str:
        return self._data.get("class_imbalance", {}).get("strategy", "CLASS_WEIGHTED_LOSS")
