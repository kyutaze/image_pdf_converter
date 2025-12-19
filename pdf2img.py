"""
This python script extracts images from a PDF.

dependencies:
    uv add PyMuPDF
"""
import argparse
import logging
from pathlib import Path
import fitz  # PyMuPDF

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

def extract_images(pdf_file_path: Path, output_dir: Path):
    """
    PDFファイルから画像を抽出し、指定されたディレクトリに保存する。

    Args:
        pdf_file_path (Path): 入力PDFファイルのパス。
        output_dir (Path): 画像を保存するディレクトリのパス。
    """
    logger.info("スクリプトを開始します。")
    logger.info(f"PDFファイルパス: {pdf_file_path}")
    logger.info(f"出力ディレクトリ: {output_dir}")

    # --- 出力ディレクトリの作成 ---
    logging.info(f"出力ディレクトリを確認・作成します: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # PDFファイルを開く
    logger.info("PDFファイルを開こうとしています...")
    try:
        doc = fitz.open(pdf_file_path)
        logger.info("PDFファイルを正常に開きました。")
    except Exception as e:
        logger.error(f"エラー: {pdf_file_path} を開けませんでした - {e}")
        exit()

    logger.info(f"{pdf_file_path} を開きました。画像を抽出します...")

    # 画像抽出カウンター
    image_counter = 0

    # 各ページを順番に処理
    for page_index in range(len(doc)):
        page = doc.load_page(page_index)
        image_list = page.get_images(full=True)

        if image_list:
            logger.info(f"ページ {page_index + 1} から {len(image_list)} 件の画像を検出しました。")

        # 検出した画像を保存
        for image_index, img in enumerate(image_list, start=1):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            # 出力ファイル名を生成
            image_counter += 1
            image_filename = f"{image_counter:04d}.{image_ext}"
            output_path = output_dir / image_filename

            try:
                output_path.write_bytes(image_bytes)
                logger.info(f"保存しました: {output_path}")
            except Exception as e:
                logger.error(f"エラー: {output_path} の保存中にエラーが発生しました - {e}")

    doc.close()
    logger.info(f"処理が完了しました。{image_counter} 件の画像を保存しました。")

def main():
    """
    コマンドライン引数を処理し、画像抽出処理を実行する。
    """

    parser = argparse.ArgumentParser(
        description="PDFファイルから画像を抽出し、連番ファイルとして保存します。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-i", "--input-pdf", type=Path, required=True, help="画像抽出の対象となるPDFファイルのパス。")
    args = parser.parse_args()
    
    # 入力PDFファイルのあるディレクトリに、PDFのファイル名（拡張子なし）のディレクトリを作成する
    output_dir = args.input_pdf.parent / args.input_pdf.stem
    extract_images(args.input_pdf, output_dir)

if __name__ == "__main__":
    main()