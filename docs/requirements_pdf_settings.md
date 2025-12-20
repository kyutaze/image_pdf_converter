## 目的
PDFファイルを見開きページ表示にして右綴じに設定するPythonスクリプトを生成する。

## 使用するライブラリ
- pikepdf

## コマンドラインオプション
- **-p** 、 **--pdf** オプション：設定するPDFファイルのパス。必須引数。
- **-l** 、 **--layout** オプション：ページレイアウト。任意引数。初期値は **/SinglePage** 。
- **-d** 、 **--direction** オプション：左綴じ/右綴じ。任意引数。初期値は **/L2R** 。

## 設定値
- **PageLayout** に **--layout** オプションの値を設定する。
- **ViewerPreferences** の **Direction** に **--direction** オプションの値を設定する。

## サンプルファイル
- sample.pdf
