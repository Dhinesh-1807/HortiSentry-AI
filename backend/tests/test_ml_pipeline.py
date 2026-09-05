import os
import sys
import pytest
from pathlib import Path
from PIL import Image
import torch
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.config import MLConfig
from ml.transforms import get_train_transforms, get_eval_transforms
from ml.model import TomatoMobileNetV3
from ml.checkpoint import save_checkpoint, load_checkpoint, export_production_artifact
from ml.metrics import calculate_classification_metrics, calculate_confusion_matrix
from app.ml.predictor import MLSafetyWrapper
from app.ml.torch_predictor import TorchPredictor
from app.core.config import settings
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ml_config_loading():
    cfg = MLConfig()
    assert cfg.crop == "tomato"
    assert len(cfg.classes) == 4
    assert cfg.num_classes == 4
    assert cfg.image_size == 224
    assert cfg.batch_size > 0
    assert cfg.epochs == 10
    assert cfg.imbalance_strategy == "CLASS_WEIGHTED_LOSS"


def test_transforms_output_shape():
    train_tf = get_train_transforms(224)
    eval_tf = get_eval_transforms(224)

    dummy_pil = Image.fromarray(np.uint8(np.random.rand(300, 300, 3) * 255))
    
    train_tensor = train_tf(dummy_pil)
    eval_tensor = eval_tf(dummy_pil)

    assert train_tensor.shape == (3, 224, 224)
    assert eval_tensor.shape == (3, 224, 224)
    assert isinstance(train_tensor, torch.Tensor)
    assert isinstance(eval_tensor, torch.Tensor)


def test_model_forward_pass():
    model = TomatoMobileNetV3(num_classes=4, pretrained=False)
    model.eval()

    dummy_input = torch.randn(2, 3, 224, 224)
    with torch.no_grad():
        outputs = model(dummy_input)

    assert outputs.shape == (2, 4)


def test_checkpoint_save_and_load(tmp_path):
    model = TomatoMobileNetV3(num_classes=4, pretrained=False)
    ckpt_path = tmp_path / "test_ckpt.pt"

    classes = ["Healthy", "Early_Blight", "Late_Blight", "Septoria_Leaf_Spot"]
    config_dict = {"image_size": 224, "batch_size": 16}

    save_checkpoint(
        filepath=ckpt_path,
        model=model,
        epoch=1,
        optimizer=None,
        val_loss=0.25,
        val_acc=92.5,
        classes=classes,
        config_dict=config_dict
    )

    assert ckpt_path.exists()

    loaded = load_checkpoint(ckpt_path)
    assert loaded["model_version"] == "tomato-v1"
    assert loaded["val_acc"] == 92.5
    assert loaded["classes"] == classes
    assert "state_dict" in loaded


def test_metrics_calculation():
    y_true = [0, 0, 1, 1, 2, 2, 3, 3]
    y_pred = [0, 0, 1, 0, 2, 2, 3, 3] # 1 misclassification
    classes = ["Healthy", "Early_Blight", "Late_Blight", "Septoria_Leaf_Spot"]

    metrics = calculate_classification_metrics(y_true, y_pred, classes)

    assert metrics["total_samples"] == 8
    assert metrics["accuracy"] == 0.875
    assert "per_class" in metrics
    assert "Healthy" in metrics["per_class"]
    assert metrics["confusion_matrix"][1][0] == 1


def test_demo_vs_real_mode_isolation(tmp_path):
    wrapper = MLSafetyWrapper()
    assert wrapper.get_ml_mode() in ["DEMO", "REAL"]

    dummy_img = Image.new("RGB", (224, 224), color=(100, 150, 200))
    res = wrapper.predict(dummy_img)

    assert "predicted_class" in res
    assert "confidence" in res
    assert len(res["top_predictions"]) >= 1


def test_model_status_endpoint():
    response = client.get("/api/model-status")
    assert response.status_code == 200
    data = response.json()
    assert "ml_mode" in data
    assert "model_version" in data
    assert "class_count" in data
