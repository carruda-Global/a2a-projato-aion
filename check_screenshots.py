from PIL import Image
import os

# Check chrome-extension screenshots
d1 = r'C:\Users\crist\Projetos\A2A - Projato AION\AION 7.0\chrome-extension\screenshots'
for f in sorted(os.listdir(d1)):
    img = Image.open(os.path.join(d1, f))
    print(f'chrome-ext/{f}: {img.size}')

# Check mensagens screenshots
d2 = r'C:\Users\crist\Projetos\A2A - Projato AION\mensagens e fotos debug\screenshots'
for f in sorted(os.listdir(d2)):
    img = Image.open(os.path.join(d2, f))
    print(f'debug/{f}: {img.size}')

# Generate 2 more screenshots at 1280x800 if needed
output = r'C:\Users\crist\Projetos\A2A - Projato AION'
count = 0
for d, prefix in [(d1, 'ext'), (d2, 'debug')]:
    for f in sorted(os.listdir(d)):
        count += 1
        if count <= 5:
            img = Image.open(os.path.join(d, f))
            if img.size != (1280, 800):
                img = img.resize((1280, 800), Image.LANCZOS)
            out = os.path.join(output, f'google_screenshot_{count}.png')
            img.save(out)
            print(f'Created: {out}')
