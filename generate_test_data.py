"""
generate_test_data.py - makes a SAFE dummy folder called TestDataset (230+ files).
Run:  python generate_test_data.py
WARNING: it deletes an old TestDataset folder first, so keep nothing important inside it.
"""
import os
import time
import random
import shutil
from PIL import Image

ROOT = "TestDataset"
FOLDERS = ["Photos/Holiday", "Photos/Family", "Documents/Reports", "Documents/Notes",
           "Music", "Videos", "Archives", "Downloads", "Projects/Old", "Projects/New"]
EXTENSIONS = [".jpg", ".png", ".pdf", ".docx", ".txt", ".mp3", ".wav", ".mp4", ".zip", ".xyz"]
FILES_PER_TYPE = 22

random.seed(1)
if os.path.exists(ROOT):
    shutil.rmtree(ROOT)
for folder in FOLDERS:
    os.makedirs(os.path.join(ROOT, folder))


def make_file(path, ext):
    if ext in (".jpg", ".png"):            # real small pictures
        img = Image.new("RGB", (random.randint(60, 600), random.randint(60, 400)),
                        (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        img.save(path)
    else:                                  # other types: random bytes
        size = random.randint(2000, 1500000) if ext == ".mp4" else random.randint(200, 60000)
        with open(path, "wb") as f:
            f.write(os.urandom(size))


created = []
for ext in EXTENSIONS:
    for i in range(1, FILES_PER_TYPE + 1):
        path = os.path.join(ROOT, random.choice(FOLDERS), f"{ext[1:]}_file_{i}{ext}")
        make_file(path, ext)
        created.append(path)

# 12 exact duplicates (same content, different name)
for source in random.sample(created, 12):
    name, ext = os.path.splitext(os.path.basename(source))
    shutil.copy2(source, os.path.join(ROOT, random.choice(FOLDERS), name + "_copy" + ext))

# Trap: same NAME but different CONTENT (must NOT be called duplicates)
for folder in ("Projects/Old", "Projects/New"):
    with open(os.path.join(ROOT, folder, "report_final.txt"), "w") as f:
        f.write("different text in " + folder + str(random.random()))

# Different modified dates (for the date filter)
now = time.time()
for folder, _, files in os.walk(ROOT):
    for name in files:
        t = now - random.randint(0, 400) * 86400
        os.utime(os.path.join(folder, name), (t, t))

total = sum(len(files) for _, _, files in os.walk(ROOT))