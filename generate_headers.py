import os
import pandas as pd

# Define the path to the directory containing the folders
base_path = '/Users/charan/Desktop/SJSU/275/CMPE-275-HPC-All_working/data_airflow'

# Define your headers
headers = [
    "Latitude", "Longitude", "UTC", "Parameter", "Concentration",
    "Unit", "RawConcentration", "AQI", "Category", "SiteName",
    "SiteAgency", "AQSID", "FullAQSID"
]

# Loop through each folder in the directory
for folder_name in os.listdir(base_path):
    folder_path = os.path.join(base_path, folder_name)
    if os.path.isdir(folder_path):
        # Loop through each file in the folder
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if file_name.endswith('.csv'):
                # Read the CSV file, assuming no header
                df = pd.read_csv(file_path, header=None)
                
                # Add the headers
                df.columns = headers
                
                # Save the DataFrame back to CSV
                df.to_csv(file_path, index=False)