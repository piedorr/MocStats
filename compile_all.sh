#!/bin/bash

set -e # Stop on error

cd mihomo
python combine.py
cd ../Comps
python combine_raw_chars.py
python hash.py

# cd Comps

echo ""
echo "MoC"
python comp_rates.py -w &
python comp_rates.py -f &
python comp_rates.py -a
echo ""
echo "Move MoC"
python move.py

echo ""
echo "PF"
python comp_rates.py -w -pf &
python comp_rates.py -f -pf &
python comp_rates.py -a -pf
echo ""
echo "Move PF"
python move.py -pf

echo ""
echo "AS"
python comp_rates.py -w -as &
python comp_rates.py -f -as &
python comp_rates.py -a -as
echo ""
echo "Move AS"
python move.py -as

echo ""
echo "MoC stats"
cd ../mihomo
python stats.py
cd ../Comps
python move.py
python combine_char.py
python copyfiles.py

echo ""
echo "PF stats"
cd ../mihomo
python stats.py -pf
cd ../Comps
python move.py -pf
python combine_char.py -pf
python copyfiles.py -pf

echo ""
echo "AS stats"
cd ../mihomo
python stats.py -as
cd ../Comps
python move.py -as
python combine_char.py -as
python copyfiles.py -as