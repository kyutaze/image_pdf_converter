"""
EPUBファイル（固定レイアウト）から画像を抽出してページ順に連番を付けて保存するスクリプト
"""
import argparse
import logging
import zipfile
import xml.etree.ElementTree as ET
import sys
import shutil
from pathlib import Path

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

# 名前空間定義
NS = {
    "container": "urn:oasis:names:tc:opendocument:xmlns:container",
    "opf": "http://www.idpf.org/2007/opf",
    "xhtml": "http://www.w3.org/1999/xhtml",
    "svg": "http://www.w3.org/2000/svg",
    "xlink": "http://www.w3.org/1999/xlink",
}


def parse_args():
    """
    コマンドライン引数を解析する。
    """
    parser = argparse.ArgumentParser(
        description="EPUBファイル（固定レイアウト）から画像を抽出してページ順に連番を付けて保存するスクリプト",
        formatter_class=argparse.RawTextHelpFormatter
        )
    parser.add_argument("-i", "--input-epub", required=True, type=Path, help="画像抽出の対象となるEPUBファイルのパス。")
    parser.add_argument("--skip-cover", action="store_true", help="表紙（1ページ目）をスキップする。")
    return parser.parse_args()


def get_opf_path(zip_ref):
    """
    container.xmlからOPFファイルのパスを取得する。
    """
    try:
        container_xml = zip_ref.read("META-INF/container.xml")
        root = ET.fromstring(container_xml)
        rootfile = root.find(".//container:rootfile", NS)
        if rootfile is None:
            raise ValueError("container.xml内にrootfileが見つかりません。")
        return rootfile.attrib["full-path"]
    except Exception as e:
        logger.error(f"OPFパスの取得に失敗しました: {e}")
        raise


def extract_images(epub_path, output_dir, skip_cover=False):
    """
    EPUBから画像を抽出し、指定ディレクトリに保存する。
    """
    logging.info(f"出力ディレクトリを確認・作成します: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(epub_path, "r") as z:
            # OPFパス取得
            opf_path_str = get_opf_path(z)
            logger.info(f"OPFファイル: {opf_path_str}")

            # OPF読み込み
            opf_content = z.read(opf_path_str)
            opf_root = ET.fromstring(opf_content)

            # マニフェスト取得 (ID -> HREF)
            manifest = {}
            for item in opf_root.findall(".//opf:manifest/opf:item", NS):
                manifest[item.attrib["id"]] = item.attrib["href"]

            # スパイン取得 (表示順)
            spine_items = []
            for itemref in opf_root.findall(".//opf:spine/opf:itemref", NS):
                spine_items.append(itemref.attrib["idref"])

            logger.info(f"総ページ数（スキップ前）: {len(spine_items)}")

            if skip_cover and len(spine_items) > 0:
                logger.info("表紙（1ページ目）をスキップします。")
                spine_items = spine_items[1:]

            logger.info(f"処理対象ページ数: {len(spine_items)}")

            # 各ページ(XHTML)から画像を抽出
            opf_dir = Path(opf_path_str).parent
            count = 1

            for item_id in spine_items:
                if item_id not in manifest:
                    logger.warning(f"SpineのID '{item_id}' がManifestに見つかりません。スキップします。")
                    continue

                xhtml_rel_path = manifest[item_id]
                # OPFからの相対パスをZIP内の絶対パスに変換
                xhtml_zip_path = (opf_dir / xhtml_rel_path).as_posix() # zip内はposixパス

                try:
                    xhtml_content = z.read(xhtml_zip_path)
                    xhtml_root = ET.fromstring(xhtml_content)

                    # 画像パスを探す
                    # 1. <svg><image xlink:href="..."> パターン (Fixed Layoutで一般的)
                    # 2. <img src="..."> パターン
                    
                    image_href = None
                    
                    # SVG image探索
                    svg_image = xhtml_root.find(".//svg:image", NS)
                    if svg_image is not None:
                        # xlink:href または href (SVG2)
                        image_href = svg_image.get(f"{{{NS['xlink']}}}href")
                        if not image_href:
                            image_href = svg_image.get("href")
                    
                    # imgタグ探索 (SVGが見つからない場合)
                    if not image_href:
                        img_tag = xhtml_root.find(".//xhtml:img", NS)
                        if img_tag is not None:
                            image_href = img_tag.get("src")

                    if image_href:
                        # 画像パスの解決 (XHTMLからの相対パス -> ZIP内のパス)
                        xhtml_dir = Path(xhtml_zip_path).parent
                        
                        import posixpath
                        xhtml_dir_posix = posixpath.dirname(xhtml_zip_path)
                        image_zip_path = posixpath.normpath(posixpath.join(xhtml_dir_posix, image_href))

                        # 画像読み込み
                        try:
                            image_data = z.read(image_zip_path)
                            
                            # 出力ファイル名生成
                            # 要件: "ファイル名は取得した画像ファイル名の前に、ゼロ埋めした数字4桁連番+"_"を付与する。"
                            output_filename = f"{count:04d}_{Path(image_zip_path).name}" 
                            
                            output_path = output_dir / output_filename
                            
                            with open(output_path, "wb") as f:
                                f.write(image_data)
                            
                            logger.info(f"保存: {output_path}")
                            count += 1
                            
                        except KeyError:
                             logger.warning(f"画像ファイルがZIP内に見つかりません: {image_zip_path}")

                    else:
                        logger.warning(f"画像リンクが {xhtml_zip_path} 内に見つかりませんでした。")

                except KeyError:
                    logger.warning(f"XHTMLファイルがZIP内に見つかりません: {xhtml_zip_path}")
                except ET.ParseError as e:
                    logger.warning(f"XML解析エラー ({xhtml_zip_path}): {e}")

    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
        sys.exit(1)


def main():
    args = parse_args()
    # 入力EPUBファイルのあるディレクトリに、EPUBのファイル名（拡張子なし）のディレクトリを作成する
    output_dir = args.input_epub.parent / args.input_epub.stem
    extract_images(args.input_epub, output_dir, args.skip_cover)


if __name__ == "__main__":
    main()
