#include "logger.h"
#include <fstream>
#include <sstream>
#include <iostream>

void logMessage(const std::string& message, int rank) {
    std::ostringstream filename;
    filename << "../logs/log_process_" << rank << ".txt";
    std::ofstream logFile(filename.str(), std::ios::app);
    if (logFile.is_open()) {
        logFile << message << std::endl;
        logFile.close();
    } else {
        std::cerr << "Failed to open log file for process " << rank << std::endl;
    }
}

// Implement the new function
void logMetrics(double startTime, double endTime, int recordsProcessed, int rank) {
    std::ostringstream filename;
    filename << "metrics_process_" << rank << ".txt"; // Separate file for metrics
    std::ofstream metricsFile(filename.str(), std::ios::app);
    if (metricsFile.is_open()) {
        double duration = endTime - startTime;
        double recordsPerSecond = recordsProcessed / duration;
        metricsFile << "Duration: " << duration << "s, Records Per Second: " << recordsPerSecond << std::endl;
        metricsFile.close();
    } else {
        std::cerr << "Failed to open metrics file for process " << rank << std::endl;
    }
}
