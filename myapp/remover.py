import json

def clean_json(input_file):
    # Read the JSON file
    with open(input_file, 'r') as file:
        data = json.load(file)
    count=0
    # Process each item to remove specific fields
    for item in data:
        count+=1
    return count
    

# Call the function to clean and modify JSON

input_file =r"D:\pycharm\Edtech\education\myapp\University-data1.json"
print(clean_json(input_file))

