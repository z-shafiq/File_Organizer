# database.py
import sqlite3

DB_NAME = "file_organizer.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    """Create tables for scans and inventory files if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table for general scan sessions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_time TEXT,
            root_folder TEXT,
            total_files INTEGER,
            total_folders INTEGER,
            total_size TEXT,
            duplicate_groups INTEGER,
            recoverable_space TEXT
        )
    """)
    
    # Table for individual files found during the scan
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id INTEGER,
            name TEXT,
            path TEXT,
            relative_path TEXT,
            folder TEXT,
            extension TEXT,
            category TEXT,
            size_bytes INTEGER,
            size_human TEXT,
            created_at TEXT,
            modified_at TEXT,
            FOREIGN KEY (scan_id) REFERENCES scans(id)
        )
    """)
    
    conn.commit()
    conn.close()

def save_scan_to_db(root_dir, scan_time, summary, inventory):
    """Save a complete scan session and its files into SQLite."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    # Insert summary session info
    cursor.execute("""
        INSERT INTO scans (scan_time, root_folder, total_files, total_folders, total_size, duplicate_groups, recoverable_space)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        scan_time,
        root_dir,
        summary['total_files'],
        summary['total_folders'],
        summary['total_size'],
        summary['duplicate_groups'],
        summary['recoverable_space']
    ))
    scan_id = cursor.lastrowid
    
    # Insert all inventory files linked to this scan_id
    file_rows = []
    for rec in inventory:
        file_rows.append((
            scan_id,
            rec['name'],
            rec['path'],
            rec['relative_path'],
            rec['folder'],
            rec['extension'],
            rec['category'],
            rec['size_bytes'],
            rec['size_human'],
            rec['created_at'],
            rec['modified_at']
        ))
        
    cursor.executemany("""
        INSERT INTO files (scan_id, name, path, relative_path, folder, extension, category, size_bytes, size_human, created_at, modified_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, file_rows)
    
    conn.commit()
    conn.close()
    return scan_id
