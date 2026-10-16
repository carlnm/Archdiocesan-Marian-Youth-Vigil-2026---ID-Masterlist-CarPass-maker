import glob
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

# ================= CONFIGURATION =================
PARENT_BADGES_DIR = "./badges"  # Root folder containing parish/vicariate subfolders
BACK_IMAGE_NAME = "back.png"  # Optional local back image name inside subfolder, or root fallback
ROOT_BACK_IMAGE = "./back.png"

# Grid setup (2 columns x 2 rows per sheet)
COLS = 2
ROWS = 2
BADGES_PER_PAGE = COLS * ROWS

# Max badge bounding box dimensions on paper (in mm)
CARD_WIDTH_MM = 96
CARD_HEIGHT_MM = 139

# Border styling
BORDER_COLOR = colors.black  # Clear visible border (or e.g., colors.HexColor("#444444"))
BORDER_LINE_WIDTH = 1.0  # Thickness in points

# Margins & spacing for A4 (210 x 297 mm)
PAGE_WIDTH, PAGE_HEIGHT = A4
CARD_W = CARD_WIDTH_MM * mm
CARD_H = CARD_HEIGHT_MM * mm

MARGIN_X = (PAGE_WIDTH - (COLS * CARD_W)) / 2
MARGIN_Y = (PAGE_HEIGHT - (ROWS * CARD_H)) / 2
# =================================================


def draw_image_with_cling_border(c, img_path, cell_x, cell_y, cell_w, cell_h):
    """
    Draws the image preserving aspect ratio centered within the cell,
    and draws a tight border hugging the exact rendered dimensions.
    """
    img_reader = ImageReader(img_path)
    img_pixel_w, img_pixel_h = img_reader.getSize()

    # Calculate scale factor for preserveAspectRatio=True
    scale = min(cell_w / img_pixel_w, cell_h / img_pixel_h)
    rendered_w = img_pixel_w * scale
    rendered_h = img_pixel_h * scale

    # Calculate centered position of the actual rendered image
    actual_x = cell_x + (cell_w - rendered_w) / 2
    actual_y = cell_y + (cell_h - rendered_h) / 2

    # Draw the image
    c.drawImage(
        img_reader,
        actual_x,
        actual_y,
        width=rendered_w,
        height=rendered_h,
        preserveAspectRatio=False,  # Dimensions are already scaled
    )

    # Draw visible border tightly around the image
    c.setStrokeColor(BORDER_COLOR)
    c.setLineWidth(BORDER_LINE_WIDTH)
    c.rect(actual_x, actual_y, rendered_w, rendered_h, stroke=1, fill=0)


def generate_pdf_for_folder(folder_path, folder_name):
    # Gather image files inside this specific subfolder
    exts = ("*.png", "*.jpg", "*.jpeg")
    badge_files = []
    for ext in exts:
        for file in glob.glob(os.path.join(folder_path, ext)):
            # Ignore the back.png file from being treated as a badge
            if os.path.basename(file).lower() != BACK_IMAGE_NAME.lower():
                badge_files.append(file)

    badge_files.sort()

    if not badge_files:
        print(f"Skipping '{folder_name}': No badge images found.")
        return

    # Check if a custom back.png exists in this folder; otherwise fall back to root back.png
    subfolder_back = os.path.join(folder_path, BACK_IMAGE_NAME)
    if os.path.exists(subfolder_back):
        active_back = subfolder_back
    elif os.path.exists(ROOT_BACK_IMAGE):
        active_back = ROOT_BACK_IMAGE
    else:
        active_back = None

    # Target output PDF path saved directly into the main badges folder
    output_pdf = os.path.join(PARENT_BADGES_DIR, f"{folder_name}_badges.pdf")

    # Force delete existing PDF before recreating
    if os.path.exists(output_pdf):
        try:
            os.remove(output_pdf)
        except PermissionError:
            print(f"Error: Could not overwrite '{output_pdf}'. Please close the PDF file in your viewer and run again.")
            return

    c = canvas.Canvas(output_pdf, pagesize=A4)

    # Process badges in chunks of BADGES_PER_PAGE
    for i in range(0, len(badge_files), BADGES_PER_PAGE):
        batch = badge_files[i : i + BADGES_PER_PAGE]

        # ----------------- 1. FRONT PAGE -----------------
        for idx, img_path in enumerate(batch):
            col = idx % COLS
            row = idx // COLS

            x = MARGIN_X + (col * CARD_W)
            y = PAGE_HEIGHT - MARGIN_Y - ((row + 1) * CARD_H)

            draw_image_with_cling_border(c, img_path, x, y, CARD_W, CARD_H)

        c.showPage()  # Commit front page

        # ----------------- 2. BACK PAGE ------------------
        for idx, img_path in enumerate(batch):
            col = idx % COLS
            row = idx // COLS

            # Horizontal mirror for duplex long-edge printing
            mirrored_col = (COLS - 1) - col

            x = MARGIN_X + (mirrored_col * CARD_W)
            y = PAGE_HEIGHT - MARGIN_Y - ((row + 1) * CARD_H)

            target_back = active_back if active_back else img_path
            draw_image_with_cling_border(c, target_back, x, y, CARD_W, CARD_H)

        c.showPage()  # Commit back page

    c.save()
    print(f"Generated / Replaced: {output_pdf} ({len(badge_files)} badges)")


def process_all_subfolders():
    if not os.path.exists(PARENT_BADGES_DIR):
        print(f"Directory '{PARENT_BADGES_DIR}' not found.")
        return

    # List all subdirectories inside badges/
    subfolders = [
        f
        for f in os.listdir(PARENT_BADGES_DIR)
        if os.path.isdir(os.path.join(PARENT_BADGES_DIR, f))
    ]

    if not subfolders:
        print(f"No subfolders found inside '{PARENT_BADGES_DIR}'.")
        return

    for folder_name in sorted(subfolders):
        folder_path = os.path.join(PARENT_BADGES_DIR, folder_name)
        generate_pdf_for_folder(folder_path, folder_name)


if __name__ == "__main__":
    process_all_subfolders()