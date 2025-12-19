import argparse
import csv
import logging
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


def get_namespace(element):
    """
    ElementTreeのElementから名前空間を取得する。
    """
    if element.tag.startswith("{"):
        return element.tag.split("}", 1)[0] + "}"
    return ""


def parse_container(zip_ref):
    """
    META-INF/container.xml を解析してOPFファイルのパスを取得する。
    """
    try:
        with zip_ref.open("META-INF/container.xml") as f:
            tree = ET.parse(f)
            root = tree.getroot()
            ns = get_namespace(root)
            rootfiles = root.find(f"{ns}rootfiles")
            if rootfiles is not None:
                for rootfile in rootfiles.findall(f"{ns}rootfile"):
                    if rootfile.get("media-type") == "application/oebps-package+xml":
                        return rootfile.get("full-path")
    except Exception as e:
        logger.error(f"container.xml の解析に失敗しました: {e}")
        return None
    return None


def parse_opf(zip_ref, opf_path):
    """
    OPFファイルを解析して、以下の情報を取得する。
    1. idref -> 連番 のマッピング (ログ出力用)
    2. href (full path in zip) -> 連番 のマッピング (目次検索用)
    3. NCXファイルのパス (full path in zip)
    """
    id_to_seq = {}
    href_to_seq = {}
    ncx_path = None
    
    opf_dir = Path(opf_path).parent

    try:
        with zip_ref.open(opf_path) as f:
            tree = ET.parse(f)
            root = tree.getroot()
            ns = get_namespace(root)

            # マニフェストの解析 (id -> href)
            manifest = root.find(f"{ns}manifest")
            id_to_href = {}
            if manifest is not None:
                for item in manifest.findall(f"{ns}item"):
                    item_id = item.get("id")
                    item_href = item.get("href")
                    media_type = item.get("media-type")

                    # hrefをzip内のフルパスに変換
                    full_href = (opf_dir / item_href).as_posix() # Windowsでも/区切りにするためas_posix
                    id_to_href[item_id] = full_href

                    # NCXファイルの特定
                    if media_type == "application/x-dtbncx+xml":
                        ncx_path = full_href

            # スパインの解析 (順序の決定)
            spine = root.find(f"{ns}spine")
            if spine is not None:
                seq = 1
                for itemref in spine.findall(f"{ns}itemref"):
                    idref = itemref.get("idref")
                    id_to_seq[idref] = seq
                    
                    if idref in id_to_href:
                        href_to_seq[id_to_href[idref]] = seq
                    
                    seq += 1

            # 内部テーブル(idref -> seq)のログ出力
            logger.info("内部テーブル (idref -> seq):")
            for idref, s in id_to_seq.items():
                logger.info(f"  idref: {idref}, seq: {s}")

    except Exception as e:
        logger.error(f"OPFファイルの解析に失敗しました: {e}")
        return None, None, None

    return id_to_seq, href_to_seq, ncx_path


def parse_ncx(zip_ref, ncx_path, href_to_seq):
    """
    NCXファイルを解析して目次情報を抽出する。
    """
    toc_data = []
    ncx_dir = Path(ncx_path).parent

    try:
        with zip_ref.open(ncx_path) as f:
            tree = ET.parse(f)
            root = tree.getroot()
            ns = get_namespace(root)
            
            nav_map = root.find(f"{ns}navMap")
            if nav_map is not None:
                # 階層構造になっているnavPointをすべて取得するため iter を使用する
                for nav_point in nav_map.iter(f"{ns}navPoint"):
                    # タイトルの取得
                    nav_label = nav_point.find(f"{ns}navLabel")
                    text_element = nav_label.find(f"{ns}text") if nav_label is not None else None
                    title = text_element.text if text_element is not None else ""

                    # リンク先の取得
                    content = nav_point.find(f"{ns}content")
                    src = content.get("src") if content is not None else ""

                    # srcをzip内のフルパスに正規化 (アンカー除去含む)
                    src_path_str = src.split("#")[0]
                    full_src_path = (ncx_dir / src_path_str).as_posix()

                    # ページ番号の検索
                    page = href_to_seq.get(full_src_path)

                    if page is not None:
                        # levelは固定値1
                        toc_data.append(["1", title, str(page)])
                    else:
                        logger.warning(f"ページが見つかりません: {title} -> {full_src_path}")

    except Exception as e:
        logger.error(f"NCXファイルの解析に失敗しました: {e}")
        return []

    return toc_data


def main():
    parser = argparse.ArgumentParser(description="EPUBファイルから目次を抽出してCSVに出力します。")
    parser.add_argument("--input-epub", required=True, help="目次抽出の対象となるEPUBファイルのパス")
    args = parser.parse_args()

    input_epub_path = Path(args.input_epub)

    if not input_epub_path.exists():
        logger.error(f"指定されたファイルが存在しません: {input_epub_path}")
        sys.exit(1)

    try:
        with zipfile.ZipFile(input_epub_path, "r") as zip_ref:
            # 1. OPFパスの取得
            opf_path = parse_container(zip_ref)
            if not opf_path:
                logger.error("OPFファイルが見つかりませんでした。処理を中断します。")
                sys.exit(1)

            logger.info(f"OPFファイル: {opf_path}")

            # 2. OPF解析 (idref->seq, href->seq, ncx_path)
            id_to_seq, href_to_seq, ncx_path = parse_opf(zip_ref, opf_path)
            
            if not ncx_path:
                logger.error("NCXファイル(目次)が見つかりませんでした。処理を中断します。")
                sys.exit(1)
            
            logger.info(f"NCXファイル: {ncx_path}")

            # 3. NCX解析とCSVデータ生成
            toc_data = parse_ncx(zip_ref, ncx_path, href_to_seq)

            # 4. CSVファイルへの出力
            output_csv_path = input_epub_path.parent / (input_epub_path.stem + "_toc.txt")
            
            logger.info(f"CSVファイルを出力します: {output_csv_path}")
            
            with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
                # すべてのフィールドを二重引用符で囲む
                writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
                # ヘッダーは要件にないため、データのみ出力 (出力項目: level, title, page)
                writer.writerows(toc_data)
            
            logger.info("処理が完了しました。")

    except zipfile.BadZipFile:
        logger.error("無効なEPUBファイルです。")
        sys.exit(1)
    except Exception as e:
        logger.error(f"予期せぬエラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
