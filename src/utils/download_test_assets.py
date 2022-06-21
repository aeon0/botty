import urllib.request
import zipfile
import os
import shutil

url = "https://github.com/bottytools/botty-test-assets/archive/refs/heads/main.zip"
extract_dir = "tmp"
asset_dir = "test/assets"

if not os.path.exists(asset_dir):
    print(f"Downloading test assets...")
    try:
        zip_path, _ = urllib.request.urlretrieve(url)
        print(f"Extracting {zip_path}...")
        with zipfile.ZipFile(zip_path, "r") as f:
            f.extractall(extract_dir)
        shutil.move(f"{extract_dir}/botty-test-assets-main/assets", asset_dir)
        shutil.rmtree(f"{extract_dir}")
        os.remove(zip_path)
        print(f"Download complete, delete {zip_path}")
    except:
        print(f"Could not retrieve test assets...")
