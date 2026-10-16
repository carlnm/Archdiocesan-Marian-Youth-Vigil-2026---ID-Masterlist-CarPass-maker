import pandas as pd
import re

# ============================================================
# SETTINGS
# ============================================================

INPUT_FILE = "CYM/(CYM) Marian Youth Vigil 2026 - Official Group Registration (Responses)-4.xlsx"
OUTPUT_FILE = "CYM/Marian_Youth_Vigil_2026_Cleaned_School_CYM.xlsx"


# ============================================================
# OFFICIAL VICARIATE / SCHOOL-CYM LIST
# ============================================================

archdioceseData = [

    {
        "name": "Vicariate of St. John the Evangelist",
        "parishes": [
            "CYM Universities - Dagupan Chapter"
        ]
    },

    {
        "name": "Vicariate of St. Vincent Ferrer",
        "parishes": [
            "Pangasinan State University - CYM"
        ]
    },

    {
        "name": "Vicariate of St. Ildephonse",
        "parishes": [
            "Malasiqui Catholic School"
        ]
    },

    {
        "name": "Vicariate of St. Dominic de Guzman",
        "parishes": [
            "Urbiztondo Catholic School"
        ]
    },

    {
        "name": "Vicariate of Our Lady of Purification",
        "parishes": [
            "Binmaley Catholic School"
        ]
    },

    {
        "name": "Vicariate of St. Thomas Aquinas",
        "parishes": [
            "San Jacinto Catholic School",
            "Archdiocesan School of San Fabian",
            "St. Thomas Catholic School"
        ]
    }

]


# ============================================================
# READ EXCEL FILE
# ============================================================

print("Reading Excel file...")

df = pd.read_excel(
    INPUT_FILE
)

print(
    f"Loaded {len(df)} registration responses."
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_value(value):

    if pd.isna(value):
        return ""

    return str(value).strip()


def clean_text(value):

    value = clean_value(value)

    if not value:
        return ""

    # Remove duplicate spaces
    value = re.sub(
        r"\s+",
        " ",
        value
    )

    # Normalize capitalization
    value = value.lower().title()

    replacements = {

        "St.": "St.",

        "Sts.": "Sts.",


        "Br.": "Br.",


        "Fr.": "Fr.",


        "Sr.": "Sr.",


        "Jr.": "Jr.",

        "Ii": "II",
        "Iii": "III",
        "Iv": "IV",

        "Psu": "PSU",
        "Cym": "CYM",
        "Pym": "PYM",
        "Soccom": "SocCom",

    }

    for old, new in replacements.items():

        value = re.sub(
            rf"\b{re.escape(old)}\b",
            new,
            value
        )

    return value.strip()


# ============================================================
# NORMALIZE FOR COMPARISON
# ============================================================

def normalize_for_comparison(value):

    value = clean_value(value)

    value = value.lower()

    # Normalize ampersand
    value = value.replace(
        "&",
        "and"
    )

    # Normalize hyphens
    value = value.replace(
        "-",
        " "
    )

    # Remove punctuation
    value = re.sub(
        r"[^a-z0-9\s]",
        "",
        value
    )

    # Remove duplicate spaces
    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


# ============================================================
# FIND SCHOOL / CYM AFFILIATION COLUMNS
# ============================================================

school_columns = []

for column in df.columns:

    if (
        "Select your School / CYM Affiliation"
        in str(column)
    ):

        school_columns.append(
            column
        )


print()
print(
    "School / CYM affiliation columns detected:",
    len(school_columns)
)

for column in school_columns:

    print(
        "  -",
        column
    )


# ============================================================
# IMPORTANT:
# PANDAS MAY RENAME DUPLICATE EXCEL COLUMNS
#
# Example:
# Select your School / CYM Affiliation
# Select your School / CYM Affiliation.1
# Select your School / CYM Affiliation.2
#
# The detection above handles all of them.
# ============================================================


# ============================================================
# FIND PARTICIPANT NUMBERS
# ============================================================

participant_numbers = []

for column in df.columns:

    match = re.match(
        r"Participant (\d+) Full Name",
        str(column)
    )

    if match:

        participant_numbers.append(
            int(match.group(1))
        )


participant_numbers = sorted(
    set(participant_numbers)
)


print()
print(
    "Participant slots detected:",
    participant_numbers
)


# ============================================================
# CREATE CLEANED RECORDS
# ============================================================

records = []


for _, row in df.iterrows():

    # --------------------------------------------------------
    # GENERAL INFORMATION
    # --------------------------------------------------------

    timestamp = clean_value(
        row.get("Timestamp")
    )

    email = clean_value(
        row.get("Email Address")
    )

    vicariate = clean_text(
        row.get("Select Your Vicariate")
    )


    # --------------------------------------------------------
    # DELEGATION HEAD
    # --------------------------------------------------------

    delegation_head_name = clean_text(
        row.get(
            "Delegation Head Full Name"
        )
    )

    delegation_head_nickname = clean_text(
        row.get(
            "Delegation Head Nickname"
        )
    )

    delegation_head_age = clean_value(
        row.get(
            "Delegation Head Age"
        )
    )

    delegation_head_size = clean_value(
        row.get(
            "Delegation Head T-Shirt Size"
        )
    )

    contact_number = clean_value(
        row.get(
            "Delegation Head Contact Number"
        )
    )


    # ========================================================
    # GET ALL SCHOOL / CYM AFFILIATIONS
    # ========================================================

    schools = []


    for school_column in school_columns:

        school = clean_text(
            row.get(school_column)
        )

        if (
            school
            and school not in schools
        ):

            schools.append(
                school
            )


    # If none was provided
    if not schools:

        schools = [""]


    school_text = "; ".join(
        schools
    )


    # ========================================================
    # ADD DELEGATION HEAD
    # ========================================================

    if delegation_head_name:

        records.append({

            "Type":
                "Delegation Head",

            "Timestamp":
                timestamp,

            "Email":
                email,

            "Vicariate":
                vicariate,

            "School / CYM Affiliation":
                school_text,

            "Full Name":
                delegation_head_name,

            "Nickname":
                delegation_head_nickname,

            "Age":
                delegation_head_age,

            "T-Shirt Size":
                delegation_head_size,

            "Contact Number":
                contact_number,

        })


    # ========================================================
    # ADD PARTICIPANTS
    # ========================================================

    for participant_number in participant_numbers:

        name_column = (
            f"Participant {participant_number} Full Name"
        )

        nickname_column = (
            f"Participant {participant_number} Nickname"
        )

        age_column = (
            f"Participant {participant_number} Age"
        )

        size_column = (
            f"Participant {participant_number} T-Shirt Size"
        )


        # ----------------------------------------------------
        # NAME
        # ----------------------------------------------------

        name = clean_text(
            row.get(name_column)
        )


        # Skip empty slots
        if not name:

            continue


        # ----------------------------------------------------
        # OTHER DETAILS
        # ----------------------------------------------------

        nickname = clean_text(
            row.get(nickname_column)
        )

        age = clean_value(
            row.get(age_column)
        )

        shirt_size = clean_value(
            row.get(size_column)
        )


        # ----------------------------------------------------
        # ADD RECORD
        # ----------------------------------------------------

        records.append({

            "Type":
                "Participant",

            "Timestamp":
                timestamp,

            "Email":
                "",

            "Vicariate":
                vicariate,

            "School / CYM Affiliation":
                school_text,

            "Full Name":
                name,

            "Nickname":
                nickname,

            "Age":
                age,

            "T-Shirt Size":
                shirt_size,

            "Contact Number":
                "",

        })


# ============================================================
# CREATE PARTICIPANT DATAFRAME
# ============================================================

cleaned_df = pd.DataFrame(
    records
)


cleaned_df.insert(
    0,
    "Person No.",
    range(
        1,
        len(cleaned_df) + 1
    )
)


# ============================================================
# BUILD SUBMITTED SCHOOL / CYM LOOKUP
# ============================================================

submitted_vicariates = set()

submitted_schools = set()


for _, row in cleaned_df.iterrows():

    # --------------------------------------------------------
    # Vicariate
    # --------------------------------------------------------

    vicariate_key = (
        normalize_for_comparison(
            row["Vicariate"]
        )
    )

    if vicariate_key:

        submitted_vicariates.add(
            vicariate_key
        )


    # --------------------------------------------------------
    # School / CYM
    # --------------------------------------------------------

    school_data = clean_value(
        row[
            "School / CYM Affiliation"
        ]
    )


    if school_data:

        for school in school_data.split(";"):

            school_key = (
                normalize_for_comparison(
                    school
                )
            )

            if school_key:

                submitted_schools.add(
                    school_key
                )


# ============================================================
# CREATE SUBMISSION STATUS
# ============================================================

status_records = []


for vicariate_data in archdioceseData:

    official_vicariate = (
        vicariate_data["name"]
    )

    vicariate_key = (
        normalize_for_comparison(
            official_vicariate
        )
    )


    vicariate_has_submission = (
        vicariate_key
        in submitted_vicariates
    )


    for school in vicariate_data["parishes"]:

        school_key = (
            normalize_for_comparison(
                school
            )
        )


        school_has_submission = (
            school_key
            in submitted_schools
        )


        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        if school_has_submission:

            school_status = "SUBMITTED"

        else:

            school_status = "NO PARTICIPANTS"


        if vicariate_has_submission:

            vicariate_status = "SUBMITTED"

        else:

            vicariate_status = "NO SUBMISSION"


        status_records.append({

            "Vicariate":
                official_vicariate,

            "School / CYM":
                school,

            "Vicariate Status":
                vicariate_status,

            "School / CYM Status":
                school_status,

        })


# ============================================================
# STATUS DATAFRAME
# ============================================================

status_df = pd.DataFrame(
    status_records
)


# ============================================================
# ADD PARTICIPANT COUNT
# ============================================================

status_df[
    "Participant Count"
] = 0


for index, status_row in status_df.iterrows():

    school = status_row[
        "School / CYM"
    ]

    school_key = (
        normalize_for_comparison(
            school
        )
    )


    count = 0


    for _, participant in cleaned_df.iterrows():

        if (
            participant["Type"]
            != "Participant"
        ):

            continue


        school_data = clean_value(
            participant[
                "School / CYM Affiliation"
            ]
        )


        participant_schools = [
            normalize_for_comparison(s)
            for s in school_data.split(";")
            if s.strip()
        ]


        if school_key in participant_schools:

            count += 1


    status_df.at[
        index,
        "Participant Count"
    ] = count


# ============================================================
# VICARIATE SUMMARY
# ============================================================

vicariate_summary = []


for vicariate_data in archdioceseData:

    vicariate = (
        vicariate_data["name"]
    )


    vicariate_rows = status_df[
        status_df["Vicariate"]
        == vicariate
    ]


    total_schools = len(
        vicariate_rows
    )


    submitted_schools_count = len(
        vicariate_rows[
            vicariate_rows[
                "School / CYM Status"
            ]
            == "SUBMITTED"
        ]
    )


    missing_schools_count = (
        total_schools
        - submitted_schools_count
    )


    total_participants = (
        vicariate_rows[
            "Participant Count"
        ].sum()
    )


    if missing_schools_count == 0:

        status = "COMPLETE"

    elif submitted_schools_count == 0:

        status = "NO SUBMISSIONS"

    else:

        status = "INCOMPLETE"


    vicariate_summary.append({

        "Vicariate":
            vicariate,

        "Total Schools / CYMs":
            total_schools,

        "Submitted":
            submitted_schools_count,

        "Missing":
            missing_schools_count,

        "Total Participants":
            total_participants,

        "Status":
            status,

    })


vicariate_summary_df = pd.DataFrame(
    vicariate_summary
)


# ============================================================
# MISSING SCHOOLS ONLY
# ============================================================

missing_schools_df = status_df[
    status_df[
        "School / CYM Status"
    ]
    == "NO PARTICIPANTS"
].copy()


# ============================================================
# SAVE EXCEL
# ============================================================

print()
print("Saving Excel file...")


with pd.ExcelWriter(
    OUTPUT_FILE,
    engine="openpyxl"
) as writer:

    cleaned_df.to_excel(
        writer,
        index=False,
        sheet_name="Participants"
    )


    status_df.to_excel(
        writer,
        index=False,
        sheet_name="Submission Status"
    )


    vicariate_summary_df.to_excel(
        writer,
        index=False,
        sheet_name="Vicariate Summary"
    )


    missing_schools_df.to_excel(
        writer,
        index=False,
        sheet_name="Missing Schools"
    )


# ============================================================
# CONSOLE SUMMARY
# ============================================================

total_vicariates = len(
    archdioceseData
)

total_schools = sum(
    len(v["parishes"])
    for v in archdioceseData
)

submitted_school_count = len(
    status_df[
        status_df[
            "School / CYM Status"
        ]
        == "SUBMITTED"
    ]
)

missing_school_count = (
    total_schools
    - submitted_school_count
)

total_participant_count = (
    cleaned_df[
        cleaned_df["Type"]
        == "Participant"
    ].shape[0]
)


print()
print(
    "=================================================="
)

print(
    "CLEANING + SCHOOL/CYM SUBMISSION CHECK COMPLETE"
)

print(
    "=================================================="
)

print()

print(
    f"Total registration responses: "
    f"{len(df)}"
)

print(
    f"Total people extracted: "
    f"{len(cleaned_df)}"
)

print(
    f"Delegation Heads: "
    f"{(
        cleaned_df['Type']
        == 'Delegation Head'
    ).sum()}"
)

print(
    f"Participants: "
    f"{total_participant_count}"
)

print()

print(
    f"Total Vicariates: "
    f"{total_vicariates}"
)

print(
    f"Total Schools / CYMs: "
    f"{total_schools}"
)

print(
    f"Schools / CYMs with participants: "
    f"{submitted_school_count}"
)

print(
    f"Schools / CYMs without participants: "
    f"{missing_school_count}"
)

print()

print(
    f"Output file: "
    f"{OUTPUT_FILE}"
)


# ============================================================
# PRINT MISSING SCHOOLS
# ============================================================

print()
print(
    "=================================================="
)

print(
    "SCHOOLS / CYMs WITHOUT PARTICIPANTS"
)

print(
    "=================================================="
)


for vicariate_data in archdioceseData:

    vicariate = (
        vicariate_data["name"]
    )


    missing = status_df[
        (
            status_df["Vicariate"]
            == vicariate
        )
        &
        (
            status_df[
                "School / CYM Status"
            ]
            == "NO PARTICIPANTS"
        )
    ]


    if not missing.empty:

        print()
        print(
            vicariate
        )


        for school in missing[
            "School / CYM"
        ]:

            print(
                f"  - {school}"
            )


print()
print(
    "=================================================="
)

print(
    "DONE"
)

print(
    "=================================================="
)