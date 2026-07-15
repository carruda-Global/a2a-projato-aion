from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import os

screenshots_dir = r"C:\Users\crist\Projetos\A2A - Projato AION\mensagens e fotos debug\screenshots"
output_pdf = r"C:\Users\crist\Projetos\A2A - Projato AION\SallesJam_AddIn_Screenshots.pdf"

images = sorted([f for f in os.listdir(screenshots_dir) if f.startswith("screenshot") and f.endswith(".png")])

c = canvas.Canvas(output_pdf, pagesize=letter)
width, height = letter

for i, img_name in enumerate(images):
    img_path = os.path.join(screenshots_dir, img_name)
    img = Image.open(img_path)
    img_width, img_height = img.size

    # Scale to fit page with margins
    max_w = width - 72
    max_h = height - 72
    scale = min(max_w / img_width, max_h / img_height)
    display_w = img_width * scale
    display_h = img_height * scale
    x = (width - display_w) / 2
    y = (height - display_h) / 2

    c.setFont("Helvetica-Bold", 14)
    c.drawString(36, height - 36, f"Screenshot {i+1}: {img_name}")

    c.drawImage(ImageReader(img_path), x, y, width=display_w, height=display_h)
    c.showPage()

c.save()
print(f"PDF generated: {output_pdf}")
print(f"Pages: {len(images)}")
