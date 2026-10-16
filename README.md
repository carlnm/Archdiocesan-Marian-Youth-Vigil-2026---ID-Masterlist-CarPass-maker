# Archdiocesan-Marian-Youth-Day-2026---ID-Masterlist-Car-Pass-maker
Here is the complete, integrated `README.md` containing both the pipeline setup instructions and the detailed input data dictionary.

---

# Parish Registration Data Pipeline (Marian Youth Vigil 2026)

This repository contains automated data-cleaning and sorting pipelines to process, normalize, and organize raw parish group registrations exported from Google Forms for the New Marian Youth Vigil 2026.

---

## Repository Structure

```text
.
├── Input/
│   └── (Parishes) New Marian Youth Vigil 2026 - Official Group Registration (Responses)-11.xlsx
├── Scripts/
│   ├── Cleaner.py
│   └── Sorter.py
├── Parish Cleaned.xlsx
├── .gitignore
├── requirements.txt
└── README.md

```

* **`Input/`**: Stores raw, unprocessed participant registration data exported from Google Forms/Sheets.


* **`Scripts/Cleaner.py`**: Trims blank trailing columns, coalesces conditional parish selections, handles null values, unpivots participant blocks, and formats data.


* **`Scripts/Sorter.py`**: Groups, alphabetizes, and arranges records by vicariate and parish into the final operational layout.


* **`Parish Cleaned.xlsx`**: The final production-ready output workbook for event logistics and coordination.



---

## Input Data Dictionary

The source file in `Input/` is a wide, unpivoted spreadsheet where each row corresponds to one delegation submission containing 1 Delegation Head and up to 29 participants.

### 1. Submission & Delegation Metadata

Fields tracking submission timestamp and diocesan jurisdiction.

| Column Name | Data Type | Description |
| --- | --- | --- |
| `Timestamp` | DateTime | Submission date and time (`MM/DD/YYYY HH:MM:SS`). |
| `Email Address` | String | Contact email of the submitting youth coordinator. |
| `Select Your Vicariate` | Categorical / String | Administrative ecclesiastical district/vicariate under the diocese. |

### 2. Delegation Head Details

Details of the primary adult/youth leader managing the group delegation.

| Column Name | Data Type | Description |
| --- | --- | --- |
| `Delegation Head Contact Number` | String | Primary mobile or phone contact. |
| `Delegation Head Full Name` | String | Full name of the delegation leader. |
| `Delegation Head Nickname` | String | Preferred name for badges and announcements. |
| `Delegation Head Age` | Integer | Leader's age in years. |
| `Delegation Head T-Shirt Size` | Categorical | Event apparel size (e.g., `XS`, `S`, `M`, `L`, `XL`, `2XL`). |

### 3. Conditional Parish Affiliation Columns

Because Google Forms uses branched logic based on vicariate selection, responses route into separate vicariate-specific church lists:

* `Select your Parish / Church Affiliation` (Vicariate 1)
* `Select your Parish / Church Affiliation 2` through `Select your Parish / Church Affiliation 9` (Vicariates 2 through 9)

> **ETL Rule:** For any single submission row, only **one** of these nine columns contains a parish name; the other eight are empty (`NaN`). `Cleaner.py` coalesces these into a single consolidated `Parish` column.
> 
> 

### 4. Participant Blocks (`Participant 1` to `Participant 29`)

The form provides repeating blocks of four attributes for up to 29 participants per delegation:

* `Participant [i] Full Name`
* `Participant [i] Nickname`
* `Participant [i] Age`
* `Participant [i] T-Shirt Size`

> **ETL Rule:** Blank attendee blocks indicate unused slots. `Cleaner.py` unpivots (melts) valid attendee rows from wide format to long format, linking each attendee back to their Delegation Head, Parish, and Vicariate.
> 
> 

### 5. Verification & Financial Proofs

* **`Upload your receipt Here`**: URL linking to the uploaded payment slip or deposit receipt in Google Drive.
* **`Group Verification & Endorsement`**: Verification file link or statement from parish clergy endorsing the delegation.

### 6. Trailing Blank Columns (`Column1` through `Column16249`)

Artifacts generated during sheet export representing unused worksheet grid cells. These columns contain no response data and are discarded immediately upon loading the workbook:

```python
df = df.loc[:, ~df.columns.str.startswith('Column')]

```

---

## Setup & Installation

1. **Clone the repository:**
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>

```


2. **Create and activate a virtual environment:**
* **macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate

```


* **Windows:**
```bash
python -m venv venv
venv\Scripts\activate

```




3. **Install dependencies:**
```bash
pip install pandas openpyxl

```



---

## Execution Workflow

Run the data pipeline scripts from the repository root:

1. **Clean and normalize the raw data:**
```bash
python Scripts/Cleaner.py

```


Removes phantom columns, coalesces parish fields, standardizes sizes, and melts participant groups into flat tabular records.


2. **Sort and generate the final distribution sheets:**
```bash
python Scripts/Sorter.py

```


Sorts participants by vicariate, parish, and name, writing the finalized table to `Parish Cleaned.xlsx`.



---

Here is a comprehensive `README.md` file tailored specifically for `sorter.py`.

---

# Delegation Sorter & Publishing Pipeline (`sorter.py`)

`sorter.py` is the downstream processing and document generation engine for the **Archdiocesan Marian Youth Vigil 2026**. It consumes cleaned parish and school/CYM datasets, segments participants by ecclesiastical boundaries, and automatically compiles printable reports, identification labels, delegation workbooks, and an interactive tracking dashboard.

---


## Overview & Architecture

```text
[Parishes/Parish Cleaned.xlsx]  ──┐
                                  ├──> [sorter.py] ──> Multi-Format Distribution:
[CYM Input Excel (Optional)]    ──┘      │
                                         ├── 1. Interactive Excel Tracker (Formulas, Live Caps)
                                         ├── 2. Master Delegation PDF (Folio/Legal, Endorsement Signatures)
                                         ├── 3. Printable Name Badge Labels PDF (Letter, 3x8 Grid)
                                         ├── 4. Hierarchical Excel Folders (Per Vicariate/Parish)
                                         └── 5. Logistics Reports (T-Shirt & Business Analytics)

```

---

## Input Requirements

The script expects the following source files relative to the working directory:

| Path / Constant | Required | Description |
| --- | --- | --- |
| `Parishes/Parish Cleaned.xlsx` | **Yes** | Master cleaned dataset for Parishes generated by `Cleaner.py`. |
| `CYM/Marian_Youth_Vigil_2026_Cleaned_School_CYM.xlsx` | Optional | Cleaned roster for School and CYM delegations. Handled gracefully if missing. |
| `banner.png` / `.jpg` | Optional | Header banner image applied to each page of the Master PDF. Scales proportionally across the top page margin. |
| Fonts (`Garet-*.ttf`) | Optional | Custom brand typography (`Garet-Regular`, `Garet-Bold`). Falls back to `Helvetica` automatically if not found locally. |

### Minimum Required Columns in Input Data:

* **Participant Names:** `Full Name`
* **Geographic Jurisdiction:** `Vicariate`
* **Affiliation:** `Parish / Church` (or auto-detected via `School / CYM`, `School Name`, `Parish`, etc.)
* **Participant Classification:** `Type` (or `type_col`) containing values `Participant` vs `Delegation Head`
* **Logistics Fields:** T-shirt size (detected from `T-Shirt Size`, `Shirt Size`, etc.) and Nickname (detected from `Nickname`, `Call Sign`, `Alias`, etc.)

---

## Generated Outputs

All compiled artifacts are written to `Parishes/Marian Youth Vigil 2026 - Delegations/`:

```text
Parishes/Marian Youth Vigil 2026 - Delegations/
├── Unified_Parish_CYM_Delegation_Tracker.xlsx   # Interactive quota & registration tracker
├── Masterlist_All_Parishes.pdf                  # Official delegation sign-off sheet (Folio/Legal)
├── Participant_Labels_All.pdf                   # 3x8 badge label sheets (Letter, 24/page)
├── Delegation Heads.xlsx                         # Dedicated contact roster for leaders
├── T-Shirt Summary.xlsx                         # Total aggregate apparel counts
├── Business Insights.xlsx                       # Cross-tabulations & participation metrics
└── [Vicariate Folders]/                         # e.g., "Vicariate 1", "Vicariate 2"
    ├── [Parish Name 1].xlsx
    └── [Parish Name 2].xlsx

```

---

## Key Features & Business Logic

### 1. Interactive Excel Tracker (`Unified_Parish_CYM_Delegation_Tracker.xlsx`)

* **Real-time Quota Monitoring:** Built-in Excel formulas monitor checked delegations against a strict **400-delegate cap**:

$$\text{Selected Pax} = \text{SUMIF}(A7:A_N, \text{TRUE}, G7:G_N)$$


* **Dynamic Warning Banner:** Row 2 features an dynamic alert string that counts remaining slots and updates live when rows are toggled.
* **Conditional Formatting:** The alert banner automatically switches to a red warning fill (`#FED7D7`) and dark red text (`#9B2C2C`) when selected attendees reach or exceed 400.
* **Interactive Validation:** Column A is pre-configured with `TRUE`/`FALSE` drop-down menus via Excel Data Validation.

### 2. Official Delegation Master PDF (`Masterlist_All_Parishes.pdf`)

* **Formal Parish Page Breaks:** Each parish delegation starts cleanly on a fresh page.
* **Header & Endorsement Blocks:** Displays vicariate, total delegation headcount, and dynamically matches the **Delegation Head** name at the bottom with a signature-over-printed-name verification block.
* **Dynamic Running Footers:** Implements a two-pass `NumberedCanvas` displaying accurate `"Page X of Y"` and event credentials.

### 3. Printable Name Labels (`Participant_Labels_All.pdf`)

* **Integrated Delegation Heads:** Expands and sorts leaders to appear at the very beginning of their parish's label sequence.
* **Distinct Visual Roles:** Delegation heads feature a dedicated `[ DELEGATION HEAD ]` subtitle tag rendered in royal blue (`#0D6EFD`).
* **Auto-Shrink & Truncation Engine (`fit_text`):** Automatically scales down long names to fit inside fixed boundary boxes, dropping to a minimum font threshold before applying smart ellipsis truncation (`...`).

### 4. Modular Vicariate Export

* Scans all parish participants and partitions them into dedicated subfolders named after their respective vicariates (`Vicariate 1/`, `Vicariate 2/`, etc.).
* Strips invalid filesystem characters (`:`, `/`, `\`, `?`, `*`, `<`, `>`, `|`) from sheet and file titles automatically.

---

## Prerequisites & Dependencies

The pipeline requires **Python 3.9+** and standard data science / document publishing libraries:

```bash
pip install pandas openpyxl pillow reportlab

```

---

## Usage & Execution

1. Place the cleaned datasets into their designated folders:
* `Parishes/Parish Cleaned.xlsx`
* `CYM/Marian_Youth_Vigil_2026_Cleaned_School_CYM.xlsx` *(optional)*


2. *(Optional)* Place your branding banner (`banner.png` or `banner.jpg`) and font files (`Garet-Regular.ttf`, `Garet-Bold.ttf`) in the root directory.
3. Execute the script from the project root:
```bash
python Scripts/sorter.py

```


4. Access the generated documents inside `Parishes/Marian Youth Vigil 2026 - Delegations/`.

---

## Design, Dimensions & Printing Standards

| Document | Target Paper | Page Dimensions | Layout Specifications |
| --- | --- | --- | --- |
| **Master PDF** | **US Folio / Long Legal** | $8.5" \times 13.0"$ ($612 \times 936\text{ pt}$) | Top margin accommodates dynamic header banner; 0.5" side margins. |
| **Participant Labels** | **US Letter** | $8.5" \times 11.0"$ ($612 \times 792\text{ pt}$) | **3 Columns $\times$ 8 Rows** (24 labels per sheet). Outer margins: $0.20"$, inner gaps: $0.06"$. |

> ⚠️ **Printer Setting Advisory for Labels & Master PDFs:**
> When printing via Adobe Acrobat or system print dialogs, select **Actual Size (100%)**. Do **not** select *"Fit to Page"* or *"Shrink Oversized Pages"*, as automatic scaling disrupts the coordinate geometry of the pre-cut label grid.



---

# ID Maker & Badge Generation Pipeline Instructions (A4 Duplex Edition)

This guide documents the end-to-end workflow: taking cleaned participant registration data, bulk-generating individual ID badges in Canva, structuring the exported assets by parish folder, and compiling them into **A4 back-to-back (duplex) printable PDFs**.

---

## 1. End-to-End Pipeline Overview

```text
[Parish Cleaned.xlsx] (Output from Sorter.py)
         │
         ▼
[Export Parish CSV / Masterlist]
         │
         ▼
[Canva Bulk Create] (Map fields: Name, Nickname, Vicariate, Parish, Role)
         │
         ▼
[Export as PNG/JPG (ZIP)]
         │
         ▼
[Extract & Rename Folder -> badges/Raw ID/<Parish Name>/]
         │
         ▼
[badges/printer.py] (ReportLab Layout & Duplex Grid Engine)
         │
         ▼
[Compiled A4 Back-to-Back PDFs ready for Duplex Printing]

```

---

## 2. Directory Structure

Ensure the `badges/` workspace follows this layout:

```text
badges/
├── Raw ID/
│   ├── St. John the Baptist Parish/
│   │   ├── 1.png
│   │   ├── 2.png
│   │   └── ...
│   ├── Our Lady of the Rosary Parish/
│   │   ├── 1.png
│   │   └── ...
│   └── app.py
├── output_pdfs/
│   └── ...
├── printer.py
└── requirements.txt

```

---

## 3. Step-by-Step Instructions

### Step 1: Export Data for Canva

1. Open `Parish Cleaned.xlsx`.


2. Filter by the target Parish (or batch by Vicariate).


3. Ensure the required badge fields are present:
* `Full Name`

* `Nickname`

* `Parish`

* `Vicariate`

* `Role` (*Delegation Head* or *Participant*)




4. Export/save the filtered sheet as a **CSV (Comma Delimited)** file (e.g., `St_John_Parish.csv`).

---

### Step 2: Canva Bulk Create Execution

1. Open your official Marian Youth Vigil ID template in **Canva**.
2. On the left sidebar, click **Apps** $\rightarrow$ select **Bulk Create**.
3. Click **Upload CSV** and choose your exported CSV file.
4. Right-click text elements on the canvas to link them:
* Name element $\rightarrow$ **Connect Data** $\rightarrow$ `Full Name` (or `Nickname`).
* Parish element $\rightarrow$ **Connect Data** $\rightarrow$ `Parish`.
* Vicariate element $\rightarrow$ **Connect Data** $\rightarrow$ `Vicariate`.


5. Click **Continue**, select all records, and click **Generate Designs**.
* Canva will produce a multi-page document containing all individual badge pages.



---

### Step 3: Export & Rename Folder (Critical)

1. In Canva, click **Share** $\rightarrow$ **Download**.
2. Select **PNG** (preferred for sharp typography) or high-quality **JPG**.
3. Download all pages (Canva bundles them into a `.zip` archive).
4. **Extract the ZIP file**.
5. **Rename the unzipped folder** to match the exact parish name (e.g., `St. John the Baptist Parish`).
6. Move the renamed folder into `badges/Raw ID/`:
```text
badges/Raw ID/<Parish Name>/

```



---

### Step 4: Run the Badge Compiler (`printer.py`)

1. Activate your Python virtual environment:
```bash
cd badges
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate

```


2. Install dependencies:
```bash
pip install reportlab pillow openpyxl pandas

```


3. Run the generator:
```bash
python printer.py

```


*(or run `python "Raw ID/app.py"` depending on your entry point)*.



The script pairs front and back badge cards on mirrored grid coordinates so that each card's front aligns directly with its back when flipped along the page axis.

---

## 4. Printing Guidelines: Ensuring Perfect Front-to-Back Alignment

> ⚠️ **CRITICAL PAPER REQUIREMENT: USE ONLY A4 PAPER**
> The generator calculations (cell margins, card dimensions, gutters, and mirrored coordinate offsets) are calibrated specifically to the **ISO A4 standard (210 mm × 297 mm)**.
> * **DO NOT USE Letter (8.5" × 11") or Legal (8.5" × 14") paper.**
> * Using non-A4 paper will cause cumulative vertical and horizontal offsets, throwing the front and back badge borders out of alignment during duplex printing.
> 
> 

### Recommended Printer Settings

When printing the compiled PDF from Adobe Acrobat, Google Chrome, or system print dialogs:

| Setting | Required Value | Reason |
| --- | --- | --- |
| **Paper Size** | **A4** (210 × 297 mm) | Matches the ReportLab layout coordinate system. |
| **Page Scaling / Sizing** | **Actual Size** or **100%** | **Do NOT use "Fit to Page" or "Shrink oversized pages"**, as auto-scaling alters the margin offsets and shifts alignment. |
| **Two-Sided Printing** | **Print on both sides (Duplex)** | Enables front-to-back printing. |
| **Flip / Binding Edge** | **Flip on Long Edge** (Portrait) | Matches the vertical duplex page sequence built by `printer.py`.

 |
| **Auto-Rotate & Center** | **Off / Center Checked** | Prevents the print driver from shifting alternating pages. |

---

## 5. Alignment Troubleshooting Checklist

* [ ] **First-Copy Test:** Always run **1 test sheet** before starting full batch production. Hold the printed sheet up to a light source to verify front-to-back border registration.
* [ ] **Paper Tray Guides:** Ensure the paper tray guides are snug against the A4 paper stack so the sheets do not feed at an angle.
* [ ] **Manual Duplexing:** If using a manual duplex printer (feeding the page back in by hand), always re-insert the paper along the same leading edge without rotating it 180 degrees.


---

# Vehicle Pass & Car Pass Generation Pipeline Instructions

This guide outlines the complete workflow for managing vehicle access controls, bulk-creating vehicle passes in Canva, organizing vehicle passes by vicariate/parish, and compiling them into printable PDFs using the vehicle pass generation engine.

---

## 1. Directory Structure

Ensure the `vehicle/` workspace is structured as follows:

```text
vehicle/
├── Vehicle Control Masterlist.xlsx   # Source spreadsheet containing vehicle records
├── photos/                           # Exported pass images from Canva
│   ├── batch1/                       # Pass image files (e.g., PNG/JPG)
│   └── batch2/                       # Additional batches if exported in parts
├── vicariate_pdfs/                   # Output directory for generated pass PDFs
├── app.py                            # Layout and PDF generation script
└── requirements.txt

```

---

## 2. Input Data Dictionary: `Vehicle Control Masterlist.xlsx`

The vehicle masterlist tracks authorized vehicles and delegation convoys for parking allocation, security checkpoints, and pass issuance.

| Column Name | Data Type | Description | Usage / Formatting Guidelines |
| --- | --- | --- | --- |
| **`Control No.`** | String / Integer | Unique serial identifier assigned to each vehicle (e.g., `VP-001`, `001`). | Displayed prominently on the vehicle pass for checkpoint verification and gate access logging. |
| **`Vicariate`** | Categorical / String | Diocesan district or vicariate the delegation belongs to (e.g., `Vicariate 1`). | Used as the primary grouping key to bundle passes into vicariate-specific distribution PDFs. |
| **`Parish`** | String | Name of the parish or church sending the vehicle delegation. | Identifies the delegation origin and assists marshals in parking zone assignment. |
| **`Type of Vehicle`** | Categorical / String | Vehicle classification (e.g., `Van`, `Bus`, `Coaster`, `Jeepney`, `SUV`, `Private Car`, `Motorcycle`). | Dictates parking area designation (e.g., heavy bus vs. light vehicle parking bays). |

---

## 3. Step-by-Step Workflow

### Step 1: Prepare Masterlist Data

1. Open `vehicle/Vehicle Control Masterlist.xlsx`.


2. Verify that all vehicles have an assigned **`Control No.`**, **`Vicariate`**, **`Parish`**, and **`Type of Vehicle`**.
3. Export the worksheet (or specific vicariate slice) as a **CSV (Comma Delimited)** file (e.g., `vehicle_control.csv`).

---

### Step 2: Bulk Generate Car Passes in Canva

1. Open the official **Marian Youth Vigil Vehicle Pass** template in **Canva**.
2. From the left sidebar, navigate to **Apps** $\rightarrow$ select **Bulk Create**.
3. Click **Upload CSV** and choose `vehicle_control.csv`.
4. Connect the data fields to the designated text placeholders on the pass design:
* Control Number banner $\rightarrow$ **Connect Data** $\rightarrow$ `Control No.`
* Vicariate field $\rightarrow$ **Connect Data** $\rightarrow$ `Vicariate`
* Parish field $\rightarrow$ **Connect Data** $\rightarrow$ `Parish`
* Vehicle classification / badge tag $\rightarrow$ **Connect Data** $\rightarrow$ `Type of Vehicle`


5. Click **Continue**, select all records, and click **Generate Designs**.

---

### Step 3: Export & Organize Pass Assets

1. In Canva, select **Share** $\rightarrow$ **Download**.
2. Select **PNG** (recommended for sharp typography and barcode/QR clarity) or **JPG** at maximum quality.
3. Download the generated pass set (downloaded as a `.zip` archive).
4. Extract the `.zip` archive.
5. Move the exported image files into the appropriate folder under `vehicle/photos/`:
```text
vehicle/photos/batch1/

```


*(or `vehicle/photos/batch2/` if working in multiple export rounds)*.



---

### Step 4: Run the Car Pass Generator (`app.py`)

1. Navigate to the `vehicle/` directory and activate your virtual environment:
```bash
cd vehicle
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate

```


2. Install dependencies:
```bash
pip install reportlab pillow openpyxl pandas

```


3. Run the generator script:
```bash
python app.py

```



---

## 4. Output & Printing Guidelines

### Output Location

* The script reads pass images from `photos/` and cross-references `Vehicle Control Masterlist.xlsx` to group and sort records.


* The compiled multi-pass printable sheets are saved directly to:
```text
vehicle/vicariate_pdfs/

```


*(e.g., `Vicariate_1_Vehicle_Passes.pdf`, `Vicariate_2_Vehicle_Passes.pdf`)*.



### Print & Paper Guidelines

* **Paper Standard:** Use standard **A4 paper** (or A4 heavy cardstock/vellum board, recommended 180–230 gsm for windshield display).
* **Print Scaling:** Set **Actual Size** or **100%** (avoid "Fit to Printable Area").
* **Lamination / Display:** Vehicle passes are intended for dashboard or front windshield visibility. Ensure the `Control No.` and `Type of Vehicle` are unobstructed after cutting and laminating.