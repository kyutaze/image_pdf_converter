# image_pdf_converter

PDFファイル作成に係るツール。  
コマンドライン引数は```-h```オプションでご確認ください。

|スクリプト|説明|
|--|--|
|addToc2pdf.py|PDFファイルに目次を設定する|
|epub2img.py|EPUBファイル（固定レイアウト）から画像を抽出してページ順に連番を付けて保存する|
|epub2toc.py|EPUBファイルから目次を抽出してCSVに出力する|
|images2pdf.py|画像ファイルからPDFファイルを作成する|
|pdf2img.py|PDFファイルから画像を抽出してページ順に連番で保存する|
|pdf_settings.py|PDFのページレイアウトや綴じ方向などの表示設定を変更する|

## インストール

```bash
uv sync
```

## 使用例1
```Powershell
# example.epubから画像ファイルを抽出してexampleフォルダに保存する。
uv run epub2img.py --input-epub "C:\Users\foo\hoge\example.epub"

# example.epubから目次を抽出してexample_toc.csvに出力する。
uv run epub2toc.py --input-epub "C:\Users\foo\hoge\example.epub"

# exampleフォルダの画像ファイルからexample.pdfを作成する。
uv run images2pdf.py --input-dir "C:\Users\foo\hoge\example"

# example.pdfに目次（example_toc.csv）を設定する。
uv run addToc2pdf.py --pdf "C:\Users\foo\hoge\example.pdf" --toc "C:\Users\foo\hoge\example_toc.csv"

# example.pdfを右綴じに設定する。
uv run pdf_settings.py --pdf "C:\Users\foo\hoge\example.pdf" --direction /R2L
```

## 使用例2
使用例1を一連で実行する。
```Powershell
$path = "C:\Users\foo\hoge\example.epub"
uv run epub2img.py --input-epub "$path"
uv run epub2toc.py --input-epub "$path"
uv run images2pdf.py --input-dir ([System.IO.Path]::ChangeExtension($path, $null))
uv run addToc2pdf.py --pdf ([System.IO.Path]::ChangeExtension($path, ".pdf")) --toc (Join-Path ([System.IO.Path]::GetDirectoryName($path)) (([System.IO.Path]::GetFileNameWithoutExtension($path) + "_toc") + ".csv"))
uv run pdf_settings.py --pdf ([System.IO.Path]::ChangeExtension($path, ".pdf")) --direction /R2L
```
