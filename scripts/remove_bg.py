import os
from rembg import remove
from PIL import Image

INPUT_DIR = "input"
OUTPUT_DIR = "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def process_image(input_path, output_path):
    with open(input_path, "rb") as i:
        input_data = i.read()

    # AI background removal
    output_data = remove(input_data)

    with open(output_path, "wb") as o:
        o.write(output_data)

def run_batch():
    for file in os.listdir(INPUT_DIR):
        input_path = os.path.join(INPUT_DIR, file)

        if not os.path.isfile(input_path):
            continue

        if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            name = os.path.splitext(file)[0]
            output_path = os.path.join(OUTPUT_DIR, name + ".png")

            try:
                process_image(input_path, output_path)
                print(f"Processed: {file}")
            except Exception as e:
                print(f"Failed: {file} -> {e}")

    print("\nDone.")

if __name__ == "__main__":
    run_batch()