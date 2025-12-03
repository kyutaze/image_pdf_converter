""""
This python script creates a PDF from images.

dependencies:
    uv add pillow
"""
import logging
import argparse
from pathlib import Path
from PIL import Image  # pillow

logger = logging.getLogger(__name__)

def create_pdf_from_images(image_folder: Path, output_pdf_path: Path):
    image_files = []
    if not image_folder.is_dir():
        logger.error(f"Input directory not found: {image_folder}")
        return

    for filepath in image_folder.iterdir():
        if filepath.is_file() and filepath.suffix.lower() in (".jpg", ".jpeg"):
            image_files.append(filepath)

    # Sort files lexicographically based on their stem (name without extension)
    image_files.sort(key=lambda f: f.stem)

    if not image_files:
        logger.warning(f"No JPEG images found in {image_folder}")
        return

    images = []
    for img_path in image_files:
        try:
            img = Image.open(img_path)
            # Convert to RGB if not already, as some images might be RGBA or P
            if img.mode != "RGB":
                img = img.convert("RGB")
            images.append(img)
        except Exception as e:
            logger.error(f"Error processing {img_path}: {e}")

    if not images:
        logger.warning("No images were successfully processed.")
        return

    # Ensure the output directory exists
    try:
        output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger.error(f"Error creating output directory {output_pdf_path.parent}: {e}")
        return

    # Save the first image, appending the rest
    try:
        images[0].save(output_pdf_path, save_all=True, append_images=images[1:])
        logger.info(f"Successfully created PDF: {output_pdf_path}")
    except Exception as e:
        logger.error(f"Error saving PDF to {output_pdf_path}: {e}")


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

    parser = argparse.ArgumentParser(
        description="Create a PDF from images.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-i", "--input-dir", type=Path, required=True, help="Directory containing the image files.")
    parser.add_argument("-o", "--output-dir", type=Path, required=True, help="Directory to save the output PDF file.")
    args = parser.parse_args()

    output_pdf_name = "output.pdf"
    output_pdf_path = args.output_dir / output_pdf_name

    create_pdf_from_images(args.input_dir, output_pdf_path)

if __name__ == "__main__":
    main()
