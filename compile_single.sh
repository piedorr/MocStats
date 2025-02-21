#!/bin/bash

set -e # Stop on error

cd Comps
python comp_rates.py -w &
python comp_rates.py -f &
python comp_rates.py -a

cd ../mihomo
python stats.py
cd ../Comps
python move.py
python combine_char.py