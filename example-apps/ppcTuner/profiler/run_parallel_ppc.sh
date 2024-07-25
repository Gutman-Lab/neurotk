#!/bin/bash
number_jobs=6
doit() {
    id=$1
    /home/candano/miniconda3/envs/ppctuner/bin/python3.10 get_image.py -t wsi -id $id
}

export -f doit

# Measure the time taken to run the parallel command
start_time=$(date +%s)

# Run in parallel
parallel -j $number_jobs doit :::: id.txt &

# Get the PID of the parallel process
parallel_pid=$!

# Monitor CPU usage of the Python process and its threads
pidstat -t -p $parallel_pid 1 > results/cpu_usage.txt &

# Monitor load average for each CPU and save it every minute
mpstat -P ALL 60 > results/load_average_$(date +%Y%m%d_%H%M%S).txt &

# Wait for the parallel process to finish
wait $parallel_pid

end_time=$(date +%s)
execution_time=$((end_time - start_time))

# Save the execution time to a text file
echo "Execution time: $execution_time seconds" > results/execution_time.txt

echo "Execution time saved to execution_time.txt"
echo "CPU usage data saved to cpu_usage.txt"
echo "Load average data saved to results/load-average/load_average_$(date +%Y%m%d_%H%M%S).txt"


