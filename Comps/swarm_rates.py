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

    PATHS = ["Preservation","Remembrance","Nihility","Abundance","The Hunt","Destruction","Elation","Propagation"]
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
    appears_curio = {}
    for curio in CURIOS:
        temp_curio = curio
        while(len(temp_curio) < 3):
            temp_curio = "0" + temp_curio
        temp_curio = "1" + temp_curio
        appears_curio[temp_curio] = {
            "flat": 0,
            "percent": 0.00,
            "name": CURIOS[curio]["name"],
            "desc": CURIOS[curio]["desc"],
            "icon": CURIOS[curio]["icon"].replace("icon/curio/", "").replace(".png", ""),
        }

    with open('../data/simulated_blocks.json') as char_file:
        TILES = json.load(char_file)
    path_averages = {}
    for resonance in PATHS:
        path_averages[resonance] = {
            "app_percent": 0.00,
            "weakness": {},
            "disruption": [],
            "bless_count": {},
            "tiles": {},
        }
        for path in PATHS:
            path_averages[resonance]["bless_count"][path] = []
        for tile in TILES:
            if TILES[tile]["name"] not in ["Boss: Swarm", "Boss", ""]:
                path_averages[resonance]["tiles"][TILES[tile]["name"]] = 0

    global self_uids
    if os.path.isfile("../../uids.csv"):
        with open("../../uids.csv", 'r', encoding='UTF8') as f:
            reader = csv.reader(f, delimiter=',')
            self_uids = list(reader)[0]
    else:
        self_uids = []

    if os.path.exists("../data/raw_csvs_real/"):
        f = open("../data/raw_csvs_real/" + RECENT_PHASE + "_rogue.json")
    else:
        f = open("../data/raw_csvs/" + RECENT_PHASE + "_rogue.json")
    json_data = json.load(f)

    # uid_freq will help detect duplicate UIDs
    comps_dict = {}
    uid_freq = {}
    self_freq = {}
    # last_uid = "0"
    sample_size = {
        "Total": 0,
        "SelfReport": 0,
        "Random": 0,
        "Overall": 0,
    }
    for path in PATHS:
        sample_size[path] = 0

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

                comp = Composition(0, row["characters"], RECENT_PHASE, row["fury"], 3, row["difficulty"], alt_comps)
                comp_tuple = tuple(comp.characters)
                if len(comp_tuple) == 4:
                    if comp_tuple not in comps_dict:
                        comps_dict[comp_tuple] = {
                            "uses": 0,
                            "comp_name": comp.comp_name,
                            "alt_comp_name": comp.alt_comp_name,
                            "paths" : {},
                        }
                        for path in PATHS:
                            comps_dict[comp_tuple]["paths"][path] = 0
                    comps_dict[comp_tuple]["uses"] += 1
                    comps_dict[comp_tuple]["paths"][resonance] += 1

                for path in row["blessings"]:
                    for blessing in row["blessings"][path]:
                        appears_bless["Overall"][str(blessing["id"])]["flat"] += 1
                        appears_bless[resonance][str(blessing["id"])]["flat"] += 1
                        if blessing["up"]:
                            appears_bless["Overall"][str(blessing["id"])]["enhanced_flat"] += 1
                            appears_bless[resonance][str(blessing["id"])]["enhanced_flat"] += 1
                for curio in row["curios"]:
                    appears_curio[str(curio)]["flat"] += 1

                row["weakness"][1] = row["weakness"][1].replace("While battling Swarm: True Sting (Complete) in the third plane's Boss: Swarm domain, ", "")
                row["weakness"][1] = row["weakness"][1][0].capitalize() + row["weakness"][1][1:]
                if row["weakness"][1] not in path_averages[resonance]["weakness"]:
                    path_averages[resonance]["weakness"][row["weakness"][1]] = 1
                else:
                    path_averages[resonance]["weakness"][row["weakness"][1]] += 1

                for block in row["blocks"]:
                    if block not in ["Boss: Swarm", "Boss"]:
                        path_averages[resonance]["tiles"][block] += row["blocks"][block]
                for path in row["bless_count"]:
                    path_averages[resonance]["bless_count"][path].append(row["bless_count"][path])
                path_averages[resonance]["disruption"].append(row["fury"])

                sample_size[resonance] += 1
                sample_size["Overall"] += 1
                uid_freq[uid] = 1
                if uid in self_uids:
                    self_freq[uid] = 1

        # else:
        #     uid_freq[uid] += 1
        # last_uid = uid
        # if not skip_uid:

    for character in CHARACTERS:
        for path in appears_char:
            appears_char[path][character]["percent"] = round(
                100 * appears_char[path][character]["flat"] / sample_size[path], 2
            )
    for path in appears_char:
        appears_char[path] = dict(sorted(appears_char[path].items(), key=lambda t: t[1]["flat"], reverse=True))

    rates = []
    for comp in comps_dict:
        comps_dict[comp]["app_rate"] = round(
            100.0 * comps_dict[comp]["uses"] / sample_size["Overall"], 2
        )
        rates.append(comps_dict[comp]["app_rate"])
        for path in PATHS:
            comps_dict[comp]["paths"][str(path) + "_app_rate"] = round(
                100.0 * comps_dict[comp]["paths"][path] / sample_size[path], 2
            )
    rates.sort(reverse=True)

    comps_dict = dict(sorted(comps_dict.items(), key=lambda t: t[1]["uses"], reverse=True))
    comp_names = []
    out_json = []
    out_comps = []
    for comp in comps_dict:
        comps_dict[comp]["app_rank"] = rates.index(comps_dict[comp]["app_rate"]) + 1
        comp_name = comps_dict[comp]["comp_name"]
        alt_comp_name = comps_dict[comp]["alt_comp_name"]
        # Only one variation of each comp name is included,
        # unless if it's used for a character's infographic
        if comp_name not in comp_names or comp_name == "-":
            if comps_dict[comp]["app_rate"] >= app_rate_threshold:
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
                    "app_rate": str(comps_dict[comp]["app_rate"]) + "%",
                    "uses": str(comps_dict[comp]["uses"]),
                }
                out_comps.append(out_comps_append)
                comp_names.append(comp_name)

        out_json_dict = {
            "char_one": comp[0],
            "char_two": comp[1],
            "char_three": comp[2],
            "char_four": comp[3],
        }
        out_json_dict["app_rate"] = comps_dict[comp]["app_rate"]
        out_json_dict["rank"] = comps_dict[comp]["app_rank"]
        out_json.append(out_json_dict)

    csv_writer = csv.writer(open("../rogue_results/comps_usage_rogue.csv", 'w', newline=''))
    for comps in out_comps:
        csv_writer.writerow(comps.values())

    with open("../rogue_results/appcomps.json", "w") as out_file:
        out_file.write(json.dumps(out_json,indent=4))

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

    for curio in appears_curio:
        appears_curio[curio]["percent"] = round(
            100 * appears_curio[curio]["flat"] / sample_size["Overall"], 2
        )
    appears_curio = dict(sorted(appears_curio.items(), key=lambda t: t[1]["flat"], reverse=True))

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
        path_averages[resonance]["disruption"] = round(statistics.mean(path_averages[resonance]["disruption"]), 2)
        for path in PATHS:
            path_averages[resonance]["bless_count"][path] = round(statistics.mean(path_averages[resonance]["bless_count"][path]), 2)
        path_averages[resonance]["bless_count"] = dict(sorted(path_averages[resonance]["bless_count"].items(), key=lambda t: t[1], reverse=True))
        for tile in path_averages[resonance]["tiles"]:
            path_averages[resonance]["tiles"][tile] = round(
                path_averages[resonance]["tiles"][tile] / sample_size[resonance], 2
            )
        path_averages[resonance]["tiles"] = dict(sorted(path_averages[resonance]["tiles"].items(), key=lambda t: t[1], reverse=True))
        temp_resonance_list.append({"name": resonance} | path_averages[resonance])
    path_averages = temp_resonance_list


    for path in appears_char:
        csv_writer = csv.writer(open("../rogue_results/char_" + path + ".csv", 'w', newline=''))
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
        csv_writer = csv.writer(open("../rogue_results/bless_" + path + ".csv", 'w', newline=''))
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
    csv_writer = csv.writer(open("../rogue_results/curio.csv", 'w', newline=''))
    count = 0
    temp_curio_list = []
    for curio in appears_curio:
        temp_curio_list.append({"id": curio} | appears_curio[curio])
        if count == 0:
            header = temp_curio_list[-1].keys()
            csv_writer.writerow(header)
            count += 1
        csv_writer.writerow(temp_curio_list[-1].values())
    appears_curio = temp_curio_list

    with open("../rogue_results/appchar.json", "w") as out_file:
        out_file.write(json.dumps(appears_char,indent=4))
    with open("../rogue_results/appbless.json", "w") as out_file:
        out_file.write(json.dumps(appears_bless,indent=4))
    with open("../rogue_results/appcurio.json", "w") as out_file:
        out_file.write(json.dumps(appears_curio,indent=4))
    with open("../rogue_results/apppath.json", "w") as out_file:
        out_file.write(json.dumps(path_averages,indent=4))

    sample_size["Total"] = len(uid_freq)
    sample_size["SelfReport"] = len(self_freq)
    sample_size["Random"] = sample_size["Total"] - sample_size["SelfReport"]
    sample_size = dict(sorted(sample_size.items(), key=lambda t: t[1], reverse=True))
    with open("../rogue_results/demographic.json", "w") as out_file:
        out_file.write(json.dumps(sample_size,indent=4))

    cur_time = time.time()
    print("done json: ", (cur_time - start_time), "s")
    # print(sample_size)

    csv_writer = csv.writer(open("../rogue_results/uids.csv", 'w', newline=''))
    for uid in uid_freq.keys():
        csv_writer.writerow([uid])
    # print(uid_freq)
    # exit()

    # if "Comp usage all stages" in run_commands:
    #     comp_usages(rogue_table, all_players, whaleCheck, whaleSigWeap, sigWeaps, rooms=["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2", "5-1", "5-2", "6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2"], filename="all", floor=True)
    #     cur_time = time.time()
    #     print("done comp all: ", (cur_time - start_time), "s")

#     if "Character specific infographics" in run_commands:
#         comp_usages(rogue_table, all_players, whaleCheck, whaleSigWeap, sigWeaps, rooms=["6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2"], filename=char_infographics, info_char=True, floor=True)
#         cur_time = time.time()
#         print("done char infographics: ", (cur_time - start_time), "s")

def comp_usages(comps,
                players,
                whaleCheck,
                whaleSigWeap,
                sigWeaps,
                rooms=["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2", "5-1", "5-2", "6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2"],
                filename="comp_usages",
                offset=1,
                info_char=False,
                floor=False):
    comps_dict = used_comps(players, comps, rooms, filename, whaleCheck, whaleSigWeap, sigWeaps, floor=floor, offset=offset)
    rank_usages(comps_dict, owns_offset=offset)
    comp_usages_write(comps_dict, filename, floor, info_char, True)
    comp_usages_write(comps_dict, filename, floor, info_char, False)

def used_comps(players, comps, rooms, filename, whaleCheck, whaleSigWeap, sigWeaps, phase=RECENT_PHASE, floor=False, offset=1):
    # Returns the dictionary of all the comps used and how many times they were used
    comps_dict = [{},{},{},{},{}]
    error_uids = []
    # lessFour = []
    # lessFourComps = {}
    global total_comps
    total_comps = 0
    total_self_comps = 0
    whaleCount = 0
    healerless = 0
    for comp in comps:
        comp_tuple = tuple(comp.characters)
        # Check if the comp is used in the rooms that are being checked
        if comp.room not in rooms:
            continue

        foundchar = resetfind()
        for char in comp.characters:
            findchars(char, foundchar)
        if find_archetype(foundchar):
            total_comps += 1
            if comp.player in self_uids:
                total_self_comps += 1
            if len(comp_tuple) < 4:
            #     lessFour.append(comp.player)
                continue

            healer = False
            for i in ["Bailu", "Gepard", "Natasha"]:
                if i in comp_tuple:
                    healer = True
            if not healer:
                healerless +=1

            whaleComp = False
            for char in range (4):
                if comp_tuple[char] in players[phase][comp.player].owned:
                # if comp_tuple[char] in players[phase][comp.player].owned and comp_tuple[char] == "Blade":
                    if (
                        players[phase][comp.player].owned[comp_tuple[char]]["cons"] != 0
                        and CHARACTERS[comp_tuple[char]]["availability"] in ["Limited 5*"]
                    ) or (
                        whaleSigWeap and players[phase][comp.player].owned[comp_tuple[char]]["weapon"] in sigWeaps
                    ):
                        whaleComp = True
            if whaleComp:
                whaleCount += 1
                if whaleCheck:
                    continue

            for star_threshold in range(0,5):
                if star_threshold != 4 and comp.star_num != star_threshold:
                    continue
                if comp_tuple not in comps_dict[star_threshold]:
                    comps_dict[star_threshold][comp_tuple] = {
                        "uses": 0,
                        "owns": 0,
                        "5* count": comp.fivecount,
                        "comp_name": comp.comp_name,
                        "alt_comp_name": comp.alt_comp_name,
                        "star_num": comp.star_num,
                        "round_num": {
                            "1": [],
                            "2": [],
                            "3": [],
                            "4": [],
                            "5": [],
                            "6": [],
                            "7": [],
                            "8": [],
                            "9": [],
                            "10": [],
                        },
                        "deepwood": 0,
                        "whale_count": set(),
                        "players": set(),
                    }
                comps_dict[star_threshold][comp_tuple]["uses"] += 1
                comps_dict[star_threshold][comp_tuple]["round_num"][list(str(comp.room).split("-"))[0]].append(comp.round_num)
                comps_dict[star_threshold][comp_tuple]["players"].add(comp.player)
                if whaleComp:
                    comps_dict[star_threshold][comp_tuple]["whale_count"].add(comp.player)
    chamber_num = list(str(filename).split("-"))
    # print(error_uids)
    # print("Less than four: " + str(lessFour))
    # print("Less than four: " + str(len(lessFour)/total_comps))
    # print("Healerless: " + str(healerless))
    # print("Healerless: " + str(healerless/total_comps))
    if whaleCheck:
        print("Whale percentage: " + str(whaleCount/total_comps))
    # print("Tighnari with deepwood: " + str(deepwoodTighnari))
    # print(deepwoodEquipChars)
    return comps_dict

def rank_usages(comps_dict, owns_offset=1):
    # Calculate the usage rate and sort the comps according to it
    for star_threshold in range(0,5):
        rates = []
        rounds = []
        for comp in comps_dict[star_threshold]:
            # skewness = 0
            # if comps_dict[star_threshold][comp]["uses"] > 5:
            #     skewness = round(skew(comps_dict[star_threshold][comp]["round_num"], axis=0, bias=True), 2)
            # if skewness < 1:
            #     avg_round = round(statistics.mean(comps_dict[star_threshold][comp]["round_num"]), 2)
            # else:
            #     avg_round = round(statistics.median(comps_dict[star_threshold][comp]["round_num"]), 2)
            avg_round = []
            for room_num in range(1,11):
                if (comps_dict[star_threshold][comp]["round_num"][str(room_num)]):
                    # avg_round.append(statistics.mean(comps_dict[star_threshold][comp]["round_num"][str(room_num)]))
                    avg_round += comps_dict[star_threshold][comp]["round_num"][str(room_num)]
            avg_round = round(statistics.mean(avg_round), 2)
            app = int(100.0 * comps_dict[star_threshold][comp]["uses"] / (total_comps * owns_offset) * 200 + .5) / 100.0
            comps_dict[star_threshold][comp]["app_rate"] = app
            comps_dict[star_threshold][comp]["round"] = avg_round
            # rate = int(100.0 * comps_dict[star_threshold][comp]["uses"] / comps_dict[star_threshold][comp]["owns"] * 100 + .5) / 100.0
            comps_dict[star_threshold][comp]["usage_rate"] = 0
            # own = int(100.0 * comps_dict[star_threshold][comp]["owns"] / (total_comps * owns_offset) * 100 + .5) / 100.0
            comps_dict[star_threshold][comp]["own_rate"] = 0
            # deepwood = int(100.0 * comps_dict[star_threshold][comp]["deepwood"] / comps_dict[star_threshold][comp]["uses"] * 100 + .5) / 100.0
            # comps_dict[star_threshold][comp]["deepwood_rate"] = deepwood
            rates.append(app)
            rounds.append(avg_round)
        rates.sort(reverse=True)
        rounds.sort(reverse=False)
        for comp in comps_dict[star_threshold]:
            comps_dict[star_threshold][comp]["app_rank"] = rates.index(comps_dict[star_threshold][comp]["app_rate"]) + 1
            comps_dict[star_threshold][comp]["round_rank"] = rounds.index(comps_dict[star_threshold][comp]["round"]) + 1

    # # To check the list of weapons and artifacts for a comp
    # comp_tuples = [('Blade', 'Bronya', 'Yukong', 'Luocha'), ('Blade', 'Bronya', 'Silver Wolf', 'Luocha')]
    # for comp_tuple in comp_tuples:
    #     print(comp_tuple)
    #     print("   App: " + str(comps_dict[4][comp_tuple]["app_rate"]))
    #     print("   Own: " + str(comps_dict[4][comp_tuple]["own_rate"]))
    #     print("   Usage: " + str(comps_dict[4][comp_tuple]["usage_rate"]))
    #     print("   5* Count: " + str(comps_dict[4][comp_tuple]["5* count"]))
    #     # print("   Deepwood Holders: " + str(comps_dict[4][comp_tuple]["deepwood"]))
    #     # print("   Deepwood Rate: " + str(comps_dict[4][comp_tuple]["deepwood_rate"]))
    #     if comps_dict[4][comp_tuple]["5* count"] <= 1:
    #         print("   F2P App: " + str(comps_dict[4][comp_tuple]["app_rate"]))
    #     print()
    #     for i in comp_tuple:
    #         print(i + ": ")
    #         for weapon in comps_dict[4][comp_tuple][i]["weapon"]:
    #             print("   " + weapon + ": " + str(comps_dict[4][comp_tuple][i]["weapon"][weapon]))
    #         print()
    #         for artifacts in comps_dict[4][comp_tuple][i]["artifacts"]:
    #             print("   " + artifacts + ": " + str(comps_dict[4][comp_tuple][i]["artifacts"][artifacts]))
    #         print()

def comp_usages_write(comps_dict, filename, floor, info_char, sort_app):
    out_json = []
    out_comps = []
    outvar_comps = []
    var_comps = []
    exc_comps = []
    variations = {}
    if sort_app:
        threshold = app_rate_threshold
    else:
        threshold = app_rate_threshold_round

    # Sort the comps according to their usage rate
    for star_threshold in range(0,5):
        if sort_app:
            comps_dict[star_threshold] = dict(sorted(comps_dict[star_threshold].items(), key=lambda t: t[1]["app_rate"], reverse=True))
        else:
            comps_dict[star_threshold] = dict(sorted(comps_dict[star_threshold].items(), key=lambda t: t[1]["round"], reverse=False))
        comp_names = []
        # print(list(comps_dict[1]))
        for comp in comps_dict[star_threshold]:
            if info_char and filename not in comp:
                continue
            if star_threshold == 4:
                comp_name = comps_dict[star_threshold][comp]["comp_name"]
                alt_comp_name = comps_dict[star_threshold][comp]["alt_comp_name"]
                # Only one variation of each comp name is included,
                # unless if it's used for a character's infographic
                if comp_name not in comp_names or comp_name == "-" or info_char:
                    if comps_dict[star_threshold][comp]["app_rate"] >= threshold or (info_char and comps_dict[star_threshold][comp]["app_rate"] > char_app_rate_threshold):
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
                            # "own_rate": str(comps_dict[star_threshold][comp]["own_rate"]) + "%",
                            # "usage_rate": str(comps_dict[star_threshold][comp]["usage_rate"]) + "%"
                        }
                        out_comps_append["app_rate"] = str(comps_dict[star_threshold][comp]["app_rate"]) + "%"
                        out_comps_append["avg_round"] = str(comps_dict[star_threshold][comp]["round"])
                        if info_char:
                            if comp_name not in comp_names:
                                variations[comp_name] = 1
                                out_comps_append["variation"] = variations[comp_name]
                            else:
                                variations[comp_name] += 1
                                out_comps_append["variation"] = variations[comp_name]

                        out_comps_append["whale_count"] = str(len(comps_dict[star_threshold][comp]["whale_count"]))
                        out_comps_append["app_flat"] = str(len(comps_dict[star_threshold][comp]["players"]))
                        out_comps_append["uses"] = str(comps_dict[star_threshold][comp]["uses"])

                        if info_char:
                            if comp_name not in comp_names:
                                out_comps.append(out_comps_append)
                            else:
                                var_comps.append(out_comps_append)
                        else:
                            out_comps.append(out_comps_append)
                        comp_names.append(comp_name)

                    elif floor:
                        temp_comp_name = "-"
                        if alt_comp_name != "-":
                            temp_comp_name = alt_comp_name
                        else:
                            temp_comp_name = comp_name
                        exc_comps_append = {
                            "comp_name": temp_comp_name,
                            "char_1": comp[0],
                            "char_2": comp[1],
                            "char_3": comp[2],
                            "char_4": comp[3],
                            # "own_rate": str(comps_dict[star_threshold][comp]["own_rate"]) + "%",
                            # "usage_rate": str(comps_dict[star_threshold][comp]["usage_rate"]) + "%",
                        }
                        exc_comps_append["app_rate"] = str(comps_dict[star_threshold][comp]["app_rate"]) + "%"
                        exc_comps_append["avg_round"] = str(comps_dict[star_threshold][comp]["round"])
                        exc_comps.append(exc_comps_append)
                elif comp_name in comp_names:
                    temp_comp_name = "-"
                    if alt_comp_name != "-":
                        temp_comp_name = alt_comp_name
                    else:
                        temp_comp_name = comp_name
                    outvar_comps_append = {
                        "comp_name": temp_comp_name,
                        "char_1": comp[0],
                        "char_2": comp[1],
                        "char_3": comp[2],
                        "char_4": comp[3],
                        # "own_rate": str(comps_dict[star_threshold][comp]["own_rate"]) + "%",
                        # "usage_rate": str(comps_dict[star_threshold][comp]["usage_rate"]) + "%"
                    }
                    outvar_comps_append["app_rate"] = str(comps_dict[star_threshold][comp]["app_rate"]) + "%"
                    outvar_comps_append["avg_round"] = str(comps_dict[star_threshold][comp]["round"])
                    outvar_comps.append(outvar_comps_append)
            if not info_char and (
                comps_dict[star_threshold][comp]["app_rate"] >= json_threshold or filename not in ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2", "5-1", "5-2"]
            ):
                out = name_filter(comp, mode="out")
                out_json_dict = {
                    "char_one": out[0],
                    "char_two": out[1],
                    "char_three": out[2],
                    "char_four": out[3],
                }
                out_json_dict["app_rate"] = comps_dict[star_threshold][comp]["app_rate"]
                out_json_dict["rank"] = comps_dict[star_threshold][comp]["app_rank"]
                out_json_dict["avg_round"] = comps_dict[star_threshold][comp]["round"]
                out_json_dict["star_num"] = str(star_threshold)
                # out_json_dict["rank"] = comps_dict[star_threshold][comp]["round_rank"]
                out_json.append(out_json_dict)

    if info_char:
        out_comps += var_comps

    if archetype != "all":
        filename = filename + "_" + archetype

    if not(sort_app):
        filename = filename + "_rounds"

    # if not(whaleCheck):
    #     filename = filename + "_C1"

    # if floor and not info_char:
    #     # csv_writer = csv.writer(open("../rogue_results/f2p_app_" + filename + ".csv", 'w', newline=''))
    #     # for comps in f2p_comps:
    #     #     csv_writer.writerow(comps.values())
    #     with open("../rogue_results/var_" + filename + ".json", "w") as out_file:
    #         out_file.write(json.dumps(outvar_comps,indent=4))

    if floor:
        csv_writer = csv.writer(open("../rogue_results/comps_usage_" + filename + ".csv", 'w', newline=''))
        for comps in out_comps:
            csv_writer.writerow(comps.values())
        # with open("../rogue_results/exc_" + filename + ".json", "w") as out_file:
        #     out_file.write(json.dumps(exc_comps,indent=4))

    if not info_char and sort_app:
        # csv_writer = csv.writer(open("../rogue_results/csv/" + filename + ".csv", 'w', newline=''))
        # csv_writer.writerow(out_json[0].keys())
        # for comps in out_json:
        #     csv_writer.writerow(comps.values())

        # with open("../rogue_results/exc_" + filename + ".json", "w") as out_file:
        #     out_file.write(json.dumps(exc_comps,indent=4))
        with open("../rogue_results/json/" + filename + ".json", "w") as out_file:
            out_file.write(json.dumps(out_json,indent=4))

# def duo_usages(comps,
#                 players,
#                 usage,
#                 archetype,
#                 rooms=["6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2"],
#                 filename="duo_usages"):
#     duos_dict = used_duos(players, comps, rooms, usage, archetype)
#     duo_write(duos_dict, usage, filename, archetype)

# def used_duos(players, comps, rooms, usage, archetype, phase=RECENT_PHASE):
#     # Returns dictionary of all the duos used and how many times they were used
#     duos_dict = {}

#     for comp in comps:
#         if len(comp.characters) < 2 or comp.room not in rooms:
#             continue

#         foundchar = resetfind()
#         for char in comp.characters:
#             findchars(char, foundchar)
#         if not find_archetype(foundchar):
#             continue

#         # Permutate the duos, for example if Ganyu and Xiangling are used,
#         # two duos are used, Ganyu/Xiangling and Xiangling/Ganyu
#         duos = list(permutations(comp.characters, 2))
#         for duo in duos:
#             if duo not in duos_dict:
#                 duos_dict[duo] = 1
#             else:
#                 duos_dict[duo] += 1

#     sorted_duos = (sorted(
#         duos_dict.items(),
#         key = operator.itemgetter(1),
#         reverse=True
#     ))
#     duos_dict = {k: v for k, v in sorted_duos}

#     sorted_duos = {}
#     for duo in duos_dict:
#         if usage[4][duo[0]]["app_flat"] > 0:
#             # Calculate the appearance rate of the duo by dividing the appearance count
#             # of the duo with the appearance count of the first character
#             duos_dict[duo] = round(duos_dict[duo] * 100 / usage[4][duo[0]]["app_flat"], 2)
#             if duo[0] not in sorted_duos:
#                 sorted_duos[duo[0]] = []
#             sorted_duos[duo[0]].append([duo[1], duos_dict[duo]])

#     return sorted_duos

# def duo_write(duos_dict, usage, filename, archetype):
#     out_duos = []
#     for char in duos_dict:
#         if usage[4][char]["app_flat"] > 20:
#             out_duos_append = {
#                 "char": char,
#                 "round": usage[4][char]["round"],
#             }
#             for i in range(8):
#                 if i < len(duos_dict[char]):
#                     out_duos_append["app_rate_" + str(i + 1)] = str(duos_dict[char][i][1]) + "%"
#                     out_duos_append["char_" + str(i + 1)] = duos_dict[char][i][0]
#                 else:
#                     out_duos_append["app_rate_" + str(i + 1)] = "0%"
#                     out_duos_append["char_" + str(i + 1)] = "-"
#             out_duos.append(out_duos_append)
#     out_duos = sorted(out_duos, key=lambda t: t["round"], reverse = False)

#     if archetype != "all":
#         filename = filename + "_" + archetype
#     csv_writer = csv.writer(open("../rogue_results/" + filename + ".csv", 'w', newline=''))
#     count = 0
#     for duos in out_duos:
#         if count == 0:
#             csv_writer.writerow(duos.keys())
#             count += 1
#         csv_writer.writerow(duos.values())

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

# def comp_chars(row):
#     comp = []
#     for i in range(5, 9):
#         if row[i] != "":
#             comp.append(row[i])
#     return comp

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
