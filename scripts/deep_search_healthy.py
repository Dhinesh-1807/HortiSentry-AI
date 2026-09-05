import urllib.request
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DeepSearch")

HEADERS = {'User-Agent': 'Mozilla/5.0'}

def search_github(query):
    url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return [item['full_name'] for item in data.get('items', [])]
    except Exception as e:
        logger.error(f"Search error: {e}")
        return []

def scan_repo(repo):
    url = f"https://api.github.com/repos/{repo}/git/trees/main?recursive=1"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            tree = data.get('tree', [])
            healthy_files = [
                item['path'] for item in tree
                if ('potato' in item['path'].lower() or 'healthy' in item['path'].lower())
                and item['path'].lower().endswith(('.jpg', '.jpeg', '.png'))
                and ('healthy' in item['path'].lower() or 'leaf' in item['path'].lower())
            ]
            if healthy_files:
                logger.info(f"{repo}: Found {len(healthy_files)} candidate image files!")
                print(f"=== {repo} ===")
                for f in healthy_files[:10]:
                    print("  ", f)
    except Exception as e:
        pass

def main():
    repos = search_github("potato leaf healthy dataset")
    repos += search_github("potato disease classification dataset")
    repos = list(dict.fromkeys(repos))
    logger.info(f"Scanning {len(repos)} repos...")
    for r in repos[:20]:
        scan_repo(r)

if __name__ == "__main__":
    main()
