import time
import os.path
import statistics
# import csv
# import re
# import operator
# import char_usage as cu
# import pygsheets
# import statistics
# from scipy.stats import skew
# from itertools import permutations
from composition import Composition
from comp_rates_config import *
from archetypes import *

def main():
    start_time = time.time()
    print("start")

    PATHS = ["Preservation","Remembrance","Nihility","Abundance","The Hunt","Destruction","Elation","Propagation","Erudition"]
    DICES = ["Trotter Extrapolation", "Walker Symbiosis", "Ultra-Remote Beacon", "Occurrence Extrapolation", "Combat Extrapolation", "Pursuit", "Countdown", "Amber Barrier", "Investment Sale", "Company Time", "Curio Extrapolation", "Data Inflation"]
    TILES = ["Occurrence: Abnormal", "Intra-Cognition", "Transaction", "Occurrence", "Reward", "Adventure", "Elite", "Combat", "Blank"]
    with open('../data/characters.json') as char_file:
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
                "rarity": CHARACTERS[character]["availability"]
            }

    appears_comps = {
        "Overall": {},
    }
    for path in PATHS:
        appears_comps[path] = {}

    with open('../data/simulated_blessings.json') as char_file:
        BLESSINGS = json.load(char_file)
    appears_bless = {
        "Overall": {},
    }
    for path in PATHS:
        appears_bless[path] = {}
    for blessing in BLESSINGS:
        if BLESSINGS[blessing]["name"]:
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

    with open('../data/simulated_curios.json') as char_file:
        CURIOS = json.load(char_file)
    appears_curio = {
        "Overall": {},
    }
    # for dice_name in DICES:
    #     appears_curio[dice_name] = {}
    for curio in CURIOS:
        temp_curio = curio
        if temp_curio[0] == "3" and len(temp_curio) == 3:
            temp_curio = "2" + temp_curio[1:]
        while(len(temp_curio) < 3):
            temp_curio = "0" + temp_curio
        temp_curio = "3" + temp_curio
        for dice_name in appears_curio:
            appears_curio[dice_name][temp_curio] = {
                "flat": 0,
                "percent": 0.00,
                "name": CURIOS[curio]["name"],
                "desc": CURIOS[curio]["desc"],
                "icon": CURIOS[curio]["icon"].replace("icon/curio/", "").replace(".png", ""),
            }

    with open('../data/nous_dice_hoyolab.json') as dice_face_files:
        DICE_FACES = json.load(dice_face_files)
    appears_dice_faces = {}
    for dice_name in DICES:
        appears_dice_faces[dice_name] = {}
    for dice_name in appears_dice_faces:
        for dice_face in DICE_FACES:
            appears_dice_faces[dice_name][dice_face] = {
                "flat": 0,
                "percent": 0.00,
                "name": DICE_FACES[dice_face]["name"],
                "rarity": DICE_FACES[dice_face]["rarity"],
                "desc": DICE_FACES[dice_face]["description"].replace("**","").replace("1[i]","[?]").replace("2[i]","[?]").replace("3[i]","[?]"),
                "icon": DICE_FACES[dice_face]["shortIcon"],
            }

    path_averages = {}
    for resonance in PATHS:
        path_averages[resonance] = {
            "app_percent": 0.00,
            "bless_count": {},
            "enemy_resonance": {},
            "weakness": {},
        }
        for path in PATHS:
            path_averages[resonance]["bless_count"][path] = []

    dice_averages = {}
    for dice_name in DICES:
        dice_averages[dice_name] = {
            "app_percent": 0.00,
            "bless_count": [],
            "disruption": [],
            "tiles": {},
        }
        for tile in TILES:
            dice_averages[dice_name]["tiles"][tile] = 0

    global self_uids
    if os.path.isfile("../../uids.csv"):
        with open("../../uids.csv", 'r', encoding='UTF8') as f:
            reader = csv.reader(f, delimiter=',')
            self_uids = list(reader)[0]
    else:
        self_uids = []

    if os.path.exists("../data/raw_csvs_real/"):
        f = open("../data/raw_csvs_real/" + RECENT_PHASE + "_nous.json")
    else:
        f = open("../data/raw_csvs/" + RECENT_PHASE + "_nous.json")
    json_data = json.load(f)

    # uid_freq will help detect duplicate UIDs
    comps_dict = {}
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
    for dice_name in DICES:
        sample_size[dice_name] = 0

    for uid in json_data:
        if skip_self and uid in self_uids:
            continue
        # if uid != last_uid:
        # skip_uid = False
        # if uid in uid_freq:
        #     skip_uid = True
        #     # print("duplicate UID in comp: " + uid)
        for row in json_data[uid]:
            if row["difficulty"] == 5:
                conundrumCount = 0
                conundrumCount += row["difficulty_type1"]
                conundrumCount += row["difficulty_type2"]
                if conundrumCount < 10:
                    continue
                resonance = ""
                found_resonance = False
                for path in row["blessings"]:
                    for blessing in row["blessings"][path]:
                        if blessing["id"] % 100 == 20:
                            resonance = match_blessing(blessing["id"])
                            resonance = resonance[0]
                            found_resonance = True
                            break
                    if found_resonance:
                        break
                if not(found_resonance):
                    # resonance = "None"
                    continue

                for char in row["characters"]:
                    appears_char["Overall"][char]["flat"] += 1
                    appears_char[resonance][char]["flat"] += 1

                comp = Composition(0, row["characters"], RECENT_PHASE, row["fury"], 3, conundrumCount, alt_comps)
                comp_tuple = tuple(comp.characters)
                if len(comp_tuple) == 4:
                    for path in ["Overall", resonance]:
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
                        appears_bless["Overall"][str(blessing["id"])]["flat"] += 1
                        appears_bless[resonance][str(blessing["id"])]["flat"] += 1
                        if blessing["up"]:
                            appears_bless["Overall"][str(blessing["id"])]["enhanced_flat"] += 1
                            appears_bless[resonance][str(blessing["id"])]["enhanced_flat"] += 1
                for curio in row["curios"]:
                    appears_curio["Overall"][str(curio)]["flat"] += 1
                    # appears_curio[row["dice_name"]][str(curio)]["flat"] += 1

                row["weakness"][1] = row["weakness"][1].replace("In the Third Plane's Boss Domain challenge, Resonance Extrapolation: ", "").replace(" and its corresponding Formation Extrapolation will occur.", "")
                row["weakness"][1] = row["weakness"][1][0].capitalize() + row["weakness"][1][1:]
                if row["weakness"][1] not in path_averages[resonance]["enemy_resonance"]:
                    path_averages[resonance]["enemy_resonance"][row["weakness"][1]] = 0
                path_averages[resonance]["enemy_resonance"][row["weakness"][1]] += 1

                row["weakness"][2] = row["weakness"][2].replace("In the Third Plane's Boss Domain challenge, ", "")
                row["weakness"][2] = row["weakness"][2][0].capitalize() + row["weakness"][2][1:]
                if row["weakness"][2] not in path_averages[resonance]["weakness"]:
                    path_averages[resonance]["weakness"][row["weakness"][2]] = 0
                path_averages[resonance]["weakness"][row["weakness"][2]] += 1

                for block in row["blocks"]:
                    if block not in ["Boss", "Respite"]:
                        dice_averages[row["dice_name"]]["tiles"][block] += row["blocks"][block]

                for dice_face in row["dice_face"]:
                    appears_dice_faces[row["dice_name"]][dice_face]["flat"] += 1

                total_bless_count = 0
                for path in row["bless_count"]:
                    path_averages[resonance]["bless_count"][path].append(row["bless_count"][path])
                    total_bless_count += row["bless_count"][path]
                dice_averages[row["dice_name"]]["bless_count"].append(total_bless_count)
                dice_averages[row["dice_name"]]["disruption"].append(row["fury"])

                sample_size[resonance] += 1
                sample_size[row["dice_name"]] += 1
                sample_size["Overall"] += 1
                uid_freq.add(uid)
                if uid in self_uids:
                    self_freq.add(uid)

        # else:
        #     uid_freq[uid] += 1
        # last_uid = uid
        # if not skip_uid:

    for path in appears_char:
        for character in CHARACTERS:
            appears_char[path][character]["percent"] = round(
                100 * appears_char[path][character]["flat"] / sample_size[path], 2
            )
        appears_char[path] = dict(sorted(appears_char[path].items(), key=lambda t: t[1]["flat"], reverse=True))

    for path in appears_comps:
        rates = []
        for comp in appears_comps[path]:
            appears_comps[path][comp]["app_rate"] = round(
                100.0 * appears_comps[path][comp]["uses"] / sample_size["Overall"], 2
            )
            rates.append(appears_comps[path][comp]["app_rate"])
        rates.sort(reverse=True)

        appears_comps[path] = dict(sorted(appears_comps[path].items(), key=lambda t: t[1]["uses"], reverse=True))
        comp_names = []
        out_json = []
        out_comps = []
        for comp in appears_comps[path]:
            appears_comps[path][comp]["app_rank"] = rates.index(appears_comps[path][comp]["app_rate"]) + 1
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
            csv_writer = csv.writer(open("../rogue_results/comps/comps.csv", 'w', newline=''))
            for comps in out_comps:
                csv_writer.writerow(comps.values())

            with open("../rogue_results/appcomps.json", "w") as out_file:
                out_file.write(json.dumps(out_json,indent=4))

        csv_writer = csv.writer(open("../rogue_results/comps/" + path + ".csv", 'w', newline=''))
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

    for blessing in BLESSINGS:
        if BLESSINGS[blessing]["name"]:
            for path in appears_bless:
                if appears_bless[path][blessing]["flat"] > 0:
                    appears_bless[path][blessing]["enhanced_percent"] = round(
                        100 * appears_bless[path][blessing]["enhanced_flat"] / appears_bless[path][blessing]["flat"], 2
                    )
                    appears_bless[path][blessing]["percent"] = round(
                        100 * appears_bless[path][blessing]["flat"] / sample_size[path], 2
                    )
    for path in appears_bless:
        appears_bless[path] = dict(sorted(appears_bless[path].items(), key=lambda t: t[1]["flat"], reverse=True))

    for dice_name in appears_curio:
        for curio in appears_curio[dice_name]:
            appears_curio[dice_name][curio]["percent"] = round(
                100 * appears_curio[dice_name][curio]["flat"] / sample_size[dice_name], 2
            )
    for dice_name in appears_curio:
        appears_curio[dice_name] = dict(sorted(appears_curio[dice_name].items(), key=lambda t: t[1]["flat"], reverse=True))

    for dice_name in appears_dice_faces:
        for dice_face in appears_dice_faces[dice_name]:
            appears_dice_faces[dice_name][dice_face]["percent"] = round(
                100 * appears_dice_faces[dice_name][dice_face]["flat"] / sample_size[dice_name], 2
            )
            del appears_dice_faces[dice_name][dice_face]["flat"]
    for dice_name in appears_dice_faces:
        appears_dice_faces[dice_name] = dict(sorted(appears_dice_faces[dice_name].items(), key=lambda t: t[1]["percent"], reverse=True))

    temp_resonance_list = []
    for resonance in path_averages:
        path_averages[resonance]["app_percent"] = round(100 * sample_size[resonance] / sample_size["Overall"], 2)
    path_averages = dict(sorted(path_averages.items(), key=lambda t: t[1]["app_percent"], reverse=True))
    for resonance in path_averages:
        for weakness in path_averages[resonance]["weakness"]:
            path_averages[resonance]["weakness"][weakness] = round(
                100 * path_averages[resonance]["weakness"][weakness] / sample_size[resonance], 2
            )
        path_averages[resonance]["weakness"] = dict(sorted(path_averages[resonance]["weakness"].items(), key=lambda t: t[1], reverse=True))
        for enemy_resonance in path_averages[resonance]["enemy_resonance"]:
            path_averages[resonance]["enemy_resonance"][enemy_resonance] = round(
                100 * path_averages[resonance]["enemy_resonance"][enemy_resonance] / sample_size[resonance], 2
            )
        path_averages[resonance]["enemy_resonance"] = dict(sorted(path_averages[resonance]["enemy_resonance"].items(), key=lambda t: t[1], reverse=True))
        for path in PATHS:
            path_averages[resonance]["bless_count"][path] = round(statistics.mean(path_averages[resonance]["bless_count"][path]), 2)
        path_averages[resonance]["bless_count"] = dict(sorted(path_averages[resonance]["bless_count"].items(), key=lambda t: t[1], reverse=True))
        temp_resonance_list.append({"name": resonance} | path_averages[resonance])
    path_averages = temp_resonance_list

    temp_dice_list = []
    for dice_name in dice_averages:
        dice_averages[dice_name]["app_percent"] = round(100 * sample_size[dice_name] / sample_size["Overall"], 2)
    dice_averages = dict(sorted(dice_averages.items(), key=lambda t: t[1]["app_percent"], reverse=True))
    for dice_name in dice_averages:
        dice_averages[dice_name]["bless_count"] = round(statistics.mean(dice_averages[dice_name]["bless_count"]), 2)
        dice_averages[dice_name]["disruption"] = round(statistics.mean(dice_averages[dice_name]["disruption"]), 2)
        for tile in dice_averages[dice_name]["tiles"]:
            dice_averages[dice_name]["tiles"][tile] = round(
                dice_averages[dice_name]["tiles"][tile] / sample_size[dice_name], 2
            )
        dice_averages[dice_name]["tiles"] = dict(sorted(dice_averages[dice_name]["tiles"].items(), key=lambda t: t[1], reverse=True))
        temp_dice_list.append({"name": dice_name} | dice_averages[dice_name])
    dice_averages = temp_dice_list


    for path in appears_char:
        csv_writer = csv.writer(open("../rogue_results/char/" + path + ".csv", 'w', newline=''))
        count = 0
        temp_char_list = []
        for char in appears_char[path]:
            appears_char[path][char]["percent"] = str(appears_char[path][char]["percent"]) + "%"
            temp_char_list.append({"name": char} | appears_char[path][char])
            if count == 0:
                header = temp_char_list[-1].keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(temp_char_list[-1].values())
        appears_char[path] = temp_char_list

    for path in appears_bless:
        csv_writer = csv.writer(open("../rogue_results/bless/" + path + ".csv", 'w', newline=''))
        count = 0
        temp_bless_list = []
        for bless in appears_bless[path]:
            temp_bless_list.append({"id": bless} | appears_bless[path][bless])
            if count == 0:
                header = temp_bless_list[-1].keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(temp_bless_list[-1].values())
        appears_bless[path] = temp_bless_list

    for dice_name in appears_curio:
        csv_writer = csv.writer(open("../rogue_results/curio_" + dice_name + ".csv", 'w', newline=''))
        count = 0
        temp_curio_list = []
        for curio in appears_curio[dice_name]:
            temp_curio_list.append({"id": curio} | appears_curio[dice_name][curio])
            if count == 0:
                header = temp_curio_list[-1].keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(temp_curio_list[-1].values())
        appears_curio[dice_name] = temp_curio_list

    csv_writer_2 = csv.writer(open("../rogue_results/dice_faces.csv", 'w', newline=''))
    for dice_name in appears_dice_faces:
        csv_writer = csv.writer(open("../rogue_results/dice_faces/" + dice_name + ".csv", 'w', newline=''))
        count = 0
        temp_dice_face_list = []
        temp_dice_face_list_2 = [dice_name]
        dice_face_keys = list(appears_dice_faces[dice_name].keys())
        for i in range(8):
            temp_dice_face_list_2.extend(list(appears_dice_faces[dice_name][dice_face_keys[i]].values()))
        csv_writer_2.writerow(temp_dice_face_list_2)
        for dice_face in appears_dice_faces[dice_name]:
            if appears_dice_faces[dice_name][dice_face]["percent"] == 0:
                continue
            temp_dice_face_list.append(appears_dice_faces[dice_name][dice_face])
            if count == 0:
                header = temp_dice_face_list[-1].keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(temp_dice_face_list[-1].values())

    csv_writer = csv.writer(open("../rogue_results/dice_tiles.csv", 'w', newline=''))
    for dice_name in dice_averages:
        temp_tiles_list = [dice_name["name"]]
        tile_keys = list(dice_name["tiles"].keys())
        for i in range(9):
            temp_tiles_list.append(tile_keys[i])
            temp_tiles_list.append(dice_name["tiles"][tile_keys[i]])
        csv_writer.writerow(temp_tiles_list)

    with open("../rogue_results/appchar.json", "w") as out_file:
        out_file.write(json.dumps(appears_char,indent=4))
    with open("../rogue_results/appbless.json", "w") as out_file:
        out_file.write(json.dumps(appears_bless,indent=4))
    with open("../rogue_results/appcurio.json", "w") as out_file:
        out_file.write(json.dumps(appears_curio,indent=4))
    with open("../rogue_results/apppath.json", "w") as out_file:
        out_file.write(json.dumps(path_averages,indent=4))
    with open("../rogue_results/appdice.json", "w") as out_file:
        out_file.write(json.dumps(dice_averages,indent=4))

    sample_size["Total"] = len(uid_freq)
    sample_size["SelfReport"] = len(self_freq)
    sample_size["Random"] = sample_size["Total"] - sample_size["SelfReport"]
    # sample_size = dict(sorted(sample_size.items(), key=lambda t: t[1], reverse=True))
    with open("../rogue_results/demographic.json", "w") as out_file:
        out_file.write(json.dumps(sample_size,indent=4))

    cur_time = time.time()
    print("done json: ", (cur_time - start_time), "s")
    # print(sample_size)

    csv_writer = csv.writer(open("../rogue_results/uids.csv", 'w', newline=''))
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
    #TODO Need to create a structure for bad names --> names

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
            print("res not found: " + str(blessing_id))
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
            print("res not found: " + str(blessing_id))
            arr_return.append("None")
    return(arr_return)

main()
