import argparse
import csv
from collections import Counter
from datetime import datetime, timedelta

BASE_MINUTE_RATE = 0.5
BUSSINESS_HOUR_RATE = 1  # Minute rate in interval <8:00:00,16:00:00
TIME_MIN_FOR_BONUS_RATE = 5
DISCOUNT_RATE = 0.2  # For calls longer than 5 mins bonus rate 0,20 CZK
BEGINNING_OF_THE_BUSSINESS_DAY = datetime.strptime("8:00:00", "%H:%M:%S").time()
END_OF_THE_BUSSINESS_DAY = datetime.strptime("16:00:00", "%H:%M:%S").time()


def read(filename):
    """Read the CSV file contents as a string."""
    # Read the CSV file contents as a string
    with open(filename, "r") as file:
        return file.readlines()


def extract_data(csv_content):
    """Extract data from file"""
    return [data.replace("\n", "").split(",") for data in csv_content]


def find_most_common_phone(parsed_data):
    """Find the most common number"""
    phone_numbers = [row["phone_number"] for row in parsed_data]
    number_counts = Counter(phone_numbers)  # check for more numbers
    most_common_phone = number_counts.most_common()
    if len(most_common_phone) > 1:
        max_count = max(count for _, count in most_common_phone)
        # If there is more than one most common phone number
        most_common_phones = [
            phone for phone, count in most_common_phone if count == max_count
        ]
        most_common_phone = max(most_common_phones)
    else:
        most_common_phone = most_common_phones[0][0]
    return most_common_phone


def parse_data(all_data):
    """Parsed data."""
    parsed_data = []
    for row_number, data in enumerate(all_data):
        try:
            processed_row = {
                "phone_number": int(data[0].lstrip("+")),
                "start_time": datetime.strptime(data[1], "%Y-%m-%d %H:%M:%S"),
                "end_time": datetime.strptime(data[2], "%Y-%m-%d %H:%M:%S"),
            }
            parsed_data.append(processed_row)
        except (IndexError, ValueError):
            raise ValueError(f"Not valid data on a line {row_number}")
    return parsed_data


def calculate_cost(parsed_data):
    """Calculate cost for each call."""
    most_common_phone = find_most_common_phone(parsed_data)
    cost_struct = {}
    for data in parsed_data:
        phone_number = data["phone_number"]
        start_time = data["start_time"]
        end_time = data["end_time"]
        duration = end_time - start_time - timedelta(seconds=1)
        minutes = 1 + (duration.seconds // 60)
        if data["phone_number"] == most_common_phone:
            cost = 0  # For the most common phone, call is free
        else:
            if (
                start_time.time() >= BEGINNING_OF_THE_BUSSINESS_DAY
                and end_time.time() <= END_OF_THE_BUSSINESS_DAY
            ):
                if minutes <= TIME_MIN_FOR_BONUS_RATE:
                    cost = minutes * BUSSINESS_HOUR_RATE
                else:
                    cost = (
                        BUSSINESS_HOUR_RATE * TIME_MIN_FOR_BONUS_RATE
                        + (minutes - TIME_MIN_FOR_BONUS_RATE) * DISCOUNT_RATE
                    )
            else:
                if minutes <= TIME_MIN_FOR_BONUS_RATE:
                    cost = minutes * BASE_MINUTE_RATE
                else:
                    cost = (
                        BASE_MINUTE_RATE * TIME_MIN_FOR_BONUS_RATE
                        + (minutes - TIME_MIN_FOR_BONUS_RATE) * DISCOUNT_RATE
                    )
        cost_struct[phone_number] = round(float(cost), 2)

    return cost_struct


def save_data(new_filename, cost_struct):
    """Save edited data in new file."""
    with open(new_filename, "w", newline="") as new_filename:
        writer = csv.writer(new_filename)
        writer.writerow(["Phone Number", "Cost"])
        for phone_number, cost in cost_struct.items():
            writer.writerow([phone_number, cost])


def parse_arg():
    """Command line user interface."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input-filename",
        help="Csv source of data.",
        type=str,
        required=True,
        dest="input_file",
    )
    parser.add_argument(
        "-o",
        "--output-filename",
        help="Processed data.",
        type=str,
        required=True,
        dest="output_file",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arg()
    csv_content = read(args.input_file)
    all_data = extract_data(csv_content)
    parsed_data = parse_data(all_data)
    cost_struct = calculate_cost(parsed_data)
    save_data(args.output_file, cost_struct)
