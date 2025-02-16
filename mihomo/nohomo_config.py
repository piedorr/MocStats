import csv
import json
import os.path
import sys

sys.path.append("../Comps/")
from comp_rates_config import (
    RECENT_PHASE,
    skew_num,
    pf_mode,
    as_mode,
    run_chars_name,
    run_all_chars,
)

skip_self = False
skip_random = False
print_chart = False
# as: pf True
# pf_mode = True
# as_mode = False

# stats.py
# comp_stats = ['Bailu', 'Jing Yuan', 'Tingyun', 'Yukong']
comp_stats = []
check_char = True
check_char_name = "Yanqing"
# check_stats = ["cvalue"]
check_stats = []


phase_num = RECENT_PHASE
if as_mode:
    phase_num = phase_num + "_as"
elif pf_mode:
    phase_num = phase_num + "_pf"

f = open("../data/relics.json")
relics_data = json.load(f)

f = open("../data/characters.json")
characters = json.load(f)

trailblazer_ids = []
for char_name, char in characters.items():
    if "trailblazer_ids" in char:
        for trailblazer_id in char["trailblazer_ids"]:
            trailblazer_ids.append(trailblazer_id)

if os.path.exists("../char_results/uids.csv"):
    with open("../char_results/uids.csv", "r", encoding="UTF8") as f:
        reader = csv.reader(f, delimiter=",")
        uids = list(reader)
        uids = [int(uid[0]) for uid in uids]
        uids = list(dict.fromkeys(uids))
        # uids = uids[uids.index({uid})+1:]
else:
    uids = [806411333]

filenum = 1
while os.path.exists("output" + str(filenum) + ".csv"):
    filenum += 1
filename = "output" + str(filenum)
