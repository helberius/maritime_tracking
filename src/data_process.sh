#!/bin/bash

pythonScript="/maritime_tracking/src/data_process/data_process.py"
dataSource="/maritime_tracking/src/configuration/data_processor.json"
echo $pythonScript
echo $dataSource
python $pythonScript $dataSource