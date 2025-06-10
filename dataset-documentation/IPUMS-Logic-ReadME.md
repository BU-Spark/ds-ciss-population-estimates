# Household Relationship Derivation from IPUMS-USA PUMS Data

This script processes individual-level household data from the IPUMS-USA dataset (`usa_00214.csv`) to derive relationship-based variables within each household, such as the age of a person’s mother, father, and head of household.

---

## File: `usa_00214.csv`

This file is expected to be a Public Use Microdata Sample (PUMS) dataset from IPUMS, containing variables such as:

- `SERIAL`: Unique household identifier
- `PERNUM`: Person number within the household
- `AGE`: Person's age
- `RELATE`: Relationship to household head (coded; 1 = head)
- `MOMLOC`, `POPLOC`, `SPLOC`: Pointers to mother, father, and spouse (PERNUM within the household)

---

## What the Script Does

The script adds the following **derived columns**:

| Column Name             | Description |
|-------------------------|-------------|
| `AGE_MOM_RECREATED`     | Age of the person's mother, based on `MOMLOC` pointer |
| `AGE_POP_RECREATED`     | Age of the person's father, based on `POPLOC` pointer |
| `AGE_HEAD_RECREATED`    | Age of the household head, for each person |
| `MOMLOC_HEAD_RECREATED` | Person number of the household head’s mother |
| `POPLOC_HEAD_RECREATED` | Person number of the household head’s father |
| `SPLOC_HEAD_RECREATED`  | Person number of the household head’s spouse |

---

## How It Works

Each derived variable is computed using `apply()` with a custom function that:

1. Identifies the **relevant person** in the household using `SERIAL` and a pointer variable (like `MOMLOC` or `SPLOC`)
2. Retrieves that person's age or person number (`PERNUM`) from the data
3. Returns `None` if the pointer is missing or invalid

---

## Usage

1. Ensure `usa_00214.csv` is downloaded and saved locally.
2. Update the `file_path` variable to match your file location.
3. Run the script in any Python 3 environment with `pandas` installed.

---

## Requirements

- Python 3.x
- `pandas` library

```bash
pip install pandas
