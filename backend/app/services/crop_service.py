import os
import yaml
import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class CropConfigLoader:
    _cached_config: Dict[str, Any] = None

    @classmethod
    def load_config(cls) -> Dict[str, Any]:
        """Loads crop configuration from YAML file specified in settings."""
        if cls._cached_config is not None:
            return cls._cached_config

        config_path = settings.CROP_CONFIG_PATH
        if not os.path.exists(config_path):
            logger.warning(f"Crop config file not found at {config_path}. Falling back to default inline structure.")
            return cls._get_default_config()

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                cls._cached_config = data
                return data
        except Exception as e:
            logger.error(f"Error loading crops.yaml from {config_path}: {e}")
            return cls._get_default_config()

    @classmethod
    def get_supported_crops(
        cls,
        category: Optional[str] = None,
        search_query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Returns list of active crop definitions with optional category and search query filters."""
        config = cls.load_config()
        crops = []
        
        for key, details in config.items():
            if not isinstance(details, dict):
                continue
            if not details.get("is_active", True):
                continue

            crop_category = details.get("category", "vegetables")
            if category and category.lower() != "all" and crop_category.lower() != category.lower():
                continue

            common_name = details.get("common_name", key.capitalize())
            scientific_name = details.get("scientific_name", "")
            display_name_en = details.get("display_name_en", common_name)
            display_name_ta = details.get("display_name_ta", "")

            if search_query:
                q = search_query.lower().strip()
                match = (
                    q in key.lower() or
                    q in common_name.lower() or
                    q in scientific_name.lower() or
                    q in display_name_en.lower() or
                    q in display_name_ta.lower()
                )
                if not match:
                    continue

            crops.append({
                "key": key,
                "common_name": common_name,
                "display_name": common_name,
                "display_name_en": display_name_en,
                "display_name_ta": display_name_ta,
                "scientific_name": scientific_name,
                "category": crop_category,
                "supported_status": details.get("supported_status", "active"),
                "disease_knowledge_status": details.get("disease_knowledge_status", "verified"),
                "vision_support_status": details.get("vision_support_status", "knowledge_review"),
                "model_id": details.get("model_id"),
                "description": details.get("description", ""),
                "stages": details.get("stages", []),
                "symptoms": details.get("symptoms", []),
                "disease_classes": details.get("disease_classes", [])
            })
        return crops

    @classmethod
    def get_crop_details(cls, crop_key: str) -> Optional[Dict[str, Any]]:
        """Returns details for a specific crop key."""
        config = cls.load_config()
        details = config.get(crop_key.lower())
        if details and isinstance(details, dict):
            details["key"] = crop_key.lower()
            details.setdefault("common_name", crop_key.capitalize())
            details.setdefault("display_name", details["common_name"])
            details.setdefault("category", "vegetables")
            details.setdefault("vision_support_status", "knowledge_review")
        return details

    @classmethod
    def _get_default_config(cls) -> Dict[str, Any]:
        return {
            "tomato": {
                "key": "tomato",
                "common_name": "Tomato",
                "display_name_en": "Tomato",
                "display_name_ta": "தக்காளி",
                "scientific_name": "Solanum lycopersicum",
                "category": "vegetables",
                "supported_status": "active",
                "disease_knowledge_status": "verified",
                "vision_support_status": "trained_model",
                "model_id": "tomato-v1",
                "is_active": True,
                "stages": [
                    {"key": "SEEDLING", "display_name": "Seedling"},
                    {"key": "VEGETATIVE", "display_name": "Vegetative"},
                    {"key": "FLOWERING", "display_name": "Flowering"},
                    {"key": "FRUITING", "display_name": "Fruiting"},
                    {"key": "HARVEST", "display_name": "Harvest"}
                ],
                "symptoms": [
                    "Yellow spots", "Brown spots", "Dark lesions", "Leaf curling",
                    "White patches", "Holes", "Wilting", "Discoloration", "Drying", "Other"
                ],
                "disease_classes": [
                    {"key": "Healthy", "display_name": "Healthy", "scientific_name": "N/A"},
                    {"key": "Early Blight", "display_name": "Early Blight", "scientific_name": "Alternaria solani"},
                    {"key": "Late Blight", "display_name": "Late Blight", "scientific_name": "Phytophthora infestans"},
                    {"key": "Leaf Spot", "display_name": "Septoria Leaf Spot", "scientific_name": "Septoria lycopersici"}
                ]
            }
        }
