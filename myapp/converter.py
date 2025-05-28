import csv
import json

# Path to your CSV file
csv_file_path = 'university_data.csv'
json_file_path = 'university_data_real.json'

# List to hold the JSON data
college_data = []

# Read the CSV file
with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
    csvreader = csv.DictReader(csvfile)

    # Convert each row to a dictionary and append to the list
    for row in csvreader:
        # Convert the row data into a dictionary
        college_info = {
            "college_name": row["college_name"],
            "address": row["address"],
            "year": row["year"],
            "organization_type": row["organization_type"],
            "size": row["size"],
            "area": row["area"],
            "graduation_rate": row["graduation_rate"],
            "financial_aid": row["financial_aid"],
            "sat_score": row["sat_score"]
        }
        college_data.append(college_info)

# Write the data to a JSON file
with open(json_file_path, mode='w', encoding='utf-8') as jsonfile:
    json.dump(college_data, jsonfile, indent=4)

print(f'CSV data has been successfully converted to {json_file_path}')
