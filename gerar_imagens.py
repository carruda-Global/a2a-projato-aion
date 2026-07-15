from PIL import Image, ImageDraw, ImageFont
import os

output_dir = r"C:\Users\crist\Projetos\A2A - Projato AION"

# 1. Check existing screenshot sizes
screenshots_dir = r"C:\Users\crist\Projetos\A2A - Projato AION\mensagens e fotos debug\screenshots"
for f in sorted(os.listdir(screenshots_dir)):
    if f.endswith(".png"):
        img = Image.open(os.path.join(screenshots_dir, f))
        print(f"{f}: {img.size}")

# 2. Create marketplace icon (300x300)
icon = Image.new("RGBA", (300, 300), (12, 19, 34, 255))
draw = ImageDraw.Draw(icon)
# Green circle
draw.ellipse([50, 50, 250, 250], fill=(0, 195, 107, 255))
# S letter
draw.text((116, 114), "S", fill=(255, 255, 255, 255), font=None)
icon.save(os.path.join(output_dir, "marketplace_icon.png"))
print(f"Icon saved: marketplace_icon.png")

# 3. Resize screenshots to 1366x768 if needed
existing = [f for f in sorted(os.listdir(screenshots_dir)) if f.endswith(".png")]
for i, f in enumerate(existing):
    img = Image.open(os.path.join(screenshots_dir, f))
    if img.size != (1366, 768):
        img = img.resize((1366, 768), Image.LANCZOS)
    out_path = os.path.join(output_dir, f"marketplace_screenshot_{i+1}.png")
    img.save(out_path)
    print(f"Screenshot {i+1} saved: {out_path} ({img.size})")
