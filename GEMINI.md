## 技術スタック
- Python

## コーディング規約
- *PEP8* （https://github.com/python/peps/blob/main/peps/pep-0008.rst）に従うこと。ただし、一行の文字数は119桁とする。
- ```if __name__ == "__main__":```を記述すること。
- ```if __name__ == "__main__":```には```main()```のみを記載すること。
- 引数操作には **argparse** を使用すること。
- ファイル操作には **pathlib** を使用すること。
- ログ出力には **logging** を使用すること。設定は以下のとおりとする。
```
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)
```
- 引用符には二重引用符を使用すること。
- 適宜日本語でコメントを入れること。
- 修正に関係のないコードおよびコメントは変更しないこと。

## 重要な注意事項
- Pythonのパッケージ管理には *uv* を使用すること。
