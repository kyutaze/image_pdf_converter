"""
PDFファイルに目次を設定するスクリプト

dependencies:
    uv add pymupdf
"""
import argparse
import csv
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


def add_toc_to_pdf(pdf_path: Path, toc_path: Path):
    """
    PDFファイルにCSVファイルから読み込んだ目次を設定する。

    Args:
        pdf_path (Path): 対象のPDFファイルパス。
        toc_path (Path): 目次情報のCSVファイルパス。
    """
    if not pdf_path.exists():
        logger.error(f"PDFファイルが見つかりません: {pdf_path}")
        return
    if not toc_path.exists():
        logger.error(f"目次ファイルが見つかりません: {toc_path}")
        return

    # CSV読み込み
    toc_entries = []
    logger.info(f"目次ファイルを読み込んでいます: {toc_path}")
    try:
        with toc_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f, quotechar='"')
            for line_no, row in enumerate(reader, start=1):
                if not row:
                    continue
                # level, title, page の3列を期待
                if len(row) < 3:
                    logger.warning(f"{line_no}行目: 列数が不足しているためスキップします: {row}")
                    continue

                try:
                    level = int(row[0])
                    title = row[1]
                    page = int(row[2])
                    # PyMuPDFのtoc形式: [lvl, title, page, dest]
                    # pageは1-based
                    toc_entries.append([level, title, page])
                except ValueError as e:
                    logger.warning(f"{line_no}行目: 数値変換エラーのためスキップします: {row} - {e}")
    except Exception as e:
        logger.error(f"目次ファイルの読み込み中にエラーが発生しました: {e}")
        return

    if not toc_entries:
        logger.warning("有効な目次情報が見つかりませんでした。処理を中断します。")
        return

    # PDF処理
    logger.info(f"PDFファイルを開いています: {pdf_path}")
    try:
        doc = fitz.open(pdf_path)

        # 目次を設定
        logger.info(f"{len(toc_entries)} 件の目次を設定します。")
        doc.set_toc(toc_entries)

        # 保存 (インクリメンタル保存)
        logger.info("PDFファイルを保存しています...")
        # incremental=True で同じファイルに追記保存する
        doc.save(doc.name, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
        doc.close()

        logger.info("処理が正常に完了しました。")

    except Exception as e:
        logger.error(f"PDF処理中にエラーが発生しました: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="PDFファイルに目次(アウトライン)を設定します。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--pdf", type=Path, required=True, help="目次を設定するPDFファイルのパス。")
    parser.add_argument("--toc", type=Path, required=True, help="目次情報を含むCSVファイルのパス。")

    args = parser.parse_args()

    add_toc_to_pdf(args.pdf, args.toc)


if __name__ == "__main__":
    main()
