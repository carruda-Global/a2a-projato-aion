import sys
from pathlib import Path
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def ocr_read(image_path: str) -> str:
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang="por")
    return text.strip()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python ocr_read.py <caminho_da_imagem>")
        sys.exit(1)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"Arquivo nao encontrado: {path}")
        sys.exit(1)

    result = ocr_read(path)
    print(result)
