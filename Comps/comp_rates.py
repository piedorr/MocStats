import csv
import re
import time
import operator
import char_usage as cu
import pygsheets
import statistics
import os.path
from scipy.stats import skew
from itertools import permutations
from composition import Composition
from player_phase import PlayerPhase
from comp_rates_config import *
from archetypes import *

def main():
    global sample_size
    sample_size = {}
    start_time = time.time()
    print("start")

    global self_uids
    if os.path.isfile("../../uids.csv"):
        with open("../../uids.csv", 'r', encoding='UTF8') as f:
            reader = csv.reader(f, delimiter=',')
            self_uids = list(reader)[0]
    else:
        self_uids = []

    if os.path.exists("../data/raw_csvs_real/"):
        stats = open("../data/raw_csvs_real/" + RECENT_PHASE + ".csv")
    else:
        stats = open("../data/raw_csvs/" + RECENT_PHASE + ".csv")

    # uid_freq_comp will help detect duplicate UIDs
    reader = csv.reader(stats)
    col_names_comps = next(reader)
    comp_table = []
    uid_freq_comp = {}
    self_freq_comp = {}
    last_uid = "0"

    for line in reader:
        if skip_self and line[0] in self_uids:
            continue
        if line[0] != last_uid:
            skip_uid = False
            if line[0] in uid_freq_comp:
                skip_uid = True
                # print("duplicate UID in comp: " + line[0])
            elif int(''.join(filter(str.isdigit, line[1]))) > 5:
                uid_freq_comp[line[0]] = 1
                if line[0] in self_uids:
                    self_freq_comp[line[0]] = 1
        # else:
        #     uid_freq_comp[line[0]] += 1
        last_uid = line[0]
        if not skip_uid:
            comp_table.append(line)
    sample_size["all"] = {
        "total": len(uid_freq_comp),
        "self_report": len(self_freq_comp),
        "random": len(uid_freq_comp) - len(self_freq_comp)
    }

    if os.path.exists("../data/raw_csvs_real/"):
        stats = open("../data/raw_csvs_real/" + RECENT_PHASE + "_char.csv")
    else:
        stats = open("../data/raw_csvs/" + RECENT_PHASE + "_char.csv")

    # uid_freq_char and last_uid will help detect duplicate UIDs
    reader = csv.reader(stats)
    col_names = next(reader)
    player_table = []
    uid_freq_char = []
    last_uid = "0"

    # Append lines
    for line in reader:
        line[1] = RECENT_PHASE
        if line[0] in uid_freq_comp:
            if line[0] != last_uid:
                skip_uid = False
                if line[0] in uid_freq_char:
                    skip_uid = True
                    # print("duplicate UID in char: " + line[0])
                else:
                    uid_freq_char.append(line[0])
            last_uid = line[0]
            if not skip_uid:
                player_table.append(line)
    cur_time = time.time()
    print("done csv: ", (cur_time - start_time), "s")

    csv_writer = csv.writer(open("../char_results/uids.csv", 'w', newline=''))
    for uid in uid_freq_comp.keys():
        csv_writer.writerow([uid])
    # print(uid_freq_comp)
    # exit()

    all_comps = form_comps(col_names_comps, comp_table, alt_comps)
    all_players = form_players(player_table, all_comps, [RECENT_PHASE])
    cur_time = time.time()
    print("done form: ", (cur_time - start_time), "s")

    if "Char usages all stages" in run_commands:
        usage_low = char_usages(all_players, archetype, past_phase, filename="all", floor=True)
        cur_time = time.time()
        print("done char: ", (cur_time - start_time), "s")

    if "Char usages 6 - 10" in run_commands:
        global usage
        usage = char_usages(all_players, archetype, past_phase, rooms=["6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2"], filename="all", floor=True)
        duo_usages(all_comps, all_players, usage, archetype)
        # appearances = {}
        # rounds = {}
        # for star_num in usage:
        #     appearances[star_num] = dict(sorted(usage[star_num].items(), key=lambda t: t[1]["app"], reverse=True))
        #     rounds[star_num] = dict(sorted(usage[star_num].items(), key=lambda t: t[1]["round"], reverse=False))
        #     for char in usage[star_num]:
        #         appearances[star_num][char] = {
        #             "app": usage[star_num][char]["app"],
        #             "rarity": usage[star_num][char]["rarity"],
        #             "diff": usage[star_num][char]["diff"]
        #         }
        #         if usage[star_num][char]["round"] == 0.0:
        #             continue
        #         rounds[star_num][char] = {
        #             "round": usage[star_num][char]["round"],
        #             "rarity": usage[star_num][char]["rarity"],
        #             "diff": usage[star_num][char]["diff_rounds"]
        #         }
        # with open("../char_results/appearance_top.json", "w") as out_file:
        #     out_file.write(json.dumps(appearances,indent=4))
        # with open("../char_results/rounds_top.json", "w") as out_file:
        #     out_file.write(json.dumps(rounds,indent=4))
        cur_time = time.time()
        print("done char 6 - 10: ", (cur_time - start_time), "s")

    if "Char usages for each stage" in run_commands:
        char_chambers = {
            "all": {}
        }
        for star_num in usage:
            char_chambers["all"][star_num] = usage[star_num].copy()
        for room in ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2", "5-1", "5-2", "6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2"]:
            char_chambers[room] = char_usages(all_players, archetype, past_phase, rooms=[room], filename=room, offset=2)
        appearances = {}
        rounds = {}
        for room in char_chambers:
            appearances[room] = {}
            rounds[room] = {}
            for star_num in char_chambers[room]:
                appearances[room][star_num] = dict(sorted(char_chambers[room][star_num].items(), key=lambda t: t[1]["app"], reverse=True))
                rounds[room][star_num] = dict(sorted(char_chambers[room][star_num].items(), key=lambda t: t[1]["round"], reverse=False))
                for char in char_chambers[room][star_num]:
                    appearances[room][star_num][char] = {
                        "app": char_chambers[room][star_num][char]["app"],
                        "rarity": char_chambers[room][star_num][char]["rarity"],
                        "diff": char_chambers[room][star_num][char]["diff"]
                    }
                    if char_chambers[room][star_num][char]["round"] == 0.0:
                        continue
                    rounds[room][star_num][char] = {
                        "round": char_chambers[room][star_num][char]["round"],
                        "rarity": char_chambers[room][star_num][char]["rarity"],
                        "diff": char_chambers[room][star_num][char]["diff_rounds"]
                    }
        with open("../char_results/appearance.json", "w") as out_file:
            out_file.write(json.dumps(appearances,indent=4))
        with open("../char_results/rounds.json", "w") as out_file:
            out_file.write(json.dumps(rounds,indent=4))
        cur_time = time.time()
        print("done char stage: ", (cur_time - start_time), "s")

    if "Char usages for each stage (combined)" in run_commands:
        char_chambers = {
            "all": {}
        }
        for star_num in usage:
            char_chambers["all"][star_num] = usage[star_num].copy()
        for room in [["1-1", "1-2"], ["2-1", "2-2"], ["3-1", "3-2"], ["4-1", "4-2"], ["5-1", "5-2"], ["6-1", "6-2"], ["7-1", "7-2"], ["8-1", "8-2"], ["9-1", "9-2"], ["10-1", "10-2"]]:
            char_chambers[room[0]] = char_usages(all_players, archetype, past_phase, rooms=room, filename=room[0].split('-')[0])
        appearances = {}
        rounds = {}
        for room in char_chambers:
            appearances[room] = {}
            rounds[room] = {}
            for star_num in char_chambers[room]:
                appearances[room][star_num] = dict(sorted(char_chambers[room][star_num].items(), key=lambda t: t[1]["app"], reverse=True))
                rounds[room][star_num] = dict(sorted(char_chambers[room][star_num].items(), key=lambda t: t[1]["round"], reverse=False))
                for char in char_chambers[room][star_num]:
                    appearances[room][star_num][char] = {
                        "app": char_chambers[room][star_num][char]["app"],
                        "rarity": char_chambers[room][star_num][char]["rarity"],
                        "diff": char_chambers[room][star_num][char]["diff"]
                    }
                    if char_chambers[room][star_num][char]["round"] == 0.0:
                        continue
                    rounds[room][star_num][char] = {
                        "round": char_chambers[room][star_num][char]["round"],
                        "rarity": char_chambers[room][star_num][char]["rarity"],
                        "diff": char_chambers[room][star_num][char]["diff_rounds"]
                    }
        with open("../char_results/appearance_combine.json", "w") as out_file:
            out_file.write(json.dumps(appearances,indent=4))
        with open("../char_results/rounds_combine.json", "w") as out_file:
            out_file.write(json.dumps(rounds,indent=4))
        cur_time = time.time()
        print("done char stage (combine): ", (cur_time - start_time), "s")

    if "Comp usage all stages" in run_commands:
        comp_usages(all_comps, all_players, whaleCheck, whaleSigWeap, sigWeaps, rooms=["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2", "5-1", "5-2", "6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2"], filename="all", floor=True)
        cur_time = time.time()
        print("done comp all: ", (cur_time - start_time), "s")

    if "Comp usage 6 - 10" in run_commands:
        comp_usages(all_comps, all_players, whaleCheck, whaleSigWeap, sigWeaps, rooms=["6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2"], filename="top", floor=True)
        cur_time = time.time()
        print("done comp 6 - 10: ", (cur_time - start_time), "s")

    if "Comp usages for each stage" in run_commands:
        for room in ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2", "5-1", "5-2", "6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2"]:
            comp_usages(all_comps, all_players, whaleCheck, whaleSigWeap, sigWeaps, rooms=[room], filename=room, offset=2)
        with open("../char_results/demographic.json", "w") as out_file:
            out_file.write(json.dumps(sample_size,indent=4))
        cur_time = time.time()
        print("done comp stage: ", (cur_time - start_time), "s")

    if "Character specific infographics" in run_commands:
        comp_usages(all_comps, all_players, whaleCheck, whaleSigWeap, sigWeaps, rooms=["6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2"], filename=char_infographics, info_char=True, floor=True)
        cur_time = time.time()
        print("done char infographics: ", (cur_time - start_time), "s")

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
    if len(chamber_num) > 1:
        if chamber_num[1] == "1":
            sample_size[chamber_num[0]] = {
                "total": total_comps,
                "self_report": total_self_comps,
                "random": total_comps - total_self_comps
            }
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

def duo_usages(comps,
                players,
                usage,
                archetype,
                rooms=["6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2"],
                filename="duo_usages"):
    duos_dict = used_duos(players, comps, rooms, usage, archetype)
    duo_write(duos_dict, usage, filename, archetype)

def used_duos(players, comps, rooms, usage, archetype, phase=RECENT_PHASE):
    # Returns dictionary of all the duos used and how many times they were used
    duos_dict = {}

    for comp in comps:
        if len(comp.characters) < 2 or comp.room not in rooms:
            continue

        foundchar = resetfind()
        for char in comp.characters:
            findchars(char, foundchar)
        if not find_archetype(foundchar):
            continue

        # Permutate the duos, for example if Ganyu and Xiangling are used,
        # two duos are used, Ganyu/Xiangling and Xiangling/Ganyu
        duos = list(permutations(comp.characters, 2))
        for duo in duos:
            if duo not in duos_dict:
                duos_dict[duo] = 1
            else:
                duos_dict[duo] += 1

    sorted_duos = (sorted(
        duos_dict.items(),
        key = operator.itemgetter(1),
        reverse=True
    ))
    duos_dict = {k: v for k, v in sorted_duos}

    sorted_duos = {}
    for duo in duos_dict:
        if usage[4][duo[0]]["app_flat"] > 0:
            # Calculate the appearance rate of the duo by dividing the appearance count
            # of the duo with the appearance count of the first character
            duos_dict[duo] = round(duos_dict[duo] * 100 / usage[4][duo[0]]["app_flat"], 2)
            if duo[0] not in sorted_duos:
                sorted_duos[duo[0]] = []
            sorted_duos[duo[0]].append([duo[1], duos_dict[duo]])

    return sorted_duos

def char_usages(players,
                archetype,
                past_phase,
                rooms=["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2", "5-1", "5-2", "6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2"],
                filename="char_usages",
                offset=1,
                info_char=False,
                floor=False):
    # own = cu.ownership(players, chambers = rooms)
    own = {}
    app = cu.appearances(players, own, archetype, chambers = rooms, offset = offset, info_char = info_char)
    chars_dict = cu.usages(own, app, past_phase, filename, chambers = rooms, offset = offset)
    # # Print the list of weapons and artifacts used for a character
    # if floor:
    #     print(app[RECENT_PHASE][filename])
    if rooms == ["6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2"]:
        char_usages_write(chars_dict[4], filename, floor, archetype)
    return chars_dict

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

                        # j = 1
                        # if floor:
                        #     for i in comp:
                        #         if len(list(comps_dict[star_threshold][comp][i]["weapon"])):
                        #             out_comps_append["weapon_" + str(j)] = list(comps_dict[star_threshold][comp][i]["weapon"])[0]
                        #         else:
                        #             out_comps_append["weapon_" + str(j)] = "-"
                        #         if len(list(comps_dict[star_threshold][comp][i]["artifacts"])):
                        #             out_comps_append["artifact_" + str(j)] = list(comps_dict[star_threshold][comp][i]["artifacts"])[0]
                        #         else:
                        #             out_comps_append["artifact_" + str(j)] = "-"
                        #         j += 1
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
    #     # csv_writer = csv.writer(open("../comp_results/f2p_app_" + filename + ".csv", 'w', newline=''))
    #     # for comps in f2p_comps:
    #     #     csv_writer.writerow(comps.values())
    #     with open("../comp_results/var_" + filename + ".json", "w") as out_file:
    #         out_file.write(json.dumps(outvar_comps,indent=4))

    if floor:
        csv_writer = csv.writer(open("../comp_results/comps_usage_" + filename + ".csv", 'w', newline=''))
        for comps in out_comps:
            csv_writer.writerow(comps.values())
        # with open("../comp_results/exc_" + filename + ".json", "w") as out_file:
        #     out_file.write(json.dumps(exc_comps,indent=4))

    if not info_char and sort_app:
        # csv_writer = csv.writer(open("../comp_results/csv/" + filename + ".csv", 'w', newline=''))
        # csv_writer.writerow(out_json[0].keys())
        # for comps in out_json:
        #     csv_writer.writerow(comps.values())

        # with open("../comp_results/exc_" + filename + ".json", "w") as out_file:
        #     out_file.write(json.dumps(exc_comps,indent=4))
        with open("../comp_results/json/" + filename + ".json", "w") as out_file:
            out_file.write(json.dumps(out_json,indent=4))

def duo_write(duos_dict, usage, filename, archetype):
    out_duos = []
    for char in duos_dict:
        if usage[4][char]["app_flat"] > 20:
            out_duos_append = {
                "char": char,
                "round": usage[4][char]["round"],
            }
            for i in range(8):
                if i < len(duos_dict[char]):
                    out_duos_append["app_rate_" + str(i + 1)] = str(duos_dict[char][i][1]) + "%"
                    out_duos_append["char_" + str(i + 1)] = duos_dict[char][i][0]
                else:
                    out_duos_append["app_rate_" + str(i + 1)] = "0%"
                    out_duos_append["char_" + str(i + 1)] = "-"
            out_duos.append(out_duos_append)
    out_duos = sorted(out_duos, key=lambda t: t["round"], reverse = False)

    if archetype != "all":
        filename = filename + "_" + archetype
    csv_writer = csv.writer(open("../comp_results/" + filename + ".csv", 'w', newline=''))
    count = 0
    for duos in out_duos:
        if count == 0:
            csv_writer.writerow(duos.keys())
            count += 1
        csv_writer.writerow(duos.values())

def char_usages_write(chars_dict, filename, floor, archetype):
    out_chars = []
    weap_len = 10
    arti_len = 10
    planar_len = 5
    chars_dict = dict(sorted(chars_dict.items(), key=lambda t: t[1]["round"], reverse=False))
    for char in chars_dict:
        out_chars_append = {
            "char": char,
            "app_rate": str(chars_dict[char]["app"]) + "%",
            "avg_round": str(chars_dict[char]["round"]),
            # "usage_rate": str(chars_dict[char]["usage"]) + "%",
            # "own_rate": str(chars_dict[char]["own"]) + "%",
            "rarity": chars_dict[char]["rarity"],
            "diff": str(chars_dict[char]["diff"]) + "%",
            "diff_rounds": str(chars_dict[char]["diff_rounds"])
        }
        for i in ["app_rate","diff","diff_rounds"]:
            if out_chars_append[i] == "-%":
                out_chars_append[i] = "-"
        if (list(chars_dict[char]["weapons"])):
            for i in range(weap_len):
                out_chars_append["weapon_" + str(i + 1)] = list(chars_dict[char]["weapons"])[i]
                out_chars_append["weapon_" + str(i + 1) + "_app"] = str(list(chars_dict[char]["weapons"].values())[i]) + "%"
                if out_chars_append["weapon_" + str(i + 1) + "_app"] == "-%":
                    out_chars_append["weapon_" + str(i + 1) + "_app"] = "-"
            for i in range(arti_len):
                out_chars_append["artifact_" + str(i + 1)] = list(chars_dict[char]["artifacts"])[i]
                if out_chars_append["artifact_" + str(i + 1)] == "Flex":
                    out_chars_append["artifact_" + str(i + 1)] = str(i)
                out_chars_append["artifact_" + str(i + 1) + "_app"] = str(list(chars_dict[char]["artifacts"].values())[i]) + "%"
                if out_chars_append["artifact_" + str(i + 1) + "_app"] == "-%":
                    out_chars_append["artifact_" + str(i + 1) + "_app"] = "-"
            for i in range(planar_len):
                out_chars_append["planar_" + str(i + 1)] = list(chars_dict[char]["planars"])[i]
                if out_chars_append["planar_" + str(i + 1)] == "Flex":
                    out_chars_append["planar_" + str(i + 1)] = str(i)
                out_chars_append["planar_" + str(i + 1) + "_app"] = str(list(chars_dict[char]["planars"].values())[i]) + "%"
                if out_chars_append["planar_" + str(i + 1) + "_app"] == "-%":
                    out_chars_append["planar_" + str(i + 1) + "_app"] = "-"
            # for i in range(7):
            #     out_chars_append["use_" + str(i)] = str(list(list(chars_dict[char]["cons_usage"].values())[i].values())[2]) + "%"
            #     if out_chars_append["use_" + str(i)] == "-%":
            #         out_chars_append["use_" + str(i)] = "-"
            #     out_chars_append["own_" + str(i)] = str(list(list(chars_dict[char]["cons_usage"].values())[i].values())[1]) + "%"
            #     if out_chars_append["own_" + str(i)] == "-%":
            #         out_chars_append["own_" + str(i)] = "-"
            for i in range(7):
                out_chars_append["app_" + str(i)] = str(list(list(chars_dict[char]["cons_usage"].values())[i].values())[0]) + "%"
                if out_chars_append["app_" + str(i)] == "-%":
                    out_chars_append["app_" + str(i)] = "-"
        else:
            for i in range(weap_len):
                out_chars_append["weapon_" + str(i + 1)] = str(i)
                out_chars_append["weapon_" + str(i + 1) + "_app"] = "-"
            for i in range(arti_len):
                out_chars_append["artifact_" + str(i + 1)] = str(i)
                out_chars_append["artifact_" + str(i + 1) + "_app"] = "-"
            for i in range(planar_len):
                out_chars_append["planar_" + str(i + 1)] = str(i)
                out_chars_append["planar_" + str(i + 1) + "_app"] = "-"
            # for i in range(7):
            #     out_chars_append["use_" + str(i)] = str(list(list(chars_dict[char]["cons_usage"].values())[i].values())[2]) + "%"
            #     if out_chars_append["use_" + str(i)] == "-%":
            #         out_chars_append["use_" + str(i)] = "-"
            #     out_chars_append["own_" + str(i)] = str(list(list(chars_dict[char]["cons_usage"].values())[i].values())[1]) + "%"
            #     if out_chars_append["own_" + str(i)] == "-%":
            #         out_chars_append["own_" + str(i)] = "-"
            for i in range(7):
                out_chars_append["app_" + str(i)] = "0.0%"
        out_chars_append["cons_avg"] = chars_dict[char]["cons_avg"]
        out_chars_append["sample"] = chars_dict[char]["sample"]
        out_chars.append(out_chars_append)
        if char == filename:
            break

    if archetype != "all":
        filename = filename + "_" + archetype
    csv_writer = csv.writer(open("../char_results/" + filename + ".csv", 'w', newline=''))
    count = 0
    for chars in out_chars:
        if count == 0:
            header = chars.keys()
            csv_writer.writerow(header)
            count += 1
        csv_writer.writerow(chars.values())

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

def comp_chars(row):
    comp = []
    for i in range(5, 9):
        if row[i] != "":
            comp.append(row[i])
    return comp

def form_comps(col_names, table, info_char):
    round_num = col_names.index('round_num')
    star_num = col_names.index('star_num')
    room = col_names.index('node')
    floor = col_names.index('floor')
    comps = []

    for row in table:
        comp = Composition(row[0], comp_chars(row), RECENT_PHASE, row[round_num], row[star_num],
                           str(re.findall('[0-9]+', row[floor])[0]) + "-" + str(row[room]), info_char)
        comps.append(comp)

    return comps

def add_players_comps(players, comps):
    for comp in comps:
        if comp.phase in players:
            if comp.player not in players[comp.phase]:
                players[comp.phase][comp.player] = PlayerPhase(comp.player, comp.phase)
            players[comp.phase][comp.player].add_comp(comp)

def form_players(table, comps, phases):
    # index 0 is player id, 1 is phase, 2 is character name, 3 is character level
    # 4 is constellation, 5 is weapons, 6 is artifacts
    players = {}
    for phase in phases:
        players[phase] = {}

    phase = table[0][1]
    id = table[0][0]
    player = PlayerPhase(id, phase)
    for row in table:
        if row[0] != id or row[1] != phase:
            players[phase][id] = player
            id = row[0]
            phase = row[1]
            player = PlayerPhase(id, phase)
        player.add_character(row[2], row[3], row[4], row[5], row[6], row[7], row[8])
    players[phase][id] = player

    add_players_comps(players, comps)
    return players

main()
