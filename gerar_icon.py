from PIL import Image
import os

output_dir = r"C:\Users\crist\Projetos\A2A - Projato AION"

# Use the existing 128px icon and upscale to 300x300
icon_src = r"C:\Users\crist\Projetos\A2A - Projato AION\AION 7.0\static\icons\icon-128.png"
if os.path.exists(icon_src):
    img = Image.open(icon_src).convert("RGBA")
    # Create 300x300 canvas with dark background
    canvas = Image.new("RGBA", (300, 300), (12, 19, 34, 255))
    # Paste the icon centered and resized
    icon_size = 256
    resized = img.resize((icon_size, icon_size), Image.LANCZOS)
    x = (300 - icon_size) // 2
    y = (300 - icon_size) // 2
    canvas.paste(resized, (x, y), resized if resized.mode == "RGBA" else None)
    canvas.save(os.path.join(output_dir, "marketplace_icon.png"))
    print("Icon created from existing assets")
else:
    print("Icon source not found, keeping simple icon")

print("Done!")
