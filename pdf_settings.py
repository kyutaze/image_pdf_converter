"""
PDFのページレイアウトや綴じ方向などの表示設定を変更するスクリプト

dependencies:
    uv add pikepdf
"""
import logging
import argparse
import sys
from pathlib import Path
import pikepdf

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

def set_pdf_settings(pdf_path: Path, layout: str, direction: str):
    if not pdf_path.is_file():
        logger.error(f"ファイルが見つかりません: {pdf_path}")
        return

    # 名前が / で始まることを確認
    if not layout.startswith("/"):
        layout = "/" + layout
    if not direction.startswith("/"):
        direction = "/" + direction

    try:
        # PDFを開く
        # 入力ファイルへの上書きを許可するために allow_overwriting_input=True が必要
        with pikepdf.Pdf.open(pdf_path, allow_overwriting_input=True) as pdf:
            
            # ページレイアウトを設定
            pdf.Root.PageLayout = pikepdf.Name(layout)

            # ViewerPreferences の Direction（綴じ方向）を設定
            if "ViewerPreferences" not in pdf.Root:
                pdf.Root.ViewerPreferences = pikepdf.Dictionary()
            
            pdf.Root.ViewerPreferences.Direction = pikepdf.Name(direction)

            # ファイルを保存（上書き）
            pdf.save(pdf_path)
            
            logger.info(f"設定を更新しました: {pdf_path}")
            logger.info(f"  PageLayout: {layout}")
            logger.info(f"  Direction: {direction}")

    except Exception as e:
        logger.error(f"{pdf_path} の処理中にエラーが発生しました: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="PDFのページレイアウトや綴じ方向などの表示設定を変更するスクリプト",
        formatter_class=argparse.RawTextHelpFormatter
    )
    # -p / --pdf
    parser.add_argument("-p", "--pdf", type=Path, required=True, help="PDFファイルのパス。")
    # -l / --layout
    parser.add_argument("-l", "--layout", type=str, default="/SinglePage", 
                        help="ページレイアウト (例: /SinglePage, /TwoPageRight)。初期値: /SinglePage")
    # -d / --direction
    parser.add_argument("-d", "--direction", type=str, default="/L2R", 
                        help="表示方向 (例: /L2R, /R2L)。初期値: /L2R")

    args = parser.parse_args()

    set_pdf_settings(args.pdf, args.layout, args.direction)

if __name__ == "__main__":
    main()
