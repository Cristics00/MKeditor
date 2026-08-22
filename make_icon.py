import os

from PIL import Image, ImageDraw, ImageFont

SIZE = 512
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")


def find_font(size):
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\msyhbd.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = size * 0.03
    r = size * 0.22
    box = [m, m, size - m, size - m]
    d.rounded_rectangle(
        [x + size * 0.012 for x in box], radius=r,
        fill=(0, 0, 0, 60))
    d.rounded_rectangle(box, radius=r, fill=(255, 255, 255, 255),
                        outline=(210, 210, 210, 255), width=max(2, size // 96))
    font = find_font(int(size * 0.42))
    text = "MK"
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (size - tw) / 2 - bbox[0]
    y = (size - th) / 2 - bbox[1]
    d.text((x, y), text, font=font, fill=(30, 30, 30, 255))
    return img


def main():
    base = draw_icon(SIZE)
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64),
             (128, 128), (256, 256)]
    base.save(OUTPUT, format="ICO", sizes=sizes)
    print("已生成图标:", OUTPUT)


if __name__ == "__main__":
    main()
