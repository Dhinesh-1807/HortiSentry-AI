import sys
import os
import json
import urllib.request
import urllib.parse
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AcquirePotatoData")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
POTATO_RAW_DIR = PROJECT_ROOT / "data" / "raw" / "multi_crop" / "potato"

CANONICAL_CLASSES = {
    "Potato_Healthy": POTATO_RAW_DIR / "Potato_Healthy",
    "Potato_Early_Blight": POTATO_RAW_DIR / "Potato_Early_Blight",
    "Potato_Late_Blight": POTATO_RAW_DIR / "Potato_Late_Blight"
}

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def fetch_github_folder_items(owner: str, repo: str, path: str):
    """Fetch item listing from GitHub REST API."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{urllib.parse.quote(path)}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return [item for item in data if item.get('type') == 'file']
    except Exception as e:
        logger.error(f"Failed to list GitHub folder {path}: {e}")
        return []

def download_file(download_url: str, target_path: Path):
    """Download a single image file if not already present."""
    if target_path.exists() and target_path.stat().st_size > 0:
        return True, "already_exists"
    req = urllib.request.Request(download_url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            if len(content) > 0:
                with open(target_path, "wb") as f:
                    f.write(content)
                return True, "downloaded"
    except Exception as e:
        logger.warning(f"Failed download from {download_url}: {e}")
    return False, "failed"

def acquire_plantvillage_potato():
    logger.info("\n--- Acquiring PlantVillage Potato Dataset ---")
    owner, repo = "spMohanty", "PlantVillage-Dataset"
    
    mapping = {
        "raw/color/Potato___healthy": ("Potato_Healthy", "pv_healthy"),
        "raw/color/Potato___Early_blight": ("Potato_Early_Blight", "pv_eb"),
        "raw/color/Potato___Late_blight": ("Potato_Late_Blight", "pv_lb")
    }

    download_tasks = []
    for remote_path, (canonical_cls, prefix) in mapping.items():
        out_dir = CANONICAL_CLASSES[canonical_cls]
        out_dir.mkdir(parents=True, exist_ok=True)
        
        items = fetch_github_folder_items(owner, repo, remote_path)
        logger.info(f"Found {len(items)} items in {remote_path}")
        
        for item in items:
            fname = item['name']
            dl_url = item['download_url']
            target_name = f"{prefix}_{fname}"
            target_path = out_dir / target_name
            download_tasks.append((dl_url, target_path))

    logger.info(f"Downloading {len(download_tasks)} PlantVillage images in parallel...")
    success_count = 0
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(download_file, url, path): (url, path) for url, path in download_tasks}
        for future in as_completed(futures):
            ok, status = future.result()
            if ok:
                success_count += 1

    logger.info(f"PlantVillage download completed: {success_count}/{len(download_tasks)} images ready.")

def acquire_plantdoc_potato():
    logger.info("\n--- Acquiring PlantDoc Potato Dataset (Field Images) ---")
    owner, repo = "pratikkayal", "PlantDoc-Dataset"

    mapping = [
        ("train/Potato leaf early blight", "Potato_Early_Blight", "plantdoc_eb"),
        ("test/Potato leaf early blight", "Potato_Early_Blight", "plantdoc_eb"),
        ("train/Potato leaf late blight", "Potato_Late_Blight", "plantdoc_lb"),
        ("test/Potato leaf late blight", "Potato_Late_Blight", "plantdoc_lb"),
    ]

    download_tasks = []
    for remote_path, canonical_cls, prefix in mapping:
        out_dir = CANONICAL_CLASSES[canonical_cls]
        out_dir.mkdir(parents=True, exist_ok=True)

        items = fetch_github_folder_items(owner, repo, remote_path)
        logger.info(f"Found {len(items)} items in {remote_path}")

        for item in items:
            fname = item['name']
            dl_url = item['download_url']
            target_name = f"{prefix}_{fname}"
            target_path = out_dir / target_name
            download_tasks.append((dl_url, target_path))

    logger.info(f"Downloading {len(download_tasks)} PlantDoc images in parallel...")
    success_count = 0
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(download_file, url, path): (url, path) for url, path in download_tasks}
        for future in as_completed(futures):
            ok, status = future.result()
            if ok:
                success_count += 1

    logger.info(f"PlantDoc download completed: {success_count}/{len(download_tasks)} field images ready.")

def main():
    logger.info("==================================================================")
    logger.info("HORTISENTRY PHASE 12A: POTATO DATASET ACQUISITION SCRIPT")
    logger.info("==================================================================")

    for path in CANONICAL_CLASSES.values():
        path.mkdir(parents=True, exist_ok=True)

    acquire_plantvillage_potato()
    acquire_plantdoc_potato()

    # Log summary of raw directory
    logger.info("\n--- Potato Raw Directory Summary ---")
    total_imgs = 0
    for cls_name, cls_dir in CANONICAL_CLASSES.items():
        imgs = list(cls_dir.glob("*.jpg")) + list(cls_dir.glob("*.JPG")) + list(cls_dir.glob("*.png")) + list(cls_dir.glob("*.webp"))
        logger.info(f"{cls_name}: {len(imgs)} images")
        total_imgs += len(imgs)

    logger.info(f"\nTotal Raw Potato Images Acquired: {total_imgs}")
    logger.info("==================================================================")

if __name__ == "__main__":
    main()
