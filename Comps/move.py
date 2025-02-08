import sys
from os import listdir, path, mkdir
import shutil

sys.path.append("../Comps/")
from comp_rates_config import RECENT_PHASE, as_mode, pf_mode

if as_mode:
    RECENT_PHASE_PF = RECENT_PHASE + "_as"
elif pf_mode:
    RECENT_PHASE_PF = RECENT_PHASE + "_pf"
else:
    RECENT_PHASE_PF = RECENT_PHASE

source_dirs = [
    "../char_results",
    "../comp_results",
    "../comp_results/json",
    "../mihomo",
    "../mihomo/results_real",
]

for source_dir in source_dirs:
    if source_dir == "../comp_results/json":
        target_dir = "../comp_results/" + RECENT_PHASE_PF + "/json"
    elif source_dir == "../mihomo":
        target_dir = "../mihomo/results_real"
    elif source_dir == "../mihomo/results_real":
        target_dir = source_dir + "/" + RECENT_PHASE
    else:
        target_dir = source_dir + "/" + RECENT_PHASE_PF

    file_names = listdir(source_dir)
    if not path.exists(target_dir):
        mkdir(target_dir)
    for file_name in file_names:
        if (source_dir == "../mihomo" and file_name.startswith("output")) or (
            source_dir != "../mihomo" and file_name.endswith(tuple([".json", ".csv"]))
        ):
            shutil.move(path.join(source_dir, file_name), target_dir)
