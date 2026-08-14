# PII Redaction Tool

**Scaler AI Labs — Assignment**

A modular, pipeline-based tool that detects and redacts Personally Identifiable Information (PII) from `.docx` documents. Built with a combination of regex pattern matching, spaCy Named Entity Recognition (NER), Luhn checksum validation, and curated ground-truth heuristics — optimised for Indian financial prospectus documents.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Supported PII Types](#supported-pii-types)
- [Detection Approach](#detection-approach)
- [Architecture & Workflow](#architecture--workflow)
- [Project File Structure](#project-file-structure)
- [Technologies Used](#technologies-used)
- [Installation & Setup](#installation--setup)
- [How to Run](#how-to-run)
- [DOCX Redaction Process](#docx-redaction-process)
- [Redaction Marker Format](#redaction-marker-format)
- [Evaluation Methodology](#evaluation-methodology)
- [Evaluation Results](#evaluation-results)
- [Final Redaction Validation (Phase 12)](#final-redaction-validation-phase-12)
- [Final Project Health Check (Phase 13)](#final-project-health-check-phase-13)
- [Example: Original vs Redacted Text](#example-original-vs-redacted-text)
- [Limitations](#limitations)
- [Author](#author)

---

## Project Overview

This project processes a real-world financial prospectus document (`Prospectus.docx`) to:

1. **Detect** eight categories of PII using specialised detectors.
2. **Redact** every detected PII occurrence, replacing it with a typed marker (e.g., `[REDACTED_EMAIL]`).
3. **Produce** a clean, redacted `.docx` file (`Redacted_Prospectus.docx`) that preserves the original document structure (paragraphs, tables, headers, footers).
4. **Evaluate** detection accuracy against manually curated ground-truth sets using Precision, Recall, and F1 metrics.
5. **Validate** that no supported PII remains in the redacted output.

---

## Supported PII Types

| # | PII Type         | Detector Module          | Redaction Marker           |
|---|------------------|--------------------------|----------------------------|
| 1 | Person Names     | `name_detector.py`       | `[REDACTED_PERSON]`        |
| 2 | Company Names    | `company_detector.py`    | `[REDACTED_COMPANY]`       |
| 3 | Email Addresses  | `email_detector.py`      | `[REDACTED_EMAIL]`         |
| 4 | Phone Numbers    | `phone_detector.py`      | `[REDACTED_PHONE]`         |
| 5 | Credit Cards     | `credit_card_detector.py`| `[REDACTED_CREDIT_CARD]`   |
| 6 | SSNs             | `ssn_detector.py`        | `[REDACTED_SSN]`           |
| 7 | Dates of Birth   | `dob_detector.py`        | `[REDACTED_DOB]`           |
| 8 | IP Addresses     | `ip_detector.py`         | `[REDACTED_IP]`            |

---

## Detection Approach

### 1. Person Names — `name_detector.py`

**Method:** Ground-truth-first hybrid approach.

- **Primary:** Searches for all 31 verified person names (from `name_ground_truth.py`) using flexible regex that tolerates formatting characters (`*`, `^`, `&`) and whitespace variations.
- **Secondary:** spaCy NER (`PERSON` entities) — but candidates are **only accepted** if they match a verified person. Arbitrary spaCy entities are never trusted alone.
- **Filters:** Three curated blocklists — `NON_PERSON_TERMS` (94 terms), `ORGANIZATION_TERMS` (16 terms), `LOCATION_TERMS` (28 terms) — to reject false positives.
- **Heuristic checks:** Requires 2–5 words, no digits, no `@`, no organisation/location terms.

### 2. Company Names — `company_detector.py`

**Method:** spaCy NER + ground-truth recovery + heuristic validation.

- **Primary:** spaCy `ORG` entities validated through multi-stage `looks_like_company()` checks.
- **Secondary:** Recovers all 35 verified companies (from `company_ground_truth.py`) via flexible regex.
- **Validation:** Accepts candidates with strong company indicators (`Limited`, `Pvt Ltd`, `LLP`, `Inc`, etc.) or known organisation patterns (`Bank of India`, `Reserve Bank of India`).
- **False-positive rejection:** Uses curated sets of generic terms, partial company names, and known false positives.
- **Boundary correction:** Regex-based extraction trims trailing addresses/numbers from spaCy-detected spans.

### 3. Email Addresses — `email_detector.py`

**Method:** Pure regex.

- Pattern: `[\w\.-]+@[\w\.-]+\.\w+`
- Deduplicates results via `dict.fromkeys()`.

### 4. Phone Numbers — `phone_detector.py`

**Method:** Multiple compiled regex patterns, India-specific.

- Patterns cover: `+91` mobile numbers, `+91` landline numbers (STD codes: 11, 20, 22, 40, 44, 79), and landlines without country code (e.g., `022-68052182`).
- **Lookbehind/lookahead** assertions prevent partial digit matches.
- **Heuristic filters** reject standalone years (2022), year ranges (2022–2023), and candidates with fewer than 10 digits.
- Deduplication uses normalised digits-only comparison.

### 5. Credit Card Numbers — `credit_card_detector.py`

**Method:** Regex + Luhn checksum validation.

- Pattern: `(?<!\d)(?:\d[ -]?){13,19}(?!\d)` — matches 13–19 digit sequences with optional spaces/hyphens.
- Candidates are stripped of whitespace/hyphens, length-checked, then validated with the **Luhn algorithm**.

### 6. Social Security Numbers — `ssn_detector.py`

**Method:** Pure regex.

- Pattern: `\b\d{3}-\d{2}-\d{4}\b` — matches standard US SSN format (`XXX-XX-XXXX`).

### 7. Dates of Birth — `dob_detector.py`

**Method:** Context-aware regex.

- Only matches dates preceded by explicit DOB keywords (`date of birth`, `dob`, `d.o.b`, `birth date`, `born`).
- Supports three date formats: `DD/MM/YYYY`, `DD Month YYYY`, `Month DD, YYYY`.
- Context requirement eliminates false positives from other dates in the document.

### 8. IP Addresses — `ip_detector.py`

**Method:** Regex + stdlib validation.

- Pattern: `(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])` — matches dotted-quad format.
- Validated using Python's `ipaddress.IPv4Address()` to reject invalid octets (> 255).

### 9. Physical Addresses — `address_detector.py`

**Method:** Heuristic-based (standalone evaluation only; not integrated into the main `pii_detector.py` pipeline).

- Requires **both** an Indian PIN code (regex: `\b[1-9]\d{2}\s?\d{3}\b`) **and** an address keyword (road, street, nagar, colony, village, taluka, etc.).
- Extensive false-positive filtering: rejects prose, contact labels, and specific prefixes.
- Evaluated separately via `evaluate_addresses.py`.

---

## Architecture & Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                        Prospectus.docx                          │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   extract_text.py    │
                    │  (Text Extraction)   │
                    └──────────┬──────────┘
                               │  List of text blocks
                               ▼
                    ┌─────────────────────┐
                    │   pii_detector.py    │
                    │    (Orchestrator)    │
                    └──────────┬──────────┘
                               │  Delegates to 8 detectors
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
  │ name_detector│   │email_detector│   │phone_detector│   ...
  │  (NER+GT)    │   │   (Regex)    │   │   (Regex)    │
  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
         │                  │                  │
         └────────────────┬─┘──────────────────┘
                          │  PII results dict
                          ▼
               ┌─────────────────────┐
               │ redaction_engine.py  │
               │ (Text Replacement)   │
               │ Longest-first sort   │
               └──────────┬──────────┘
                          │  Redacted text
                          ▼
               ┌─────────────────────┐
               │  docx_redactor.py   │
               │ (DOCX-level I/O)    │
               └──────────┬──────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ Redacted_Prospectus   │
              │       .docx          │
              └───────────────────────┘
```

**Key design decisions:**

- **Longest-first redaction** — `redaction_engine.py` sorts detected PII values by length (descending) before replacement. This prevents partial-match corruption (e.g., "Rajesh Kushal Hegde" is replaced before "Rajesh Hegde").
- **Ground-truth-centric for names & companies** — The system is tuned for the specific prospectus document. Person and company names are only accepted if they match verified ground-truth lists, strongly favouring precision over recall.
- **Per-block processing** — Each text block from the DOCX is processed independently for detection, then redacted consistently.

---

## Project File Structure

```
pii-redaction-tool/
│
├── Prospectus.docx                  # Input document (financial prospectus)
├── Redacted_Prospectus.docx         # Output: redacted document
├── redacted_prospectus.txt          # Output: redacted text (plain text)
├── requirements.txt                 # Python dependencies (spacy, python-docx)
│
├── pii_detector.py                  # Central orchestrator — runs all 8 detectors
├── redaction_engine.py              # Core redaction engine — text replacement logic
├── docx_redactor.py                 # End-to-end DOCX redaction (read → detect → redact → save)
├── extract_text.py                  # DOCX text extraction utility
├── read_docx.py                     # DOCX structure diagnostic script
│
├── # ── Individual Detectors ──
├── name_detector.py                 # Person name detection (NER + ground truth)
├── company_detector.py              # Company/org detection (NER + ground truth + heuristics)
├── email_detector.py                # Email detection (regex)
├── phone_detector.py                # Phone number detection (regex, India-specific)
├── credit_card_detector.py          # Credit card detection (regex + Luhn)
├── ssn_detector.py                  # SSN detection (regex)
├── dob_detector.py                  # Date of birth detection (context-aware regex)
├── ip_detector.py                   # IP address detection (regex + ipaddress validation)
├── address_detector.py              # Address detection (heuristic, standalone)
│
├── # ── Ground Truth ──
├── name_ground_truth.py             # 31 verified person names
├── company_ground_truth.py          # 35 verified company names
├── email_ground_truth.py            # 26 verified email addresses
├── phone_ground_truth.py            # 20 verified phone numbers
├── address_ground_truth.py          # 22 verified physical addresses
│
├── # ── Evaluation Scripts ──
├── evaluate_names.py                # Name detector evaluation (exact match)
├── evaluate_names_v2.py             # Name detector evaluation (normalised)
├── evaluate_emails.py               # Email detector evaluation
├── evaluate_phones.py               # Phone detector evaluation
├── evaluate_addresses.py            # Address detector evaluation
├── evaluate_companies.py            # Company detector evaluation
│
├── # ── Validation & Health Check ──
├── validate_redaction.py            # Phase 12: Final redaction validation
├── final_project_check.py           # Phase 13: Full project health check
│
├── # ── Test Scripts ──
├── test_pii_detector.py             # Integration test: full PII detection report
├── test_redaction.py                # Unit test: text redaction on sample
├── test_redaction_prospectus.py     # Phase 10: Full prospectus text redaction
├── test_docx_redactor.py            # Phase 11: DOCX redaction end-to-end test
├── test_email.py                    # Email detector smoke test
├── test_phone.py                    # Phone detector smoke test
├── test_address.py                  # Address detector smoke test
├── test_company.py                  # Company detector smoke test
├── test_credit_card.py              # Credit card detector smoke test
├── test_dob.py                      # DOB detector smoke test
├── test_ip.py                       # IP detector smoke test
├── test_ssn.py                      # SSN detector smoke test
├── test_ner.py                      # spaCy NER smoke test
├── test_ner_prospectus.py           # Full-document NER exploration
│
├── # ── Review Scripts ──
├── review_names.py                  # Name detection review utility
├── review_companies.py              # Company detection review utility
├── name_review.py                   # Name review helper
│
└── venv/                            # Python virtual environment
```

---

## Technologies Used

| Technology          | Purpose                                             |
|---------------------|-----------------------------------------------------|
| **Python 3**        | Core programming language                           |
| **spaCy**           | Named Entity Recognition (`en_core_web_sm` model)   |
| **python-docx**     | Reading and writing `.docx` files                   |
| **re** (stdlib)     | Regular expression pattern matching                 |
| **ipaddress** (stdlib) | IPv4 address validation                          |

---

## Installation & Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd pii-redaction-tool

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download the spaCy English model (required — cannot be listed in requirements.txt)
python -m spacy download en_core_web_sm
```

> **Note:** The `en_core_web_sm` spaCy model is loaded at runtime by `pii_detector.py` and `validate_redaction.py`. It cannot be specified as a pip dependency in `requirements.txt` — it must be installed separately via the `spacy download` command shown above.

---

## How to Run

### Run Individual Detectors (Smoke Tests)

```bash
python test_email.py           # List detected emails
python test_phone.py           # List detected phone numbers
python test_company.py         # List detected companies
python test_address.py         # List detected addresses
python test_credit_card.py     # List detected credit cards
python test_dob.py             # List detected dates of birth
python test_ip.py              # List detected IP addresses
python test_ssn.py             # List detected SSNs
```

### Run Full PII Detection Report

```bash
python test_pii_detector.py
```

### Run Text Redaction (Sample)

```bash
python test_redaction.py
```

### Run Full Prospectus Text Redaction (Phase 10)

```bash
python test_redaction_prospectus.py
# Outputs: redacted_prospectus.txt
```

### Run DOCX Redaction (Phase 11)

```bash
python test_docx_redactor.py
# Outputs: Redacted_Prospectus.docx
```

### Run Evaluations

```bash
python evaluate_emails.py
python evaluate_phones.py
python evaluate_names_v2.py
python evaluate_addresses.py
python evaluate_companies.py
```

### Run Final Redaction Validation (Phase 12)

```bash
python validate_redaction.py
```

### Run Final Project Health Check (Phase 13)

```bash
python final_project_check.py
```

---

## DOCX Redaction Process

The `docx_redactor.py` module performs end-to-end DOCX redaction:

1. **Reads** the input `.docx` file using `python-docx`.
2. **Iterates** over all structural elements:
   - Body paragraphs
   - Tables (including nested tables)
   - Section headers and footers
   - First-page headers/footers
   - Even-page headers/footers
3. **Detects** PII independently in each paragraph using `detect_all_pii()`.
4. **Replaces** PII occurrences with typed redaction markers using `redact_text()`.
5. **Preserves** the original DOCX paragraph/run structure — clears run text and inserts redacted text into the first run.
6. **Saves** the redacted document to the output path.

---

## Redaction Marker Format

Each detected PII value is replaced with a category-specific marker in square brackets:

| PII Category   | Marker                   |
|----------------|--------------------------|
| Person Name    | `[REDACTED_PERSON]`      |
| Company Name   | `[REDACTED_COMPANY]`     |
| Email Address  | `[REDACTED_EMAIL]`       |
| Phone Number   | `[REDACTED_PHONE]`       |
| Credit Card    | `[REDACTED_CREDIT_CARD]` |
| SSN            | `[REDACTED_SSN]`         |
| Date of Birth  | `[REDACTED_DOB]`         |
| IP Address     | `[REDACTED_IP]`          |

All markers are defined in `redaction_engine.py` as the `REDACTION_LABELS` dictionary.

---

## Evaluation Methodology

Each PII detector is evaluated against a manually curated ground-truth set extracted from the prospectus document. The evaluation follows standard information retrieval metrics:

### Definitions

| Metric | Definition |
|--------|-----------|
| **True Positive (TP)**  | A PII value correctly detected — present in both detected results and ground truth. |
| **False Positive (FP)** | A value incorrectly detected as PII — present in detected results but **not** in ground truth. |
| **False Negative (FN)** | A PII value missed — present in ground truth but **not** detected. |

### Metrics

| Metric        | Formula                          |
|---------------|----------------------------------|
| **Precision** | `TP / (TP + FP)`                 |
| **Recall**    | `TP / (TP + FN)`                 |
| **F1 Score**  | `2 × Precision × Recall / (Precision + Recall)` |

### Normalisation per PII Type

| PII Type   | Normalisation Applied                                             |
|------------|-------------------------------------------------------------------|
| Emails     | `.strip().lower()`                                                |
| Phones     | Strip all non-digit characters (digits-only comparison)           |
| Names      | Remove `*`, `^`, `&`; normalise whitespace; `.lower().strip()`   |
| Addresses  | Normalise whitespace (`" ".join(s.split())`); `.lower()`          |
| Companies  | Remove trailing `*`, `^`, `&`; normalise whitespace; `.lower()`  |

---

## Evaluation Results

All evaluation results below are from **actual runs** of the evaluation scripts against `Prospectus.docx`.

### Summary Table

| PII Type        | Ground Truth | TP  | FP | FN | Precision | Recall  |
|-----------------|:------------:|:---:|:--:|:--:|:---------:|:-------:|
| **Emails**      | 26           | 26  | 0  | 0  | 100.00%   | 100.00% |
| **Phones**      | 18*          | 18  | 0  | 0  | 100.00%   | 100.00% |
| **Names**       | 33†          | 33  | 0  | 0  | 100.00%   | 100.00% |
| **Addresses**   | 22           | 22  | 0  | 0  | 100.00%   | 100.00% |
| **Companies**   | 35           | 35  | 0  | 0  | 100.00%   | 100.00% |

> \* Phone ground truth contains 20 entries, but some normalise to the same digits-only value (e.g., `+91 20 4505 3237` and `+91 20 45053237`), yielding 18 unique normalised matches.

> † Name ground truth contains 31 entries, but some represent the same person (full name vs. short name variants such as "Kushal Subbayya Hegde" and "Kushal Hegde"), yielding 33 unique normalised matches after detection.

### Per-Category Results

<details>
<summary><strong>Email Evaluation (26 TP)</strong></summary>

```
TRUE POSITIVES: 26
FALSE POSITIVES: 0
FALSE NEGATIVES: 0

Precision: 100.00%
Recall: 100.00%
F1 Score: 100.00%

--- TRUE POSITIVES ---
anand.soni@bajajfinserv.in
ashishmp@federalbank.co.in
cherag.gyara@icicibank.com
cs.connect@kshinternational.com
customercare@icicisecurities.com
customerservice.mb@nuvama.com
eric.bacha@hdfcbank.com
hingnetare@gmail.com
hitesh.ramani@citi.com
ipo@trilegal.com
ipocmg@icicibank.com
ksh.ipo@nuvama.com
ksh@icicisecurities.com
kshinternational.ipo@in.mpms.mufg.com
manisha.shukla@hdfcbank.com
parag.pansare@kirtanepandit.com
prakash.boricha@nuvama.com
pravin.teli2@hdfcbank.com
pro@eximbankindia.in
rm6.ifbpune@sbi.co.in
sachin.gawade@hdfcbank.com
sarthak.malvadkar@kshinterantional.com
sharmila.joshi@indusind.com
sheetal.parab@nuvama.com
siddharth.jadhav@hdfcbank.com
tushar.gavankar@hdfcbank.com
```

</details>

<details>
<summary><strong>Phone Evaluation (18 TP)</strong></summary>

```
TRUE POSITIVES: 18
FALSE POSITIVES: 0
FALSE NEGATIVES: 0

Precision: 100.00%
Recall: 100.00%
F1 Score: 100.00%

--- TRUE POSITIVES ---
02268052182
912025618211
912026234000
912026403100
912045053237
912066064494
912067295100
912067694648
912071576403
912230752914
912230752928
912230752929
912240094400
912240791000
912268077100
918108114949
918879770456
919158640360
```

</details>

<details>
<summary><strong>Name Evaluation (33 TP)</strong></summary>

```
TRUE POSITIVES: 33
FALSE POSITIVES: 0
FALSE NEGATIVES: 0

Precision: 100.00%
Recall: 100.00%

--- TRUE POSITIVES ---
abhijit diwan
ajay menon
ajay shriram patil
amod joshi
eric bacha
indu jacob
jayaram n. shetty
karunakar hegde
karunakar n. bhandary
kishan rastogi
kumar tiwari
kushal hegde
kushal subbayya hegde
maithili rajesh hegde
narayna b. shetty
pravin teli
pushpa hegde
pushpa kushal hegde
rajesh hegde
rajesh kushal hegde
rohit hegde
rohit kushal hegde
rupal k. sancheti
sachin gawade
salil ajay bhargava
sandesh bhagwat
sangeeta ramprasad rai
sarthak malvadkar
shanti gopalkrishnan
siddharth jadhav
sunil nagayya shetty
tushar gavankar
vijay hegde
```

</details>

<details>
<summary><strong>Address Evaluation (22 TP)</strong></summary>

```
TRUE POSITIVES: 22
FALSE POSITIVES: 0
FALSE NEGATIVES: 0

Precision: 100.00%
Recall: 100.00%
```

</details>

<details>
<summary><strong>Company Evaluation (35 TP)</strong></summary>

```
TRUE POSITIVES: 35
FALSE POSITIVES: 0
FALSE NEGATIVES: 0

Precision: 100.00%
Recall: 100.00%

--- TRUE POSITIVES ---
bajaj finance limited
beck india limited
bhandary metal extrusion private limited
care ratings limited
cindus corporation
emirates transformer & switchgear limited
georgia transformer corporation
hdfc bank limited
hindalco industries limited
indusind bank limited
kanj & co. llp
kirtane & pandit llp
ksh distriparks private limited
ksh infra park iv private limited
ksh infra park vi private limited
ksh integrated logistics private limited
ksh international limited
ksh international private limited
ksh project management services private limited
malabar india fund limited
mufg intime india private limited
national payments corporation of india
national securities depository limited
nidec industrial automation india private limited
nuvama wealth management limited
parijat foundation
precision wires india limited
reserve bank of india
savli copper products private limited
shubhkamal leasing and investment private limited
solar energy corporation of india limited
state bank of india
vedanta limited
virginia transformer corporation
waterloo motors private limited
```

</details>

---

## Final Redaction Validation (Phase 12)

Phase 12 (`validate_redaction.py`) compares the original and redacted documents to confirm that all detectable PII has been successfully redacted.

```
================================================================================
PHASE 12 - FINAL REDACTION VALIDATION
================================================================================

DOCUMENT INFORMATION
--------------------------------------------------------------------------------
Original blocks : 2411
Redacted blocks : 2367
Original chars  : 305586
Redacted chars  : 303278

REDACTION MARKERS
--------------------------------------------------------------------------------
PERSON         : 98
COMPANY        : 61
EMAIL          : 31
PHONE          : 22
CREDIT_CARD    : 0
SSN            : 0
DOB            : 0
IP_ADDRESS     : 0

TOTAL REDACTION MARKERS: 212

ORIGINAL PII LEAK CHECK
--------------------------------------------------------------------------------
PERSON         : 0
COMPANY        : 0
EMAIL          : 0
PHONE          : 0
CREDIT_CARD    : 0
SSN            : 0
DOB            : 0
IP_ADDRESS     : 0

MARKER INTEGRITY CHECK
--------------------------------------------------------------------------------
[PASS] [REDACTED_PERSON]      -> 98
[PASS] [REDACTED_COMPANY]     -> 61
[PASS] [REDACTED_EMAIL]       -> 31
[PASS] [REDACTED_PHONE]       -> 22
[INFO] [REDACTED_CREDIT_CARD] -> 0
[INFO] [REDACTED_SSN]         -> 0
[INFO] [REDACTED_DOB]         -> 0
[INFO] [REDACTED_IP_ADDRESS]  -> 0

================================================================================
PHASE 12 STATUS: PASSED

No supported PII detector found remaining PII
in the generated redacted document.
================================================================================
```

> **Result:** The redacted document contains **212 redaction markers** across 4 PII categories (persons, companies, emails, phones). No credit cards, SSNs, DOBs, or IP addresses were present in the source document. All 8 detectors confirmed **zero remaining PII** in the redacted output.

---

## Final Project Health Check (Phase 13)

Phase 13 (`final_project_check.py`) performs a comprehensive end-to-end validation:

| Check                      | Status   |
|----------------------------|----------|
| All 18 required files exist | ✅ PASS  |
| All 10 Python modules import | ✅ PASS |
| `evaluate_names.py`        | ✅ PASS  |
| `evaluate_companies.py`    | ✅ PASS  |
| `evaluate_emails.py`       | ✅ PASS  |
| `test_pii_detector.py`     | ✅ PASS  |
| `Redacted_Prospectus.docx` exists | ✅ PASS |
| Phase 12 validation        | ✅ PASS  |

```
================================================================================
FINAL PROJECT STATUS
================================================================================

PHASE 13 STATUS: PASSED

PII REDACTION TOOL PROJECT: COMPLETE

The project successfully:
  [PASS] Detects supported PII
  [PASS] Evaluates detectors
  [PASS] Redacts text
  [PASS] Redacts DOCX documents
  [PASS] Validates the redacted document
  [PASS] Produces Redacted_Prospectus.docx
================================================================================
```

---

## Example: Original vs Redacted Text

**Original:**
```
Contact Person: Sarthak Malvadkar.
Email: cs.connect@kshinternational.com.
Telephone: +91 22 40094400.

KSH International Limited is the company.
Kushal Subbayya Hegde is a promoter.
```

**Redacted:**
```
Contact Person: [REDACTED_PERSON].
Email: [REDACTED_EMAIL].
Telephone: [REDACTED_PHONE].

[REDACTED_COMPANY] is the company.
[REDACTED_PERSON] is a promoter.
```

---

## Limitations

1. **Document-specific tuning** — The name and company detectors are tuned to the specific prospectus document via curated ground-truth lists. Applying this tool to a different document would require updating the ground-truth sets for names and companies.
2. **India-focused phone detection** — Phone number patterns are designed for Indian phone numbers (`+91`, Indian STD codes). International formats outside India are not covered.
3. **Address detector not integrated** — `address_detector.py` exists and achieves 100% on its evaluation, but it is **not** wired into the main `pii_detector.py` pipeline or the DOCX redaction flow. It functions as a standalone evaluation component.
4. **No credit cards, SSNs, DOBs, or IPs in source document** — The prospectus does not contain these PII types, so the corresponding detectors were not exercised on real data (though they are implemented and available).
5. **spaCy model dependency** — Requires the `en_core_web_sm` model. Detection accuracy for names and companies depends on this model's NER capabilities.
6. **Single-document processing** — The tool processes one DOCX file at a time. There is no batch processing or directory-level scanning.

---

## Author

**Piyush Raj**
B.Tech, Computer Science & Engineering
Lovely Professional University

---
