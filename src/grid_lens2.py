import io
from PIL import Image, ImageDraw, ImageFont, ImageChops


def overlay_vastu_grid(image_source) -> io.BytesIO:
    """
    Accepts either a file path (str) or a BytesIO object.
    Returns a BytesIO buffer containing the grid-overlaid image.
    Nothing is written to disk.
    """
    if isinstance(image_source, (str, bytes)):
        img = Image.open(image_source).convert("RGB")
    else:
        image_source.seek(0)
        img = Image.open(image_source).convert("RGB")

    # Auto-crop white margins
    bg = Image.new(img.mode, img.size, (255, 255, 255))
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    if bbox:
        img = img.crop(bbox)

    draw = ImageDraw.Draw(img)
    w, h = img.size

    grid_labels = [
        ["NW", "N",      "NE"],
        ["W",  "CENTER", "E" ],
        ["SW", "S",      "SE"],
    ]

    step_x, step_y = w / 3, h / 3

    try:
        font = ImageFont.truetype("arial.ttf", size=max(14, int(min(w, h) * 0.035)))
    except OSError:
        font = ImageFont.load_default()

    for row in range(3):
        for col in range(3):
            x0, y0 = col * step_x, row * step_y
            x1, y1 = (col + 1) * step_x, (row + 1) * step_y

            draw.rectangle([x0, y0, x1, y1], outline="red", width=3)

            label = grid_labels[row][col]
            text_bbox = draw.textbbox((0, 0), label, font=font)
            text_w = text_bbox[2] - text_bbox[0]
            text_h = text_bbox[3] - text_bbox[1]

            bx0, by0 = x0 + 8, y0 + 8
            bx1, by1 = bx0 + text_w + 10, by0 + text_h + 8

            draw.rectangle([bx0, by0, bx1, by1], fill="black")
            draw.text((bx0 + 5, by0 + 2), label, fill="white", font=font)

    draw.text((10, h - 35), "ORIENTATION: NORTH = UP", fill="red", font=font)

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    return buffer