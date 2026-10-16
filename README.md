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

## Recommended `.gitignore`

```gitignore
# macOS metadata
.DS_Store
__MACOSX/
._*

# Python environment & cache
__pycache__/
*.py[cod]
venv/
.env

# Raw attendee data (exclude if subject to data privacy restrictions)
# Input/*.xlsx

```