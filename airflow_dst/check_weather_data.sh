#!/bin/bash

# Script to check weather data collection progress
echo "=== Weather Data Collection Status ==="

docker exec -it airflow_dst_airflow-worker_1 bash -c "
echo 'Raw files directory:'
ls -la /app/raw_files/ | grep -E '\.json$' | wc -l | xargs echo 'Total JSON files:'

echo ''
echo 'Latest files:'
ls -lt /app/raw_files/*.json 2>/dev/null | head -5

echo ''
echo 'Total observations:'
python3 -c '
import json
import glob
total = 0
files = glob.glob(\"/app/raw_files/*.json\")
for file in files:
    with open(file) as f:
        data = json.load(f)
        total += len(data)
print(f\"Total observations: {total}\")
print(f\"Files processed: {len(files)}\")
if total >= 15:
    print(\"✓ Ready for ML pipeline!\")
else:
    print(f\"Need {15-total} more observations\")
'
"
