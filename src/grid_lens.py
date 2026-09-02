import io
from PIL import Image, ImageDraw, ImageFont, ImageChops

def overlay_vastu_grid(image_source) -> io.BytesIO:
    """
    Overlays a non-destructive 3x3 Vastu grid onto the floor plan image.
    Safely handles raw bytes, file paths (str), and file stream buffers.
    """
    if isinstance(image_source, bytes):
        img = Image.open(io.BytesIO(image_source)).convert("RGB")
    elif isinstance(image_source, str):
        img = Image.open(image_source).convert("RGB")
    elif hasattr(image_source, "read"):
        image_source.seek(0)
        img = Image.open(io.BytesIO(image_source.read())).convert("RGB")
    else:
        raise TypeError(f"Unsupported image source type: {type(image_source)}")

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
        font = ImageFont.truetype("arial.ttf", size=max(12, int(min(w, h) * 0.025)))
    except OSError:
        font = ImageFont.load_default()

    for row in range(3):
        for col in range(3):
            x0, y0 = col * step_x, row * step_y
            x1, y1 = (col + 1) * step_x, (row + 1) * step_y

            # Thin grid lines (width=1) so door symbols stay visible
            draw.rectangle([x0, y0, x1, y1], outline="red", width=1)

            label = grid_labels[row][col]
            # Render text without opaque background boxes
            draw.text((x0 + 6, y0 + 6), label, fill="red", font=font)

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    return buffer