# Theme Creator Script - Understanding & Flow

## 🎯 What I Understand

### End-to-End Workflow

1. **Input Phase**
   - Run background removal script → outputs cleaned images to `scripts/output/`
   - Images may have inconsistent or generic names (e.g., `unknown_A_3.png`)

2. **Analysis Phase (Smart Naming)**
   - Read all images from `scripts/output/`
   - Extract embeddings for each image using CLIP/DINOv2 (or similar vision model)
   - Identify known building patterns from existing themes (japan, vietnam)
   - Build prototypes by averaging embeddings of known building groups
   - Example: `proto_sales_office = avg(japan's sales_office_v5, vietnam's sales_office_v5)`

3. **Classification Phase**
   - For each unknown/new image:
     - Calculate similarity to each known building prototype
     - Assign label to the building it matches most closely
     - Example: `unknown_A_3` → 95% match to `sales_office` → rename to `sales_office_??`

4. **Creation Phase**
   - User passes `--name korea` flag
   - Script creates `sim_companies/themes/korea/` folder
   - Copy all images from `scripts/output/` to new theme folder
   - Rename each image: `building_name_korea_v1.png` format
   - Align naming with existing themes (japan, vietnam patterns)

5. **Integration**
   - Run `sync_versions.py` to update `AVAILABLE_THEMES` in tamper script
   - Theme is now available and auto-discovered

---

## 📋 To-Do List

- [x] **Analyze Existing Theme Patterns**
  - Read japan/ and vietnam/ folders
  - Extract all building base names and their patterns
  - Store as reference anchors

- [x] **Create Image Embedding System**
  - Load/install CLIP or DINOv2 model
  - Convert each image to embedding vector
  - Build prototype vectors from known buildings

- [x] **Implement Unknown Image Classification**
  - Compare new images against prototypes
  - Assign building labels via cosine similarity
  - Rank matches by confidence

- [x] **Build Theme Creation CLI**
  - Accept `--name` flag for theme name
  - Accept optional `--version` or auto-detect from existing
  - Read cleaned images from `scripts/output/`
  - Classify and rename each image
  - Create theme folder and copy renamed images

- [x] **Integrate with sync_versions.py**
  - Ensure new theme is auto-discovered
  - Update AVAILABLE_THEMES in tamper script

- [ ] **Testing**
  - Test classification accuracy on known images
  - Test theme creation with sample images
  - Verify naming convention alignment
  - Verify tamper script discovers new theme

---

## 🔄 Final Script Flow

```
Input: python create_theme.py --name [theme_name] --output-path scripts/output
         ↓
Read reference patterns from existing themes
         ↓
Load images from scripts/output/
         ↓
Generate embeddings for all images
         ↓
Build prototypes from known buildings
         ↓
Classify unknown images (assign building names)
         ↓
Create themes/[theme_name]/ folder
         ↓
Copy & rename images to: building_name_[theme_name]_v[version].ext
         ↓
Auto-update AVAILABLE_THEMES in tamper script
         ↓
Output: New theme ready to use
```

---

## ✅ Confirmation

**Is this the correct understanding?** Yes/No - Let me know if I'm missing anything or need to adjust the direction.

---

## 🚀 Usage

### Installation (First Time)
```bash
pip install sentence-transformers scikit-learn pillow
```

### Create a New Theme
```bash
# After running background removal and images are in scripts/output/
python create_theme.py --name korea

# With custom output path
python create_theme.py --name thailand --output-path /path/to/images

# With confidence threshold (warn if below 60%)
python create_theme.py --name vietnam --confidence 0.6
```

### What Happens
1. Loads CLIP model to understand image content
2. Analyzes japan/ and vietnam/ themes to learn building patterns
3. Classifies each image in `scripts/output/` based on visual similarity
4. Creates `themes/[name]/` folder
5. Copies images with renamed: `building_name_[theme_name]_v[version].png`
6. Runs `sync_versions.py` to update tamper script
7. Theme is auto-discovered and ready to use!

### Example Output
```
Theme Created: korea
├── sales_office_korea_v5.png
├── refinery_korea_v2.png
├── aerospace_factory_korea_v3.png
...
```

Then M key menu in Sim Companies will show 🇯🇵 🇻🇳 🇰🇷 themes!
