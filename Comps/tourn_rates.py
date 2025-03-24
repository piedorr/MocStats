import time
import os.path
import statistics

import csv

# import re
# import operator
# import char_usage as cu
# import pygsheets
# import statistics
# from scipy.stats import skew
# from itertools import permutations
from composition import Composition
from comp_rates_config import (
    RECENT_PHASE,
    CHARACTERS,
    json,
    skip_self,
    alt_comps,
    app_rate_threshold,
)


def main():
    start_time = time.time()
    print("start")

    PATHS = [
        "Preservation",
        "Remembrance",
        "Nihility",
        "Abundance",
        "The Hunt",
        "Destruction",
        "Elation",
        "Propagation",
        "Erudition",
    ]
    with open("../data/characters.json") as char_file:
        CHARACTERS = json.load(char_file)

    appears_char = {
        "Overall": {},
    }
    for path in PATHS:
        appears_char[path] = {}
    for character in CHARACTERS:
        for path in appears_char:
            appears_char[path][character] = {
                "flat": 0,
                "percent": 0.00,
                "rarity": CHARACTERS[character]["availability"],
            }

    appears_comps = {
        "Overall": {},
    }
    for path in PATHS:
        appears_comps[path] = {}

    with open("../data/simulated_blessings.json") as char_file:
        BLESSINGS = json.load(char_file)
    appears_bless = {
        "Overall": {},
    }
    for path in PATHS:
        appears_bless[path] = {}
    for blessing in BLESSINGS:
        if (
            BLESSINGS[blessing]["name"]
            and BLESSINGS[blessing]["id"][:2] != "67"
            and BLESSINGS[blessing]["id"][:3] != "612"
            and (
                BLESSINGS[blessing]["id"][4] != "2"
                or BLESSINGS[blessing]["id"][:3] != "615"
            )
        ):
            bless_id = match_blessing(blessing)
            for path in appears_bless:
                appears_bless[path][blessing] = {
                    "flat": 0,
                    "percent": 0.00,
                    "enhanced_flat": 0,
                    "enhanced_percent": 0.00,
                    "path": bless_id[0],
                    "name": BLESSINGS[blessing]["name"],
                    "rarity": bless_id[1],
                    "desc": BLESSINGS[blessing]["desc"],
                }

    with open("../data/tourn_equations.json") as char_file:
        EQUATIONS = json.load(char_file)
    appears_equation = {
        "Overall": {},
    }
    for path in PATHS:
        appears_equation[path] = {}
    for equation in EQUATIONS:
        if EQUATIONS[equation]["name"]:
            for path in appears_equation:
                appears_equation[path][equation] = {
                    "flat": 0,
                    "percent": 0.00,
                    "name": EQUATIONS[equation]["name"],
                    "main_type": EQUATIONS[equation]["main_type"],
                    "sub_type": EQUATIONS[equation]["sub_type"],
                    "category": EQUATIONS[equation]["category"],
                    "desc": EQUATIONS[equation]["buff_desc"],
                    "main_icon": EQUATIONS[equation]["main_icon"],
                    "sub_icon": EQUATIONS[equation]["sub_icon"],
                }

    with open("../data/tourn_curios.json") as char_file:
        CURIOS = json.load(char_file)
    appears_curio = {
        "Overall": {},
    }
    for curio in CURIOS:
        for dice_name in appears_curio:
            appears_curio[dice_name][curio] = {
                "flat": 0,
                "percent": 0.00,
                "name": CURIOS[curio]["name"],
                "category": CURIOS[curio]["category"],
                "desc": CURIOS[curio]["desc"],
                "icon": CURIOS[curio]["icon"],
            }

    path_averages = {}
    for resonance in PATHS:
        path_averages[resonance] = {
            "app_percent": 0.00,
            "bless_count": {},
        }
        for path in PATHS:
            path_averages[resonance]["bless_count"][path] = []

    global self_uids
    if os.path.isfile("../../uids.csv"):
        with open("../../uids.csv", "r", encoding="UTF8") as f:
            reader = csv.reader(f, delimiter=",")
            self_uids = list(reader)[0]
    else:
        self_uids = []

    if os.path.exists("../data/raw_csvs_real/"):
        f = open("../data/raw_csvs_real/" + RECENT_PHASE + "_tourn.json")
    else:
        f = open("../data/raw_csvs/" + RECENT_PHASE + "_tourn.json")
    json_data = json.load(f)

    # uid_freq will help detect duplicate UIDs
    uid_freq = set()
    self_freq = set()
    # last_uid = "0"
    sample_size = {
        "Total": 0,
        "SelfReport": 0,
        "Random": 0,
        "Overall": 0,
    }
    for path in PATHS:
        sample_size[path] = 0
    # for dice_name in DICES:
    #     sample_size[dice_name] = 0

    for row in json_data:
        if skip_self and str(row["uid"]) in self_uids:
            continue
        conundrumCount = int(row["difficulty"])
        if conundrumCount < 4:
            continue
        resonances = []
        max_bless_count = 0
        for path in row["bless_count"]:
            if row["bless_count"][path] > max_bless_count:
                max_bless_count = row["bless_count"][path]
        for path in row["bless_count"]:
            if row["bless_count"][path] == max_bless_count:
                resonances.append(path)

        comp_chars_temp = []
        cons_chars_temp = []
        for char in row["characters"]:
            comp_chars_temp.append(char)
            cons_chars_temp.append(row["characters"][char])
            appears_char["Overall"][char]["flat"] += 1
            for resonance in resonances:
                appears_char[resonance][char]["flat"] += 1

        comp = Composition(
            0,
            comp_chars_temp,
            RECENT_PHASE,
            5,
            3,
            conundrumCount,
            alt_comps,
            "",
            cons_chars_temp,
        )
        comp_tuple = tuple(comp.characters)
        if len(comp_tuple) == 4:
            for path in ["Overall"] + resonances:
                if comp_tuple not in appears_comps[path]:
                    appears_comps[path][comp_tuple] = {
                        "uses": 0,
                        "comp_name": comp.comp_name,
                        "alt_comp_name": comp.alt_comp_name,
                    }
                appears_comps[path][comp_tuple]["uses"] += 1

            # if comp_tuple not in comps_dict:
            #     comps_dict[comp_tuple] = {
            #         "uses": 0,
            #         "comp_name": comp.comp_name,
            #         "alt_comp_name": comp.alt_comp_name,
            #         "paths" : {},
            #     }
            # comps_dict[comp_tuple]["uses"] += 1

        for path in row["blessings"]:
            for blessing in row["blessings"][path]:
                appears_bless["Overall"][str(blessing)]["flat"] += 1
                for resonance in resonances:
                    appears_bless[resonance][str(blessing)]["flat"] += 1
                if row["blessings"][path][blessing]:
                    appears_bless["Overall"][str(blessing)]["enhanced_flat"] += 1
                    for resonance in resonances:
                        appears_bless[resonance][str(blessing)]["enhanced_flat"] += 1
        for equation in row["equations"]:
            appears_equation["Overall"][str(equation)]["flat"] += 1
            for resonance in resonances:
                appears_equation[resonance][str(equation)]["flat"] += 1
        for curio in row["curios"]:
            appears_curio["Overall"][str(curio)]["flat"] += 1
        for curio in row["weighted_curios"]:
            appears_curio["Overall"][str(curio)]["flat"] += 1
            # appears_curio[row["dice_name"]][str(curio)]["flat"] += 1

        total_bless_count = 0
        for path in row["bless_count"]:
            for resonance in resonances:
                path_averages[resonance]["bless_count"][path].append(
                    row["bless_count"][path]
                )
            total_bless_count += row["bless_count"][path]

        for resonance in resonances:
            sample_size[resonance] += 1
        sample_size["Overall"] += 1
        uid_freq.add(row["uid"])
        if str(row["uid"]) in self_uids:
            self_freq.add(row["uid"])

    for path in appears_char:
        for character in CHARACTERS:
            appears_char[path][character]["percent"] = round(
                100 * appears_char[path][character]["flat"] / sample_size[path], 2
            )
        appears_char[path] = dict(
            sorted(appears_char[path].items(), key=lambda t: t[1]["flat"], reverse=True)
        )

    for path in appears_comps:
        rates = []
        for comp in appears_comps[path]:
            appears_comps[path][comp]["app_rate"] = round(
                100.0 * appears_comps[path][comp]["uses"] / sample_size["Overall"], 2
            )
            rates.append(appears_comps[path][comp]["app_rate"])
        rates.sort(reverse=True)

        appears_comps[path] = dict(
            sorted(
                appears_comps[path].items(), key=lambda t: t[1]["uses"], reverse=True
            )
        )
        comp_names = []
        out_json = []
        out_comps = []
        for comp in appears_comps[path]:
            appears_comps[path][comp]["app_rank"] = (
                rates.index(appears_comps[path][comp]["app_rate"]) + 1
            )
            comp_name = appears_comps[path][comp]["comp_name"]
            alt_comp_name = appears_comps[path][comp]["alt_comp_name"]
            # Only one variation of each comp name is included,
            # unless if it's used for a character's infographic
            if (comp_name not in comp_names or comp_name == "-") and path == "Overall":
                if appears_comps[path][comp]["app_rate"] >= app_rate_threshold:
                    temp_comp_name = "-"
                    if alt_comp_name != "-":
                        temp_comp_name = alt_comp_name
                    else:
                        temp_comp_name = comp_name
                    out_comps_append = {
                        "comp_name": temp_comp_name,
                        "char_1": comp[0],
                        "char_2": comp[1],
                        "char_3": comp[2],
                        "char_4": comp[3],
                        "app_rate": str(appears_comps[path][comp]["app_rate"]) + "%",
                        "uses": str(appears_comps[path][comp]["uses"]),
                    }
                    out_comps.append(out_comps_append)
                    comp_names.append(comp_name)

            out_json_dict = {
                "char_one": comp[0],
                "char_two": comp[1],
                "char_three": comp[2],
                "char_four": comp[3],
            }
            out_json_dict["app_rate"] = appears_comps[path][comp]["app_rate"]
            out_json_dict["rank"] = appears_comps[path][comp]["app_rank"]
            out_json.append(out_json_dict)

        if path == "Overall":
            csv_writer = csv.writer(
                open("../rogue_results/comps/comps.csv", "w", newline="")
            )
            for comps in out_comps:
                csv_writer.writerow(comps.values())

            with open("../rogue_results/appcomps.json", "w") as out_file:
                out_file.write(json.dumps(out_json, indent=4))

        csv_writer = csv.writer(
            open("../rogue_results/comps/" + path + ".csv", "w", newline="")
        )
        count = 0
        temp_comp_list = []
        for comp in out_json:
            comp["app_rate"] = str(comp["app_rate"]) + "%"
            temp_comp_list.append(comp)
            if count == 0:
                header = temp_comp_list[-1].keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(temp_comp_list[-1].values())

    for path in appears_bless:
        for blessing in appears_bless[path]:
            if appears_bless[path][blessing]["flat"] > 0:
                appears_bless[path][blessing]["enhanced_percent"] = round(
                    100
                    * appears_bless[path][blessing]["enhanced_flat"]
                    / appears_bless[path][blessing]["flat"],
                    2,
                )
                appears_bless[path][blessing]["percent"] = round(
                    100 * appears_bless[path][blessing]["flat"] / sample_size[path], 2
                )
    for path in appears_bless:
        appears_bless[path] = dict(
            sorted(
                appears_bless[path].items(), key=lambda t: t[1]["flat"], reverse=True
            )
        )

    for equation in EQUATIONS:
        if EQUATIONS[equation]["name"]:
            for path in appears_equation:
                if appears_equation[path][equation]["flat"] > 0:
                    appears_equation[path][equation]["percent"] = round(
                        100
                        * appears_equation[path][equation]["flat"]
                        / sample_size[path],
                        2,
                    )
    for path in appears_equation:
        appears_equation[path] = dict(
            sorted(
                appears_equation[path].items(), key=lambda t: t[1]["flat"], reverse=True
            )
        )

    for dice_name in appears_curio:
        for curio in appears_curio[dice_name]:
            appears_curio[dice_name][curio]["percent"] = round(
                100 * appears_curio[dice_name][curio]["flat"] / sample_size[dice_name],
                2,
            )
    for dice_name in appears_curio:
        appears_curio[dice_name] = dict(
            sorted(
                appears_curio[dice_name].items(),
                key=lambda t: t[1]["flat"],
                reverse=True,
            )
        )

    temp_resonance_list = []
    for resonance in path_averages:
        path_averages[resonance]["app_percent"] = round(
            100 * sample_size[resonance] / sample_size["Overall"], 2
        )
    path_averages = dict(
        sorted(path_averages.items(), key=lambda t: t[1]["app_percent"], reverse=True)
    )
    for resonance in path_averages:
        for path in PATHS:
            path_averages[resonance]["bless_count"][path] = round(
                statistics.mean(path_averages[resonance]["bless_count"][path]), 2
            )
        path_averages[resonance]["bless_count"] = dict(
            sorted(
                path_averages[resonance]["bless_count"].items(),
                key=lambda t: t[1],
                reverse=True,
            )
        )
        temp_resonance_list.append({"name": resonance} | path_averages[resonance])
    path_averages = temp_resonance_list

    for path in appears_char:
        csv_writer = csv.writer(
            open("../rogue_results/char/" + path + ".csv", "w", newline="")
        )
        count = 0
        temp_char_list = []
        for char in appears_char[path]:
            appears_char[path][char]["percent"] = (
                str(appears_char[path][char]["percent"]) + "%"
            )
            temp_char_list.append({"name": char} | appears_char[path][char])
            if count == 0:
                header = temp_char_list[-1].keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(temp_char_list[-1].values())
        appears_char[path] = temp_char_list  # type: ignore

    for path in appears_bless:
        csv_writer = csv.writer(
            open("../rogue_results/bless/" + path + ".csv", "w", newline="")
        )
        count = 0
        temp_bless_list = []
        for bless in appears_bless[path]:
            temp_bless_list.append({"id": bless} | appears_bless[path][bless])
            if count == 0:
                header = temp_bless_list[-1].keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(temp_bless_list[-1].values())
        appears_bless[path] = temp_bless_list  # type: ignore

    for path in appears_equation:
        csv_writer = csv.writer(
            open("../rogue_results/equation/" + path + ".csv", "w", newline="")
        )
        count = 0
        temp_equation_list = []
        for equation in appears_equation[path]:
            temp_equation_list.append(
                {"id": equation} | appears_equation[path][equation]
            )
            if count == 0:
                header = temp_equation_list[-1].keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(temp_equation_list[-1].values())
        appears_equation[path] = temp_equation_list  # type: ignore

    for dice_name in appears_curio:
        csv_writer = csv.writer(
            open("../rogue_results/curio_" + dice_name + ".csv", "w", newline="")
        )
        count = 0
        temp_curio_list = []
        for curio in appears_curio[dice_name]:
            temp_curio_list.append({"id": curio} | appears_curio[dice_name][curio])
            if count == 0:
                header = temp_curio_list[-1].keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(temp_curio_list[-1].values())
        appears_curio[dice_name] = temp_curio_list  # type: ignore

    with open("../rogue_results/appchar.json", "w") as out_file:
        out_file.write(json.dumps(appears_char, indent=4))
    with open("../rogue_results/appbless.json", "w") as out_file:
        out_file.write(json.dumps(appears_bless, indent=4))
    with open("../rogue_results/appequation.json", "w") as out_file:
        out_file.write(json.dumps(appears_equation, indent=4))
    with open("../rogue_results/appcurio.json", "w") as out_file:
        out_file.write(json.dumps(appears_curio, indent=4))
    with open("../rogue_results/apppath.json", "w") as out_file:
        out_file.write(json.dumps(path_averages, indent=4))

    sample_size["Total"] = len(uid_freq)
    sample_size["SelfReport"] = len(self_freq)
    sample_size["Random"] = sample_size["Total"] - sample_size["SelfReport"]
    # sample_size = dict(sorted(sample_size.items(), key=lambda t: t[1], reverse=True))
    with open("../rogue_results/demographic.json", "w") as out_file:
        out_file.write(json.dumps(sample_size, indent=4))

    cur_time = time.time()
    print("done json: ", (cur_time - start_time), "s")
    # print(sample_size)

    csv_writer = csv.writer(open("../rogue_results/uids.csv", "w", newline=""))
    for uid in uid_freq:
        csv_writer.writerow([uid])
    # print(uid_freq)
    # exit()


def name_filter(comp, mode="out"):
    filtered = []
    if mode == "out":
        for char in comp:
            if CHARACTERS[char]["out_name"]:
                filtered.append(CHARACTERS[char]["alt_name"])
            else:
                filtered.append(char)
    return filtered
    # TODO Need to create a structure for bad names --> names


def match_blessing(blessing_id):
    arr_return = []
    match str(blessing_id)[3]:
        case "0":
            arr_return.append("Preservation")
        case "1":
            arr_return.append("Remembrance")
        case "2":
            arr_return.append("Nihility")
        case "3":
            arr_return.append("Abundance")
        case "4":
            arr_return.append("The Hunt")
        case "5":
            arr_return.append("Destruction")
        case "6":
            arr_return.append("Elation")
        case "7":
            arr_return.append("Propagation")
        case "8":
            arr_return.append("Erudition")
        case _:
            print("path not found: " + str(blessing_id))
            arr_return.append("None")
    match str(blessing_id)[4]:
        case "2":
            arr_return.append("Resonance")
        case "3":
            arr_return.append("3")
        case "4":
            arr_return.append("2")
        case "5":
            arr_return.append("1")
        case _:
            print("type not found: " + str(blessing_id))
            arr_return.append("None")
    return arr_return


main()
