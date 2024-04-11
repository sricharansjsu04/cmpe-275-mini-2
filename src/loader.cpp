#include <algorithm>
#include <fstream>
#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <unordered_map>
#include "logger.h"
#include <omp.h> // Include OpenMP for parallel processing
#include <mpi.h>

void processRecords(std::vector<std::string>& records, int rank) {
    int numRecords = records.size();
    std::vector<std::string> updatedRecords(numRecords);

    std::ostringstream msg;
    double processStartTime = MPI_Wtime();  // Start timing

    msg << "Starting time of processRecords: " << processStartTime * 1000 << " milliseconds.";
    logMessage(msg.str(), rank);
    msg.str("");

    msg << "Starting to process records in parallel. Total records: " << numRecords;
    logMessage(msg.str(), rank);
    msg.str("");

    // Define the indices of the columns to be dropped
    std::vector<int> columnsToDrop = { 12 };

    std::unordered_map<int, int> recordsPerMillisecondGlobal;

    #pragma omp parallel
    {
        std::unordered_map<int, int> recordsPerMillisecondLocal; // Thread-local metrics collection

        #pragma omp for nowait
        for (int i = 0; i < numRecords; ++i) {
            std::stringstream ss(records[i]);
            std::string token;
            std::vector<std::string> fields;
            
            // Split record into fields
            while (getline(ss, token, ',')) {
                fields.push_back(token);
            }
            
            // Prepare to reconstruct the record without dropped columns
            std::string reconstructedRecord;
            for (size_t j = 0; j < fields.size(); ++j) {
                // Skip columns marked to be dropped
                if (std::find(columnsToDrop.begin(), columnsToDrop.end(), static_cast<int>(j)) != columnsToDrop.end()) {
                    continue;
                }

                // Append "NULL" for empty fields except for columns to be dropped
                std::string fieldValue = fields[j].empty() ? "NULL" : fields[j];

                // Construct the updated record
                if (!reconstructedRecord.empty()) {
                    reconstructedRecord += ",";
                }
                reconstructedRecord += fieldValue;
            }

            updatedRecords[i] = reconstructedRecord;

            // Metrics collection
            double currentTime = MPI_Wtime(); // Current time in seconds
            int elapsedMilliseconds = static_cast<int>(currentTime - processStartTime); 
            recordsPerMillisecondLocal[elapsedMilliseconds]++;
        }

        // Combine local metrics into a global structure
        #pragma omp critical
        {
            for (auto& pair : recordsPerMillisecondLocal) {
                recordsPerMillisecondGlobal[pair.first] += pair.second;
            }
        }
    }

    records.swap(updatedRecords); // Update original records with processed ones

    // Export the cleaned data to a CSV file
    std::ofstream outputFile("../data/cleaned_data_rank_" + std::to_string(rank) + ".csv");
    if (outputFile.is_open()) {
        for (const auto& record : records) {
            outputFile << record << std::endl;
        }
        outputFile.close();
        msg.str("");
        msg << "Cleaned data exported to CSV file for rank: " + std::to_string(rank);
        logMessage(msg.str(), rank);
    } else {
        msg.str("");
        msg << "Failed to open CSV file for writing for rank: " + std::to_string(rank);
        logMessage(msg.str(), rank);
    }

    // Output metrics to a file
    std::ofstream metricsFile("../data/records_per_second_process_" + std::to_string(rank) + ".csv");
    if (!metricsFile) {
        std::cerr << "Failed to open metrics file for writing." << std::endl;
        return;
    }

    metricsFile << "Seconds,RecordsProcessed\n";
    for (const auto& pair : recordsPerMillisecondGlobal) {
        metricsFile << pair.first << "," << pair.second << "\n";
    }

    metricsFile.close();

    msg.str("");
    msg << "Finished processing records in parallel. Total records processed: " << numRecords;
    logMessage(msg.str(), rank);

    // Log the end of processing
    double processEndTime = MPI_Wtime();  // End timing
    double processTime = processEndTime - processStartTime;

    msg.str("");
    msg<< "Ending time of processRecords: " << processEndTime * 1000 << " millisecondsseconds.";
    logMessage(msg.str(), rank);
    msg.str("");
    msg << "Process " << rank << " processing time: " << processTime << " seconds.";
    logMessage(msg.str(), rank);
}
