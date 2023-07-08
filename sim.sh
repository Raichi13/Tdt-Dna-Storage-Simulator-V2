#! /bin/bash

. venv/bin/activate

python simulation.py -p sim12.csv

python simulation.py -p sim14.csv

python simulation.py -p sim15.csv

python simulation.py -p sim16.csv

python simulation.py -p sim17.csv

cd ../

deactivate
