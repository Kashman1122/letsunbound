import pandas as pd

# Read the CSV files
# Replace these paths with the actual paths to your files
university_data = pd.read_csv('university_data.csv')
academics_data = pd.read_csv('academics_detail.csv')  # This is the file with majors data

# Merge the dataframes on the college_name column
# Using left join to keep all universities from university_data
merged_data = pd.merge(
    university_data,
    academics_data,
    on='college_name',  # Assuming both files have a column called 'college_name'
    how='left'  # Keep all rows from university_data
)

# Save the merged data to a new CSV file
merged_data.to_csv('merged_university_data.csv', index=False)

print(f"Merged data saved to 'merged_university_data.csv'")
print(f"Original university_data rows: {len(university_data)}")
print(f"Academics data rows: {len(academics_data)}")
print(f"Merged data rows: {len(merged_data)}")