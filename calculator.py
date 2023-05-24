import argparse
import csv
from collections import Counter
from datetime import datetime, timedelta

BASE_MINUTE_RATE = 0.5
BUSSINESS_HOUR_RATE = 1  # Minute rate in interval <8:00:00,16:00:00
TIME_MINS_FOR_BONUS_RATE = 5
DISCOUNT_RATE = 0.2  # For calls longer than 5 mins bonus rate 0,20 CZK
BEGINNING_OF_THE_BUSSINESS_DAY = datetime.strptime("8:00:00", "%H:%M:%S").time()
END_OF_THE_BUSSINESS_DAY = datetime.strptime("16:00:00", "%H:%M:%S").time()


def read(filename):
    """Read the CSV file contents as a string."""
    with open(filename, "r") as file:
        return file.readlines()


def extract_data(csv_content):
    """Extract data from file"""
    return [data.replace("\n", "").split(",") for data in csv_content]


def find_most_common_phone(parsed_data):
    """Find most common number"""
    phone_numbers = [row["phone_number"] for row in parsed_data]
    number_counts = Counter(phone_numbers)  # Check for more numbers
    most_common_phones = []
    highest_frequence_call = number_counts.most_common(1)[0][1]
    for phone, count in number_counts.most_common():
        if count == highest_frequence_call:
            most_common_phones.append(phone)
        else:
            return max(most_common_phones)  

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
        end_time = end_time - timedelta(seconds=1) # In call end last second is not included in call length
        minutes = calculate_duration(start_time, end_time)
        cost = calculation(data, minutes, most_common_phone)
        update_cost_struct(cost_struct, phone_number, cost)
    return cost_struct

def calculate_duration(start_time, end_time):
    """Calculate the duration of the call."""
    return 1 + ((end_time - start_time).total_seconds()) // 60 # Count cost from the first second in tarif minute

def calculation(data, minutes, most_common_phone):
    """Calculation using const"""
    if data["phone_number"] == most_common_phone:
        return 0  # For most common phone, call is free
    else:
        if (
            data["start_time"].time() >= BEGINNING_OF_THE_BUSSINESS_DAY
            and data["end_time"].time() <= END_OF_THE_BUSSINESS_DAY
        ): # Contol if minute rate in interval <8:00:00,16:00:00)
            if minutes <= TIME_MINS_FOR_BONUS_RATE: # Control if call is shorter than 5 minutes
                return minutes * BUSSINESS_HOUR_RATE
            return (
                BUSSINESS_HOUR_RATE * TIME_MINS_FOR_BONUS_RATE
                + (minutes - TIME_MINS_FOR_BONUS_RATE) * DISCOUNT_RATE # For calls longer than 5 mins discount rate
            )
        else:
            if minutes <= TIME_MINS_FOR_BONUS_RATE:
                return minutes * BASE_MINUTE_RATE
            return (
                BASE_MINUTE_RATE * TIME_MINS_FOR_BONUS_RATE
                + (minutes - TIME_MINS_FOR_BONUS_RATE) * DISCOUNT_RATE
            )

def update_cost_struct(cost_struct, phone_number, cost):
    """Update the cost structure with the calculated cost."""
    if phone_number in cost_struct:
        cost_struct[phone_number] += round(float(cost), 2)
    else:
        cost_struct[phone_number] = round(float(cost), 2)

def save_data(new_filename, cost_struct, most_common_number):
    """Save edited data in new file."""
    with open(new_filename, "w", newline="") as new_filename:
        writer = csv.writer(new_filename)
        writer.writerow(["Most_common_number:", most_common_number])
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
    most_common_phone = find_most_common_phone(parsed_data)
    save_data(args.output_file, cost_struct, most_common_phone)
