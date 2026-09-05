import urllib.request
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SearchHealthy")

HEADERS = {'User-Agent': 'Mozilla/5.0'}

def check_repo_folder(owner_repo, path):
    url = f"https://api.github.com/repos/{owner_repo}/contents/{path}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if isinstance(data, list):
                files = [f for f in data if f.get('type') == 'file']
                dirs = [f for f in data if f.get('type') == 'dir']
                logger.info(f"{owner_repo}/{path}: {len(files)} files, {len(dirs)} dirs")
                return data
    except Exception as e:
        logger.debug(f"{owner_repo}/{path} error: {e}")
    return None

def main():
    candidate_repos = [
        "spMohanty/PlantVillage-Dataset",
        "ai-agriculture-circuits-and-systems/Plant_Village_Potato",
        "arjun-k-55/Potato-Leaf-Disease-Detection",
        "nabil-dewan/Potato-Leaf-Disease-Recognition",
        "samy-ghebache/Potato-Disease-Classification-Model",
        "Bibhuti5/Potato-Disease-Classification",
        "Vishal2546/Potato-Disease-Classification",
        "Akshat-6/Potato-Leaf_Disease_Detection-using-CNN",
        "diapaza/PotatoLeafDiseaseDataset",
        "pratikkayal/PlantDoc-Dataset"
    ]

    candidate_paths = [
        "raw/color/Potato___healthy",
        "Potato___healthy",
        "data/Potato___healthy",
        "dataset/Potato___healthy",
        "Dataset/Potato___healthy",
        "Potato_Healthy",
        "data/Potato_Healthy",
        "Healthy",
        "data/Healthy",
        "train/Potato___healthy",
        "train/Potato_Healthy",
        "val/Potato___healthy",
        "test/Potato___healthy",
        "Potato/Potato___healthy",
        "PlantVillage/Potato___healthy",
        "PlantVillage/Potato_Healthy"
    ]

    for repo in candidate_repos:
        for path in candidate_paths:
            res = check_repo_folder(repo, path)

if __name__ == "__main__":
    main()
