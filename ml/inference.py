import sys
import time
import argparse
from pathlib import Path
import json
import torch
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.transforms import get_eval_transforms
from ml.model import TomatoMobileNetV3
from ml.checkpoint import load_checkpoint

def run_single_inference(image_path: Path, artifact_path: Path = None):
    """Run inference on a single image path using trained PyTorch model artifact."""
    image_path = Path(image_path)
    if not image_path.exists():
        print(f"Error: Image file not found at {image_path}")
        sys.exit(1)

    if artifact_path is None:
        artifact_path = PROJECT_ROOT / "ml" / "artifacts" / "tomato_v1.pt"
        if not artifact_path.exists():
            artifact_path = PROJECT_ROOT / "ml" / "checkpoints" / "tomato_mobilenetv3_best.pt"

    if not artifact_path.exists():
        print(f"Error: Model artifact not found at {artifact_path}. Please run 'python -m ml.train' first.")
        sys.exit(1)

    # Load artifact
    checkpoint = load_checkpoint(artifact_path, map_location="cpu")
    classes = checkpoint.get("classes", ["Healthy", "Early_Blight", "Late_Blight", "Septoria_Leaf_Spot"])
    
    # Load model
    model = TomatoMobileNetV3(num_classes=len(classes), pretrained=False)
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()

    # Preprocess Image
    transform = get_eval_transforms(image_size=checkpoint.get("image_size", 224))
    with Image.open(image_path) as img:
        pil_img = img.convert("RGB")
    
    tensor_img = transform(pil_img).unsqueeze(0)

    # Predict
    start_time = time.time()
    with torch.no_grad():
        outputs = model(tensor_img)
        probs = torch.softmax(outputs, dim=1).squeeze(0)

    inference_ms = round((time.time() - start_time) * 1000.0, 2)

    # Extract Top-3 predictions
    top_prob, top_indices = torch.topk(probs, k=min(3, len(classes)))
    
    top_predictions = []
    for p, idx in zip(top_prob.tolist(), top_indices.tolist()):
        top_predictions.append({
            "class_name": classes[idx],
            "confidence": round(p, 4)
        })

    predicted_class = classes[top_indices[0].item()]
    confidence = round(top_prob[0].item(), 4)

    result = {
        "image_path": str(image_path),
        "predicted_class": predicted_class,
        "confidence": confidence,
        "top_predictions": top_predictions,
        "model_version": checkpoint.get("model_version", "tomato-v1"),
        "inference_time_ms": inference_ms,
        "is_demo_mode": False
    }

    print("\n--- HortiSentry Real ML Model Inference Result ---")
    print(json.dumps(result, indent=2))
    return result

def main():
    parser = argparse.ArgumentParser(description="HortiSentry Real ML Model Single Image Inference CLI")
    parser.add_argument("--image", "-i", type=str, required=True, help="Path to leaf image file for disease inference.")
    parser.add_argument("--artifact", "-a", type=str, default=None, help="Optional path to model artifact file (.pt).")

    args = parser.parse_args()
    run_single_inference(Path(args.image), Path(args.artifact) if args.artifact else None)

if __name__ == "__main__":
    main()
