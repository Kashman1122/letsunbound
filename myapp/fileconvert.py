import json
import csv
import re

def extract_detail_info(details):
    """
    Extracts information from details list using a more flexible approach
    """
    extracted_info = {
        'year': 'Unknown',
        'organization_type': 'Unknown',
        'size': 'Unknown',
        'area': 'Unknown',
        'graduation_rate': 'Unknown',
        'financial_aid': 'Unknown',
        'sat_score': 'Unknown'
    }
    
    # Flatten details and remove empty strings
    flat_details = [detail.strip() for detail in ' '.join(details).split('\n') if detail.strip()]
    
    for detail in flat_details:
        # Year detection (generalized)
        if re.search(r'\d+-year', detail):
            extracted_info['year'] = detail
        
        # Organization type detection
        if detail in ['Public', 'Private', 'For-Profit']:
            extracted_info['organization_type'] = detail
        
        # Size detection
        size_options = ['Tiny', 'Small', 'Medium', 'Large', 'Very Large']
        if any(size in detail for size in size_options):
            extracted_info['size'] = detail
        
        # Area detection
        area_options = ['Urban', 'Suburban', 'Rural', 'Urban-Suburban', 'Rural-Suburban']
        if any(area in detail for area in area_options):
            extracted_info['area'] = detail
        
        # Graduation rate detection
        if '%' in detail and 'graduation' in detail.lower():
            extracted_info['graduation_rate'] = detail
        
        # Financial aid detection
        if '$' in detail and ('average' in detail.lower() or 'per year' in detail.lower()):
            extracted_info['financial_aid'] = detail
        
        # SAT score detection
        if re.search(r'\d+[-–]\d+', detail):
            extracted_info['sat_score'] = detail
    
    return extracted_info

def json_to_csv(input_file, output_file):
    # Read the JSON file
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Prepare the CSV columns
    columns = [
        'college_name', 
        'address', 
        'year', 
        'organization_type', 
        'size', 
        'area', 
        'graduation_rate', 
        'financial_aid', 
        'sat_score'
    ]
    
    # Open the CSV file for writing
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        
        # Write the header
        writer.writeheader()
        
        # Process each item in the JSON
        for item in data:
            # Extract details information
            details_info = extract_detail_info(item.get('details', []))
            
            # Prepare the row
            row = {
                'college_name': item.get('college_name', 'Unknown'),
                'address': item.get('address', 'Unknown'),
                'year': details_info['year'],
                'organization_type': details_info['organization_type'],
                'size': details_info['size'],
                'area': details_info['area'],
                'graduation_rate': details_info['graduation_rate'],
                'financial_aid': details_info['financial_aid'],
                'sat_score': details_info['sat_score']
            }
            
            # Write the row to the CSV
            writer.writerow(row)
    
    print(f"CSV file has been created at {output_file}")

# Example usage
input_file = r'D:\pycharm\Edtech\education\myapp\university_data.json'  # Input JSON file
output_file = r'D:\pycharm\Edtech\education\myapp\colleges.csv'  # Output CSV file

# Call the function to convert JSON to CSV
json_to_csv(input_file, output_file)