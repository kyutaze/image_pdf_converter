""""
This python script extracts images from an inner HTML of Impress Web Book Viewer.
"""
import logging
import argparse
from pathlib import Path
import re
import base64
import urllib.request
import sys

logger = logging.getLogger(__name__)

def extract_images(html_file_path: Path, output_dir: Path):
    """
    HTMLファイルから画像を抽出し、指定されたディレクトリに保存する。

    Args:
        html_file_path (Path): 入力HTMLファイルのパス。
        output_dir (Path): 画像を保存するディレクトリのパス。
    """
    # --- 出力ディレクトリの作成 ---
    logging.info(f"出力ディレクトリを確認・作成します: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- HTMLコンテンツの読み込み ---
    # ファイルが大きいため、一行ずつ読み込んで処理することも検討しましたが、
    # <div class="slide"> が複数行にまたがることを考えると、全体を読み込む必要があります。
    logging.info(f"{html_file_path} を読み込んでいます...")
    try:
        html_content = html_file_path.read_text(encoding='utf-8')
    except FileNotFoundError:
        logging.error(f"ファイルが見つかりません: {html_file_path}")
        sys.exit(1)
    except MemoryError:
        logging.error("ファイルが大きすぎてメモリに読み込めません。")
        sys.exit(1)

    logging.info("読み込みが完了しました。画像ソースを検索します...")

    # --- 正規表現による画像ソースの抽出 ---
    # 1. まず、<div class="slide...">...</div> で囲まれたブロックをすべて抽出します。
    #    re.DOTALLフラグは '.' が改行を含むすべての文字にマッチするようにします。
    #    re.IGNORECASEフラグは <div class="slide..."> のように大文字小文字を区別せずに検索します。
    slide_pattern = r'<div class="slide.*?>(.*?)</div>'
    slide_div_contents = re.findall(slide_pattern, html_content, re.DOTALL | re.IGNORECASE)

    # 2. 次に、各ブロックの中から <img> タグのsrcをすべて抽出します。
    image_srcs = []
    img_pattern = r'<img src="(.*?)"'
    for content in slide_div_contents:
        srcs_in_content = re.findall(img_pattern, content, re.IGNORECASE)
        image_srcs.extend(srcs_in_content)

    if not image_srcs:
        logging.warning("画像ソースが見つかりませんでした。HTMLの構造を確認してください。")
        logging.warning(f"試したスライドパターン: {slide_pattern}")
        logging.warning(f"試した画像パターン: {img_pattern}")
        sys.exit(0)

    logging.info(f"{len(image_srcs)} 件の画像ソースが見つかりました。ファイルを保存します...")

    # --- 画像データの処理と保存 ---
    # 画像ファイル名の連番カウンター
    image_counter = 1
    saved_count = 0
    for src in image_srcs:
        # 出力ファイル名を生成 (例: 0001.jpg)
        file_name = f"{image_counter:04d}.jpg"
        output_path = output_dir / file_name

        try:
            image_data = None
            # srcがデータURI (Base64) かどうかを判定
            source_type = "不明"
            if src.startswith('data:image'):
                # "data:image/jpeg;base64," のようなヘッダー部分を分離
                header, encoded = src.split(',', 1)
                # Base64データをデコード
                image_data = base64.b64decode(encoded)
                source_type = "Base64"

            # srcがURLの場合
            elif src.startswith(('http://', 'https://')):
                # URLからデータをダウンロード
                with urllib.request.urlopen(src) as response:
                    image_data = response.read()
                source_type = "URL"

            else:
                # 想定外のsrc形式
                logging.warning(f"スキップしました: サポートされていないsrc形式です - {src[:70]}...")
                continue # 次のsrcへ

            # データがあればファイルに書き込み
            if image_data:
                output_path.write_bytes(image_data)
                logging.info(f"保存しました: {output_path} (ソース: {source_type})")
                saved_count += 1
        
        except Exception as e:
            logging.error(f"エラー: {src[:70]}... の処理中にエラーが発生しました - {e}")
        
        finally:
            # srcの形式に関わらずファイル名はインクリメントする
            image_counter += 1

    logging.info(f"処理が完了しました。{saved_count} / {len(image_srcs)} 件の画像を保存しました。")

def main():
    """
    コマンドライン引数を処理し、画像抽出処理を実行する。
    """
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

    parser = argparse.ArgumentParser(
        description="HTMLファイルからスライド内の画像を抽出し、連番ファイルとして保存します。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-i", "--input-file", type=Path, required=True, help="画像抽出の対象となるHTMLファイルのパス。")
    parser.add_argument("-o", "--output-dir", type=Path, required=True, help="抽出した画像ファイルを保存するディレクトリのパス。")
    args = parser.parse_args()

    extract_images(args.input_file, args.output_dir)

if __name__ == "__main__":
    main()
