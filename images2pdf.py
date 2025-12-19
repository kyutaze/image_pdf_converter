"""
This python script creates a PDF from images.

dependencies:
    uv add img2pdf
"""
import logging
import argparse
import sys
from pathlib import Path
import img2pdf

# log settings
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

def create_pdf_from_images(image_folder: Path, output_pdf_path: Path, dpi: int = 72):
    if not image_folder.is_dir():
        logger.error(f"Input directory not found: {image_folder}")
        return

    # Gather all JPG/JPEG files
    image_files = []
    for filepath in image_folder.iterdir():
        if filepath.is_file() and filepath.suffix.lower() in (".jpg", ".jpeg"):
            image_files.append(filepath)

    # Sort files lexicographically based on their stem (name without extension)
    image_files.sort(key=lambda f: f.stem)

    if not image_files:
        logger.warning(f"No JPEG images found in {image_folder}")
        return

    # Ensure the output directory exists
    try:
        output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger.error(f"Error creating output directory {output_pdf_path.parent}: {e}")
        return

    # Convert images to PDF
    logger.info(f"Converting {len(image_files)} images to PDF using DPI={dpi}...")
    try:
        # img2pdf.convert expects a list of filenames (strings) or binary data
        # layout_fun is used to force a specific DPI, ignoring the image's internal DPI
        layout_function = img2pdf.get_fixed_dpi_layout_fun((dpi, dpi))
        pdf_bytes = img2pdf.convert([str(p) for p in image_files], layout_fun=layout_function)
        
        with open(output_pdf_path, "wb") as f:
            f.write(pdf_bytes)
            
        logger.info(f"Successfully created PDF: {output_pdf_path}")
    except Exception as e:
        logger.error(f"Error creating PDF: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Create a PDF from images (lossless).",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-i", "--input-dir", type=Path, required=True, help="Directory containing the image files.")
    parser.add_argument("--dpi", type=int, default=72, help="DPI to use for the PDF (default: 72).")
    args = parser.parse_args()

    # Determine output path based on input directory
    # Output directory is the parent of the input directory
    # Filename is the directory name + .pdf
    input_dir = args.input_dir.resolve()
    output_dir = input_dir.parent
    output_pdf_name = f"{input_dir.name}.pdf"
    output_pdf_path = output_dir / output_pdf_name

    create_pdf_from_images(args.input_dir, output_pdf_path, dpi=args.dpi)

if __name__ == "__main__":
    main()
