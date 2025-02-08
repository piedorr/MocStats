#!/bin/bash

set -e # Stop on error

cd mihomo
python combine.py
cd ../Comps
python combine_raw_chars.py
python hash.py &
python comp_rates.py -w &
python comp_rates.py -f &
python comp_rates.py -a

cd ../mihomo
python stats.py
cd ../Comps
python move.py
python combine_char.py