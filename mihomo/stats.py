import sys
sys.path.append('../Comps/')

import os.path
import numpy as np
import operator
import csv
import json
import statistics
import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import skew
from pynput import keyboard
from itertools import chain
from archetypes import *
from nohomo_config import *

with open("output1.csv", 'r') as f:
    reader = csv.reader(f, delimiter=',')
    headers = next(reader)
    data = np.array(list(reader))

# lastuid = ""
# for i in data:
#     if i[0] != lastuid:
#         lastuid = i[0]
#         print(i[0])
# exit()

pf_filename = ""
if pf_mode:
    pf_filename = "_pf"

if os.path.exists("../data/raw_csvs_real/"):
    f = open("../data/raw_csvs_real/" + phase_num + pf_filename + ".csv", 'r')
else:
    f = open("../data/raw_csvs/" + phase_num + pf_filename + ".csv", 'r')
reader = csv.reader(f, delimiter=',')
headers = next(reader)
spiral = list(reader)

with open("../char_results/all.csv", 'r') as f:
    reader = csv.reader(f, delimiter=',')
    headers = next(reader)
    build = np.array(list(reader))

archetype = "all"

chars = []
stats = {}
median = {}
mean = {}
mainstats = {}
substats = {}

spiral_rows = {}
for spiral_row in spiral:
    if int(''.join(filter(str.isdigit, spiral_row[1]))) > 9 or (pf_mode and int(''.join(filter(str.isdigit, spiral_row[1]))) > 3):
        if spiral_row[0] not in spiral_rows:
            spiral_rows[spiral_row[0]] = {}
        # if comp_stats:
        #     spiral_temp = []
        #     for i in range(5,9):
        #         spiral_temp.append(spiral_row[i])
        #     spiral_temp.sort()
        #     if spiral_temp != ['Bailu', 'Jing Yuan', 'Tingyun', 'Yukong']:
        #         continue
        for i in range(5,9):
            if "Dan Heng â€¢ Imbibitor Lunae" in spiral_row[i]:
                spiral_row[i] = "Dan Heng • Imbibitor Lunae"
            if "Topaz and Numby" in spiral_row[i]:
                spiral_row[i] = "Topaz & Numby"
            if spiral_row[i] not in spiral_rows[spiral_row[0]]:
                spiral_rows[spiral_row[0]][spiral_row[i]] = 1
            else:
                spiral_rows[spiral_row[0]][spiral_row[i]] += 1

for row in build:
    chars.append(row[0])

for char in chars:
    stats[char] = {
        "name": char,
        "char_lvl": [],
        "light_cone_lvl": [],
        "attack_lvl": [],
        "skill_lvl": [],
        "ultimate_lvl": [],
        "talent_lvl": [],
        "max_hp": [],
        "atk": [],
        "dfns": [],
        "speed": [],
        "crate": [],
        "cdmg": [],
        "dmg_boost": [],
        "heal_boost": [],
        "energy_regen": [],
        "effect_res": [],
        "effect_rate": [],
        "break_effect": [],
        "spd_sub": [],
        "hp_sub": [],
        "atk_sub": [],
        "def_sub": [],
        "crate_sub": [],
        "cdmg_sub": [],
        "res_sub": [],
        "ehr_sub": [],
        "break_sub": [],
        # "cvalue": [],
        "sample_size": 0,
        "sample_size_players": 0
    }
    mean[char] = {
        "char_lvl": 0,
        "light_cone_lvl": 0,
        "attack_lvl": 0,
        "skill_lvl": 0,
        "ultimate_lvl": 0,
        "talent_lvl": 0,
        "max_hp": 0,
        "atk": 0,
        "dfns": 0,
        "speed": 0,
        "crate": 0,
        "cdmg": 0,
        "dmg_boost": 0,
        "heal_boost": 0,
        "energy_regen": 0,
        "effect_res": 0,
        "effect_rate": 0,
        "break_effect": 0,
        "spd_sub": 0,
        "hp_sub": 0,
        "atk_sub": 0,
        "def_sub": 0,
        "crate_sub": 0,
        "cdmg_sub": 0,
        "res_sub": 0,
        "ehr_sub": 0,
        "break_sub": 0,
        # "cvalue": 0,
    }
    median[char] = {
        "char_lvl": 0,
        "light_cone_lvl": 0,
        "attack_lvl": 0,
        "skill_lvl": 0,
        "ultimate_lvl": 0,
        "talent_lvl": 0,
        "max_hp": 0,
        "atk": 0,
        "dfns": 0,
        "speed": 0,
        "crate": 0,
        "cdmg": 0,
        "dmg_boost": 0,
        "heal_boost": 0,
        "energy_regen": 0,
        "effect_res": 0,
        "effect_rate": 0,
        "break_effect": 0,
        "spd_sub": 0,
        "hp_sub": 0,
        "atk_sub": 0,
        "def_sub": 0,
        "crate_sub": 0,
        "cdmg_sub": 0,
        "res_sub": 0,
        "ehr_sub": 0,
        "break_sub": 0,
        # "cvalue": 0,
    }
    mainstats[char] = {
        "body_stats": {},
        "feet_stats": {},
        "sphere_stats": {},
        "rope_stats": {}
    }
    substats[char] = {
        "spd_sub": 2.3,
        "hp_sub": 0.03888,
        "atk_sub": 0.03888,
        "def_sub": 0.0486,
        "crate_sub": 0.02916,
        "cdmg_sub": 0.05832,
        "res_sub": 0.03888,
        "ehr_sub": 0.03888,
        "break_sub": 0.05832
    }
ar = 0
count = 0
uid = 0
statkeys = list(stats[chars[0]].keys())
mainstatkeys = list(mainstats[chars[0]].keys())
substatkeys = list(substats[chars[0]].keys())

if os.path.isfile("../../uids.csv"):
    with open("../../uids.csv", 'r', encoding='UTF8') as f:
        reader = csv.reader(f, delimiter=',')
        self_uids = list(reader)[0]

for row in data:
    if skip_self and row[0] in self_uids:
        continue
    if skip_random and row[0] not in self_uids:
        continue
    # if (row[2].isnumeric()):
    #     row.insert(2,"Nilou")
    if row[0] != uid:
        uid = row[0]
        ar+=int(row[1])
        count+=1
    if row[2] not in chars:
        if "Dan Heng â€¢ Imbibitor Lunae" in row[2]:
            row[2] = "Dan Heng • Imbibitor Lunae"
        elif "Topaz and Numby" in row[2]:
            row[2] = "Topaz & Numby"
        elif "Trailblazer" in row[2]:
            row[2] = "Trailblazer"
        else:
            print(row[2])
            exit()
    if row[2] == "Trailblazer":
        match row[4]:
            case "Fire":
                row[2] = "Fire Trailblazer"
            case "Physical":
                row[2] = "Physical Trailblazer"
            case "Ice":
                row[2] = "Ice Trailblazer"
            case "Lightning":
                row[2] = "Lightning Trailblazer"
            case "Wind":
                row[2] = "Wind Trailblazer"
            case "Quantum":
                row[2] = "Quantum Trailblazer"
            case "Imaginary":
                row[2] = "Imaginary Trailblazer"
    # for char in chars:
    #     if row[2] == char:
            # elif row[4] == "None":
            #     row[2] = "Traveler-D"

            # found = False
            # for char_row in chardata:
            #     if char_row[0] == row[0] and not found:
            #         if char_row[2] == char and char_row[3] == "Dendro":
            #             found = True
    found = False
    if row[0] in spiral_rows:
        if row[2] in spiral_rows[row[0]] or (
            "Trailblazer" in spiral_rows[row[0]] and "Trailblazer" in row[2]
        ):
            found = True
        # for char in spiral_rows[row[0]]:
        #     if char in ["Thoma","Yoimiya","Yanfei","Hu Tao","Xinyan","Diluc","Amber","Xiangling","Klee","Bennett","Dehya"]:
        #         foundPyro = True
        # if found and char_arti == "Gilded Dreams":
        # if found and ((float(row[9]) * 2) + float(row[10]) > 1.8 and float(row[18]) > 0.4):

        # isValidChar = False
        # match archetype:
        #     # case "melt":
        #     #     if found and foundPyro:
        #     #         isValidChar = True
        #     case _:
        if found:
        #     isValidChar = True
        # # if found and foundDendro and foundHydro: # Hyperbloom
        # # if found and foundDendro and not foundHydro: # Aggravate/Spread
        # if isValidChar:
            stats[row[2]]["sample_size_players"] += 1
            for i in range(spiral_rows[row[0]][row[2]]):
                stats[row[2]]["char_lvl"].append(float(row[3]))
                stats[row[2]]["sample_size"] += 1
                stats[row[2]]["spd_sub"].append(float(row[23]))
                if (row[6].isnumeric()):
                    stats[row[2]]["light_cone_lvl"].append(float(row[6]))
                for i in range(3,11):
                    stats[row[2]][statkeys[i]].append(float(row[i+4]))
                for i in chain(range(11,19), range(20,28)):
                    stats[row[2]][statkeys[i]].append(float(row[i+4])/100)
                for i in range(4):
                    if row[i+32] in mainstats[row[2]][mainstatkeys[i]]:
                        mainstats[row[2]][mainstatkeys[i]][row[i+32]] += 1
                    else:
                        mainstats[row[2]][mainstatkeys[i]][row[i+32]] = 1
                # stats[row[2]]["cvalue"].append(stats[row[2]]["crate"][-1] * 2 + stats[row[2]]["cdmg"][-1])

                # if char_arti in artifacts[char]:
                #     artifacts[char][char_arti] += 1
                # else:
                #     artifacts[char][char_arti] = 1
copy_chars = chars.copy()
for char in copy_chars:
    # print(artifacts[char])
    if stats[char]["sample_size"] > 0:
        # print(char + ": " + str(stats[char]["sample_size"]))
        # print()
        for stat in stats[char]:
            skewness = 0
            if not stats[char][stat]:
                stats[char][stat] = 0
            elif stat != "name" and "sample_size" not in stat:
                if stat in ["char_lvl", "light_cone_lvl", "attack_lvl", "skill_lvl", "ultimate_lvl", "talent_lvl", "max_hp", "atk", "dfns", "speed"]:
                    median[char][stat] = round(statistics.median(stats[char][stat]), 2)
                    mean[char][stat] = round(statistics.mean(stats[char][stat]), 2)
                else:
                    median[char][stat] = round(statistics.median(stats[char][stat]), 4)
                    mean[char][stat] = round(statistics.mean(stats[char][stat]), 4)
                if (mean[char][stat] > 0 and median[char][stat] > 0 and stats[char]["sample_size"] > 5):
                    if stat not in ["char_lvl", "light_cone_lvl", "attack_lvl", "skill_lvl", "ultimate_lvl", "talent_lvl", "energy_regen", "dmg_boost"]:
                        skewness = round(skew(stats[char][stat], axis=0, bias=True), 2)
                if abs(skewness) > skew_num:
                    if print_chart:
                        if (not(check_char) or char == check_char_name) and stat in check_stats:
                            print("skewness: " + str(skewness))
                            print(stat + ": " + str(mean[char][stat]) + ", " + str(median[char][stat]))
                            try:
                                plt.hist(stats[char][stat])
                                plt.show()
                            except Exception:
                                pass
                            # print("1 - Mean, 2 - Median: ")
                            with keyboard.Events() as events:
                                event = events.get(1e6)
                                if event.key == keyboard.KeyCode.from_char('1'):
                                    stats[char][stat] = str(mean[char][stat])
                                else:
                                    stats[char][stat] = str(median[char][stat])
                        else:
                            stats[char][stat] = median[char][stat]
                    else:
                        stats[char][stat] = median[char][stat]
                else:
                    stats[char][stat] = mean[char][stat]

        for stat in mainstats[char]:
            sorted_stats = (sorted(
                mainstats[char][stat].items(),
                key = operator.itemgetter(1),
                reverse=True
            ))
            mainstats[char][stat] = {k: v for k, v in sorted_stats}
            for mainstat in mainstats[char][stat]:
                mainstats[char][stat][mainstat] = round(
                    mainstats[char][stat][mainstat] / stats[char]["sample_size"], 4
                )
            mainstatlist = list(mainstats[char][stat])
            i = 0
            while i < 3:
                if i >= len(mainstatlist):
                    stats[char][stat + "_" + str(i+1)] = "-"
                    stats[char][stat + "_" + str(i+1) + "_app"] = "-"
                else:
                    stats[char][stat + "_" + str(i+1)] = mainstatlist[i]
                    stats[char][stat + "_" + str(i+1) + "_app"] = mainstats[char][stat][mainstatlist[i]]
                i += 1

        # for i in range(9):
        #     substats[char][substatkeys[i]] = float(stats[char][statkeys[i+19]]) / substats[char][substatkeys[i]]
        # sorted_stats = (sorted(
        #     substats[char].items(),
        #     key = operator.itemgetter(1),
        #     reverse=True
        # ))
        # substats[char] = {k: v for k, v in sorted_stats}
        # substatlist = list(substats[char])
        # for i in range(9):
        #     stats[char]["sub_" + str(i+1)] = substatlist[i]
        #     stats[char]["sub_" + str(i+1) + "_app"] = stats[char][substatlist[i]]
        #     del stats[char][substatlist[i]]

    else:
        for stat in stats[char]:
            if not stats[char][stat]:
                stats[char][stat] = 0
            elif stat != "name" and "sample_size" not in stat:
                stats[char][stat] = 0
        for stat in mainstats[char]:
            i = 0
            while i < 3:
                stats[char][stat + "_" + str(i+1)] = "-"
                stats[char][stat + "_" + str(i+1) + "_app"] = "-"
                i += 1

if os.path.exists("results_real"):
    file1 = open("results_real/chars.csv", 'w', newline='')
    file2 = open("results_real/demographic.csv", 'w', newline='')
else:
    file1 = open("results/chars.csv", 'w', newline='')
    file2 = open("results/demographic.csv", 'w', newline='')

csv_writer = csv.writer(file1)
csv_writer2 = csv.writer(file2)
del stats[chars[0]]["sample_size"]
csv_writer.writerow(stats[chars[0]].keys())
for char in chars:
    if char != chars[0]:
        del stats[char]["sample_size"]
    csv_writer.writerow(stats[char].values())
    csv_writer2.writerow([char + ": " + str(stats[char]["sample_size_players"])])

temp_stats = []
iter_char = 0
with open('../char_results/all.json') as char_file:
    CHARACTERS = json.load(char_file)
with open('../char_results/appearance_combine.json') as app_char_file:
    APP = json.load(app_char_file)
with open('../char_results/rounds_combine.json') as round_char_file:
    ROUND = json.load(round_char_file)
for char in stats:
    for i in chain(range(11,19), range(20,28)):
        stats[char][statkeys[i]] = round(stats[char][statkeys[i]] * 100, 2)
    iterate_value_app = []
    for i in range(3):
        iterate_value_app.append("body_stats_" + str(i + 1) + "_app")
        iterate_value_app.append("feet_stats_" + str(i + 1) + "_app")
        iterate_value_app.append("sphere_stats_" + str(i + 1) + "_app")
        iterate_value_app.append("rope_stats_" + str(i + 1) + "_app")
    for value in iterate_value_app:
        if isinstance(stats[char][value], float):
            stats[char][value] = round(stats[char][value] * 100, 2)
        else:
            stats[char][value] = 0.00

    if stats[char]["name"] == CHARACTERS[iter_char]["char"]:
        del stats[char]["name"]
    else:
        print(stats[char]["name"])
        print(CHARACTERS[iter_char]["char"])
        exit()

    app_dict = {}
    if not(pf_mode):
        app_dict = {
            "12_app": APP["12-1"]["4"][char]["app"],
            "12_round": ROUND["12-1"]["4"][char]["round"],
        }
    else:
        app_dict = {
            "4_app": APP["4-1"]["4"][char]["app"],
            "4_round": ROUND["4-1"]["4"][char]["round"],
        }
    temp_stats.append((CHARACTERS[iter_char] | stats[char]) | app_dict)
    # temp_stats.append((CHARACTERS[iter_char]) | app_dict)
    iter_char += 1
with open('../char_results/all2.json', 'w') as char_file:
    char_file.write(json.dumps(temp_stats,indent=2))

print("Average AR: ", (ar/count))
