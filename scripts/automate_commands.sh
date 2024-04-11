#!/bin/bash



# Run the Python script to delete unwanted files
python3 delete_files.py

# Navigate to the 'src' directory
cd ../src

# Prompt the user to input the number of processes
read -p "Enter the number of processes: " process_count

# Compile C++ program
g++-13 -o my_program main.cpp reader.cpp loader.cpp logger.cpp -std=c++17 -fopenmp -I/opt/homebrew/Cellar/open-mpi/5.0.2_1/include -L/opt/homebrew/Cellar/open-mpi/5.0.2_1/lib -lmpi

# # Execute C++ program with MPI
mpiexec -n $process_count ./my_program


data_directory="/Users/charan/Desktop/SJSU/275/CMPE-275-HPC-All_working/data"

# Check if the required files are generated
while ! ls $data_directory/records_per_second_process_*.csv 1> /dev/null 2>&1; do
    echo "Waiting for files to be generated..."
    sleep 10
done

# Run Python script to merge CSV files
echo $process_count

# Run Python script to merge CSV files with user input
python3 ../scripts/csv_merger.py $process_count

# Navigate to the 'ui' directory
cd ../src/ui

# Set Flask app environment variable
export FLASK_APP=app.py

# Run Flask application
flask run &

# Wait for Flask to start
sleep 20

# Navigate back to the 'scripts' directory
cd ../../scripts

# Run the Python script to delete unwanted files again
python3 delete_files.py
