import sys
sys.path.append('../Comps/')

import os
import numpy as np
import operator
import csv
import statistics
import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import skew
from pynput import keyboard
from nohomo_config import phase_num

with open("output1.csv", 'r') as f:
    reader = csv.reader(f, delimiter=',')
    headers = next(reader)
    data = np.array(list(reader))

if os.path.exists("../data/raw_csvs_real/"):
    f = open("../data/raw_csvs_real/" + phase_num + ".csv", 'r')
else:
    f = open("../data/raw_csvs/" + phase_num + ".csv", 'r')
reader = csv.reader(f, delimiter=',')
headers = next(reader)
spiral = list(reader)

with open("../char_results/all.csv", 'r') as f:
    reader = csv.reader(f, delimiter=',')
    headers = next(reader)
    build = np.array(list(reader))

archetype = "all"

# chars = []
# for row in build:
#     chars.append(row[0])
chars = ["Lynx"]
stats = {}
median = {}
mean = {}
sample = {}
weapons = {}
copy_weapons = {}

spiral_rows = {}
for spiral_row in spiral:
    if spiral_row[0] not in spiral_rows:
        spiral_rows[spiral_row[0]] = set()
    spiral_rows[spiral_row[0]].update([spiral_row[5], spiral_row[6], spiral_row[7], spiral_row[8]])

for char in chars:
    stats[char] = {}
    median[char] = {}
    mean[char] = {}
    sample[char] = {}
    weapons[char] = []

    for row in build:
        if row[0] == char:
            for j in range (6,33,3):
                if row[j+1]!="-":
                    weapons[char].append(row[j])
                    stats[char][row[j]] = {
                        "name": row[j],
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
                        "break_effect": []
                    }
                    median[char][row[j]] = {
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
                        "break_effect": 0
                    }
                    mean[char][row[j]] = {
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
                        "break_effect": 0
                    }
                    sample[char][row[j]] = 0
            break

statkeys = list(stats[chars[0]][weapons[chars[0]][0]].keys())

for row in data:
    # if (row[2].isnumeric()):
    #     row.insert(2,"Nilou")
    if "Dan Heng â€¢ Imbibitor Lunae" in row[2]:
        row[2] = "Dan Heng • Imbibitor Lunae"
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
    # if row[2] == char and float(row[13]) < 100: #EM < 100
        # for chars_row in chars:
        #     if chars_row[2] == "Traveler":
        #         if chars_row[3] == "Geo":
        #             chars_row[2] = "Traveler-G"
        #         elif chars_row[3] == "Anemo":
        #             chars_row[2] = "Traveler-A"
        #         elif chars_row[3] == "Electro":
        #             chars_row[2] = "Traveler-E"
        #         elif chars_row[3] == "Dendro":
        #             chars_row[2] = "Traveler-D"
        #     # if spiral_row[0] == chars_row[0] and chars_row[2] == char:
        #     if row[0] == chars_row[0] and chars_row[2] == char:
    if row[2] in chars:
        found = False
        if row[0] in spiral_rows:
            if row[2] in spiral_rows[row[0]] or ("Trailblazer" in spiral_rows[row[0]] and "Trailblazer" in row[2]):
                found = True
            # for char in spiral_rows[row[0]]:
            #     if char in ["Thoma","Yoimiya","Yanfei","Hu Tao","Xinyan","Diluc","Amber","Xiangling","Klee","Bennett","Dehya"]:
            #         foundPyro = True
            if found:
                # if row[5] not in weapons:
                #     weapons.append(row[5])
                #     stats[row[2]][row[5]] = {
                #         "name": row[5],
                #         "attack_lvl": [],
                #         "skill_lvl": [],
                #         "burst_lvl": [],
                #         "max_hp": [],
                #         "atk": [],
                #         "dfns": [],
                #         "crate": [],
                #         "cdmg": [],
                #         "charge": [],
                #         "heal": [],
                #         "em": [],
                #         "phys": [],
                #         "pyro": [],
                #         "electro": [],
                #         "hydro": [],
                #         "dendro": [],
                #         "anemo": [],
                #         "geo": [],
                #         "cryo": []
                #     }
                #     median[char][row[5]] = {
                #         "name": row[5],
                #         "attack_lvl": 0,
                #         "skill_lvl": 0,
                #         "burst_lvl": 0,
                #         "max_hp": 0,
                #         "atk": 0,
                #         "dfns": 0,
                #         "crate": 0,
                #         "cdmg": 0,
                #         "charge": 0,
                #         "heal": 0,
                #         "em": 0,
                #         "phys": 0,
                #         "pyro": 0,
                #         "electro": 0,
                #         "hydro": 0,
                #         "dendro": 0,
                #         "anemo": 0,
                #         "geo": 0,
                #         "cryo": 0
                #     }
                #     mean[char][row[5]] = {
                #         "name": row[5],
                #         "attack_lvl": 0,
                #         "skill_lvl": 0,
                #         "burst_lvl": 0,
                #         "max_hp": 0,
                #         "atk": 0,
                #         "dfns": 0,
                #         "crate": 0,
                #         "cdmg": 0,
                #         "charge": 0,
                #         "heal": 0,
                #         "em": 0,
                #         "phys": 0,
                #         "pyro": 0,
                #         "electro": 0,
                #         "hydro": 0,
                #         "dendro": 0,
                #         "anemo": 0,
                #         "geo": 0,
                #         "cryo": 0
                #     }
                #     sample[row[2]][row[5]] = 0
                if row[5] in weapons[row[2]]:
                    sample[row[2]][row[5]] += 1
                    stats[row[2]][row[5]]["char_lvl"].append(float(row[3]))
                    if (row[6].isnumeric()):
                        stats[row[2]][row[5]]["light_cone_lvl"].append(float(row[6]))
                    for i in range(3,11):
                        stats[row[2]][row[5]][statkeys[i]].append(float(row[i+4]))
                    for i in range(11,19):
                        stats[row[2]][row[5]][statkeys[i]].append(float(row[i+4])/100)

for char in chars:
    copy_weapons[char] = weapons[char].copy()
    for weapon in copy_weapons[char]:
        if sample[char][weapon] > 0:
            # print()
            # print(weapon + ": " + str(sample[char][weapon]))
            for stat in stats[char][weapon]:
                skewness = 0
                if stat not in ["name"]:
                    if stat in ["char_lvl", "light_cone_lvl", "attack_lvl", "skill_lvl", "ultimate_lvl", "talent_lvl", "max_hp", "atk", "dfns", "speed"]:
                        median[char][weapon][stat] = round(statistics.median(stats[char][weapon][stat]), 2)
                        mean[char][weapon][stat] = round(statistics.mean(stats[char][weapon][stat]), 2)
                    else:
                        median[char][weapon][stat] = round(statistics.median(stats[char][weapon][stat]), 4)
                        mean[char][weapon][stat] = round(statistics.mean(stats[char][weapon][stat]), 4)
                    if (mean[char][weapon][stat] > 0 and median[char][weapon][stat] > 0 and sample[char][weapon] > 5):
                        if stat not in ["char_lvl", "light_cone_lvl", "attack_lvl", "skill_lvl", "ultimate_lvl", "talent_lvl", "energy_regen", "dmg_boost"]:
                            skewness = round(skew(stats[char][weapon][stat], axis=0, bias=True), 2)
                    if skewness > 1:
                        stats[char][weapon][stat] = str(median[char][weapon][stat])
                        # print(stat + ": " + str(mean[char][weapon][stat]) + ", " + str(median[char][weapon][stat]))
                        # try:
                        #     plt.hist(stats[char][weapon][stat])
                        #     plt.show()
                        # except Exception:
                        #     pass
                        # # print("1 - Mean, 2 - Median: ")
                        # with keyboard.Events() as events:
                        #     event = events.get(1e6)
                        #     if event.key == keyboard.KeyCode.from_char('1'):
                        #         stats[char][weapon][stat] = str(mean[char][weapon][stat])
                        #     else:
                        #         stats[char][weapon][stat] = str(median[char][weapon][stat])
                    else:
                        stats[char][weapon][stat] = str(mean[char][weapon][stat])
        else:
            del stats[char][weapon]
            weapons[char].remove(weapon)

    print()
    print()
    if os.path.exists("results_real"):
        csv_writer = csv.writer(open("results_real/" + char + "_weapons.csv", 'w', newline=''))
    else:
        csv_writer = csv.writer(open("results/" + char + "_weapons.csv", 'w', newline=''))
    csv_writer.writerow(stats[char][weapons[char][0]].keys())
    for weapon in weapons[char]:
        print(weapon + ": " + str(sample[char][weapon]))
        csv_writer.writerow(stats[char][weapon].values())
