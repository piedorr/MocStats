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
from itertools import chain

with open("output.csv", 'r', encoding='UTF8') as f:
    reader = csv.reader(f, delimiter=',')
    headers = next(reader)
    data = np.array(list(reader))

with open("data/moc.csv", 'r', encoding='UTF8') as f:
    reader = csv.reader(f, delimiter=',')
    headers = next(reader)
    spiral = np.array(list(reader))

with open("data/all.csv", 'r', encoding='UTF8') as f:
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
    if spiral_row[0] not in spiral_rows:
        spiral_rows[spiral_row[0]] = set()
    spiral_rows[spiral_row[0]].update([spiral_row[5], spiral_row[6], spiral_row[7], spiral_row[8]])

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
        "sample_size": 0
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
        "break_sub": 0
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
        "break_sub": 0
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
for row in data:
    # if (row[2].isnumeric()):
    #     row.insert(2,"Nilou")
    if row[0] != uid:
        uid = row[0]
        ar+=int(row[1])
        count+=1
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
        if row[2] in spiral_rows[row[0]] or ("Trailblazer" in spiral_rows[row[0]] and "Trailblazer" in row[2]):
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
            elif stat != "name" and stat != "sample_size":
                if stat in ["char_lvl", "light_cone_lvl", "attack_lvl", "skill_lvl", "ultimate_lvl", "talent_lvl", "max_hp", "atk", "dfns", "speed"]:
                    median[char][stat] = round(statistics.median(stats[char][stat]), 2)
                    mean[char][stat] = round(statistics.mean(stats[char][stat]), 2)
                else:
                    median[char][stat] = round(statistics.median(stats[char][stat]), 4)
                    mean[char][stat] = round(statistics.mean(stats[char][stat]), 4)
                if (mean[char][stat] > 0 and median[char][stat] > 0 and stats[char]["sample_size"] > 5):
                    if stat not in ["char_lvl", "light_cone_lvl", "attack_lvl", "skill_lvl", "ultimate_lvl", "talent_lvl", "energy_regen", "dmg_boost"]:
                        skewness = round(skew(stats[char][stat], axis=0, bias=True), 2)
                if skewness > 1:
                    stats[char][stat] = str(median[char][stat])
                    # print(skewness)
                    # print(stat + ": " + str(mean[char][stat]) + ", " + str(median[char][stat]))
                    # try:
                    #     plt.hist(stats[char][stat])
                    #     plt.show()
                    # except Exception:
                    #     pass
                    # # print("1 - Mean, 2 - Median: ")
                    # with keyboard.Events() as events:
                    #     event = events.get(1e6)
                    #     if event.key == keyboard.KeyCode.from_char('1'):
                    #         stats[char][stat] = str(mean[char][stat])
                    #     else:
                    #         stats[char][stat] = str(median[char][stat])
                else:
                    stats[char][stat] = str(mean[char][stat])

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
        del stats[char]
        chars.remove(char)

csv_writer = csv.writer(open("results/chars.csv", 'w', newline=''))
csv_writer.writerow(stats[chars[0]].keys())
csv_writer2 = csv.writer(open("results/demographic.csv", 'w', newline=''))
for char in chars:
    csv_writer.writerow(stats[char].values())
    csv_writer2.writerow([char + ": " + str(stats[char]["sample_size"])])

print("Average AR: ", (ar/count))