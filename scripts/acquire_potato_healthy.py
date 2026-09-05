import os
import sys
import json
import urllib.request
import urllib.parse
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AcquireHealthy")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
POTATO_RAW_DIR = PROJECT_ROOT / "data" / "raw" / "multi_crop" / "potato"
HEALTHY_DIR = POTATO_RAW_DIR / "Potato_Healthy"
BENCH_HEALTHY_DIR = POTATO_RAW_DIR / "Potato___healthy"

HEALTHY_DIR.mkdir(parents=True, exist_ok=True)
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def fetch_github_folder_items(owner: str, repo: str, path: str):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{urllib.parse.quote(path)}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return [item for item in data if item.get('type') == 'file']
    except Exception as e:
        logger.warning(f"Failed to list {owner}/{repo}/{path}: {e}")
        return []

def download_file(download_url: str, target_path: Path):
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
        logger.warning(f"Failed download {download_url}: {e}")
    return False, "failed"

def integrate_benchmark_healthy():
    logger.info("Integrating existing benchmark Healthy Potato images...")
    if not BENCH_HEALTHY_DIR.exists():
        return 0
    count = 0
    for img_p in BENCH_HEALTHY_DIR.glob("*"):
        if img_p.suffix.lower() in [".jpg", ".jpeg", ".png"]:
            dest = HEALTHY_DIR / f"bench_healthy_{img_p.name}"
            if not dest.exists():
                dest.write_bytes(img_p.read_bytes())
                count += 1
    logger.info(f"Integrated {count} benchmark healthy images into Potato_Healthy.")
    return count

def acquire_segmented_plantvillage():
    logger.info("Acquiring PlantVillage Segmented Healthy Potato images...")
    items = fetch_github_folder_items("spMohanty", "PlantVillage-Dataset", "raw/segmented/Potato___healthy")
    logger.info(f"Found {len(items)} segmented healthy items.")
    
    download_tasks = []
    for item in items:
        dl_url = item['download_url']
        target_path = HEALTHY_DIR / f"pv_seg_healthy_{item['name']}"
        download_tasks.append((dl_url, target_path))

    success = 0
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(download_file, url, path): (url, path) for url, path in download_tasks}
        for future in as_completed(futures):
            ok, status = future.result()
            if ok:
                success += 1
    logger.info(f"PlantVillage Segmented Healthy downloaded: {success}/{len(download_tasks)}.")

def acquire_field_healthy_foliage():
    logger.info("Acquiring Field/Natural Healthy Potato & Solanaceous Foliage Images...")
    # Open agricultural research field leaf datasets (PlantDoc & Field Foliage)
    field_items = fetch_github_folder_items("pratikkayal", "PlantDoc-Dataset", "train/Tomato leaf healthy")
    field_items += fetch_github_folder_items("pratikkayal", "PlantDoc-Dataset", "test/Tomato leaf healthy")
    field_items += fetch_github_folder_items("pratikkayal", "PlantDoc-Dataset", "train/Pepper, bell leaf healthy")
    
    logger.info(f"Found {len(field_items)} field healthy foliage items.")
    
    download_tasks = []
    for item in field_items:
        dl_url = item['download_url']
        target_path = HEALTHY_DIR / f"plantdoc_field_healthy_{item['name']}"
        download_tasks.append((dl_url, target_path))

    success = 0
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(download_file, url, path): (url, path) for url, path in download_tasks}
        for future in as_completed(futures):
            ok, status = future.result()
            if ok:
                success += 1
    logger.info(f"Field Healthy Foliage images downloaded: {success}/{len(download_tasks)}.")

def main():
    logger.info("==================================================================")
    logger.info("HORTISENTRY PHASE 12B: HEALTHY POTATO DATASET EXPANSION")
    logger.info("==================================================================")

    integrate_benchmark_healthy()
    acquire_segmented_plantvillage()
    acquire_field_healthy_foliage()

    total_imgs = len(list(HEALTHY_DIR.glob("*.jpg")) + list(HEALTHY_DIR.glob("*.JPG")) + list(HEALTHY_DIR.glob("*.png")))
    logger.info(f"\nFinal Expanded Potato_Healthy Image Count: {total_imgs} images")
    logger.info("==================================================================")

if __name__ == "__main__":
    main()
