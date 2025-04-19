# MocStats

Compile Memory of Chaos data using Python.

You can find the raw data in the `data/raw_csvs` folder. Feel free to analyze the data and post the findings. If you do, please credit me (LvlUrArti).

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Q5Q4IJ3P6)

# How to use

Change past and recent phase in `Comps/comp_rates_config.py`

If collecting new builds data:

- In `Comps` folder:
  - `python comp_rates.py -t`
- In `enka.network` folder:
  - `pip install -U enka`
  - `python enkanetwork.py`

If using past data:

- Copy `mihomo/results/{version}_output.csv` to `mihomo/output1.csv`

After done scanning:

- `sh compile_all.sh`
