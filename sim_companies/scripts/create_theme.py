#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Theme Creator Script - Create new theme from images
Supports two modes:
  1. MANUAL MODE (--input-folders): Read pre-organized folders from scripts/
     - Folders named: {building}_{level}_{version}/
     - Script renames images and copies to theme folder
  2. CLASSIFICATION MODE: Use CLIP AI to auto-classify images (legacy)
"""

import os
import argparse
import numpy as np
from pathlib import Path
from collections import defaultdict
from PIL import Image
import shutil
import re
import subprocess

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False


# Paths
SCRIPT_DIR = Path(__file__).parent  # sim_companies/scripts
THEMES_DIR = SCRIPT_DIR.parent / "themes"  # sim_companies/themes
ORIGINAL_DIR = SCRIPT_DIR.parent / "original"  # sim_companies/original
ROOT_SCRIPTS_DIR = SCRIPT_DIR.parent.parent / "scripts"  # root scripts folder
OUTPUT_DIR = ROOT_SCRIPTS_DIR / "output"  # scripts/output (root level)
SYNC_SCRIPT = SCRIPT_DIR / "sync_versions.py"


def parse_folder_name(folder_name):
    """
    Parse folder name to extract building name and version.
    
    Format: {building}_{level}_{version}
    Examples:
    - academy_level_20_v2 -> ('academy_level_20', 2)
    - exchange_v1 -> ('exchange', 1)
    - factory_level_15_v3 -> ('factory_level_15', 3)
    """
    # Extract version from end
    version_match = re.search(r'_v(\d+)$', folder_name)
    if not version_match:
        return None, None
    
    version = int(version_match.group(1))
    building_name = folder_name[:version_match.start()]
    
    return building_name, version


def process_manual_folders(theme_name):
    """
    Process pre-organized folders from scripts/.
    
    Each folder format: {building}_{level}_{version}/
    Contains: manually sorted images
    
    Process:
    1. Find all matching folders in scripts/
    2. Rename each image: {image} -> {building}_{level}_{theme}_{version}.{ext}
    3. Copy to themes/{theme_name}/
    4. Delete source folder
    5. Run sync_versions.py
    """
    
    print("=" * 70)
    print(f"THEME CREATOR - MANUAL MODE: {theme_name.upper()}")
    print("=" * 70)
    
    # Find all folders in ROOT_SCRIPTS_DIR (not scripts/output!)
    if not ROOT_SCRIPTS_DIR.exists():
        print(f"❌ ERROR: Scripts directory not found: {ROOT_SCRIPTS_DIR}")
        return False
    
    # Look for folders matching pattern: {building}_{level}_{version}
    pattern = re.compile(r'^[a-z0-9_]+_v\d+$')
    folders_to_process = []
    
    print(f"\n📁 Scanning: {ROOT_SCRIPTS_DIR}")
    
    for item in sorted(ROOT_SCRIPTS_DIR.iterdir()):
        if not item.is_dir() or item.name.startswith('.'):
            continue
        
        if item.name in ['output', '__pycache__']:
            continue
        
        # Check if folder matches pattern
        if pattern.match(item.name):
            folders_to_process.append(item)
            print(f"   ✓ Found: {item.name}/")
    
    if not folders_to_process:
        print(f"\n❌ ERROR: No pre-organized folders found in {ROOT_SCRIPTS_DIR}")
        print(f"   Expected format: {{building}}_{{level}}_v{{version}}/")
        print(f"   Example: academy_level_20_v2/, exchange_v1/")
        return False
    
    print(f"\n📊 Found {len(folders_to_process)} folders to process")
    
    # Create theme folder
    print(f"\n📁 Creating theme folder: themes/{theme_name}/")
    theme_dir = THEMES_DIR / theme_name
    
    if theme_dir.exists():
        print(f"⚠️  Theme folder already exists: {theme_dir}")
        response = input("   Overwrite? (y/n): ").strip().lower()
        if response != 'y':
            print("❌ Aborted")
            return False
        shutil.rmtree(theme_dir)
    
    theme_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each folder
    print(f"\n📋 Processing folders...")
    total_images = 0
    total_copied = 0
    
    for folder_path in sorted(folders_to_process):
        building_name, version = parse_folder_name(folder_path.name)
        
        if building_name is None or version is None:
            print(f"\n   ⚠️  Skipping {folder_path.name}/ (invalid format)")
            continue
        
        print(f"\n   Processing: {folder_path.name}/")
        
        # Get all images in this folder
        images = list(folder_path.glob("*.png")) + list(folder_path.glob("*.jpg"))
        
        if not images:
            print(f"      ⚠️  No images found in this folder")
            continue
        
        print(f"      Found {len(images)} image(s)")
        total_images += len(images)
        
        # Process each image
        for img_path in sorted(images):
            ext = img_path.suffix
            
            # Create new filename: {building}_{theme}.{ext} (or with _v# if version > 1)
            if version > 1:
                new_filename = f"{building_name}_{theme_name}_v{version}{ext}"
            else:
                new_filename = f"{building_name}_{theme_name}{ext}"
            new_path = theme_dir / new_filename
            
            try:
                shutil.copy2(img_path, new_path)
                print(f"      ✓ {img_path.name} → {new_filename}")
                total_copied += 1
            except Exception as e:
                print(f"      ❌ Error copying {img_path.name}: {e}")
        
        # Delete the processed folder
        try:
            shutil.rmtree(folder_path)
            print(f"      ✓ Deleted folder: {folder_path.name}/")
        except Exception as e:
            print(f"      ⚠️  Could not delete folder: {e}")
    
    print(f"\n✅ Copied {total_copied}/{total_images} images")
    
    # Run sync_versions.py
    print(f"\n⚙️  Syncing versions with sync_versions.py...")
    try:
        result = subprocess.run(
            ["python", str(SYNC_SCRIPT)],
            cwd=str(SCRIPT_DIR),
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print("   ✓ Sync completed successfully")
        else:
            print(f"   ⚠️  Sync encountered issues: {result.stderr[:200]}")
    except Exception as e:
        print(f"   ⚠️  Could not run sync_versions.py: {e}")
    
    print("\n" + "=" * 70)
    print(f"✅ THEME '{theme_name}' CREATED SUCCESSFULLY")
    print("=" * 70)
    print(f"\nNew theme folder: sim_companies/themes/{theme_name}/")
    print(f"Images copied: {total_copied}")
    print("\nTheme is ready to use! Update your tamper script to use it.")
    
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a new Sim Companies theme"
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Name of the new theme (e.g., 'korea', 'thailand')"
    )
    parser.add_argument(
        "--input-folders",
        action="store_true",
        help="Use MANUAL mode: read pre-organized folders from scripts/"
    )
    parser.add_argument(
        "--output-path",
        default=str(OUTPUT_DIR),
        help=f"Path to input images (legacy classification mode, default: {OUTPUT_DIR})"
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.5,
        help="Confidence threshold (legacy mode, default: 0.5)"
    )
    
    args = parser.parse_args()
    
    if args.input_folders:
        # MANUAL MODE
        success = process_manual_folders(args.name)
    else:
        # LEGACY CLASSIFICATION MODE (disabled for now)
        print("❌ Classification mode requires CLIP model")
        print("   For manual classification, use: python create_theme.py --name <theme> --input-folders")
        success = False
    
    exit(0 if success else 1)
