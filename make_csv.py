import os
import csv


def create_csv(directory):
    # Get the list of files in the directory
    files = os.listdir(directory)

    # Create a new CSV file
    csv_file = open('file_context.csv', 'w', newline='', encoding='utf-8')
    csv_writer = csv.writer(csv_file)

    # Write the header row
    csv_writer.writerow(['file_name', 'context'])

    # Iterate through the files
    for file_name in files:
        # Read the contents of each file
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'r', encoding="utf8") as file:
            file_contents = file.read()

        # Write the file name and context to the CSV file
        csv_writer.writerow([file_name, file_contents])

    # Close the CSV file
    csv_file.close()


# Example usage
directory_path = r'C:\Users\MetroCat1\Desktop\learn_programing\genersting percy jaskson\hebrew-mil-corpus\clean'
create_csv(directory_path)
print("CSV file created successfully.")