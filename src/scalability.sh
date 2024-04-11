#!/bin/bash

# Example for running the application with 1 to 8 processes
for num_procs in {1..5}
do
    echo "Running with ${num_procs} processes:"
    mpiexec -n ${num_procs} ./my_program
done