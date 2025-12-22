"""
画像ファイルからPDFファイルを作成するスクリプト

dependencies:
    uv add img2pdf
"""
import logging
import argparse
import sys
from pathlib import Path
import img2pdf

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

def create_pdf_from_images(image_folder: Path, output_pdf_path: Path, dpi: int = 72):
    if not image_folder.is_dir():
        logger.error(f"入力ディレクトリが見つかりません: {image_folder}")
        return

    # すべてのJPG/JPEGファイルを取得
    image_files = []
    for filepath in image_folder.iterdir():
        if filepath.is_file() and filepath.suffix.lower() in (".jpg", ".jpeg"):
            image_files.append(filepath)

    # ファイル名（拡張子なし）に基づいて辞書順にソート
    image_files.sort(key=lambda f: f.stem)

    if not image_files:
        logger.warning(f"{image_folder} 内にJPEG画像が見つかりません")
        return

    # 出力ディレクトリが存在することを確認
    try:
        output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger.error(f"出力ディレクトリ {output_pdf_path.parent} の作成中にエラーが発生しました: {e}")
        return

    # 画像をPDFに変換
    logger.info(f"DPI={dpi} を使用して {len(image_files)} 枚の画像をPDFに変換中...")
    try:
        # img2pdf.convert はファイル名のリスト（文字列）またはバイナリデータを想定
        # layout_fun を使用して、画像の内部DPIを無視し、特定のDPIを強制する
        layout_function = img2pdf.get_fixed_dpi_layout_fun((dpi, dpi))
        pdf_bytes = img2pdf.convert([str(p) for p in image_files], layout_fun=layout_function)
        
        with open(output_pdf_path, "wb") as f:
            f.write(pdf_bytes)
            
        logger.info(f"PDFを正常に作成しました: {output_pdf_path}")
    except Exception as e:
        logger.error(f"PDF作成中にエラーが発生しました: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="画像ファイルからPDFファイルを作成するスクリプト",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-i", "--input-dir", type=Path, required=True, help="画像ファイルを含むディレクトリ。")
    parser.add_argument("--dpi", type=int, default=72, help="PDFに使用するDPI（デフォルト: 72）。")
    args = parser.parse_args()

    # 入力ディレクトリに基づいて出力パスを決定
    # 出力ディレクトリは入力ディレクトリの親
    # ファイル名はディレクトリ名 + .pdf
    input_dir = args.input_dir.resolve()
    output_dir = input_dir.parent
    output_pdf_name = f"{input_dir.name}.pdf"
    output_pdf_path = output_dir / output_pdf_name

    create_pdf_from_images(args.input_dir, output_pdf_path, dpi=args.dpi)

if __name__ == "__main__":
    main()
