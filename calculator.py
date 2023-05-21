from collections import Counter
from datetime import datetime
import csv

FILENAME = "generated_sample_2.csv"
NEW_FILENAME ="new_file.csv"

def read(filename):   
    # Read the CSV file contents as a string
    with open(filename, "r") as file:
        return file.readlines()

def extract_data(csv_content):
    all_data = [data.replace("\n", "").split(",") for data in csv_content]
    return all_data

def find_most_common_phone(all_data):
    phone_numbers = [phone[0] for phone in all_data]
    number_counts = Counter(phone_numbers)
    most_common_phone = number_counts.most_common(1)[0][0]  # For this number call is free
    return most_common_phone

def calculate_cost(all_data):
    cost_lst = []
    most_common_phone = find_most_common_phone(all_data)
    rate_interval_start = datetime.strptime('8:00:00', '%H:%M:%S').time()
    rate_interval_end = datetime.strptime('16:00:00', '%H:%M:%S').time()
    
    for data in all_data:
        start_time = datetime.strptime(data[1], '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(data[2], '%Y-%m-%d %H:%M:%S')
        
        duration = end_time - start_time
        minutes = 1 + (duration.seconds // 60)  # call end in format yyyy-MM-dd HH:mm:ss – last second is not included in call length !!!!
        if data[0] == most_common_phone:
            cost = 0 # For the most common phone, call is free
        else:
            if start_time.time() >= rate_interval_start and end_time.time() <= rate_interval_end:
                if minutes <= 5:
                    cost = minutes * 1
                else:
                    cost = round(1 * 5 + (minutes - 5) * 0.2, 2) # CONST
            else:
                if minutes <= 5:
                    cost = minutes * 0.5
                else:
                    cost = round(0.5 * 5 + (minutes - 5) * 0.2, 2)   
        cost_lst.append(cost)
    
    return cost_lst

def save_data(filename, new_filename, cost_lst):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)  # Read all rows from the CSV file

    # Add the new column data to each row
    for i, row in enumerate(rows):
        row.append(cost_lst[i])

    with open(new_filename, 'w', newline='') as new_filename:
        writer = csv.writer(new_filename)
        writer.writerows(rows) 
    
if __name__ == "__main__":
    csv_content = read(FILENAME)
    all_data = extract_data(csv_content)
    most_common_phone = find_most_common_phone(all_data)
    cost_lst = calculate_cost(all_data)
    save_data(FILENAME, NEW_FILENAME, cost_lst)

# change round to 2 

# Minute rate in interval <8:00:00,16:00:00) is 1 CZK for each started minute. Otherwise, it is 0,50 CZK.
# Appropriate rate is chosen for each minute of a call
# For calls longer than 5 mins bonus rate 0,20 CZK is applied for all remaining minutes, no mater of a daytime.
# There is a promo event making calls to most frequent number out of charge (free), if there is more than one number, take the one with arithmetically higher number

    
