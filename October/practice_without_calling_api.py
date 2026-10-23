
import csv
from pathlib import Path

DATA_DIR = Path("data")
INPUT_FILE = DATA_DIR / "tickets.csv"
OUTPUT_FILE = DATA_DIR / "predictions.csv"

OUTPUT_FIELDS = ["ticket_id", "predicted_category"]

CATEGORY_KEYWORDS = {
    "Technical": ["program hangs", "is crashing", "bad gateway","app hangs", "crashes", "http 504", "500 error", "app freezes", "application error","freezes", "http 503", "http 500", "http 501", "http 502", "reset my router", "wifi is down", "wi-fi is down", "page crashes", "error code 503"],
    "Billing": ["duplicate card charge","paid twice","payment was declined","invoice", "charged", "subscription" , "payment declined", "billed"],
    "Authentication": ["unresponsive", "gateway timeout", "dependency failure", "screen stays blank", "status code 504","unable to enter","get into my account", "repeated attempts", "log in", "sign in", "can't access", "cannot access", "credentials", "reset credentials"],


}

EXPECTED_PREDICTIONS = {
    "T001": "Authentication",
    "T002": "Billing",
    "T003": "Technical",
    "T004": "Unknown",
    "T005": "Authentication",
    "T006": "Billing",
    "T007": "Technical",
    "T008": "Unknown",
}


def classify_message(message):
    if not isinstance(message, str) or not message.strip():
        return "Unknown"

    normalized_message = message.replace("-", " ").casefold()

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in normalized_message for keyword in keywords):
            return category

    return "Unknown"


def generate_predictions(input_file, output_file):
    with input_file.open("r", newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)

        if not reader.fieldnames or not {"ticket_id", "message"}.issubset(reader.fieldnames):
            raise ValueError("Input CSV must contain ticket_id and message columns.")

        with output_file.open("w", newline="", encoding="utf-8") as destination:
            writer = csv.DictWriter(destination, fieldnames=OUTPUT_FIELDS)
            writer.writeheader()

            for row in reader:
                ticket_id = (row.get("ticket_id") or "").strip()
                category = classify_message(row.get("message"))

                writer.writerow({
                    "ticket_id": ticket_id,
                    "predicted_category": category,
                })


def evaluate_predictions(output_file, expected_predictions):
    predictions = {}
    duplicate_ids = set()
    total_rows = 0

    with output_file.open("r", newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)

        if not reader.fieldnames or not set(OUTPUT_FIELDS).issubset(reader.fieldnames):
            raise ValueError("Output CSV has an invalid header.")

        for row in reader:
            total_rows += 1
            ticket_id = (row.get("ticket_id") or "").strip()
            category = (row.get("predicted_category") or "").strip()

            if ticket_id in predictions:
                duplicate_ids.add(ticket_id)

            predictions[ticket_id] = category

    correct = sum(
        1
        for ticket_id, expected_category in expected_predictions.items()
        if ticket_id in predictions
        and ticket_id not in duplicate_ids
        and predictions[ticket_id] == expected_category
    )

    total_expected = len(expected_predictions)
    incorrect = total_expected - correct
    accuracy = correct / total_expected * 100 if total_expected else 0.0

    output_is_valid = (
        total_rows == total_expected
        and set(predictions) == set(expected_predictions)
        and not duplicate_ids
    )

    print(f"Output rows: {total_rows}")
    print(f"Expected tickets: {total_expected}")
    print(f"Correct predictions: {correct}")
    print(f"Incorrect or missing predictions: {incorrect}")
    print(f"Accuracy: {accuracy:.1f}%")
    print(f"Output structure valid: {output_is_valid}")


def main():
    generate_predictions(INPUT_FILE, OUTPUT_FILE)
    evaluate_predictions(OUTPUT_FILE, EXPECTED_PREDICTIONS)


if __name__ == "__main__":
    main()

test_cases = [
    ("I can't access my account", "Authentication"),
    ("Please reset my credentials", "Authentication"),
    ("SIGN IN keeps failing", "Authentication"),
    ("I was billed twice this month", "Billing"),
    ("My subscription renewal failed", "Billing"),
    ("The payment was declined", "Billing"),
    ("The app freezes on launch", "Technical"),
    ("Application error occurs during startup", "Technical"),
    ("The website returns HTTP 503", "Technical"),
    ("Thanks for your help", "Unknown"),
    ("Can you tell me your business hours?", "Unknown"),
]
passed = 0
total = len(test_cases)

for message, expected in test_cases:
    predicted = classify_message(message)

    if predicted == expected:
        passed += 1
    else:
        print("Predicted: ", predicted, " But Expected: ", expected)

print(f"Passed: {passed}/{total}")


hard_test_cases = [
    ("I have 500 unread messages", "Unknown"),
    ("I need to reset my router because Wi-Fi is down", "Technical"),
    ("My password reset page crashes", "Technical"),
    ("I have no payment problem, but the app freezes", "Technical"),
    ("The invoice contains an incorrect amount", "Billing"),
    ("I cannot sign in to my account", "Authentication"),
]

all_test_cases = test_cases + hard_test_cases

passed = 0
failures = []

for message, expected in all_test_cases:
    predicted = classify_message(message)

    if predicted == expected:
        passed += 1
    else:
        failures.append({
            "message": message,
            "expected": expected,
            "predicted": predicted,
        })

print(f"Passed: {passed}/{len(all_test_cases)}")
print(f"Failed: {len(failures)}")

for failure in failures:
    print(failure)


unseen_test_cases = [
    ("I can log in, but my subscription renewal failed", "Billing"),
    ("The app hangs when I submit my invoice", "Technical"),
    ("HTTP 504 error while opening my dashboard", "Technical"),
    ("My account was locked after repeated attempts", "Authentication"),
    ("I was double-charged for the same order", "Billing"),
    ("The invoice is missing a line item", "Billing"),
    ("The app freezes when I access my password settings", "Technical"),
    ("Please change my sign-in credentials", "Authentication"),
    ("We have 503 customer records and no errors", "Unknown"),
    ("The website displays an error code 503", "Technical"),
]

passed = 0
failures = []

for message, expected in unseen_test_cases:
    predicted = classify_message(message)

    if predicted == expected:
        passed += 1
    else:
        failures.append({
            "message": message,
            "expected": expected,
            "predicted": predicted,
        })

print(f"Passed: {passed}/{len(unseen_test_cases)}")
print(f"Failed: {len(failures)}")

for failure in failures:
    print(failure)

generalization_tests = [
    ("I can't get into my account", "Authentication"),
    ("The login form rejects my credentials", "Authentication"),
    ("I paid twice for the same order", "Billing"),
    ("I was billed for an item I never ordered", "Billing"),
    ("The program hangs when I open settings", "Technical"),
    ("The application is crashing during startup", "Technical"),
    ("The server returned Bad Gateway (502)", "Technical"),
    ("I have 502 files in my account", "Unknown"),
    ("The subscription page crashes when I renew", "Technical"),
    ("I don't have a payment issue; I can't sign in", "Authentication"),
]

passed = 0
failures = []

for message, expected in generalization_tests:
    predicted = classify_message(message)

    if predicted == expected:
        passed += 1
    else:
        failures.append({
            "message": message,
            "expected": expected,
            "predicted": predicted,
        })

print(f"Passed: {passed}/{len(generalization_tests)}")
print(f"Failed: {len(failures)}")

for failure in failures:
    print(failure)


fresh_tests = [
    ("Unable to enter my workspace", "Authentication"),
    ("A duplicate card charge appeared today", "Billing"),
    ("The client became unresponsive after launch", "Technical"),
    ("The server responded with Gateway Timeout (504)", "Technical"),
    ("We have 503 seats in the auditorium", "Unknown"),
    ("The invoice amount is incorrect", "Billing"),
    ("The application cannot start because of a dependency failure", "Technical"),
    ("The screen stays blank after I launch the app", "Technical"),
    ("My login credentials no longer work", "Authentication"),
    ("HTTP status 502 was logged, but no customer-facing issue occurred", "Unknown"),
    ("The billing page loads, but sign-in is broken", "Authentication"),
    ("The website returns status code 504", "Technical"),
]

passed = 0
failures = []

for message, expected in fresh_tests:
    predicted = classify_message(message)

    if predicted == expected:
        passed += 1
    else:
        failures.append({
            "message": message,
            "expected": expected,
            "predicted": predicted,
        })

print(f"Passed: {passed}/{len(fresh_tests)}")
print(f"Failed: {len(failures)}")

for failure in failures:
    print(failure)