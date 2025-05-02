import csv
import json
import operator
import os
import statistics
import sys
from itertools import chain

import numpy as np
from matplotlib.pyplot import hist as plt_hist  # type: ignore
from matplotlib.pyplot import show as plt_show  # type: ignore

sys.path.append("../Comps/")
from comp_rates_config import (
    skew_num,
)
from nohomo_config import (
    RECENT_PHASE,
    check_char,
    check_char_name,
    check_stats,
    pf_mode,
    phase_num,
    print_chart,
    skip_random,
    skip_self,
)
from pynput import keyboard
from scipy.stats import skew  # type: ignore

if os.path.exists("../data/raw_csvs_real/"):
    f = open("results_real/" + RECENT_PHASE + "/output1.csv")
else:
    f = open("results/" + RECENT_PHASE + "_output.csv")
reader = csv.reader(f, delimiter=",")
headers = next(reader)
data = np.array(list(reader))
f.close()

with open("../data/light_cones.json") as f:
    LIGHT_CONES = json.load(f)
with open("../Comps/prydwen-slug.json") as slug_file:
    slug = json.load(slug_file)

if os.path.exists("../data/raw_csvs_real/"):
    f = open("../data/raw_csvs_real/" + phase_num + ".csv")
else:
    f = open("../data/raw_csvs/" + phase_num + ".csv")
reader = csv.reader(f, delimiter=",")
headers = next(reader)
spiral = list(reader)
f.close()

with open("../char_results/" + phase_num + "/all.csv") as f:
    reader = csv.reader(f, delimiter=",")
    headers = next(reader)
    build = np.array(list(reader))

archetype = "all"


statkeys = [
    "char_lvl",
    "light_cone_lvl",
    "attack_lvl",
    "skill_lvl",
    "ultimate_lvl",
    "talent_lvl",
    "max_hp",
    "atk",
    "dfns",
    "speed",
    "crate",
    "cdmg",
    "dmg_boost",
    "heal_boost",
    "energy_regen",
    "effect_res",
    "effect_rate",
    "break_effect",
    "spd_sub",
    "hp_sub",
    "atk_sub",
    "def_sub",
    "crate_sub",
    "cdmg_sub",
    "res_sub",
    "ehr_sub",
    "break_sub",
]
substats = {
    "spd_sub": 2.3,
    "hp_sub": 0.03888,
    "atk_sub": 0.03888,
    "def_sub": 0.0486,
    "crate_sub": 0.02916,
    "cdmg_sub": 0.05832,
    "res_sub": 0.03888,
    "ehr_sub": 0.03888,
    "break_sub": 0.05832,
}


class StatsChar:
    def __init__(self, char: str) -> None:
        self.name = char
        self.stats_count: dict[str, list[float]] = {key: [] for key in statkeys}
        self.stats_write: dict[str, float | str] = {key: 0 for key in statkeys}
        self.sample_size = 0
        self.sample_size_players = 0


chars: list[str] = []
stats: dict[str, StatsChar] = {}
median: dict[str, dict[str, float]] = {}
mean: dict[str, dict[str, float]] = {}
mainstats: dict[str, dict[str, dict[str, float]]] = {}

spiral_rows: dict[str, dict[str, int]] = {}
for spiral_row in spiral:
    if (
        int("".join(filter(str.isdigit, spiral_row[1]))) > 11
        or (pf_mode and int("".join(filter(str.isdigit, spiral_row[1]))) > 3)
    ) and int(spiral_row[4]) == 3:
        if spiral_row[0] not in spiral_rows:
            spiral_rows[spiral_row[0]] = {}
        # if comp_stats:
        #     spiral_temp = []
        #     for i in range(5,9):
        #         spiral_temp.append(spiral_row[i])
        #     spiral_temp.sort()
        #     if spiral_temp != ['Bailu', 'Jing Yuan', 'Tingyun', 'Yukong']:
        #         continue
        for i in range(5, 9):
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
    stats[char] = StatsChar(char)
    mean[char] = {key: 0 for key in statkeys}
    median[char] = mean[char].copy()
    mainstats[char] = {
        "body_stats": {},
        "feet_stats": {},
        "sphere_stats": {},
        "rope_stats": {},
    }
ar = 0
count = 0
uid = 0
mainstatkeys: list[str] = list(mainstats[chars[0]].keys())
substatkeys: list[str] = list(substats.keys())

if os.path.isfile("../../uids.csv"):
    with open("../../uids.csv", encoding="UTF8") as f:
        reader = csv.reader(f, delimiter=",")
        self_uids = list(reader)[0]
else:
    self_uids = []

for row in data:
    char = row[2]
    cur_uid = row[0]
    if skip_self and cur_uid in self_uids:
        continue
    if skip_random and cur_uid not in self_uids:
        continue
    # if (char.isnumeric()):
    #     row.insert(2,"Nilou")
    if cur_uid != uid:
        uid = cur_uid
        ar += int(row[1])
        count += 1
    if char not in chars:
        if char in [
            "Dan Heng â€¢ Imbibitor Lunae",
            "Dan Heng Ã¢â‚¬Â¢ Imbibitor Lunae",
        ]:
            char = "Dan Heng • Imbibitor Lunae"
        elif "Topaz and Numby" in char:
            char = "Topaz & Numby"
        elif "Trailblazer" in char:
            char = "Trailblazer"
        elif "March 7th" in char:
            char = "March 7th"
        else:
            print(char)
            exit()
    if char == "Trailblazer" or char == "March 7th":
        match row[4]:
            case "Fire":
                char = "Fire " + char
            case "Physical":
                char = "Physical " + char
            case "Ice":
                char = "Ice " + char
            case "Lightning":
                char = "Lightning " + char
            case "Wind":
                char = "Wind " + char
            case "Quantum":
                char = "Quantum " + char
            case "Imaginary":
                char = "Imaginary " + char
            case _:
                pass
    # for char in chars:
    #     if char == char:
    # elif row[4] == "None":
    #     char = "Traveler-D"

    # found = False
    # for char_row in chardata:
    #     if char_row[0] == cur_uid and not found:
    #         if char_char == char and char_row[3] == "Dendro":
    #             found = True
    found = False
    if cur_uid in spiral_rows:
        if char in spiral_rows[cur_uid] or (
            "Trailblazer" in spiral_rows[cur_uid] and "Trailblazer" in char
        ):
            found = True

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
            stats[char].sample_size_players += 1
            for i in range(spiral_rows[cur_uid][char]):
                stats[char].stats_count["char_lvl"].append(float(row[3]))
                stats[char].sample_size += 1
                stats[char].stats_count["spd_sub"].append(float(row[23]))
                if row[6].isnumeric():
                    stats[char].stats_count["light_cone_lvl"].append(float(row[6]))
                for i in range(2, 10):
                    stats[char].stats_count[statkeys[i]].append(float(row[i + 5]))
                for i in chain(range(10, 18), range(19, 27)):
                    stats[char].stats_count[statkeys[i]].append(float(row[i + 5]) / 100)
                for i in range(4):
                    if row[i + 32] in mainstats[char][mainstatkeys[i]]:
                        mainstats[char][mainstatkeys[i]][row[i + 32]] += 1
                    else:
                        mainstats[char][mainstatkeys[i]][row[i + 32]] = 1

                # if char_arti in artifacts[char]:
                #     artifacts[char][char_arti] += 1
                # else:
                #     artifacts[char][char_arti] = 1
copy_chars = chars.copy()
for char in copy_chars:
    # print(artifacts[char])
    if stats[char].sample_size > 0:
        # print(char + ": " + str(stats[char].sample_size))
        # print()
        for stat in stats[char].stats_count:
            skewness = 0
            if not stats[char].stats_count[stat]:
                stats[char].stats_write[stat] = 0
            elif stat != "name" and "sample_size" not in stat:
                if stat in [
                    "char_lvl",
                    "light_cone_lvl",
                    "attack_lvl",
                    "skill_lvl",
                    "ultimate_lvl",
                    "talent_lvl",
                    "max_hp",
                    "atk",
                    "dfns",
                    "speed",
                ]:
                    median[char][stat] = round(
                        statistics.median(stats[char].stats_count[stat]), 2
                    )
                    mean[char][stat] = round(
                        statistics.mean(stats[char].stats_count[stat]), 2
                    )
                else:
                    median[char][stat] = round(
                        statistics.median(stats[char].stats_count[stat]), 4
                    )
                    mean[char][stat] = round(
                        statistics.mean(stats[char].stats_count[stat]), 4
                    )
                if (
                    mean[char][stat] > 0
                    and median[char][stat] > 0
                    and stats[char].sample_size > 5
                ):
                    if stat not in [
                        "char_lvl",
                        "light_cone_lvl",
                        "attack_lvl",
                        "skill_lvl",
                        "ultimate_lvl",
                        "talent_lvl",
                        "energy_regen",
                        "dmg_boost",
                    ]:
                        skewness = round(
                            skew(stats[char].stats_count[stat], axis=0, bias=True), 2
                        )
                if abs(skewness) > skew_num:
                    if print_chart:
                        if (
                            not (check_char) or char == check_char_name
                        ) and stat in check_stats:
                            print("skewness: " + str(skewness))
                            print(
                                stat
                                + ": "
                                + str(mean[char][stat])
                                + ", "
                                + str(median[char][stat])
                            )
                            try:
                                plt_hist(stats[char].stats_count[stat])
                                plt_show()
                            except Exception:
                                pass
                            # print("1 - Mean, 2 - Median: ")
                            with keyboard.Events() as events:
                                event = events.get(1e6)
                                if (
                                    event is not None
                                    and event.key == keyboard.KeyCode.from_char("1")
                                ):
                                    stats[char].stats_write[stat] = str(
                                        mean[char][stat]
                                    )
                                else:
                                    stats[char].stats_write[stat] = str(
                                        median[char][stat]
                                    )
                        else:
                            stats[char].stats_write[stat] = median[char][stat]
                    else:
                        stats[char].stats_write[stat] = median[char][stat]
                else:
                    stats[char].stats_write[stat] = mean[char][stat]

        stats[char].stats_write["sample_size_players"] = stats[char].sample_size_players

        for stat in mainstats[char]:
            sorted_stats = sorted(
                mainstats[char][stat].items(), key=operator.itemgetter(1), reverse=True
            )
            mainstats[char][stat] = {k: v for k, v in sorted_stats}
            for mainstat in mainstats[char][stat]:
                mainstats[char][stat][mainstat] = round(
                    mainstats[char][stat][mainstat] / stats[char].sample_size, 4
                )
            mainstatlist = list(mainstats[char][stat])
            i = 0
            while i < 3:
                if i >= len(mainstatlist):
                    stats[char].stats_write[stat + "_" + str(i + 1)] = "-"
                    stats[char].stats_write[stat + "_" + str(i + 1) + "_app"] = "-"
                else:
                    stats[char].stats_write[stat + "_" + str(i + 1)] = mainstatlist[i]
                    stats[char].stats_write[stat + "_" + str(i + 1) + "_app"] = (
                        mainstats[char][stat][mainstatlist[i]]
                    )
                i += 1

    else:
        for stat in stats[char].stats_count:
            if not stats[char].stats_count[stat]:
                stats[char].stats_write[stat] = 0
            elif stat != "name" and "sample_size" not in stat:
                stats[char].stats_write[stat] = 0

        stats[char].stats_write["sample_size_players"] = 0
        for stat in mainstats[char]:
            i = 0
            while i < 3:
                stats[char].stats_write[stat + "_" + str(i + 1)] = "-"
                stats[char].stats_write[stat + "_" + str(i + 1) + "_app"] = "-"
                i += 1

if os.path.exists("results_real"):
    file1 = open("results_real/chars.csv", "w", newline="")
    file2 = open("results_real/demographic.csv", "w", newline="")
else:
    file1 = open("results/chars.csv", "w", newline="")
    file2 = open("results/demographic.csv", "w", newline="")

csv_writer = csv.writer(file1)
csv_writer2 = csv.writer(file2)
del stats[chars[0]].sample_size
csv_writer.writerow(["name", *stats[chars[0]].stats_write.keys()])
for char in chars:
    if char != chars[0]:
        del stats[char].sample_size
    csv_writer.writerow([stats[char].name, *stats[char].stats_write.values()])
    csv_writer2.writerow([char + ": " + str(stats[char].sample_size_players)])
file1.close()
file2.close()

temp_stats: list[str] = []
iter_char = 0
with open("../char_results/" + phase_num + "/all.json") as char_file:
    CHARACTERS = json.load(char_file)
with open("../char_results/" + phase_num + "/appearance_combine.json") as app_char_file:
    APP = json.load(app_char_file)
with open("../char_results/" + phase_num + "/rounds_combine.json") as round_char_file:
    ROUND = json.load(round_char_file)
for char in stats:
    for i in chain(range(10, 18), range(19, 27)):
        stats[char].stats_write[statkeys[i]] = round(
            float(stats[char].stats_write[statkeys[i]]) * 100, 2
        )
    iterate_value_app: list[str] = []
    for i in range(3):
        iterate_value_app.append("body_stats_" + str(i + 1) + "_app")
        iterate_value_app.append("feet_stats_" + str(i + 1) + "_app")
        iterate_value_app.append("sphere_stats_" + str(i + 1) + "_app")
        iterate_value_app.append("rope_stats_" + str(i + 1) + "_app")
    for value in iterate_value_app:
        if isinstance(stats[char].stats_write[value], float):
            stats[char].stats_write[value] = round(
                float(stats[char].stats_write[value]) * 100, 2
            )
        else:
            stats[char].stats_write[value] = 0.00

    stats[char].name = stats[char].name.replace(" ", "-").lower()
    if stats[char].name in slug:
        stats[char].name = slug[stats[char].name]
    if stats[char].name == CHARACTERS[iter_char]["char"]:
        del stats[char].name
    else:
        print(stats[char].name)
        print(CHARACTERS[iter_char]["char"])
        exit()

    app_dict: dict[str, float] = {}
    if not (pf_mode):
        app_dict = {
            "12_app": APP["12-1"]["4"][char]["app"],
            "12_round": ROUND["12-1"]["4"][char]["round"],
        }
    else:
        app_dict = {
            "4_app": APP["4-1"]["4"][char]["app"],
            "4_round": ROUND["4-1"]["4"][char]["round"],
        }
    temp_stats.append((CHARACTERS[iter_char] | stats[char].stats_write) | app_dict)
    # temp_stats.append((CHARACTERS[iter_char]) | app_dict)
    iter_char += 1

if not os.path.exists("../char_results/" + phase_num):
    os.mkdir("../char_results/" + phase_num)

with open("../char_results/" + phase_num + "/all2.json", "w") as char_file:
    char_file.write(json.dumps(temp_stats, indent=2))

print("Average AR: ", (ar / count))
