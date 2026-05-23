#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Create Folders for Manual Sorting
Scans existing themes and creates empty folders in scripts/output/
Each folder named: {building}_{level}_{version}
User will manually sort cleaned images into these folders
"""

import os
import re
from pathlib import Path
from collections import defaultdict

# Paths
SCRIPT_DIR = Path(__file__).parent  # sim_companies/scripts
THEMES_DIR = SCRIPT_DIR.parent / "themes"  # sim_companies/themes
ROOT_SCRIPTS_DIR = SCRIPT_DIR.parent.parent / "scripts"  # root scripts folder
OUTPUT_DIR = ROOT_SCRIPTS_DIR / "output"  # scripts/output


def parse_filename(filename, theme_folder_name):
    """
    Parse filename to extract building name and version.
    
    Args:
        filename: The image filename (e.g., 'academy_level_20_japan_v2.png')
        theme_folder_name: The theme folder name (e.g., 'japan', 'galaxy_v2')
    
    Returns:
        (building_name, version) tuple
        building_name includes level if present (e.g., 'academy_level_20')
        version defaults to 1 if not specified in filename
    
    Examples:
    - filename='academy_level_20_japan_v2.png', theme='japan' -> ('academy_level_20', 2)
    - filename='exchange_japan.png', theme='japan' -> ('exchange', 1)  # Default v1
    - filename='exchange_galaxy_originals_only_v3.png', theme='galaxy_originals_only' -> ('exchange', 3)
    """
    ext = Path(filename).suffix  # .png or .jpg
    name_without_ext = filename.replace(ext, "")
    
    # Extract version first if it exists (e.g., "_v4")
    version_match = re.search(r'_v(\d+)$', name_without_ext)
    if version_match:
        version = int(version_match.group(1))
        name_without_version = name_without_ext[:version_match.start()]
    else:
        # NO VERSION FOUND - default to v1
        version = 1
        name_without_version = name_without_ext
    
    # Remove the theme name suffix from the filename
    # The theme name is exactly the folder name we're in
    # E.g., if in 'galaxy_originals_only' folder, remove '_galaxy_originals_only'
    if name_without_version.endswith('_' + theme_folder_name):
        building_name = name_without_version[:-len('_' + theme_folder_name)]
    else:
        # Fallback: just use what's left if theme name doesn't match
        building_name = name_without_version
    
    return building_name, version


def get_building_configs():
    """
    Scan all themes and extract unique building+version combinations.
    Returns dict: {building_name: highest_version}
    
    Skips theme folders with 'original' in the name (duplicates).
    For each building, tracks the HIGHEST version across ALL themes.
    """
    building_versions = defaultdict(int)  # building -> max version found
    
    if not THEMES_DIR.exists():
        print(f"Error: Themes directory not found: {THEMES_DIR}")
        return {}
    
    print(f"\n📚 Scanning themes in: {THEMES_DIR}")
    
    for theme_dir in sorted(THEMES_DIR.iterdir()):
        if not theme_dir.is_dir() or theme_dir.name.startswith('.'):
            continue
        
        # SKIP folders with 'original' in name (they're duplicates)
        if 'original' in theme_dir.name.lower():
            print(f"\n   Theme: {theme_dir.name} [SKIPPED - contains 'original']")
            continue
        
        print(f"\n   Theme: {theme_dir.name}")
        
        for filename in sorted(os.listdir(theme_dir)):
            if not filename.endswith(('.png', '.jpg')):
                continue
            
            # Pass the theme folder name so parse_filename can remove it correctly
            building_name, version = parse_filename(filename, theme_dir.name)
            
            if building_name:
                old_version = building_versions[building_name]
                building_versions[building_name] = max(old_version, version)
                
                if version > old_version:
                    print(f"      {building_name}: v{version} (updated from v{old_version})")
                elif old_version == 0:
                    print(f"      {building_name}: v{version}")
    
    return dict(building_versions)


def create_folders(building_configs):
    """
    Create folders in scripts/output/ for each building+version combo.
    Folder naming: {building}_{version}
    """
    if not OUTPUT_DIR.exists():
        print(f"\nError: Output directory not found: {OUTPUT_DIR}")
        return 0
    
    print(f"\n📁 Creating folders in: {OUTPUT_DIR}")
    
    created_count = 0
    
    for building_name in sorted(building_configs.keys()):
        version = building_configs[building_name]
        folder_name = f"{building_name}_v{version}"
        folder_path = OUTPUT_DIR / folder_name
        
        if folder_path.exists():
            print(f"   ⚠️  Already exists: {folder_name}/")
        else:
            try:
                folder_path.mkdir(parents=True, exist_ok=True)
                print(f"   ✓ Created: {folder_name}/")
                created_count += 1
            except Exception as e:
                print(f"   ❌ Error creating {folder_name}: {e}")
    
    return created_count


def main():
    """Main function."""
    print("=" * 70)
    print("CREATE FOLDERS FOR MANUAL SORTING")
    print("=" * 70)
    
    # Get all building+version combinations
    building_configs = get_building_configs()
    
    if not building_configs:
        print("\n❌ No buildings found in themes!")
        return False
    
    print(f"\n📊 Found {len(building_configs)} unique buildings")
    
    # Create folders
    created_count = create_folders(building_configs)
    
    print("\n" + "=" * 70)
    print(f"✅ FOLDERS CREATED: {created_count}")
    print("=" * 70)
    print(f"\nNext steps:")
    print(f"1. Open: {OUTPUT_DIR}")
    print(f"2. Drag cleaned images into the correct folders")
    print(f"3. Drag completed folders up to: {ROOT_SCRIPTS_DIR}")
    print(f"4. Run: python sim_companies/scripts/create_theme.py --name <theme_name>")
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
