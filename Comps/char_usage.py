import json
import os.path
import pandas as pd
import operator
import csv
import statistics
import matplotlib
import matplotlib.pyplot as plt
import warnings
from scipy.stats import skew, trim_mean
from archetypes import *
from comp_rates_config import RECENT_PHASE, pf_mode

warnings.filterwarnings("ignore", category=RuntimeWarning)
if pf_mode:
    ROOMS = ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2"]
else:
    ROOMS = ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2", "5-1", "5-2", "6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2", "11-1", "11-2", "12-1", "12-2"]
global gear_app_threshold
gear_app_threshold = 0
with open('../data/characters.json') as char_file:
    CHARACTERS = json.load(char_file)

def ownership(players, chambers=ROOMS):
    # Create the dict
    owns = {}
    for phase in players:
        owns[phase] = {}

    # Add a sub sub dict for each char
    for phase in owns:
        for character in CHARACTERS:
            owns[phase][character] = {
                "flat": 0,
                "percent": 0.00,
                "cons_freq": {}
            }
            for i in range (7):
                owns[phase][character]["cons_freq"][i] = {
                    "flat": 0,
                    "percent": 0,
                }

        # Tally the amount that each char is owned
        total = 0
        for player in players[phase]:
            total += 1
            for character in players[phase][player].owned.keys():
                owns[phase][character]["flat"] += 1
                owns[phase][character]["cons_freq"][
                    players[phase][player].owned[character]["cons"]
                ]["flat"] += 1
        total /= 100.0
        for char in owns[phase]:
            own_flat = owns[phase][char]["flat"] / 100.0
            if own_flat > 0:
                if "Trailblzer" in char:
                    # # Cons usage is only added for floor 12
                    # if (chambers == ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2", "5-1", "5-2", "6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2", "11-1", "11-2", "12-1", "12-2"]):
                    for cons in owns[phase][char]["cons_freq"]:
                        # if owns[phase][char]["cons_freq"][cons]["flat"] > 15:
                        owns[phase][char]["cons_freq"][cons]["percent"] = int(round(
                            owns[phase][char]["cons_freq"][cons]["flat"] / own_flat, 0
                        ))
                        # else:
                        #     owns[phase][char]["cons_freq"][cons]["percent"] = "-"
                    owns[phase][char]["percent"] = 100.0
                    owns[phase][char]["flat"] = int(total * 100)

                else:
                    # # Cons usage is only added for floor 12
                    # if (chambers == ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2", "5-1", "5-2", "6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2", "11-1", "11-2", "12-1", "12-2"]):
                    for cons in owns[phase][char]["cons_freq"]:
                        # if owns[phase][char]["cons_freq"][cons]["flat"] > 15:
                        owns[phase][char]["cons_freq"][cons]["percent"] = int(round(
                            owns[phase][char]["cons_freq"][cons]["flat"] / total, 0
                        ))
                        # else:
                        #     owns[phase][char]["cons_freq"][cons]["percent"] = "-"
                    owns[phase][char]["percent"] = round(
                        owns[phase][char]["flat"] / total, 2
                    )
    
    # print(json.dumps(owns,indent=4))

    return owns

def appearances(players, owns, archetype, chambers=ROOMS, offset=1, info_char=False):
    appears = {}
    players_chars = {}
    if os.path.exists("../char_results/duo_check.csv"):
        with open("../char_results/duo_check.csv", 'r') as f:
            valid_duo_dps = list(csv.reader(f, delimiter=','))
    else:
        valid_duo_dps = []

    for star_num in range(0, 5):
        total_battle = 0
        appears[star_num] = {}
        players_chars[star_num] = {}
        comp_error = False
        error_comps = []

        for character in CHARACTERS:
            players_chars[star_num][character] = set()
            appears[star_num][character] = {
                "flat": 0,
                "round": {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": [], "10": [], "11": [], "12": []},
                "owned": 0,
                "percent": 0.00,
                "avg_round": 0.00,
                "std_dev_round": 0.00,
                "weap_freq": {},
                "arti_freq": {},
                "planar_freq": {},
                "cons_freq": {},
                "cons_avg": 0.00,
                "sample": 0
            }
            for i in range (7):
                appears[star_num][character]["cons_freq"][i] = {
                    "flat": 0,
                    "round": {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": [], "10": [], "11": [], "12": []},
                    "percent": 0,
                    "avg_round": 0.00
                }

        # There's probably a better way to cache these things
        for player in players[RECENT_PHASE].values():
            for chamber in player.chambers:
                if chamber not in chambers:
                    continue
                if star_num != 4 and player.chambers[chamber].star_num != star_num:
                    continue
                total_battle += 1
                # foundchar = resetfind()
                whaleComp = False
                sustainCount = 0
                dpsCount = 0
                foundDuo = []
                for duo_dps in valid_duo_dps:
                    if set(duo_dps).issubset(player.chambers[chamber].characters):
                        foundDuo = duo_dps
                        break

                for char in player.chambers[chamber].characters:
                    if CHARACTERS[char]["availability"] == "Limited 5*":
                        if char in player.owned:
                            if player.owned[char]["cons"] > 0:
                                whaleComp = True
                    if CHARACTERS[char]["role"] == "Sustain":
                        sustainCount += 1
                    if CHARACTERS[char]["role"] == "Damage Dealer":
                        dpsCount += 1
                        if char == "Topaz & Numby":
                            for char_fua in ["Dr. Ratio", "Clara", "Jing Yuan", "Himeko", "Kafka", "Blade", "Herta", "Xueyi"]:
                                if char_fua in player.chambers[chamber].characters:
                                    dpsCount -= 1
                                    break
                    if "Kafka" not in player.chambers[chamber].characters:
                        if char in ["Sampo", "Black Swan", "Luka", "Guinaifen"]:
                            dpsCount += 1
                    elif char == "Serval":
                        dpsCount -= 1
                if sustainCount == 0 and pf_mode:
                    sustainCount = 1
                if "Ruan Mei" in player.chambers[chamber].characters:
                    dpsCount = 1
                # dpsCount = 1

                # findchars(char, foundchar)
                # if find_archetype(foundchar):
                # if player.chambers[chamber].characters == ['Kafka', 'Sampo', 'Silver Wolf', 'Bailu']:
                if True:
                    for char in player.chambers[chamber].characters:
                        # to print the amount of players using a character, for char infographics
                        if len(chambers) > 2 or (pf_mode and chambers == ["4-1", "4-2"]):
                            players_chars[star_num][char].add(player.player)

                        char_name = char
                        if foundDuo:
                            # if foundDuo[0] == char_name:
                            if char_name in foundDuo:
                                dpsCount = 1

                        appears[star_num][char_name]["flat"] += 1
                        if not whaleComp and (sustainCount == 1 or char_name in ["Fire Trailblazer", "March 7th"]) and dpsCount == 1:
                            if CHARACTERS[char]["availability"] == "Limited 5*":
                                appears[star_num][char_name]["cons_freq"][0]["round"][list(str(chamber).split("-"))[0]].append(player.chambers[chamber].round_num)
                            appears[star_num][char_name]["round"][list(str(chamber).split("-"))[0]].append(player.chambers[chamber].round_num)
                        # In case of character in comp data missing from character data
                        if pf_mode:
                            if chambers != ["4-1", "4-2"]:
                                continue
                        elif len(chambers) < 3:
                            continue
                        if char not in player.owned or star_num != 4:
                            # print("Comp data missing from character data: " + str(player.player) + ", " + str(char))
                            # if player.player not in error_comps:
                            #     error_comps.append(player.player)
                            # comp_error = True
                            continue
                        # if player.owned[char]["weapon"] != "Patience Is All You Need":
                        #     continue
                        # if player.owned[char]["cons"] > 0:
                        #     continue
                        appears[star_num][char_name]["owned"] += 1
                        appears[star_num][char_name]["cons_freq"][player.owned[char]["cons"]]["flat"] += 1
                        if (sustainCount == 1 or char_name in ["Fire Trailblazer", "March 7th"]) and dpsCount == 1:
                            if CHARACTERS[char]["availability"] == "Limited 5*":
                                if player.owned[char]["cons"] != 0:
                                    appears[star_num][char_name]["cons_freq"][player.owned[char]["cons"]]["round"][list(str(chamber).split("-"))[0]].append(player.chambers[chamber].round_num)
                            elif not whaleComp:
                                appears[star_num][char_name]["cons_freq"][player.owned[char]["cons"]]["round"][list(str(chamber).split("-"))[0]].append(player.chambers[chamber].round_num)
                        appears[star_num][char_name]["cons_avg"] += player.owned[char]["cons"]

                        if player.owned[char]["weapon"] != "":
                            if player.owned[char]["weapon"] not in appears[star_num][char_name]["weap_freq"]:
                                appears[star_num][char_name]["weap_freq"][player.owned[char]["weapon"]] = {
                                    "flat": 0,
                                    "round": {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": [], "10": [], "11": [], "12": []},
                                    "percent": 0,
                                    "avg_round": 0.00
                                }
                            appears[star_num][char_name]["weap_freq"][player.owned[char]["weapon"]]["flat"] += 1
                            if not whaleComp and (sustainCount == 1 or char_name in ["Fire Trailblazer", "March 7th"]) and dpsCount == 1:
                                appears[star_num][char_name]["weap_freq"][player.owned[char]["weapon"]]["round"][list(str(chamber).split("-"))[0]].append(player.chambers[chamber].round_num)

                        if player.owned[char]["artifacts"] != "":
                            if player.owned[char]["artifacts"] not in appears[star_num][char_name]["arti_freq"]:
                                appears[star_num][char_name]["arti_freq"][player.owned[char]["artifacts"]] = {
                                    "flat": 0,
                                    "round": {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": [], "10": [], "11": [], "12": []},
                                    "percent": 0,
                                    "avg_round": 0.00
                                }
                            appears[star_num][char_name]["arti_freq"][player.owned[char]["artifacts"]]["flat"] += 1
                            if not whaleComp and (sustainCount == 1 or char_name in ["Fire Trailblazer", "March 7th"]) and dpsCount == 1:
                                appears[star_num][char_name]["arti_freq"][player.owned[char]["artifacts"]]["round"][list(str(chamber).split("-"))[0]].append(player.chambers[chamber].round_num)

                        if player.owned[char]["planars"] != "":
                            if player.owned[char]["planars"] not in appears[star_num][char_name]["planar_freq"]:
                                appears[star_num][char_name]["planar_freq"][player.owned[char]["planars"]] = {
                                    "flat": 0,
                                    "round": {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": [], "10": [], "11": [], "12": []},
                                    "percent": 0,
                                    "avg_round": 0.00
                                }
                            appears[star_num][char_name]["planar_freq"][player.owned[char]["planars"]]["flat"] += 1
                            if not whaleComp and (sustainCount == 1 or char_name in ["Fire Trailblazer", "March 7th"]) and dpsCount == 1:
                                appears[star_num][char_name]["planar_freq"][player.owned[char]["planars"]]["round"][list(str(chamber).split("-"))[0]].append(player.chambers[chamber].round_num)

        if comp_error:
            df_char = pd.read_csv('../data/phase_characters.csv')
            df_spiral = pd.read_csv('../data/compositions.csv')
            df_char = df_char[~df_char['uid'].isin(error_comps)]
            df_spiral = df_spiral[~df_spiral['uid'].isin(error_comps)]
            df_char.to_csv("phase_characters.csv", index=False)
            df_spiral.to_csv("compositions.csv", index=False)
            raise ValueError("There are missing comps from character data.")

        total = total_battle * offset/200.0
        all_rounds = {}
        for char in appears[star_num]:
            all_rounds[char] = {}
            # # to print the amount of players using a character
            # print(str(char) + ": " + str(len(players_chars[star_num][char])))
            if total > 0:
                appears[star_num][char]["percent"] = round(
                    appears[star_num][char]["flat"] / total, 2
                )
            else:
                appears[star_num][char]["percent"] = 0.00
            if appears[star_num][char]["flat"] >= 10:
                avg_round = []
                std_dev_round = []
                uses_room = {}
                for room_num in range(1,13):
                    if room_num >= 10:
                        all_rounds[char][room_num] = {}
                        for i in range(41):
                            all_rounds[char][room_num][i] = 0
                    if (appears[star_num][char]["round"][str(room_num)]):
                        if room_num >= 10:
                            for round_num_iter in appears[star_num][char]["round"][str(room_num)]:
                                all_rounds[char][room_num][round_num_iter] += 1
                        uses_room[room_num] = len(appears[star_num][char]["round"][str(room_num)])
                        if len(appears[star_num][char]["round"][str(room_num)]) > 1:
                            std_dev_round.append(statistics.stdev(appears[star_num][char]["round"][str(room_num)]))
                            skewness = skew(appears[star_num][char]["round"][str(room_num)], axis=0, bias=True)
                            if abs(skewness) > 0.8:
                                avg_round.append(trim_mean(appears[star_num][char]["round"][str(room_num)], 0.25))
                            else:
                                avg_round.append(statistics.mean(appears[star_num][char]["round"][str(room_num)]))
                        else:
                            std_dev_round.append(0)
                            avg_round.append(statistics.mean(appears[star_num][char]["round"][str(room_num)]))
                        # avg_round.append(statistics.mean(appears[star_num][char]["round"][str(room_num)]))
                        # avg_round += appears[star_num][char]["round"][str(room_num)]

                is_count_cycles = True
                if not uses_room:
                    is_count_cycles = False
                if len(chambers) > 2 or (pf_mode and chambers == ["4-1", "4-2"]):
                    if len(uses_room) != len(chambers)/2:
                        is_count_cycles = False
                for room_num in uses_room:
                    if uses_room[room_num] < 10:
                        is_count_cycles = False

                # if avg_round:
                if is_count_cycles:
                    appears[star_num][char]["avg_round"] = round(statistics.mean(avg_round), 2)
                    appears[star_num][char]["std_dev_round"] = round(statistics.mean(std_dev_round), 2)
                    if pf_mode:
                        appears[star_num][char]["avg_round"] = round(appears[star_num][char]["avg_round"])
                        appears[star_num][char]["std_dev_round"] = round(appears[star_num][char]["std_dev_round"])
                else:
                    appears[star_num][char]["avg_round"] = 99.99
                    if pf_mode:
                        appears[star_num][char]["avg_round"] = 0
            else:
                appears[star_num][char]["avg_round"] = 99.99
                if pf_mode:
                    appears[star_num][char]["avg_round"] = 0

            # if (chambers == ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2", "5-1", "5-2", "6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2", "11-1", "11-2", "12-1", "12-2"]):
            appears[star_num][char]["sample"] = len(players_chars[star_num][char])

            if pf_mode:
                if chambers != ["4-1", "4-2"]:
                    continue
            elif len(chambers) < 3:
                continue
            if star_num != 4:
                continue
            # Calculate constellations
            app_flat = appears[star_num][char]["owned"] / 100.0
            # if owns[star_num][char]["flat"] > 0:
            if appears[star_num][char]["owned"] > 0:
                appears[star_num][char]["cons_avg"] = round(
                    appears[star_num][char]["cons_avg"] / appears[star_num][char]["owned"], 2
                )
            for cons in appears[star_num][char]["cons_freq"]:
                if appears[star_num][char]["cons_freq"][cons]["flat"] > 0:
                    appears[star_num][char]["cons_freq"][cons]["percent"] = round(
                        appears[star_num][char]["cons_freq"][cons]["flat"] / app_flat, 2
                    )
                    avg_round = []
                    for room_num in range(1,13):
                        if (appears[star_num][char]["cons_freq"][cons]["round"][str(room_num)]):
                            if appears[star_num][char]["cons_freq"][cons]["flat"] > 1:
                                skewness = skew(appears[star_num][char]["cons_freq"][cons]["round"][str(room_num)], axis=0, bias=True)
                                if abs(skewness) > 0.8:
                                    avg_round.append(trim_mean(appears[star_num][char]["cons_freq"][cons]["round"][str(room_num)], 0.25))
                                else:
                                    avg_round.append(statistics.mean(appears[star_num][char]["cons_freq"][cons]["round"][str(room_num)]))
                            else:
                                avg_round.append(statistics.mean(appears[star_num][char]["cons_freq"][cons]["round"][str(room_num)]))
                            # avg_round += appears[star_num][char]["cons_freq"][cons]["round"][str(room_num)]
                            # avg_round.append(statistics.mean(appears[star_num][char]["cons_freq"][cons]["round"][str(room_num)]))
                    if avg_round:
                        appears[star_num][char]["cons_freq"][cons]["avg_round"] = round(statistics.mean(avg_round), 2)
                        if pf_mode:
                            appears[star_num][char]["cons_freq"][cons]["avg_round"] = round(appears[star_num][char]["cons_freq"][cons]["avg_round"])
                    else:
                        appears[star_num][char]["cons_freq"][cons]["avg_round"] = 99.99
                        if pf_mode:
                            appears[star_num][char]["cons_freq"][cons]["avg_round"] = 0
                else:
                    appears[star_num][char]["cons_freq"][cons]["percent"] = 0.00
                    appears[star_num][char]["cons_freq"][cons]["avg_round"] = 99.99
                    if pf_mode:
                        appears[star_num][char]["cons_freq"][cons]["avg_round"] = 0

            # Calculate weapons
            sorted_weapons = (sorted(
                appears[star_num][char]["weap_freq"].items(),
                key = lambda t: t[1]["flat"],
                reverse=True
            ))
            appears[star_num][char]["weap_freq"] = {k: v for k, v in sorted_weapons}
            for weapon in appears[star_num][char]["weap_freq"]:
                # If a gear appears >15 times, include it
                # Because there might be 1* gears
                # If it's for character infographic, include all gears
                if appears[star_num][char]["weap_freq"][weapon]["flat"] > gear_app_threshold or info_char or (
                    appears[star_num][char]["weap_freq"][weapon]["flat"] / app_flat) > 20:
                    appears[star_num][char]["weap_freq"][weapon]["percent"] = round(
                        appears[star_num][char]["weap_freq"][weapon]["flat"] / app_flat, 2
                    )
                    avg_round = []
                    for room_num in range(1,13):
                        if appears[star_num][char]["weap_freq"][weapon]["round"][str(room_num)]:
                            if appears[star_num][char]["weap_freq"][weapon]["flat"] > 1:
                                skewness = skew(appears[star_num][char]["weap_freq"][weapon]["round"][str(room_num)], axis=0, bias=True)
                                if abs(skewness) > 0.8:
                                    avg_round.append(trim_mean(appears[star_num][char]["weap_freq"][weapon]["round"][str(room_num)], 0.25))
                                else:
                                    avg_round.append(statistics.mean(appears[star_num][char]["weap_freq"][weapon]["round"][str(room_num)]))
                            else:
                                avg_round.append(statistics.mean(appears[star_num][char]["weap_freq"][weapon]["round"][str(room_num)]))
                            # avg_round += appears[star_num][char]["weap_freq"][weapon]["round"][str(room_num)]
                            # avg_round.append(statistics.mean(appears[star_num][char]["weap_freq"][weapon]["round"][str(room_num)]))
                    if avg_round:
                        appears[star_num][char]["weap_freq"][weapon]["avg_round"] = round(statistics.mean(avg_round), 2)
                        if pf_mode:
                            appears[star_num][char]["weap_freq"][weapon]["avg_round"] = round(appears[star_num][char]["weap_freq"][weapon]["avg_round"])
                    else:
                        appears[star_num][char]["weap_freq"][weapon]["avg_round"] = 99.99
                        if pf_mode:
                            appears[star_num][char]["weap_freq"][weapon]["avg_round"] = 0
                else:
                    appears[star_num][char]["weap_freq"][weapon]["percent"] = 0
                    appears[star_num][char]["weap_freq"][weapon]["avg_round"] = 99.99
                    if pf_mode:
                        appears[star_num][char]["weap_freq"][weapon]["avg_round"] = 0

            # Remove flex artifacts
            if "Flex" in appears[star_num][char]["arti_freq"]:
                del appears[star_num][char]["arti_freq"]["Flex"]
            # Calculate artifacts
            sorted_arti = (sorted(
                appears[star_num][char]["arti_freq"].items(),
                key = lambda t: t[1]["flat"],
                reverse=True
            ))
            appears[star_num][char]["arti_freq"] = {k: v for k, v in sorted_arti}
            for arti in appears[star_num][char]["arti_freq"]:
                # If a gear appears >15 times, include it
                # Because there might be 1* gears
                # If it's for character infographic, include all gears
                if (appears[star_num][char]["arti_freq"][arti]["flat"] > gear_app_threshold or info_char) and arti != "Flex":
                    appears[star_num][char]["arti_freq"][arti]["percent"] = round(
                        appears[star_num][char]["arti_freq"][arti]["flat"] / app_flat, 2
                    )
                    avg_round = []
                    for room_num in range(1,13):
                        if (appears[star_num][char]["arti_freq"][arti]["round"][str(room_num)]):
                            if appears[star_num][char]["arti_freq"][arti]["flat"] > 1:
                                skewness = skew(appears[star_num][char]["arti_freq"][arti]["round"][str(room_num)], axis=0, bias=True)
                                if abs(skewness) > 0.8:
                                    avg_round.append(trim_mean(appears[star_num][char]["arti_freq"][arti]["round"][str(room_num)], 0.25))
                                else:
                                    avg_round.append(statistics.mean(appears[star_num][char]["arti_freq"][arti]["round"][str(room_num)]))
                            else:
                                avg_round.append(statistics.mean(appears[star_num][char]["arti_freq"][arti]["round"][str(room_num)]))
                            # avg_round += appears[star_num][char]["arti_freq"][arti]["round"][str(room_num)]
                            # avg_round.append(statistics.mean(appears[star_num][char]["arti_freq"][arti]["round"][str(room_num)]))
                    if avg_round:
                        appears[star_num][char]["arti_freq"][arti]["avg_round"] = round(statistics.mean(avg_round), 2)
                        if pf_mode:
                            appears[star_num][char]["arti_freq"][arti]["avg_round"] = round(appears[star_num][char]["arti_freq"][arti]["avg_round"])
                    else:
                        appears[star_num][char]["arti_freq"][arti]["avg_round"] = 99.99
                        if pf_mode:
                            appears[star_num][char]["arti_freq"][arti]["avg_round"] = 0
                else:
                    appears[star_num][char]["arti_freq"][arti]["percent"] = 0
                    appears[star_num][char]["arti_freq"][arti]["avg_round"] = 99.99
                    if pf_mode:
                        appears[star_num][char]["arti_freq"][arti]["avg_round"] = 0

            # Remove flex artifacts
            if "Flex" in appears[star_num][char]["planar_freq"]:
                del appears[star_num][char]["planar_freq"]["Flex"]
            # Calculate artifacts
            sorted_planars = (sorted(
                appears[star_num][char]["planar_freq"].items(),
                key = lambda t: t[1]["flat"],
                reverse=True
            ))
            appears[star_num][char]["planar_freq"] = {k: v for k, v in sorted_planars}
            for planar in appears[star_num][char]["planar_freq"]:
                # If a gear appears >15 times, include it
                # Because there might be 1* gears
                # If it's for character infographic, include all gears
                if (appears[star_num][char]["planar_freq"][planar]["flat"] > gear_app_threshold or info_char) and planar != "Flex":
                    appears[star_num][char]["planar_freq"][planar]["percent"] = round(
                        appears[star_num][char]["planar_freq"][planar]["flat"] / app_flat, 2
                    )
                    avg_round = []
                    for room_num in range(1,13):
                        if (appears[star_num][char]["planar_freq"][planar]["round"][str(room_num)]):
                            if appears[star_num][char]["planar_freq"][planar]["flat"] > 1:
                                skewness = skew(appears[star_num][char]["planar_freq"][planar]["round"][str(room_num)], axis=0, bias=True)
                                if abs(skewness) > 0.8:
                                    avg_round.append(trim_mean(appears[star_num][char]["planar_freq"][planar]["round"][str(room_num)], 0.25))
                                else:
                                    avg_round.append(statistics.mean(appears[star_num][char]["planar_freq"][planar]["round"][str(room_num)]))
                            else:
                                avg_round.append(statistics.mean(appears[star_num][char]["planar_freq"][planar]["round"][str(room_num)]))
                            # avg_round += appears[star_num][char]["planar_freq"][planar]["round"][str(room_num)]
                            # avg_round.append(statistics.mean(appears[star_num][char]["planar_freq"][planar]["round"][str(room_num)]))
                    if avg_round:
                        appears[star_num][char]["planar_freq"][planar]["avg_round"] = round(statistics.mean(avg_round), 2)
                        if pf_mode:
                            appears[star_num][char]["planar_freq"][planar]["avg_round"] = round(appears[star_num][char]["planar_freq"][planar]["avg_round"])
                    else:
                        appears[star_num][char]["planar_freq"][planar]["avg_round"] = 99.99
                        if pf_mode:
                            appears[star_num][char]["planar_freq"][planar]["avg_round"] = 0
                else:
                    appears[star_num][char]["planar_freq"][planar]["percent"] = 0
                    appears[star_num][char]["planar_freq"][planar]["avg_round"] = 99.99
                    if pf_mode:
                        appears[star_num][char]["planar_freq"][planar]["avg_round"] = 0
        if len(chambers) > 2 and star_num == 4:
            csv_writer = csv.writer(open("../char_results/all_rounds.csv", 'w', newline=''))
            for char in all_rounds:
                for room_num in all_rounds[char]:
                    for round_num_iter in all_rounds[char][room_num]:
                        csv_writer.writerow(["2/21/2024", char, room_num, round_num_iter, all_rounds[char][room_num][round_num_iter]])
            # exit()
    return appears

def usages(owns, appears, past_phase, filename, chambers=ROOMS, offset=1):
    uses = {}

    try:
        with open("../char_results/" + past_phase + "/appearance.json") as stats:
            past_usage = json.load(stats)
        with open("../char_results/" + past_phase + "/rounds.json") as stats:
            past_rounds = json.load(stats)
    except:
        past_usage = {}
        past_rounds = {}

    for star_num in appears:
        uses[star_num] = {}
        rates = []
        for char in appears[star_num]:
            uses[star_num][char] = {
                "app": appears[star_num][char]["percent"],
                "app_flat": appears[star_num][char]["flat"],
                "round": appears[star_num][char]["avg_round"],
                "std_dev_round": appears[star_num][char]["std_dev_round"],
                # "own": owns[star_num][char]["percent"],
                "own": 0,
                "usage" : 0,
                "diff": "-",
                "diff_rounds": "-",
                "role": CHARACTERS[char]["role"],
                "rarity": CHARACTERS[char]["availability"],
                "weapons" : {},
                "weapons_round" : {},
                "artifacts" : {},
                "artifacts_round" : {},
                "planars" : {},
                "planars_round" : {},
                "cons_usage": {},
                "cons_avg": appears[star_num][char]["cons_avg"],
                "sample": appears[star_num][char]["sample"]
            }
            # rate = round(appears[star_num][char]["flat"] / (owns[star_num][char]["flat"] * offset / 100.0), 2)
            rates.append(uses[star_num][char]["app"])

            if len(chambers) > 2 or (pf_mode and chambers == ["4-1", "4-2"]):
                stage = "all"
            else:
                stage = chambers[0]
            try:
                if char in past_usage[stage][str(star_num)]:
                    uses[star_num][char]["diff"] = round(appears[star_num][char]["percent"] - past_usage[stage][str(star_num)][char]["app"], 2)
            except:
                pass
            try:
                if char in past_rounds[stage][str(star_num)]:
                    uses[star_num][char]["diff_rounds"] = round(appears[star_num][char]["avg_round"] - past_rounds[stage][str(star_num)][char]["round"], 2)
            except:
                pass

            for i in range (7):
                uses[star_num][char]["cons_usage"][i] = {
                    "app": "-",
                    "own": "-",
                    "usage": "-",
                }

            if pf_mode:
                if chambers != ["4-1", "4-2"]:
                    continue
            elif len(chambers) < 3:
                continue
            if star_num != 4:
                continue

            weapons = list(appears[star_num][char]["weap_freq"])
            for i in range(len(weapons)):
                uses[star_num][char]["weapons"][weapons[i]] = appears[star_num][char]["weap_freq"][weapons[i]]

            artifacts = list(appears[star_num][char]["arti_freq"])
            for i in range(len(artifacts)):
                uses[star_num][char]["artifacts"][artifacts[i]] = appears[star_num][char]["arti_freq"][artifacts[i]]

            planars = list(appears[star_num][char]["planar_freq"])
            for i in range(len(planars)):
                uses[star_num][char]["planars"][planars[i]] = appears[star_num][char]["planar_freq"][planars[i]]

            for i in range (7):
                uses[star_num][char]["cons_usage"][i]["app"] = appears[star_num][char]["cons_freq"][i]["percent"]
                uses[star_num][char]["cons_usage"][i]["round"] = appears[star_num][char]["cons_freq"][i]["avg_round"]
                # uses[star_num][char]["cons_usage"][i]["own"] = owns[star_num][char]["cons_freq"][i]["percent"]
                # if "Trailblazer" in char:
                #     uses[star_num][char]["cons_usage"][i]["usage"] = round(
                #         appears[star_num][char]["cons_freq"][i]["flat"]  / (owns[star_num][char]["cons_freq"][i]["flat"] * (
                #                 owns[star_num][char]["flat"] / owns[star_num][char]["cons_freq"][i]["flat"]
                #             ) * offset / 100.0), 2
                #     )
                # else:
                #     uses[star_num][char]["cons_usage"][i]["usage"] = round(
                #         appears[star_num][char]["cons_freq"][i]["flat"] / (owns[star_num][char]["cons_freq"][i]["flat"] * offset / 100.0), 2
                #     )
        rates.sort(reverse=True)
        for char in uses[star_num]:
            # if owns[star_num][char]["flat"] > 0:
            uses[star_num][char]["rank"] = rates.index(uses[star_num][char]["app"]) + 1
    return uses
