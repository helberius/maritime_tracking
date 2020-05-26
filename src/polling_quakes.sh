#!/bin/bash

pythonScript="/maritime_tracking/src/polling_proxy/polling_proxy.py"
dataSource="/maritime_tracking/src/configuration/usgs_quakes_all_hour.json"
echo $pythonScript
echo $dataSource
python $pythonScript $dataSource