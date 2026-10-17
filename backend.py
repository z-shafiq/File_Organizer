"""
backend.py - File System Engine (simple version)
Scanning, hashing, duplicates, filters, export and safe organizing.
"""

import osc
import csv
import json
import shutil
import hashlib
import datetime
from PIL import Image, UnidentifiedImageError

# Which extension belongs to which category
FILE_CATEGORIES = {
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
    'Documents': ['.pdf', '.docx', '.doc', '.txt', '.xlsx', '.csv', '.pptx'],
    'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
    'Video': ['.mp4', '.mkv', '.mov', '.avi', '.wmv'],
    'Archives': ['.zip', '.tar', '.gz', '.7z', '.rar']
}
ALL_CATEGORIES = list(FILE_CATEGORIES.keys()) + ['Other']


def get_file_category(extension):
    """Unknown extensions go to 'Other' (so nothing crashes)."""
    for category, extensions in FILE_CATEGORIES.items():
        if extension.lower() in extensions:
            return category
    return 'Other'


def format_size(num_bytes):
    """Bytes -> B / KB / MB / GB (1 KB = 1024 bytes)."""
    size = float(num_bytes)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024 or unit == 'GB':
            return f"{int(size)} B" if unit == 'B' else f"{size:.2f} {unit}"
        size /= 1024


def scan_directory(root_dir):
    """
    Walks through the folder and ALL its subfolders (recursion).
    Returns: (list of file records, number of folders, list of problems)
    """
    inventory = []
    problems = []
    folder_count = 0

    def on_error(err):                      # called when a folder can't be opened
        problems.append(str(err.filename))

    for root, dirs, files in os.walk(root_dir, onerror=on_error):
        folder_count += len(dirs)
        for file_name in files:
            full_path = os.path.join(root, file_name)
            ext = os.path.splitext(file_name)[1].lower()
            try:
                info = os.stat(full_path)   # size and times of the file
            except OSError:                 # locked / no permission / missing
                problems.append(full_path)
                continue

            inventory.append({
                'name': file_name,
                'path': full_path,                                   # absolute path
                'relative_path': os.path.relpath(full_path, root_dir),  # path from root
                'folder': os.path.relpath(root, root_dir),
                'extension': ext if ext else 'none',
                'category': get_file_category(ext),
                'size_bytes': info.st_size,
                'size_human': format_size(info.st_size),
                # on Windows st_ctime is the creation time
                'created_at': datetime.datetime.fromtimestamp(info.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'modified_at': datetime.datetime.fromtimestamp(info.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            })
    return inventory, folder_count, problems


def calculate_sha256(file_path):
    """SHA-256 fingerprint of the file CONTENT (read in small chunks)."""
    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
    except OSError:
        return None


def find_duplicates(inventory):
    """
    Step 1: group files that have exactly the same size (fast).
    Step 2: only for those, compare SHA-256 (slow but exact).
    Same name does NOT mean same file - only same content does.
    """
    size_groups = {}
    for rec in inventory:
        if rec['size_bytes'] > 0:           # ignore empty files
            size_groups.setdefault(rec['size_bytes'], []).append(rec['path'])

    groups = []
    for size, paths in size_groups.items():
        if len(paths) > 1:
            hash_groups = {}
            for p in paths:
                h = calculate_sha256(p)
                if h:
                    hash_groups.setdefault(h, []).append(p)
            for h, same_files in hash_groups.items():
                if len(same_files) > 1:
                    groups.append({
                        'hash': h,
                        'paths': same_files,
                        'size_bytes': size,
                        'recoverable_bytes': size * (len(same_files) - 1),
                    })
    return groups


def extract_image_metadata(file_path):
    """Format and dimensions of an image."""
    try:
        with Image.open(file_path) as img:
            return {'dimensions': f"{img.width} x {img.height} px", 'format': img.format or 'Unknown'}
    except (UnidentifiedImageError, OSError):
        return {'dimensions': 'N/A', 'format': 'Unsupported/Corrupted'}


def filter_inventory(inventory, query='', category='All', min_mb=None, max_mb=None,
                     folder='', date_from='', date_to=''):
    """All filters work together (a file must pass every one). Dates: YYYY-MM-DD."""
    result = []
    for r in inventory:
        if query and query.lower() not in (r['name'] + r['extension'] + r['category']).lower():
            continue
        if category != 'All' and r['category'] != category:
            continue
        if min_mb is not None and r['size_bytes'] < min_mb * 1024 * 1024:
            continue
        if max_mb is not None and r['size_bytes'] > max_mb * 1024 * 1024:
            continue
        if folder and folder.lower() not in r['folder'].lower():
            continue
        day = r['modified_at'][:10]
        if date_from and day < date_from:
            continue
        if date_to and day > date_to:
            continue
        result.append(r)
    return result


def export_inventory_csv(inventory, root_dir, scan_time, output_path):
    """CSV: every row also carries the scan time and root folder."""
    if not inventory:
        return False
    try:
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            headers = ['scan_time', 'root_folder'] + list(inventory[0].keys())
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for rec in inventory:
                writer.writerow({'scan_time': scan_time, 'root_folder': root_dir, **rec})
        return True
    except OSError:
        return False


def export_inventory_json(inventory, summary, root_dir, scan_time, output_path):
    """JSON: scan time + root folder + summary + all files."""
    data = {'scan_time': scan_time, 'root_folder': root_dir, 'summary': summary, 'files': inventory}
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return True
    except OSError:
        return False


def unique_path(path, used):
    """If a file with this name exists, use name (1).ext, name (2).ext ... (never overwrite)."""
    base, ext = os.path.splitext(path)
    new_path, n = path, 1
    while os.path.exists(new_path) or new_path.lower() in used:
        new_path = f"{base} ({n}){ext}"
        n += 1
    return new_path


def plan_organization(inventory, target_dir):
    """Step 1: only DECIDE what would be copied where. Nothing is touched yet."""
    plan, used = [], set()
    for rec in inventory:
        wanted = os.path.join(target_dir, rec['category'], rec['name'])
        final = unique_path(wanted, used)
        used.add(final.lower())
        plan.append((rec['path'], final))
    return plan


def organize_files(plan):
    """Step 2: copy the files according to the plan. Originals stay untouched."""
    logs = []
    for source, destination in plan:
        try:
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            final = unique_path(destination, set())   # re-check: never overwrite
            shutil.copy2(source, final)
            logs.append(f"[COPIED] {source}  ->  {final}")
        except OSError as err:
            logs.append(f"[ERROR] {source}: {err}")
    return logs