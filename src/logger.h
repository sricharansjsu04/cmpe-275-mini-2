#ifndef LOGGER_H
#define LOGGER_H

#include <string>

void logMessage(const std::string& message, int rank);
void logMetrics(double startTime, double endTime, int recordsProcessed, int rank); // Add this line

#endif // LOGGER_H