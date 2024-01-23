import pandas as pd
import os

# Specify the directory where your CSV files are located
folder_path = r'C:\Users\lokes\Downloads\VS Code\Web Scrapper\downloaded_files'

# List all files in the directory
all_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.endswith('.csv')]

# Lists to store extracted data and error files
data_list = []
error_files = []

# Loop through each file and extract headers and first 5 records
for file in all_files:
    file_path = os.path.join(folder_path, file)
    try:
        # Read the CSV file
        df = pd.read_csv(file_path, nrows=5)  # Read headers and first 5 rows
        data_dict = {"File Name": file}
        for idx, header in enumerate(df.columns.tolist(), 1):
            values = df[header].tolist()
            for row_idx, value in enumerate(values, 1):
                col_name = f"{header} (Record {row_idx})"
                data_dict[col_name] = value
        data_list.append(data_dict)
    except Exception as e:
        error_files.append(file)

# Write extracted data to a new CSV file
data_df = pd.DataFrame(data_list)
data_df.to_csv(os.path.join(folder_path, "data_output.csv"), index=False)

# Write error files to a text file
with open(os.path.join(folder_path, "error_files.txt"), "w") as f:
    for error_file in error_files:
        f.write(f"{error_file}\n")

print("Data extracted and saved to 'data_output.csv'.")
print("Files with errors logged to 'error_files.txt'.")
