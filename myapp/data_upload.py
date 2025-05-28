import csv
import os
import django
import sys

# Set up Django environment
sys.path.append("D:\pycharm\Edtech\education\education")  # Update this with your project path
os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "settings")  # Update your_project with your actual project name
django.setup()

from education.myapp.models import University


def import_university_data():
    csv_file_path = "university_data_with_majors.csv"

    # Delete all existing records (optional)
    # University.objects.all().delete()

    created_count = 0
    error_count = 0

    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                try:
                    # Convert empty strings to None for numeric fields
                    year = int(row['year']) if row['year'].strip() else None
                    graduation_rate = float(row['graduation_rate']) if row['graduation_rate'].strip() else None
                    financial_aid = float(row['financial_aid']) if row['financial_aid'].strip() else None
                    sat_score = int(row['sat_score']) if row['sat_score'].strip() else None

                    University.objects.create(
                        college_name=row['college_name'],
                        address=row['address'],
                        year=year,
                        organization_type=row['organization_type'],
                        size=row['size'],
                        area=row['area'],
                        graduation_rate=graduation_rate,
                        financial_aid=financial_aid,
                        sat_score=sat_score,
                        majors=row['majors']
                    )
                    created_count += 1

                    # Print progress every 100 records
                    if created_count % 100 == 0:
                        print(f"Processed {created_count} records...")

                except Exception as e:
                    print(f"Error importing record: {row.get('college_name', 'Unknown')}: {str(e)}")
                    error_count += 1

    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")

    print(f"Import completed. Created {created_count} university records. Errors: {error_count}")


if __name__ == "__main__":
    import_university_data()