import glob
import io
import os
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, send_file, render_template_string, render_template
import matplotlib
from flask import url_for
import seaborn as sns

matplotlib.use('Agg')  # This line is crucial for non-GUI backend
app = Flask(__name__)

def clean_csv(input_file_path, output_file_path):
    with open(input_file_path, 'r', encoding='utf-8', errors='ignore') as infile, \
         open(output_file_path, 'w', encoding='utf-8') as outfile:
        for line in infile:
            corrected_line = line.strip()  # Remove leading/trailing whitespace
            # Simple check for unmatched quotes (very basic, might need adjustment)
            if corrected_line.count('"') % 2 != 0:
                corrected_line = corrected_line.replace('"', '')
            outfile.write(corrected_line + '\n')

input_file_path = '../../final_data/combined_cleaned_data.csv'
output_file_path = '../../final_data/cleaned_file.csv'
clean_csv(input_file_path, output_file_path)
# Load your CSV data
# Assuming this file path is accessible, adjust accordingly or use an uploaded file method
headers = [
    "Latitude", "Longitude", "UTC", "Parameter", "Concentration",
    "Unit", "RawConcentration", "AQI", "Category", "SiteName",
    "SiteAgency", "AQSID"]

df = pd.read_csv('../../final_data/cleaned_file.csv', low_memory=False, on_bad_lines='skip')
if len(df.columns) == len(headers):
    # Assign headers to the DataFrame
    df.columns = headers
else:
    print(f"Error: The CSV file has {len(df.columns)} columns, but {len(headers)} headers were provided.")



@app.route('/')
def index():
    return '''
    <html>
        <head>
            <title>Air Quality Plot Server</title>
        </head>
        <body>
            <h1>Welcome to the Air Quality Plot Server!</h1>
            <p>Select a category to view related plots:</p>
            <ul>
                <li><a href="/air_quality">Air Quality by Location</a></li>
                <li><a href="/time_series">Time Series of Air Quality</a></li>
                <li><a href="/pollutant_distribution">Pollutant Distribution</a></li>
                <li><a href="/heatmap_aqi">Heatmap of AQI</a></li>
            </ul>
        </body>
    </html>
    '''

# The existing /air_quality route can stay as it is.

# Route for a time series plot of AQI
@app.route('/time_series')
def time_series_plot():
    try:
        local_df = df.copy()
        local_df['UTC'] = pd.to_datetime(local_df['UTC'], errors='coerce')
        local_df = local_df.dropna(subset=['UTC', 'AQI'])
        local_df = local_df.sort_values(by='UTC')
        fig, ax = plt.subplots()
        sns.lineplot(x='UTC', y='AQI', data=local_df, ax=ax)
        ax.set_title('Time Series of AQI')
        ax.set_xlabel('Time')
        ax.set_ylabel('AQI')
        plt.xticks(rotation=45)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close(fig)
        return send_file(buf, mimetype='image/png')
    except Exception as e:
        # In production, you would log the exception to your system's log
        print(e)
        return str(e), 500  # Return the error message and a 500 Internal Server Error status code
# Route for pollutant distribution
@app.route('/pollutant_distribution')
def pollutant_distribution_plot():
    # You'd need to modify this to select the right pollutant columns
    pollutants = ['PM2.5', 'PM10']  # example pollutants
    local_df = df[df['Parameter'].isin(pollutants)]
    fig, ax = plt.subplots()
    sns.boxplot(x='Parameter', y='Concentration', data=local_df, ax=ax)
    ax.set_title('Distribution of Pollutant Concentrations')
    ax.set_xlabel('Pollutant')
    ax.set_ylabel('Concentration (UG/M3)')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype='image/png')


@app.route('/air_quality')
def plot_air_quality():
    local_df = df.copy()
    
    # Convert 'Latitude' and 'Longitude' to numeric values, coerce errors to NaN
    local_df['Latitude'] = pd.to_numeric(local_df['Latitude'], errors='coerce')
    local_df['Longitude'] = pd.to_numeric(local_df['Longitude'], errors='coerce')
    local_df['AQI'] = pd.to_numeric(local_df['AQI'], errors='coerce')

    # Drop rows with NaN values in 'Latitude', 'Longitude', or 'AQI'
    local_df = local_df.dropna(subset=['Latitude', 'Longitude', 'AQI'])
    
    fig, ax = plt.subplots()
    
    # Create a scatter plot with AQI values, limiting the AQI range to 0-200
    sc = ax.scatter(local_df['Longitude'], local_df['Latitude'], c=local_df['AQI'], cmap='viridis', vmin=0, vmax=200)
    ax.set_title('Air Quality Index (AQI) by Location')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    
    # Create a colorbar reflecting the range from 0 to 200
    plt.colorbar(sc, label='AQI')

    # Save the plot to a BytesIO buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype='image/png')


def get_csv_files(directory, exclude_file='processed.csv'):
    # This function will find all csv files in the given directory excluding the 'processed.csv'
    return [f for f in glob.glob(f"{directory}/*.csv") if exclude_file not in f]


def determine_number_of_processes(dataframe):
    # The number of processes will be one less than the number of columns
    # because the first column is for seconds
    return dataframe.shape[1] - 1


def plot_records_vs_time(dataframe, num_processes):
    # Plotting function suitable for Flask, which saves the plot to a BytesIO buffer and returns it
    fig, ax = plt.subplots()
    for i in range(num_processes):
        ax.plot(dataframe['Seconds'],
                dataframe[f'RecordsProcessed-P{i}'], label=f'Process P{i}')
    ax.set_xlabel('Time (Seconds)')
    ax.set_ylabel('Number of Records Processed')
    ax.set_title('Records Processed Over Time by Each Process')
    ax.legend()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return buf


def load_csv(file_path):
    dataframe = pd.read_csv(file_path, low_memory=False)
    num_processes = determine_number_of_processes(dataframe)
    return dataframe, num_processes


if __name__ == '__main__':
    app.run(debug=True)
