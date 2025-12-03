""""
This python script extracts images from a PDF.

dependencies:
    uv add PyMuPDF
"""
import os
import fitz  # PyMuPDF

print("スクリプトを開始します。")

# スクリプトが設置されているディレクトリを取得
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    script_dir = os.getcwd()
print(f"スクリプトディレクトリ: {script_dir}")

# 入力PDFファイルのパス
pdf_file_path = os.path.join(script_dir, 'sample.pdf')
print(f"PDFファイルパス: {pdf_file_path}")
# 画像を保存するディレクトリのパス
output_dir = os.path.join(script_dir, 'extracted_image')
print(f"出力ディレクトリ: {output_dir}")

# 画像保存ディレクトリが存在しない場合は作成する
if not os.path.exists(output_dir):
    print(f"作成します: {output_dir}")
    os.makedirs(output_dir)

# PDFファイルを開く
print("PDFファイルを開こうとしています...")
try:
    doc = fitz.open(pdf_file_path)
    print("PDFファイルを正常に開きました。")
except Exception as e:
    print(f"エラー: {pdf_file_path} を開けませんでした - {e}")
    exit()

print(f"{pdf_file_path} を開きました。画像を抽出します...")

# 画像抽出カウンター
image_counter = 0

# 各ページを順番に処理
for page_index in range(len(doc)):
    page = doc.load_page(page_index)
    image_list = page.get_images(full=True)

    if image_list:
        print(f"ページ {page_index + 1} から {len(image_list)} 件の画像を検出しました。")

    # 検出した画像を保存
    for image_index, img in enumerate(image_list, start=1):
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]

        # 出力ファイル名を生成
        image_counter += 1
        image_filename = f"{image_counter:04d}.{image_ext}"
        output_path = os.path.join(output_dir, image_filename)

        try:
            with open(output_path, "wb") as f:
                f.write(image_bytes)
            print(f"保存しました: {output_path}")
        except Exception as e:
            print(f"エラー: {output_path} の保存中にエラーが発生しました - {e}")

doc.close()
print(f"\n処理が完了しました。{image_counter} 件の画像を保存しました。")
