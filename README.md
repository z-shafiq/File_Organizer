# File Organizer

**A Python-based desktop application for intelligent file scanning, analysis, duplicate detection, and safe file organization.**

File Organizer is a desktop utility designed to make file management more efficient through automated scanning, file categorization, storage analysis, and duplicate identification. It provides a graphical interface for exploring files, analyzing directory contents, and organizing files into categorized folders without modifying the original files.

---

## Overview

Managing large directories can become challenging when files are scattered across multiple folders and contain different formats. File Organizer addresses this problem by providing a centralized interface for analyzing and organizing files.

The application scans selected directories and their subdirectories, collects file information, identifies exact duplicates, and generates useful storage insights. It also provides a preview-based organization process that allows users to review planned changes before copying files.

## Key Features

### 1. Interactive Dashboard
- Displays total files and folders.
- Shows overall storage consumption.
- Displays the number of duplicate groups.
- Visualizes storage distribution by category.
- Highlights the ten largest files.

### 2. File Explorer
- Displays scanned file information in a structured table.
- Supports searching by filename, extension, and category.
- Filters files by category, file size, folder name, and modification date.
- Supports sorting by different file attributes.
- Provides detailed file information through double-click interaction.
- Extracts image dimensions and format information.

### 3. Duplicate File Detection
- Identifies exact duplicate files using SHA-256 hashing.
- Compares file sizes before performing content hashing.
- Groups files with identical content, even when filenames differ.
- Estimates potentially recoverable storage space.
- Reports duplicate files without automatically deleting anything.

### 4. Safe File Organization
- Categorizes files according to their extensions.
- Generates an organization preview before making changes.
- Copies files into category-based destination folders.
- Preserves original files.
- Prevents existing files from being overwritten.
- Provides an operation log showing successful copies and errors.

### 5. Data Export
- Exports file inventory information to CSV.
- Exports scan summaries and inventory data to JSON.
- Includes scan timestamps and the selected root directory in exported data.

### 6. SQLite Database Support
- Provides database initialization functionality.
- Creates tables for scan sessions and individual file records.
- Supports saving scan summaries and file inventory information.

---

## File Categories

The application currently recognizes the following categories:

| Category | Supported Formats |
|---|---|
| Images | JPG, JPEG, PNG, GIF, BMP, TIFF, WEBP |
| Documents | PDF, DOCX, DOC, TXT, XLSX, CSV, PPTX |
| Audio | MP3, WAV, FLAC, AAC, OGG |
| Video | MP4, MKV, MOV, AVI, WMV |
| Archives | ZIP, TAR, GZ, 7Z, RAR |
| Other | Unrecognized file extensions |

---

## Project Structure

The project uses a modular architecture, separating the graphical interface, file-processing operations, database functionality, and test-data generation.

```text
File_Organizer/
│
├── TestDataset/
│   └── Sample files and folders for testing
│
├── __pycache__/
│   └── Python-generated cache files
│
├── app.py
│   └── Main desktop application and graphical interface
│
├── backend.py
│   └── File scanning, categorization, filtering,
│       duplicate detection, organization, and exports
│
├── database.py
│   └── SQLite database initialization and
│       scan-data storage functions
│
├── generate_test_data.py
│   └── Generates sample files and test directories
│
├── .gitignore
│   └── Defines files excluded from version control
│
└── README.md
    └── Project documentation
```

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| CustomTkinter | Modern graphical user interface |
| Tkinter | File dialogs, messages, and interface components |
| Matplotlib | Dashboard charts and visualizations |
| SQLite | Database management |
| Pillow (PIL) | Image metadata extraction and test-image generation |
| Hashlib | SHA-256 file-content hashing |
| OS | File-system navigation and directory operations |
| Shutil | File copying and directory management |
| CSV & JSON | Exporting scan information |

---

## Installation and Setup

### Prerequisites

- Python 3.8 or later
- pip package manager

### 1. Clone the Repository

```bash
git clone https://github.com/z-shafiq/File_Organizer.git
```

### 2. Navigate to the Project Directory

```bash
cd File_Organizer
```

### 3. Install Dependencies

```bash
pip install customtkinter matplotlib pillow
```

### 4. Run the Application

```bash
python app.py
```

The application window should open, allowing you to select a directory and begin scanning.

---

## How to Use

1. **Launch the Application:** Run `app.py` to open the desktop interface.
2. **Select a Directory:** Click the "Select Folder & Scan" button.
3. **Analyze Files:** View file statistics and storage visualizations on the Dashboard.
4. **Explore Files:** Use the File Explorer to search, filter, sort, and inspect scanned files.
5. **Review Duplicates:** Open Duplicate Audit to view exact duplicate groups and estimated recoverable space.
6. **Preview Organization:** Navigate to Organizer and select a destination folder to generate an organization preview.
7. **Confirm Organization:** Review the preview and confirm the operation to copy files into categorized folders.
8. **Export Results:** Export the inventory as CSV or JSON using the available export buttons.

---

## Test Data Generation

The project includes a script for generating a sample dataset containing different file formats, nested directories, and duplicate-file examples.

Run the following command:

```bash
python generate_test_data.py
```

**Important:** This script deletes an existing `TestDataset` directory before generating a new one. Make sure it does not contain files you want to keep before running it.

---

## Safety and Data Integrity

File Organizer is designed with a preview-based organization workflow.

- Original files remain untouched during organization.
- Files are copied rather than moved.
- Existing destination files are not intentionally overwritten.
- Duplicate detection is read-only and does not delete files.
- Users can review the proposed organization plan before confirming the copy operation.

---

## Project Purpose

This project demonstrates the practical application of Python programming in desktop application development, file-system automation, data processing, and database management.

It was developed to explore modular programming, graphical user interface design, file metadata analysis, hashing algorithms, and safe file-handling practices.

## Author

**Z-Shafiq**

GitHub: [@z-shafiq](https://github.com/z-shafiq)

**Repository:** [File Organizer](https://github.com/z-shafiq/File_Organizer)

---

*If you find this project interesting, consider giving the repository a star. Contributions and suggestions are welcome.*
