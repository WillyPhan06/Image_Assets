#!/usr/bin/env python3
"""
Version Synchronizer for Sim Companies Themes
Aligns image versions across Japan and Vietnam themes
Updates tamper_monkey_skin_mod.js to point to latest versions
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

# Define theme directories
THEMES_DIR = Path(__file__).parent.parent / "themes"
SCRIPT_FILE = Path(__file__).parent / "tamper_monkey_skin_mod.js"


def get_theme_directories():
    """Dynamically discover all theme directories."""
    if not THEMES_DIR.exists():
        print(f"Error: Themes directory not found: {THEMES_DIR}")
        return {}
    
    themes = {}
    for item in sorted(THEMES_DIR.iterdir()):
        if item.is_dir() and not item.name.startswith('.'):
            themes[item.name] = item
    
    return themes


def parse_filename(filename):
    """
    Parse filename to extract building name and version.
    Examples:
    - sales_office_level_15_japan_v4.png -> ('sales_office_level_15', 4, '.png')
    - exchange_japan.png -> ('exchange', None, '.png')
    """
    ext = Path(filename).suffix  # .png or .jpg
    name_without_ext = filename.replace(ext, "")
    
    # Extract version first if it exists (e.g., "_v4")
    version_match = re.search(r'_v(\d+)$', name_without_ext)
    if version_match:
        version = int(version_match.group(1))
        name_without_version = name_without_ext[:version_match.start()]
    else:
        version = None
        name_without_version = name_without_ext
    
    # Now remove theme suffix (japan/vietnam) from the remaining name
    name_without_theme = re.sub(r'_(japan|vietnam)$', '', name_without_version)
    base_name = name_without_theme
    
    return base_name, version, ext


def get_files_by_theme(theme_dir):
    """Get all image files organized by building name."""
    files_dict = defaultdict(lambda: {'files': [], 'versions': []})
    
    if not theme_dir.exists():
        print(f"Warning: Theme directory not found: {theme_dir}")
        return files_dict
    
    for filename in sorted(os.listdir(theme_dir)):
        if filename.endswith(('.png', '.jpg')):
            base_name, version, ext = parse_filename(filename)
            files_dict[base_name]['files'].append(filename)
            if version is not None:
                files_dict[base_name]['versions'].append(version)
    
    return files_dict


def get_max_version(base_name, all_themes_dicts):
    """Get the maximum version for a building across all themes."""
    versions = []
    
    for theme_name, theme_dict in all_themes_dicts.items():
        if base_name in theme_dict:
            versions.extend(theme_dict[base_name]['versions'])
    
    return max(versions) if versions else None


def rename_file(old_path, new_path):
    """Safely rename a file."""
    if old_path == new_path:
        return True
    
    if new_path.exists():
        print(f"  WARNING: Target already exists: {new_path.name}")
        return False
    
    try:
        old_path.rename(new_path)
        print(f"  RENAMED: {old_path.name} -> {new_path.name}")
        return True
    except Exception as e:
        print(f"  ERROR renaming {old_path.name}: {e}")
        return False


def sync_versions():
    """Main function to sync versions across themes."""
    print("=" * 70)
    print("SIM COMPANIES THEME VERSION SYNCHRONIZER")
    print("=" * 70)
    
    # Get all theme directories dynamically
    themes = get_theme_directories()
    
    if not themes:
        print(f"Error: No themes found in {THEMES_DIR}")
        return
    
    print(f"\nDiscovered themes: {', '.join(themes.keys())}")
    
    # Get files from all themes
    all_themes_dicts = {}
    for theme_name, theme_path in themes.items():
        all_themes_dicts[theme_name] = get_files_by_theme(theme_path)
    
    # Collect all unique building names
    all_buildings = set()
    for theme_dict in all_themes_dicts.values():
        all_buildings.update(theme_dict.keys())
    
    print(f"\nFound {len(all_buildings)} unique buildings across themes")
    
    # Track updates for script
    updates_needed = {}
    
    # Process each building
    for building_name in sorted(all_buildings):
        max_version = get_max_version(building_name, all_themes_dicts)
        
        if max_version is None:
            continue  # Skip buildings with no versions
        
        print(f"\n📦 {building_name}")
        print(f"   Max version found: v{max_version}")
        
        # Update each theme
        for theme_name, theme_path in themes.items():
            theme_dict = all_themes_dicts[theme_name]
            
            if building_name in theme_dict:
                for filename in theme_dict[building_name]['files']:
                    base, ver, ext = parse_filename(filename)
                    if ver != max_version:
                        old_file = theme_path / filename
                        new_filename = f"{base}_{theme_name}_v{max_version}{ext}"
                        new_file = theme_path / new_filename
                        rename_file(old_file, new_file)
                        updates_needed[base] = f"{base}_v{max_version}{ext}"
                    else:
                        updates_needed[base] = f"{base}_v{max_version}{ext}"
    
    # Update the tamper monkey script
    if updates_needed:
        print("\n" + "=" * 70)
        print("UPDATING tamper_monkey_skin_mod.js")
        print("=" * 70)
        update_script(updates_needed)
    
    print("\n" + "=" * 70)
    print("✅ SYNCHRONIZATION COMPLETE")
    print("=" * 70)


def update_script(updates_dict):
    """Update the REPLACEMENTS object in tamper_monkey_skin_mod.js."""
    if not SCRIPT_FILE.exists():
        print(f"Warning: Script file not found: {SCRIPT_FILE}")
        return
    
    with open(SCRIPT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # For each building that needs updating
    for base_name, new_image_name in sorted(updates_dict.items()):
        # Find all occurrences of this building in REPLACEMENTS
        # Pattern: image: "BASE_NAME_vX.ext"
        
        # Try different patterns since naming can vary
        patterns = [
            # Match with version: base_name_v\d+ (without extension, since new_image_name has it)
            (rf'(image:\s*["\']){base_name}_v\d+\.(png|jpg)["\']', rf'\1{new_image_name}"'),
            # Match without version: base_name (without extension)
            (rf'(image:\s*["\']){base_name}\.(png|jpg)["\']', rf'\1{new_image_name}"'),
        ]
        
        for pattern, replacement in patterns:
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                print(f"  ✓ Updated {base_name} -> {new_image_name}")
    
    if content != original_content:
        with open(SCRIPT_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n✅ Script file updated: {SCRIPT_FILE.name}")
    else:
        print(f"\nℹ️  No updates needed in script file")


if __name__ == "__main__":
    try:
        sync_versions()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
