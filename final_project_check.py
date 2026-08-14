import os
import subprocess
import sys


# ============================================================
# PHASE 13
# FINAL PROJECT HEALTH CHECK
# ============================================================

print("=" * 80)
print("PHASE 13 - FINAL PROJECT HEALTH CHECK")
print("=" * 80)


# ============================================================
# REQUIRED FILES
# ============================================================

required_files = [
    "Prospectus.docx",

    # Detectors
    "name_detector.py",
    "company_detector.py",
    "email_detector.py",
    "phone_detector.py",
    "credit_card_detector.py",
    "ssn_detector.py",
    "dob_detector.py",
    "ip_detector.py",

    # Ground truth
    "name_ground_truth.py",
    "company_ground_truth.py",

    # Core pipeline
    "pii_detector.py",
    "redaction_engine.py",

    # Tests
    "test_pii_detector.py",
    "test_redaction.py",
    "test_docx_redactor.py",
    "validate_redaction.py",

    # Output
    "Redacted_Prospectus.docx",
]


print()
print("FILE CHECK")
print("-" * 80)

missing_files = []

for filename in required_files:

    if os.path.exists(filename):

        size = os.path.getsize(filename)

        print(
            f"[PASS] {filename:<35} {size:,} bytes"
        )

    else:

        print(
            f"[FAIL] {filename:<35} MISSING"
        )

        missing_files.append(filename)


# ============================================================
# PYTHON IMPORT CHECK
# ============================================================

print()
print("PYTHON MODULE CHECK")
print("-" * 80)

modules = [
    "name_detector",
    "company_detector",
    "email_detector",
    "phone_detector",
    "credit_card_detector",
    "ssn_detector",
    "dob_detector",
    "ip_detector",
    "pii_detector",
    "redaction_engine",
]


import_failures = []

for module in modules:

    try:

        __import__(module)

        print(f"[PASS] {module}")

    except Exception as error:

        print(f"[FAIL] {module}")
        print(f"       {error}")

        import_failures.append(module)


# ============================================================
# RUN EVALUATION TESTS
# ============================================================

def run_test(filename):

    print()
    print("-" * 80)
    print(f"RUNNING: {filename}")
    print("-" * 80)

    result = subprocess.run(
        [sys.executable, filename],
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.stderr:
        print("STDERR:")
        print(result.stderr)

    return result.returncode == 0


test_files = [
    "evaluate_names.py",
    "evaluate_companies.py",
    "evaluate_emails.py",
]


evaluation_failures = []

for test in test_files:

    if not os.path.exists(test):

        print(f"[INFO] {test} not found")

        continue

    if not run_test(test):

        evaluation_failures.append(test)


# ============================================================
# RUN PII DETECTOR TEST
# ============================================================

if os.path.exists("test_pii_detector.py"):

    print()
    print("-" * 80)
    print("RUNNING: test_pii_detector.py")
    print("-" * 80)

    result = subprocess.run(
        [sys.executable, "test_pii_detector.py"],
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.stderr:
        print("STDERR:")
        print(result.stderr)

    pii_detector_passed = result.returncode == 0

else:

    print("[INFO] test_pii_detector.py not found")

    pii_detector_passed = True


# ============================================================
# REDACTED DOCX CHECK
# ============================================================

print()
print("REDACTED DOCX CHECK")
print("-" * 80)

redacted_file = "Redacted_Prospectus.docx"

if os.path.exists(redacted_file):

    size = os.path.getsize(redacted_file)

    if size > 0:

        print(
            f"[PASS] {redacted_file}"
        )

        print(
            f"       Size: {size:,} bytes"
        )

    else:

        print(
            f"[FAIL] {redacted_file} is empty"
        )

else:

    print(
        f"[FAIL] {redacted_file} does not exist"
    )


# ============================================================
# FINAL VALIDATION
# ============================================================

print()
print("-" * 80)
print("RUNNING FINAL REDACTION VALIDATION")
print("-" * 80)

if os.path.exists("validate_redaction.py"):

    result = subprocess.run(
        [sys.executable, "validate_redaction.py"],
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.stderr:
        print("STDERR:")
        print(result.stderr)

    validation_passed = (
        result.returncode == 0
        and "PHASE 12 STATUS: PASSED" in result.stdout
    )

else:

    print("[FAIL] validate_redaction.py not found")

    validation_passed = False


# ============================================================
# FINAL RESULT
# ============================================================

print()
print("=" * 80)
print("FINAL PROJECT STATUS")
print("=" * 80)

if missing_files:

    print()
    print("Missing files:")
    for filename in missing_files:
        print("  -", filename)


if import_failures:

    print()
    print("Import failures:")
    for module in import_failures:
        print("  -", module)


if evaluation_failures:

    print()
    print("Evaluation failures:")
    for test in evaluation_failures:
        print("  -", test)


print()

if (
    not missing_files
    and not import_failures
    and not evaluation_failures
    and pii_detector_passed
    and validation_passed
):

    print("PHASE 13 STATUS: PASSED")
    print()
    print("PII REDACTION TOOL PROJECT: COMPLETE")
    print()
    print("The project successfully:")
    print("  [PASS] Detects supported PII")
    print("  [PASS] Evaluates detectors")
    print("  [PASS] Redacts text")
    print("  [PASS] Redacts DOCX documents")
    print("  [PASS] Validates the redacted document")
    print("  [PASS] Produces Redacted_Prospectus.docx")

else:

    print("PHASE 13 STATUS: REVIEW REQUIRED")

print("=" * 80)
