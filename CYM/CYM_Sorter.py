import pandas as pd
import os
import re
from PIL import Image as PILImage

from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ============================================================
# SETTINGS & ASSETS
# ============================================================

INPUT_FILE = "CYM/Marian_Youth_Vigil_2026_Cleaned_School_CYM.xlsx"
OUTPUT_FOLDER = "CYM/Marian Youth Vigil 2026 - Delegations"

DELEGATION_HEADS_FILE = os.path.join(OUTPUT_FOLDER, "Delegation Heads.xlsx")
MASTER_PDF_PATH = os.path.join(OUTPUT_FOLDER, "Masterlist_All_School_CYM.pdf")
LABEL_PDF_PATH = os.path.join(OUTPUT_FOLDER, "Participant_Labels_All.pdf")

# Document Dimensions: 8.5 x 13 inches (Folio / Long Bond)
PAGE_WIDTH = 8.5 * inch
PAGE_HEIGHT = 13.0 * inch
PAGE_SIZE = (PAGE_WIDTH, PAGE_HEIGHT)

# Palette
COLOR_YELLOW_ACCENT = colors.HexColor("#FDB813")  # Gold/Yellow Accent
COLOR_PRIMARY_BLUE  = colors.HexColor("#0D6EFD")  # Header Royal Blue
COLOR_DARK_NAVY     = colors.HexColor("#102A43")  # Deep Navy Text
COLOR_BG_LIGHT      = colors.HexColor("#FFFBEB")  # Soft Cream/Yellow row tint
COLOR_BORDER        = colors.HexColor("#CBD5E0")


# ============================================================
# OFFICIAL VICARIATE / SCHOOL-CYM LIST
# ============================================================

archdioceseData = [
    {
        "name": "Vicariate of St. John the Evangelist",
        "schools": [
            "CYM Universities - Dagupan Chapter"
        ]
    },
    {
        "name": "Vicariate of St. Vincent Ferrer",
        "schools": [
            "Pangasinan State University - CYM"
        ]
    },
    {
        "name": "Vicariate of St. Ildephonse",
        "schools": [
            "Malasiqui Catholic School"
        ]
    },
    {
        "name": "Vicariate of St. Dominic de Guzman",
        "schools": [
            "Urbiztondo Catholic School"
        ]
    },
    {
        "name": "Vicariate of Our Lady of Purification",
        "schools": [
            "Binmaley Catholic School"
        ]
    },
    {
        "name": "Vicariate of St. Thomas Aquinas",
        "schools": [
            "San Jacinto Catholic School",
            "Archdiocesan School of San Fabian",
            "St. Thomas Catholic School"
        ]
    }
]


# ============================================================
# BANNER DIMENSION & ASPECT RATIO CALCULATION
# ============================================================

def get_banner_info():
    possible_names = ["banner.png", "banner.jpg", "banner.jpeg", "banner", "nhgv.png"]
    for name in possible_names:
        if os.path.exists(name):
            try:
                with PILImage.open(name) as img:
                    orig_w, orig_h = img.size
                    calc_width = PAGE_WIDTH
                    calc_height = (orig_h / orig_w) * calc_width
                    return name, calc_width, calc_height
            except Exception:
                return name, PAGE_WIDTH, 1.25 * inch
    return None, 0, 0

BANNER_FILE, BANNER_WIDTH, BANNER_HEIGHT = get_banner_info()


# ============================================================
# FONT REGISTRATION (Garet with Fallback)
# ============================================================

FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

def register_garet_font():
    global FONT_REGULAR, FONT_BOLD
    garet_files = {
        "Garet-Regular": ["Garet-Book.ttf", "Garet-Regular.ttf", "Garet.ttf"],
        "Garet-Bold": ["Garet-Heavy.ttf", "Garet-Bold.ttf", "Garet-ExtraBold.ttf"]
    }

    reg_found = None
    for filename in garet_files["Garet-Regular"]:
        if os.path.exists(filename):
            pdfmetrics.registerFont(TTFont("Garet-Regular", filename))
            reg_found = "Garet-Regular"
            break

    bold_found = None
    for filename in garet_files["Garet-Bold"]:
        if os.path.exists(filename):
            pdfmetrics.registerFont(TTFont("Garet-Bold", filename))
            bold_found = "Garet-Bold"
            break

    if reg_found and bold_found:
        FONT_REGULAR = reg_found
        FONT_BOLD = bold_found
        print("Garet font registered successfully.")
    elif reg_found:
        FONT_REGULAR = reg_found
        FONT_BOLD = reg_found
        print("Garet font registered (Regular).")
    else:
        print("Garet font not found locally; falling back to Helvetica.")

register_garet_font()


# ============================================================
# NUMBERED CANVAS FOR UNSTRETCHED BANNER & FOOTER
# ============================================================

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        if BANNER_FILE:
            self.drawImage(
                BANNER_FILE,
                x=0,
                y=PAGE_HEIGHT - BANNER_HEIGHT,
                width=BANNER_WIDTH,
                height=BANNER_HEIGHT,
                preserveAspectRatio=True,
                mask='auto'
            )
        self.setFont(FONT_REGULAR, 8)
        self.setFillColor(colors.HexColor("#718096"))
        self.drawString(36, 20, "Archdiocesan Marian Youth Vigil 2026 — Official Delegation List")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(PAGE_WIDTH - 36, 20, page_str)
        self.restoreState()


# ============================================================
# CLEAN FILE / FOLDER NAMES & NORMALIZATION
# ============================================================

def clean_name(name):
    name = str(name).strip()
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    return name.rstrip(" .")

def normalize_text(value):
    if pd.isna(value):
        return ""
    value = str(value).strip().lower()
    value = value.replace("-", " ")
    value = value.replace("&", "and")
    value = re.sub(r"[^a-z0-9\s]", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


# ============================================================
# FIND COLUMNS HELPER FUNCTIONS
# ============================================================

def find_tshirt_column(df):
    possible_columns = [
        "T-Shirt Size", "Tshirt Size", "T-Shirt", "Tshirt",
        "Shirt Size", "T Shirt Size", "T shirt size", "T-shirt size"
    ]
    for column in possible_columns:
        if column in df.columns:
            return column
    for column in df.columns:
        normalized = str(column).lower().replace("-", "").replace("_", "").replace(" ", "")
        if "tshirt" in normalized or "shirtsize" in normalized:
            return column
    return None

def find_nickname_column(df):
    possible_columns = [
        "Nickname", "Nick Name", "Nick_Name", "Alias", "Call Sign", "Preferred Name"
    ]
    for column in possible_columns:
        if column in df.columns:
            return column
    for column in df.columns:
        normalized = str(column).lower().replace("-", "").replace("_", "").replace(" ", "")
        if "nick" in normalized or "alias" in normalized:
            return column
    return None


# ============================================================
# SHIRT SIZE SORTING
# ============================================================

def shirt_sort_key(size):
    size_str = str(size).upper().strip()
    size_order = {
        "XXXS": 0, "XXS": 1, "XS": 2, "S": 3, "M": 4,
        "L": 5, "XL": 6, "XXL": 7, "2XL": 7, "XXXL": 8,
        "3XL": 8, "4XL": 9, "5XL": 10, "NOT SPECIFIED": 99
    }
    if size_str in size_order:
        return (size_order[size_str], size_str)
    match = re.search(r'(\d+)', size_str)
    if match:
        return (int(match.group(1)) + 20, size_str)
    return (50, size_str)


# ============================================================
# FIND DELEGATION HEAD
# ============================================================

def find_delegation_head(delegation_heads_df, vicariate_name, school_name):
    if delegation_heads_df.empty:
        return None

    possible_affil_cols = ["School / CYM Affiliation", "Parish / Church", "School", "Affiliation"]
    affil_col = next((c for c in possible_affil_cols if c in delegation_heads_df.columns), None)

    if not affil_col or "Vicariate" not in delegation_heads_df.columns or "Full Name" not in delegation_heads_df.columns:
        return None

    target_vicariate = normalize_text(vicariate_name)
    target_school = normalize_text(school_name)

    for _, row in delegation_heads_df.iterrows():
        if normalize_text(row["Vicariate"]) != target_vicariate:
            continue

        affiliations = [
            normalize_text(item)
            for item in str(row[affil_col]).split(";")
            if item.strip()
        ]

        if target_school in affiliations:
            name = row.get("Full Name")
            if pd.notna(name) and str(name).strip():
                return str(name).strip()
    return None


# ============================================================
# BUILD SINGLE SCHOOL FLOWABLES
# ============================================================

def build_school_story(
    school_name,
    vicariate_name,
    records_df,
    nickname_col,
    tshirt_col,
    delegation_head_name
):
    story_items = []
    content_width = PAGE_WIDTH - 72
    styles = getSampleStyleSheet()

    school_style = ParagraphStyle(
        'SchoolHeading',
        parent=styles['Heading1'],
        fontName=FONT_BOLD,
        fontSize=14.5,
        leading=17.5,
        textColor=COLOR_DARK_NAVY,
        spaceAfter=2
    )
    meta_left_style = ParagraphStyle(
        'MetaLeft',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor("#4A5568")
    )
    meta_right_style = ParagraphStyle(
        'MetaRight',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=9.5,
        leading=12,
        textColor=COLOR_PRIMARY_BLUE,
        alignment=TA_RIGHT
    )
    header_cell_style = ParagraphStyle(
        'HeaderCell',
        parent=styles['Normal'],
        fontName=FONT_BOLD,
        fontSize=8.5,
        leading=11,
        textColor=COLOR_DARK_NAVY
    )
    header_cell_center = ParagraphStyle(
        'HeaderCellCenter',
        parent=header_cell_style,
        alignment=TA_CENTER
    )
    body_cell_style = ParagraphStyle(
        'BodyCell',
        parent=styles['Normal'],
        fontName=FONT_REGULAR,
        fontSize=8.5,
        leading=11,
        textColor=COLOR_DARK_NAVY
    )
    body_cell_center = ParagraphStyle(
        'BodyCellCenter',
        parent=body_cell_style,
        alignment=TA_CENTER
    )
    body_cell_shirt = ParagraphStyle(
        'BodyCellShirt',
        parent=body_cell_style,
        fontName=FONT_BOLD,
        textColor=COLOR_PRIMARY_BLUE,
        alignment=TA_CENTER
    )

    story_items.append(Paragraph(str(school_name).upper(), school_style))

    meta_table_data = [[
        Paragraph(f"VICARIATE: {vicariate_name}", meta_left_style),
        Paragraph(f"TOTAL DELEGATES: {len(records_df)}", meta_right_style)
    ]]

    meta_table = Table(meta_table_data, colWidths=[350, content_width - 350])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, -1), 2.5, COLOR_YELLOW_ACCENT),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))

    story_items.append(meta_table)
    story_items.append(Spacer(1, 8))

    col_widths = [35, 255, 150, 100]
    table_data = [[
        Paragraph("#", header_cell_center),
        Paragraph("FULL NAME", header_cell_style),
        Paragraph("NICKNAME", header_cell_style),
        Paragraph("T-SHIRT", header_cell_center)
    ]]

    for idx, (_, row) in enumerate(records_df.iterrows(), start=1):
        fullname = str(row.get("Full Name", "")).strip() or "-"
        nickname = str(row.get(nickname_col, "")).strip() or "-" if nickname_col else "-"
        tshirt = str(row.get(tshirt_col, "")).strip() or "-" if tshirt_col else "-"

        table_data.append([
            Paragraph(str(idx), body_cell_center),
            Paragraph(fullname, body_cell_style),
            Paragraph(nickname, body_cell_style),
            Paragraph(tshirt, body_cell_shirt)
        ])

    participant_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    t_style = [
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_YELLOW_ACCENT),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]

    for i in range(1, len(table_data)):
        bg = COLOR_BG_LIGHT if i % 2 == 0 else colors.white
        t_style.append(('BACKGROUND', (0, i), (-1, i), bg))

    participant_table.setStyle(TableStyle(t_style))
    story_items.append(participant_table)

    story_items.append(Spacer(1, 20))
    signature_title_style = ParagraphStyle(
        'SignatureTitle', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=9.5, leading=12, textColor=COLOR_DARK_NAVY
    )
    signature_name_style = ParagraphStyle(
        'SignatureName', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=10, leading=13, textColor=COLOR_DARK_NAVY, alignment=TA_CENTER
    )
    signature_label_style = ParagraphStyle(
        'SignatureLabel', parent=styles['Normal'],
        fontName=FONT_REGULAR, fontSize=8, leading=10, textColor=colors.HexColor("#718096"), alignment=TA_CENTER
    )

    signature_table = Table(
        [
            [Paragraph("DELEGATION HEAD", signature_title_style)],
            [Spacer(1, 24)],
            [Paragraph(delegation_head_name if delegation_head_name else "________________________________", signature_name_style)],
            [Paragraph("Signature over Printed Name", signature_label_style)],
            [Spacer(1, 8)],
            [Paragraph("Date: ______________________________", signature_label_style)]
        ],
        colWidths=[250],
        hAlign='LEFT'
    )
    signature_table.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))

    story_items.append(signature_table)
    return story_items


# ============================================================
# PARTICIPANT LABEL PDF (PARTICIPANTS + DELEGATION HEADS)
# ============================================================

LABEL_PAGE_WIDTH = 8.5 * inch
LABEL_PAGE_HEIGHT = 11.0 * inch
LABEL_PAGE_SIZE = (LABEL_PAGE_WIDTH, LABEL_PAGE_HEIGHT)

LABEL_COLUMNS = 3
LABEL_ROWS = 8
LABELS_PER_PAGE = LABEL_COLUMNS * LABEL_ROWS

LABEL_MARGIN_X = 0.20 * inch
LABEL_MARGIN_Y = 0.20 * inch
LABEL_GAP_X = 0.06 * inch
LABEL_GAP_Y = 0.06 * inch

LABEL_WIDTH = (
    LABEL_PAGE_WIDTH
    - (2 * LABEL_MARGIN_X)
    - ((LABEL_COLUMNS - 1) * LABEL_GAP_X)
) / LABEL_COLUMNS

LABEL_HEIGHT = (
    LABEL_PAGE_HEIGHT
    - (2 * LABEL_MARGIN_Y)
    - ((LABEL_ROWS - 1) * LABEL_GAP_Y)
) / LABEL_ROWS


def build_participant_labels_pdf(participants_df, delegation_heads_df, output_path):
    print("\n==============================================")
    print("GENERATING COMBINED LABEL PDF (PARTICIPANTS + HEADS)...")
    print("==============================================")

    # 1. Standardize Participants
    p_df = participants_df.copy() if participants_df is not None and not participants_df.empty else pd.DataFrame()
    if not p_df.empty:
        p_df["Full Name"] = p_df["Full Name"].fillna("").astype(str).str.strip()
        p_df["School / CYM Affiliation"] = (
            p_df["School / CYM Affiliation"].fillna("Not Specified").astype(str).str.strip()
        )
        p_df["Vicariate"] = p_df["Vicariate"].fillna("Not Specified").astype(str).str.strip()
        p_df["Is_Head"] = False
        p_df = p_df[p_df["Full Name"] != ""].copy()
    else:
        p_df = pd.DataFrame(columns=["Full Name", "School / CYM Affiliation", "Vicariate", "Is_Head"])

    # 2. Expand Delegation Heads (supports multi-school affiliations split by ';')
    head_records = []
    if delegation_heads_df is not None and not delegation_heads_df.empty:
        possible_affil_cols = ["School / CYM Affiliation", "Parish / Church", "School", "Affiliation"]
        affil_col = next((c for c in possible_affil_cols if c in delegation_heads_df.columns), None)

        for _, row in delegation_heads_df.iterrows():
            name = str(row.get("Full Name", "")).strip()
            vic = str(row.get("Vicariate", "Not Specified")).strip()
            raw_affil = str(row.get(affil_col, "Not Specified")).strip() if affil_col else "Not Specified"

            if not name:
                continue

            affil_list = [a.strip() for a in raw_affil.split(";") if a.strip()]
            if not affil_list:
                affil_list = ["Not Specified"]

            for a in affil_list:
                head_records.append({
                    "Full Name": name,
                    "School / CYM Affiliation": a,
                    "Vicariate": vic,
                    "Is_Head": True
                })

    heads_expanded_df = pd.DataFrame(head_records)

    # 3. Merge & Sort (Delegation Heads first within each school)
    combined_df = pd.concat([heads_expanded_df, p_df], ignore_index=True)

    if combined_df.empty:
        print("No participants or delegation heads available to generate labels.")
        return

    combined_df = combined_df.sort_values(
        by=["Vicariate", "School / CYM Affiliation", "Is_Head", "Full Name"],
        ascending=[True, True, False, True],
        key=lambda col: col if col.name == "Is_Head" else col.astype(str).str.casefold()
    ).reset_index(drop=True)

    c = canvas.Canvas(output_path, pagesize=LABEL_PAGE_SIZE)

    NAME_FONT = FONT_BOLD
    SCHOOL_FONT = FONT_REGULAR
    VICARIATE_FONT = FONT_REGULAR
    ROLE_FONT = FONT_BOLD

    def fit_text(text, font_name, font_size, max_width, minimum_size=5):
        text = str(text).strip()
        current_size = font_size

        while current_size >= minimum_size:
            if pdfmetrics.stringWidth(text, font_name, current_size) <= max_width:
                return text, current_size
            current_size -= 0.25

        current_size = minimum_size
        ellipsis = "..."
        shortened_text = text

        while len(shortened_text) > 4:
            shortened = shortened_text[:-4] + ellipsis
            if pdfmetrics.stringWidth(shortened, font_name, current_size) <= max_width:
                return shortened, current_size
            shortened_text = shortened_text[:-1]

        return shortened_text, current_size

    def draw_centered_text(text, center_x, y, font_name, font_size, color=COLOR_DARK_NAVY):
        c.saveState()
        c.setFont(font_name, font_size)
        c.setFillColor(color)
        c.drawCentredString(center_x, y, text)
        c.restoreState()

    for index, row in combined_df.iterrows():
        position = index % LABELS_PER_PAGE
        column = position % LABEL_COLUMNS
        row_number = position // LABEL_COLUMNS

        x = LABEL_MARGIN_X + column * (LABEL_WIDTH + LABEL_GAP_X)
        y = LABEL_PAGE_HEIGHT - LABEL_MARGIN_Y - ((row_number + 1) * LABEL_HEIGHT) - (row_number * LABEL_GAP_Y)

        c.setStrokeColor(colors.HexColor("#A0AEC0"))
        c.setLineWidth(0.5)
        c.rect(x, y, LABEL_WIDTH, LABEL_HEIGHT, stroke=1, fill=0)

        center_x = x + LABEL_WIDTH / 2
        padding = 0.08 * inch
        max_text_width = LABEL_WIDTH - (2 * padding)

        fullname = row["Full Name"]
        school = row["School / CYM Affiliation"]
        vicariate = row["Vicariate"]
        is_head = row.get("Is_Head", False)

        if is_head:
            # 4-line layout tailored for Delegation Heads
            display_name, name_size = fit_text(fullname, NAME_FONT, 8.5, max_text_width, minimum_size=6.5)
            display_school, school_size = fit_text(school, SCHOOL_FONT, 6.0, max_text_width, minimum_size=5.0)
            display_vicariate, vicariate_size = fit_text(vicariate, VICARIATE_FONT, 6.0, max_text_width, minimum_size=5.0)

            name_y = y + LABEL_HEIGHT - 0.28 * inch
            role_y = y + LABEL_HEIGHT - 0.44 * inch
            school_y = y + LABEL_HEIGHT - 0.68 * inch
            vicariate_y = y + LABEL_HEIGHT - 0.88 * inch

            draw_centered_text(display_name, center_x, name_y, NAME_FONT, name_size)
            draw_centered_text("[ DELEGATION HEAD ]", center_x, role_y, ROLE_FONT, 6.0, color=COLOR_PRIMARY_BLUE)
            draw_centered_text(display_school, center_x, school_y, SCHOOL_FONT, school_size)
            draw_centered_text(display_vicariate, center_x, vicariate_y, VICARIATE_FONT, vicariate_size)
        else:
            # Standard 3-line layout for Participants
            display_name, name_size = fit_text(fullname, NAME_FONT, 9.5, max_text_width, minimum_size=7)
            display_school, school_size = fit_text(school, SCHOOL_FONT, 6.5, max_text_width, minimum_size=5.5)
            display_vicariate, vicariate_size = fit_text(vicariate, VICARIATE_FONT, 6.5, max_text_width, minimum_size=5.5)

            name_y = y + LABEL_HEIGHT - 0.36 * inch
            school_y = y + LABEL_HEIGHT - 0.63 * inch
            vicariate_y = y + LABEL_HEIGHT - 0.84 * inch

            draw_centered_text(display_name, center_x, name_y, NAME_FONT, name_size)
            draw_centered_text(display_school, center_x, school_y, SCHOOL_FONT, school_size)
            draw_centered_text(display_vicariate, center_x, vicariate_y, VICARIATE_FONT, vicariate_size)

        if position == LABELS_PER_PAGE - 1:
            c.showPage()

    if len(combined_df) % LABELS_PER_PAGE != 0:
        c.showPage()

    c.save()

    total_pages = (len(combined_df) + LABELS_PER_PAGE - 1) // LABELS_PER_PAGE
    print("Label PDF created:")
    print(f"  Participants: {len(p_df)}")
    print(f"  Delegation Head Labels: {len(heads_expanded_df)}")
    print(f"  Total Labels: {len(combined_df)}")
    print(f"  Pages: {total_pages}")
    print(f"  File: {output_path}")


# ============================================================
# READ CLEANED EXCEL FILE
# ============================================================

print("\nReading cleaned Excel file...")
df = pd.read_excel(INPUT_FILE, sheet_name="Participants")
print(f"Loaded {len(df)} records.")


# ============================================================
# READ DELEGATION HEADS FILE
# ============================================================

print("\nReading delegation heads file...")
if os.path.exists(DELEGATION_HEADS_FILE):
    delegation_heads_df = pd.read_excel(DELEGATION_HEADS_FILE, sheet_name="Delegation Heads")
    print(f"Loaded {len(delegation_heads_df)} delegation heads.")
else:
    print(f"WARNING: Delegation Heads file not found: {DELEGATION_HEADS_FILE}")
    delegation_heads_df = pd.DataFrame(columns=["Vicariate", "School / CYM Affiliation", "Full Name"])


# ============================================================
# CHECK REQUIRED COLUMNS & DETECT OPTIONAL
# ============================================================

required_columns = ["Type", "Vicariate", "School / CYM Affiliation", "Full Name"]
for column in required_columns:
    if column not in df.columns:
        raise ValueError(f"ERROR: Column '{column}' was not found.")

tshirt_column = find_tshirt_column(df)
if tshirt_column:
    print(f"T-shirt size column detected: '{tshirt_column}'")
else:
    print("WARNING: No T-shirt size column detected.")

nickname_column = find_nickname_column(df)
if nickname_column:
    print(f"Nickname column detected: '{nickname_column}'")
else:
    print("WARNING: No Nickname column detected.")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ============================================================
# STORAGE FOR ANALYSIS
# ============================================================

all_participant_rows = []
all_delegation_head_rows = []
all_attendee_rows = []
all_school_summary_rows = []
all_vicariate_summary_rows = []
all_tshirt_rows = []
master_pdf_story = []
school_count_total = 0


# ============================================================
# PROCESS EACH OFFICIAL VICARIATE
# ============================================================

for vicariate_data in archdioceseData:
    vicariate = vicariate_data["name"]
    official_schools = vicariate_data["schools"]

    print("\n==================================================")
    print(f"VICARIATE: {vicariate}")
    print("==================================================")

    vicariate_key = normalize_text(vicariate)
    vicariate_df = df[df["Vicariate"].apply(normalize_text) == vicariate_key].copy()

    vicariate_folder = clean_name(vicariate)
    vicariate_path = os.path.join(OUTPUT_FOLDER, vicariate_folder)
    os.makedirs(vicariate_path, exist_ok=True)

    # 1. Delegation Heads
    delegation_heads = vicariate_df[
        vicariate_df["Type"].apply(normalize_text) == "delegation head"
    ].copy()

    if not delegation_heads.empty:
        for _, row in delegation_heads.iterrows():
            all_delegation_head_rows.append(row.to_dict())
        print(f"Delegation Heads: {len(delegation_heads)}")
    else:
        print("Delegation Heads: 0")

    # 2. Participants
    participants = vicariate_df[
        vicariate_df["Type"].apply(normalize_text) == "participant"
    ].copy()
    print(f"Total Participants: {len(participants)}")
    for _, row in participants.iterrows():
        all_participant_rows.append(row.to_dict())

    # 3. All Attendees
    attendees = vicariate_df[
        vicariate_df["Type"].apply(normalize_text).isin(["participant", "delegation head"])
    ].copy()
    for _, row in attendees.iterrows():
        all_attendee_rows.append(row.to_dict())

    # 4. Create Excel and Append to Master PDF Per School / CYM
    vicariate_tshirt_data = []
    for school in official_schools:
        print(f"\nSchool / CYM: {school}")
        school_key = normalize_text(school)

        # Participants for School
        school_participants = []
        for _, row in participants.iterrows():
            school_data = str(row["School / CYM Affiliation"]).strip()
            if not school_data:
                continue
            row_schools = [normalize_text(s) for s in school_data.split(";") if s.strip()]
            if school_key in row_schools:
                school_participants.append(row)

        # All Attendees for School
        school_attendees = []
        for _, row in attendees.iterrows():
            school_data = str(row["School / CYM Affiliation"]).strip()
            if not school_data:
                continue
            row_schools = [normalize_text(s) for s in school_data.split(";") if s.strip()]
            if school_key in row_schools:
                school_attendees.append(row)

        school_attendees_df = pd.DataFrame(school_attendees)
        school_filename = clean_name(school) + ".xlsx"
        participants_file = os.path.join(vicariate_path, school_filename)

        if school_participants:
            school_df = pd.DataFrame(school_participants)
            if "Full Name" in school_df.columns:
                school_df = school_df.sort_values(by="Full Name", ascending=True)

            school_df.to_excel(participants_file, index=False, sheet_name="Participants")

            delegation_head_name = find_delegation_head(delegation_heads_df, vicariate, school)
            if delegation_head_name:
                print(f"    Delegation Head: {delegation_head_name}")
            else:
                print("    Delegation Head: Not found")

            if master_pdf_story:
                master_pdf_story.append(PageBreak())

            master_pdf_story.extend(
                build_school_story(
                    school_name=school,
                    vicariate_name=vicariate,
                    records_df=school_df,
                    nickname_col=nickname_column,
                    tshirt_col=tshirt_column,
                    delegation_head_name=delegation_head_name
                )
            )

            school_count_total += 1
            participant_count = len(school_df)
            attendee_count = len(school_attendees_df)
            print(f"    Participants: {participant_count} (Excel saved & added to Master PDF)")
        else:
            participant_count = 0
            attendee_count = 0
            print("    Participants: 0")
            empty_df = pd.DataFrame(columns=df.columns)
            empty_df.to_excel(participants_file, index=False, sheet_name="Participants")
            school_df = empty_df

        school_summary = {
            "Vicariate": vicariate,
            "School / CYM": school,
            "Total Attendees": attendee_count,
            "Participants Only": participant_count
        }

        if tshirt_column and not school_attendees_df.empty:
            shirt_series = (
                school_attendees_df[tshirt_column]
                .fillna("Not Specified")
                .astype(str)
                .str.strip()
                .replace("", "Not Specified")
            )
            shirt_counts = shirt_series.value_counts().to_dict()
        else:
            shirt_counts = {}

        for size, count in shirt_counts.items():
            school_summary[size] = count
            vicariate_tshirt_data.append({
                "Vicariate": vicariate,
                "School / CYM": school,
                "T-Shirt Size": size,
                "Quantity": int(count)
            })

        all_school_summary_rows.append(school_summary)

    vicariate_summary = {
        "Vicariate": vicariate,
        "Total Attendees": len(attendees),
        "Participants Only": len(participants),
        "Delegation Heads": len(delegation_heads),
        "Schools / CYMs": len(official_schools)
    }

    if tshirt_column and not attendees.empty:
        vicariate_shirts = (
            attendees[tshirt_column]
            .fillna("Not Specified")
            .astype(str)
            .str.strip()
            .replace("", "Not Specified")
            .value_counts()
            .to_dict()
        )
        for size, count in vicariate_shirts.items():
            vicariate_summary[size] = int(count)
            all_tshirt_rows.append({
                "Vicariate": vicariate,
                "T-Shirt Size": size,
                "Quantity": int(count)
            })

    all_vicariate_summary_rows.append(vicariate_summary)


# ============================================================
# BUILD COMBINED MASTER PDF
# ============================================================

if master_pdf_story:
    print("\n==============================================")
    print("GENERATING COMBINED MASTER PDF...")
    print("==============================================")
    top_margin_space = (BANNER_HEIGHT + 14) if BANNER_FILE else 36
    doc = SimpleDocTemplate(
        MASTER_PDF_PATH,
        pagesize=PAGE_SIZE,
        leftMargin=36,
        rightMargin=36,
        topMargin=top_margin_space,
        bottomMargin=36
    )
    doc.build(master_pdf_story, canvasmaker=NumberedCanvas)
    print(f"Master PDF successfully created: {MASTER_PDF_PATH} ({school_count_total} schools/CYMs)")


# ============================================================
# CREATE DATAFRAMES FOR ANALYSIS
# ============================================================

participants_all_df = pd.DataFrame(all_participant_rows)
delegation_heads_all_df = pd.DataFrame(all_delegation_head_rows)
attendees_all_df = pd.DataFrame(all_attendee_rows)
school_summary_df = pd.DataFrame(all_school_summary_rows)
vicariate_summary_df = pd.DataFrame(all_vicariate_summary_rows)
tshirt_vicariate_df = pd.DataFrame(all_tshirt_rows)


# ============================================================
# CREATE MASTER DELEGATION HEADS FILE
# ============================================================

print("\n==================================================")
print("CREATING DELEGATION HEADS")
print("==================================================")
delegation_heads_file = os.path.join(OUTPUT_FOLDER, "Delegation Heads.xlsx")

if not delegation_heads_all_df.empty:
    sort_columns = [col for col in ["Vicariate", "Full Name"] if col in delegation_heads_all_df.columns]
    if sort_columns:
        delegation_heads_all_df = delegation_heads_all_df.sort_values(sort_columns).reset_index(drop=True)
    delegation_heads_all_df.to_excel(delegation_heads_file, index=False, sheet_name="Delegation Heads")
    print(f"Delegation Heads saved: {delegation_heads_file}")
else:
    empty_heads_df = pd.DataFrame(columns=df.columns)
    empty_heads_df.to_excel(delegation_heads_file, index=False, sheet_name="Delegation Heads")
    print("Empty Delegation Heads.xlsx created.")


# ============================================================
# CREATE T-SHIRT SUMMARY
# ============================================================

print("\n==================================================")
print("CREATING T-SHIRT SUMMARY")
print("==================================================")
tshirt_summary_file = os.path.join(OUTPUT_FOLDER, "T-Shirt Summary.xlsx")

with pd.ExcelWriter(tshirt_summary_file, engine="openpyxl") as writer:
    if tshirt_column:
        all_tshirt_data = []
        for _, row in attendees_all_df.iterrows():
            shirt_size = row[tshirt_column]
            shirt_size = "Not Specified" if pd.isna(shirt_size) or not str(shirt_size).strip() else str(shirt_size).strip()
            all_tshirt_data.append({
                "Vicariate": row["Vicariate"],
                "School / CYM": row["School / CYM Affiliation"],
                "T-Shirt Size": shirt_size
            })
        all_tshirt_df = pd.DataFrame(all_tshirt_data)

        # 1. Overall Shirt Demand
        overall_shirts = (
            all_tshirt_df["T-Shirt Size"]
            .value_counts()
            .reset_index()
        )
        overall_shirts.columns = ["T-Shirt Size", "Quantity"]
        overall_shirts = overall_shirts.sort_values("T-Shirt Size", key=lambda x: x.map(shirt_sort_key))
        overall_shirts.to_excel(writer, index=False, sheet_name="All Summary")

        # 2. Shirt by Vicariate
        shirt_by_vicariate = all_tshirt_df.pivot_table(
            index="Vicariate", columns="T-Shirt Size", values="School / CYM", aggfunc="count", fill_value=0
        ).reset_index()
        size_columns = sorted([col for col in shirt_by_vicariate.columns if col != "Vicariate"], key=shirt_sort_key)
        shirt_by_vicariate = shirt_by_vicariate[["Vicariate"] + size_columns]
        shirt_by_vicariate.to_excel(writer, index=False, sheet_name="By Vicariate")

        # 3. Shirt by School / CYM
        shirt_by_school = all_tshirt_df.pivot_table(
            index=["Vicariate", "School / CYM"], columns="T-Shirt Size", values="T-Shirt Size", aggfunc="count", fill_value=0
        ).reset_index()
        size_columns = sorted([col for col in shirt_by_school.columns if col not in ["Vicariate", "School / CYM"]], key=shirt_sort_key)
        shirt_by_school = shirt_by_school[["Vicariate", "School / CYM"] + size_columns]
        shirt_by_school.to_excel(writer, index=False, sheet_name="By School CYM")

        # 4. Individual Vicariate Sheets
        for vic in sorted(all_tshirt_df["Vicariate"].unique()):
            vicariate_shirts = all_tshirt_df[all_tshirt_df["Vicariate"] == vic]
            pivot = vicariate_shirts.pivot_table(
                index="School / CYM", columns="T-Shirt Size", values="T-Shirt Size", aggfunc="count", fill_value=0
            ).reset_index()
            sizes = sorted([col for col in pivot.columns if col != "School / CYM"], key=shirt_sort_key)
            pivot = pivot[["School / CYM"] + sizes]

            total_row = {"School / CYM": "VICARIATE TOTAL"}
            for size in sizes:
                total_row[size] = int(pivot[size].sum())

            pivot = pd.concat([pivot, pd.DataFrame([total_row])], ignore_index=True)
            sheet_name = clean_name(vic)[:31]
            pivot.to_excel(writer, index=False, sheet_name=sheet_name)
    else:
        pd.DataFrame({"Message": ["No T-shirt size column was detected."]}).to_excel(
            writer, index=False, sheet_name="All Summary"
        )

print(f"T-Shirt Summary saved: {tshirt_summary_file}")


# ============================================================
# BUSINESS INSIGHTS
# ============================================================

print("\n==================================================")
print("CREATING BUSINESS INSIGHTS")
print("==================================================")
business_insights_file = os.path.join(OUTPUT_FOLDER, "Business Insights.xlsx")

total_records = len(df)
total_attendees = len(attendees_all_df)
total_participants = len(participants_all_df)
total_delegation_heads = len(delegation_heads_all_df)
total_vicariates = len(archdioceseData)
total_schools = sum(len(item["schools"]) for item in archdioceseData)

if not participants_all_df.empty:
    vicariate_counts = participants_all_df["Vicariate"].value_counts().reset_index()
    vicariate_counts.columns = ["Vicariate", "Participants"]
    vicariate_counts["Percentage of Total"] = (vicariate_counts["Participants"] / total_participants * 100).round(2)
    vicariate_counts["Rank"] = range(1, len(vicariate_counts) + 1)
    vicariate_insights = vicariate_counts[["Rank", "Vicariate", "Participants", "Percentage of Total"]]
else:
    vicariate_insights = pd.DataFrame(columns=["Rank", "Vicariate", "Participants", "Percentage of Total"])

school_insights = school_summary_df.copy()
if not school_insights.empty:
    school_insights["Percentage of Total"] = (school_insights["Participants Only"] / total_participants * 100).round(2)
    school_insights = school_insights.sort_values("Participants Only", ascending=False).reset_index(drop=True)
    school_insights["Rank"] = range(1, len(school_insights) + 1)
    base_columns = ["Rank", "Vicariate", "School / CYM", "Total Attendees", "Participants Only", "Percentage of Total"]
    other_columns = sorted([col for col in school_insights.columns if col not in base_columns], key=shirt_sort_key)
    school_insights = school_insights[base_columns + other_columns]

registration_types = df["Type"].value_counts().reset_index()
registration_types.columns = ["Registration Type", "Count"]
registration_types["Percentage"] = (registration_types["Count"] / total_records * 100).round(2)

multi_affiliation_rows = []
if not participants_all_df.empty:
    for _, row in participants_all_df.iterrows():
        affiliation = str(row["School / CYM Affiliation"]).strip()
        affiliations = [item.strip() for item in affiliation.split(";") if item.strip()]
        if len(affiliations) > 1:
            multi_affiliation_rows.append({
                "Full Name": row["Full Name"],
                "Vicariate": row["Vicariate"],
                "School / CYM Affiliation": affiliation
            })
multi_affiliation_df = pd.DataFrame(multi_affiliation_rows)

quality_rows = []
def add_quality_check(field, missing_count, total):
    percentage = (missing_count / total * 100) if total > 0 else 0
    quality_rows.append({
        "Field": field,
        "Missing Records": int(missing_count),
        "Total Records": int(total),
        "Missing Percentage": round(percentage, 2)
    })

add_quality_check("Full Name", df["Full Name"].isna().sum(), total_records)
add_quality_check("Vicariate", df["Vicariate"].isna().sum(), total_records)
add_quality_check("School / CYM Affiliation", df["School / CYM Affiliation"].isna().sum(), total_records)
if tshirt_column:
    add_quality_check("T-Shirt Size (All Attendees)", attendees_all_df[tshirt_column].isna().sum(), total_attendees)
data_quality = pd.DataFrame(quality_rows)

largest_vicariate_name = vicariate_insights.iloc[0]["Vicariate"] if not vicariate_insights.empty else "N/A"
largest_vicariate_count = int(vicariate_insights.iloc[0]["Participants"]) if not vicariate_insights.empty else 0
largest_school_name = school_insights.iloc[0]["School / CYM"] if not school_insights.empty else "N/A"
largest_school_vicariate = school_insights.iloc[0]["Vicariate"] if not school_insights.empty else "N/A"
largest_school_count = int(school_insights.iloc[0]["Participants Only"]) if not school_insights.empty else 0

if tshirt_column and not attendees_all_df.empty:
    shirt_series = attendees_all_df[tshirt_column].fillna("Not Specified").astype(str).str.strip().replace("", "Not Specified")
    shirt_demand = shirt_series.value_counts().reset_index()
    shirt_demand.columns = ["T-Shirt Size", "Quantity"]
    shirt_demand["T-Shirt Size"] = shirt_demand["T-Shirt Size"].astype(str)
    shirt_demand = shirt_demand.sort_values("T-Shirt Size", key=lambda x: x.map(shirt_sort_key)).reset_index(drop=True)
    total_shirts = int(shirt_demand["Quantity"].sum())
    top_shirt = shirt_demand.sort_values("Quantity", ascending=False).iloc[0]
    top_shirt_size = top_shirt["T-Shirt Size"]
    top_shirt_quantity = int(top_shirt["Quantity"])
else:
    shirt_demand = pd.DataFrame(columns=["T-Shirt Size", "Quantity"])
    total_shirts = 0
    top_shirt_size = "N/A"
    top_shirt_quantity = 0

key_insights = [{
    "Category": "Participation",
    "Insight": f"There are {total_participants:,} registered participants across {total_vicariates} official vicariates and {total_schools} official schools/CYMs."
}]

if largest_vicariate_count > 0:
    percentage = (largest_vicariate_count / total_participants * 100)
    key_insights.append({
        "Category": "Vicariate",
        "Insight": f"{largest_vicariate_name} has the largest delegation with {largest_vicariate_count:,} participants ({percentage:.2f}% of total participants)."
    })

if largest_school_count > 0:
    percentage = (largest_school_count / total_participants * 100)
    key_insights.append({
        "Category": "School / CYM",
        "Insight": f"{largest_school_name} under {largest_school_vicariate} has the largest school/CYM delegation with {largest_school_count:,} participants ({percentage:.2f}% of total participants)."
    })

if total_shirts > 0:
    key_insights.append({
        "Category": "T-Shirt Demand",
        "Insight": f"{total_shirts:,} shirts are currently specified across all attendees. The most requested size is {top_shirt_size} with {top_shirt_quantity:,} units."
    })

multi_affiliation_count = len(multi_affiliation_df)
if multi_affiliation_count > 0:
    key_insights.append({
        "Category": "Multiple Affiliations",
        "Insight": f"{multi_affiliation_count:,} participants have more than one school/CYM affiliation and should be reviewed for delegation and merchandise allocation."
    })

missing_values = int(data_quality["Missing Records"].sum())
key_insights.append({
    "Category": "Data Quality",
    "Insight": "No missing values were detected in the checked fields." if missing_values == 0 else f"{missing_values:,} missing field entries were detected in the checked fields."
})

key_insights_df = pd.DataFrame(key_insights)

with pd.ExcelWriter(business_insights_file, engine="openpyxl") as writer:
    executive_summary = pd.DataFrame({
        "Metric": [
            "Total Registration Records", "Total Attendees", "Total Participants",
            "Total Delegation Heads", "Official Vicariates", "Official Schools / CYMs",
            "Largest Vicariate", "Largest Vicariate Participants", "Largest School / CYM",
            "Largest School / CYM Vicariate", "Largest School / CYM Participants",
            "Total T-Shirts Specified", "Most Requested T-Shirt Size", "Most Requested Size Quantity",
            "Participants with Multiple Affiliations"
        ],
        "Value": [
            total_records, total_attendees, total_participants,
            total_delegation_heads, total_vicariates, total_schools,
            largest_vicariate_name, largest_vicariate_count, largest_school_name,
            largest_school_vicariate, largest_school_count, total_shirts,
            top_shirt_size, top_shirt_quantity, multi_affiliation_count
        ]
    })
    executive_summary.to_excel(writer, index=False, sheet_name="Executive Summary")
    key_insights_df.to_excel(writer, index=False, sheet_name="Key Insights")
    vicariate_insights.to_excel(writer, index=False, sheet_name="Vicariate Insights")
    school_insights.to_excel(writer, index=False, sheet_name="School CYM Insights")
    shirt_demand.to_excel(writer, index=False, sheet_name="T-Shirt Demand")
    if tshirt_column and not attendees_all_df.empty:
        shirt_by_vicariate.to_excel(writer, index=False, sheet_name="Shirt by Vicariate")
        shirt_by_school.to_excel(writer, index=False, sheet_name="Shirt by School CYM")
    registration_types.to_excel(writer, index=False, sheet_name="Registration Types")
    if not multi_affiliation_df.empty:
        multi_affiliation_df.to_excel(writer, index=False, sheet_name="Multi-Affiliation")
    else:
        pd.DataFrame({"Message": ["No multiple school/CYM affiliations detected."]}).to_excel(
            writer, index=False, sheet_name="Multi-Affiliation"
        )
    data_quality.to_excel(writer, index=False, sheet_name="Data Quality")

print(f"Business Insights saved: {business_insights_file}")


# ============================================================
# CREATE PARTICIPANT & DELEGATION HEAD LABEL PDF
# ============================================================

# Prefer processed dataframes, falling back to loaded file data
heads_to_pass = delegation_heads_all_df if not delegation_heads_all_df.empty else delegation_heads_df

if not participants_all_df.empty or not heads_to_pass.empty:
    build_participant_labels_pdf(
        participants_df=participants_all_df,
        delegation_heads_df=heads_to_pass,
        output_path=LABEL_PDF_PATH
    )
else:
    print("No records found; label PDF was not generated.")

print("\n==================================================")
print("PROCESS COMPLETE")
print("==================================================")
print(f"Master PDF: {os.path.abspath(MASTER_PDF_PATH)}")
print(f"Labels PDF: {os.path.abspath(LABEL_PDF_PATH)}")
print(f"Delegations Directory: {os.path.abspath(OUTPUT_FOLDER)}\n")