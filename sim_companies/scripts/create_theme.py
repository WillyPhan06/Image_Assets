#!/usr/bin/env python3
"""
Theme Creator Script - Create new theme by analyzing and classifying images
Uses CLIP embeddings to intelligently classify images based on existing theme patterns
"""

import os
import argparse
import numpy as np
from pathlib import Path
from collections import defaultdict
from PIL import Image
import shutil

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False
    print("Warning: sentence_transformers or sklearn not found. Install with:")
    print("  pip install sentence-transformers scikit-learn")


# Paths
SCRIPT_DIR = Path(__file__).parent  # sim_companies/scripts
THEMES_DIR = SCRIPT_DIR.parent / "themes"  # sim_companies/themes
ORIGINAL_DIR = SCRIPT_DIR.parent / "original"  # sim_companies/original
ROOT_SCRIPTS_DIR = SCRIPT_DIR.parent.parent / "scripts"  # root scripts folder
OUTPUT_DIR = ROOT_SCRIPTS_DIR / "output"  # scripts/output (root level)
SYNC_SCRIPT = SCRIPT_DIR / "sync_versions.py"


def get_existing_building_names():
    """Extract all building base names from existing themes."""
    buildings = set()
    
    # Scan all existing themes
    if not THEMES_DIR.exists():
        print(f"Warning: Themes directory not found: {THEMES_DIR}")
        return buildings
    
    for theme_dir in THEMES_DIR.iterdir():
        if not theme_dir.is_dir() or theme_dir.name.startswith('.'):
            continue
        
        for filename in os.listdir(theme_dir):
            if not filename.endswith(('.png', '.jpg')):
                continue
            
            # Extract building name (remove theme suffix and version)
            # Example: sales_office_japan_v5.png -> sales_office
            name_without_ext = filename.rsplit('.', 1)[0]
            name_without_version = name_without_ext.rsplit('_v', 1)[0]
            building_name = name_without_version.rsplit('_', 1)[0]  # Remove theme name
            
            if building_name:
                buildings.add(building_name)
    
    return sorted(buildings)


def load_and_embed_images(image_paths, model):
    """Load images and generate embeddings."""
    embeddings = {}
    
    for img_path in image_paths:
        try:
            img = Image.open(img_path).convert('RGB')
            embedding = model.encode(img, convert_to_numpy=True)
            embeddings[str(img_path)] = embedding
        except Exception as e:
            print(f"  ⚠️  Error embedding {img_path.name}: {e}")
    
    return embeddings


def build_prototypes(theme_dir, building_names, model):
    """Build prototype embeddings for each known building (single theme)."""
    prototypes = {}
    
    for building in building_names:
        building_embeddings = []
        
        for filename in os.listdir(theme_dir):
            if not filename.endswith(('.png', '.jpg')):
                continue
            
            # Check if this file belongs to this building
            name_without_ext = filename.rsplit('.', 1)[0]
            name_without_version = name_without_ext.rsplit('_v', 1)[0]
            file_building = name_without_version.rsplit('_', 1)[0]
            
            if file_building == building:
                img_path = theme_dir / filename
                try:
                    img = Image.open(img_path).convert('RGB')
                    embedding = model.encode(img, convert_to_numpy=True)
                    building_embeddings.append(embedding)
                except Exception as e:
                    print(f"  ⚠️  Error processing {filename}: {e}")
        
        if building_embeddings:
            # Average embeddings to create prototype
            prototype = np.mean(building_embeddings, axis=0)
            prototypes[building] = prototype
    
    return prototypes


def build_prototypes_with_originals(original_dir, themes_dir, building_names, model, max_variant_themes=2):
    """Build prototype embeddings using originals + variant themes (up to 2 variants)."""
    prototypes = {}
    
    # Always use original if it exists
    sources_to_use = []
    if original_dir.exists():
        sources_to_use.append(original_dir)
    
    # Get up to max_variant_themes from existing themes (sorted for consistency)
    available_themes = sorted([
        d for d in themes_dir.iterdir()
        if d.is_dir() and not d.name.startswith('.')
    ])
    
    sources_to_use.extend(available_themes[:max_variant_themes])
    source_names = [s.name for s in sources_to_use]
    
    print(f"   Using sources for prototypes: {', '.join(source_names)}")
    
    for building in building_names:
        building_embeddings = []
        
        # Collect embeddings from all selected sources (original + variants)
        for source_dir in sources_to_use:
            for filename in os.listdir(source_dir):
                if not filename.endswith(('.png', '.jpg')):
                    continue
                
                # Check if this file belongs to this building
                name_without_ext = filename.rsplit('.', 1)[0]
                name_without_version = name_without_ext.rsplit('_v', 1)[0]
                
                # For original dir, files might be named differently (no theme suffix)
                # Handle both cases: building_v5.png and building_japan_v5.png
                if source_dir.name == 'original':
                    file_building = name_without_version
                else:
                    file_building = name_without_version.rsplit('_', 1)[0]
                
                if file_building == building:
                    img_path = source_dir / filename
                    try:
                        img = Image.open(img_path).convert('RGB')
                        embedding = model.encode(img, convert_to_numpy=True)
                        building_embeddings.append(embedding)
                    except Exception as e:
                        pass  # Silently skip bad files
        
        if building_embeddings:
            # Average embeddings across all sources to create style-invariant prototype
            prototype = np.mean(building_embeddings, axis=0)
            prototypes[building] = prototype
    
    return prototypes


def classify_unknown_image(img_path, prototypes, model):
    """Classify an unknown image by comparing to prototypes. Returns top 5 matches."""
    try:
        img = Image.open(img_path).convert('RGB')
        embedding = model.encode(img, convert_to_numpy=True)
        
        # Get all matches ranked by similarity
        matches = []
        
        for building, prototype in prototypes.items():
            similarity = cosine_similarity([embedding], [prototype])[0][0]
            matches.append((building, similarity))
        
        # Sort by similarity (descending)
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches  # Return top matches instead of just best
    except Exception as e:
        print(f"  ⚠️  Error classifying {img_path.name}: {e}")
        return []


def assign_unique_buildings(image_matches_dict):
    """
    Assign each image to a unique building (1-to-1 mapping).
    Handles cases where multiple images classify to the same building.
    Uses greedy algorithm: keep highest confidence matches first.
    """
    assignments = {}  # image -> (building, confidence)
    used_buildings = set()
    
    # Sort by confidence descending
    sorted_images = sorted(
        image_matches_dict.items(),
        key=lambda x: x[1][0][1],  # Sort by best match confidence
        reverse=True
    )
    
    for img_path, matches in sorted_images:
        assigned = False
        
        # Try each match in descending confidence order
        for building, confidence in matches:
            if building not in used_buildings:
                assignments[img_path] = (building, confidence)
                used_buildings.add(building)
                assigned = True
                break
        
        if not assigned:
            # All buildings taken, use best available anyway (shouldn't happen)
            best_building, best_conf = matches[0]
            assignments[img_path] = (best_building, best_conf)
    
    return assignments


def get_next_version(building_name, themes_dir):
    """Determine the next version number for a building."""
    max_version = 0
    
    for theme_dir in themes_dir.iterdir():
        if not theme_dir.is_dir() or theme_dir.name.startswith('.'):
            continue
        
        for filename in os.listdir(theme_dir):
            if building_name in filename:
                # Extract version
                if '_v' in filename:
                    version_part = filename.split('_v')[-1].split('.')[0]
                    try:
                        version = int(version_part)
                        max_version = max(max_version, version)
                    except ValueError:
                        pass
    
    return max_version + 1


def create_theme(theme_name, output_path=None, confidence_threshold=0.5):
    """Main function to create a new theme."""
    if not MODELS_AVAILABLE:
        print("❌ ERROR: Required packages not installed")
        print("Install with: pip install sentence-transformers scikit-learn pillow")
        return False
    
    if output_path is None:
        output_path = OUTPUT_DIR
    
    output_path = Path(output_path)
    
    if not output_path.exists():
        print(f"❌ ERROR: Output directory not found: {output_path}")
        return False
    
    # Check for input images
    input_images = list(output_path.glob("*.png")) + list(output_path.glob("*.jpg"))
    
    if not input_images:
        print(f"❌ ERROR: No images found in {output_path}")
        return False
    
    print("=" * 70)
    print(f"THEME CREATOR: {theme_name.upper()}")
    print("=" * 70)
    
    print(f"\n📷 Found {len(input_images)} images in {output_path.name}/")
    
    # Load model
    print("\n🤖 Loading CLIP embedding model...")
    try:
        model = SentenceTransformer('clip-ViT-B-32')
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("Ensure sentence-transformers is installed: pip install sentence-transformers")
        return False
    
    # Get existing building names
    print("\n📚 Analyzing existing theme patterns...")
    building_names = get_existing_building_names()
    
    if not building_names:
        print("❌ ERROR: No building patterns found in existing themes")
        return False
    
    print(f"   Found {len(building_names)} building types")
    
    # Build prototypes from originals + up to 2 variant themes
    print(f"\n🔍 Building prototypes from originals and variants...")
    prototypes = build_prototypes_with_originals(ORIGINAL_DIR, THEMES_DIR, building_names, model, max_variant_themes=2)
    print(f"   Created {len(prototypes)} building prototypes")
    
    # Classify images
    print(f"\n🎯 Classifying {len(input_images)} images...")
    image_matches_dict = {}
    
    for img_path in sorted(input_images):
        matches = classify_unknown_image(img_path, prototypes, model)
        
        if matches:
            image_matches_dict[str(img_path)] = matches
    
    # Ensure 1-to-1 mapping (each building used only once)
    print(f"\n🔄 Assigning unique buildings (ensuring 1 image per building)...")
    classifications = assign_unique_buildings(image_matches_dict)
    
    # Display assignments
    for img_path_str, (building, confidence) in sorted(classifications.items()):
        img_path = Path(img_path_str)
        print(f"   ✓ {img_path.name:40} → {building:30} ({confidence:.2%})")
    
    unclassified = len(input_images) - len(classifications)
    if unclassified > 0:
        print(f"\n⚠️  {unclassified} images could not be classified")
    
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
    
    # Copy and rename images
    print(f"\n📋 Copying and renaming images...")
    copied_count = 0
    
    for img_path_str, (building, confidence) in sorted(classifications.items()):
        img_path = Path(img_path_str)
        ext = img_path.suffix
        
        # Determine version
        version = get_next_version(building, THEMES_DIR)
        
        # Create new filename
        new_filename = f"{building}_{theme_name}_v{version}{ext}"
        new_path = theme_dir / new_filename
        
        try:
            shutil.copy2(img_path, new_path)
            print(f"   ✓ {img_path.name:40} → {new_filename}")
            copied_count += 1
        except Exception as e:
            print(f"   ❌ Error copying {img_path.name}: {e}")
    
    print(f"\n✅ Copied {copied_count}/{len(classifications)} images")
    
    # Run sync_versions.py
    print(f"\n⚙️  Syncing versions with sync_versions.py...")
    try:
        import subprocess
        result = subprocess.run(
            ["python", str(SYNC_SCRIPT)],
            cwd=str(SCRIPT_DIR),
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("   ✓ Sync completed successfully")
        else:
            print(f"   ⚠️  Sync encountered issues: {result.stderr}")
    except Exception as e:
        print(f"   ⚠️  Could not run sync_versions.py: {e}")
    
    print("\n" + "=" * 70)
    print(f"✅ THEME '{theme_name}' CREATED SUCCESSFULLY")
    print("=" * 70)
    print(f"\nNew theme folder: sim_companies/themes/{theme_name}/")
    print(f"Images copied: {copied_count}")
    print("\nTheme is ready to use! Update your tamper script to use it.")
    
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a new Sim Companies theme from classified images"
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Name of the new theme (e.g., 'korea', 'thailand')"
    )
    parser.add_argument(
        "--output-path",
        default=str(OUTPUT_DIR),
        help=f"Path to input images (default: {OUTPUT_DIR})"
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.5,
        help="Confidence threshold for warnings (0-1, default: 0.5)"
    )
    
    args = parser.parse_args()
    
    success = create_theme(args.name, args.output_path, args.confidence)
    exit(0 if success else 1)
