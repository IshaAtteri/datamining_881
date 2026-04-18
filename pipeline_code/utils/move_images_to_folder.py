import os
import shutil
from tqdm import tqdm
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.abspath(os.path.join(BASE_DIR, "../data/processed/wikipedia_html"))
DEST_DIR = os.path.abspath(os.path.join(BASE_DIR, "../data/processed/wikipedia_images"))

os.makedirs(DEST_DIR, exist_ok=True)

IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg")

all_images = []
for movie_folder in os.listdir(SOURCE_DIR):
    folder_path = os.path.join(SOURCE_DIR, movie_folder)
    if not os.path.isdir(folder_path):
        continue
    for fname in os.listdir(folder_path):
        if fname.lower().endswith(IMAGE_EXTS):
            all_images.append(os.path.join(folder_path, fname))

skipped = 0
copied = 0

for src_path in tqdm(all_images, desc="Copying images", unit="file"):
    fname = os.path.basename(src_path)
    dest_path = os.path.join(DEST_DIR, fname)
    if os.path.exists(dest_path):
        skipped += 1
        continue
    shutil.copy2(src_path, dest_path)
    copied += 1
