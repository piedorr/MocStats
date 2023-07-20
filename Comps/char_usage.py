import json
import pandas as pd
import operator
import csv
from archetypes import *

ROOMS = ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2", "5-1", "5-2", "6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2"]
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
                    # if (chambers == ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2", "5-1", "5-2", "6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2"]):
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
                    # if (chambers == ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2", "5-1", "5-2", "6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2"]):
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
    total_battle = 0
    appears = {}
    players_chars = {}

    for phase in players:
        appears[phase] = {}
        players_chars[phase] = {}
        comp_error = False
        error_comps = []

        for character in CHARACTERS:
            players_chars[phase][character] = []
            appears[phase][character] = {
                "flat": 0,
                "round": 0,
                "owned": 0,
                "percent": 0.00,
                "avg_round": 0.00,
                "weap_freq": {},
                "arti_freq": {},
                "planar_freq": {},
                "cons_freq": {},
                "cons_avg": 0.00,
                "sample": 0
            }
            for i in range (7):
                appears[phase][character]["cons_freq"][i] = {
                    "flat": 0,
                    "round": 0,
                    "percent": 0,
                    "avg_round": 0.00
                }

        # There's probably a better way to cache these things
        for player in players[phase].values():
            for chamber in chambers:
                if player.chambers[chamber] == None:
                    continue
                total_battle += 1
                foundchar = resetfind()
                for char in player.chambers[chamber].characters:
                    findchars(char, foundchar)
                if find_archetype(foundchar):
                    for char in player.chambers[chamber].characters:
                        # to print the amount of players using a character, for char infographics
                        if player.player not in players_chars[phase][char]:
                            players_chars[phase][char].append(player.player)

                        char_name = char
                        appears[phase][char_name]["flat"] += 1
                        appears[phase][char_name]["round"] += player.chambers[chamber].round_num
                        # In case of character in comp data missing from character data
                        if char not in player.owned:
                            # print("Comp data missing from character data: " + str(player.player) + ", " + str(char))
                            # if player.player not in error_comps:
                            #     error_comps.append(player.player)
                            # comp_error = True
                            continue
                        appears[phase][char_name]["owned"] += 1
                        appears[phase][char_name]["cons_freq"][player.owned[char]["cons"]]["flat"] += 1
                        appears[phase][char_name]["cons_freq"][player.owned[char]["cons"]]["round"] += player.chambers[chamber].round_num
                        appears[phase][char_name]["cons_avg"] += player.owned[char]["cons"]

                        if player.owned[char]["weapon"] != "":
                            if player.owned[char]["weapon"] in appears[phase][char_name]["weap_freq"]:
                                appears[phase][char_name]["weap_freq"][player.owned[char]["weapon"]] += 1
                            else:
                                appears[phase][char_name]["weap_freq"][player.owned[char]["weapon"]] = 1

                        if player.owned[char]["artifacts"] != "":
                            if player.owned[char]["artifacts"] in appears[phase][char_name]["arti_freq"]:
                                appears[phase][char_name]["arti_freq"][player.owned[char]["artifacts"]] += 1
                            else:
                                appears[phase][char_name]["arti_freq"][player.owned[char]["artifacts"]] = 1

                        if player.owned[char]["planars"] != "":
                            if player.owned[char]["planars"] in appears[phase][char_name]["planar_freq"]:
                                appears[phase][char_name]["planar_freq"][player.owned[char]["planars"]] += 1
                            else:
                                appears[phase][char_name]["planar_freq"][player.owned[char]["planars"]] = 1

        if comp_error:
            df_char = pd.read_csv('../data/phase_characters.csv')
            df_spiral = pd.read_csv('../data/compositions.csv')
            df_char = df_char[~df_char['uid'].isin(error_comps)]
            df_spiral = df_spiral[~df_spiral['uid'].isin(error_comps)]
            df_char.to_csv("phase_characters.csv", index=False)
            df_spiral.to_csv("compositions.csv", index=False)
            raise ValueError("There are missing comps from character data.")

        total = total_battle * offset/200.0
        for char in appears[phase]:
            # # to print the amount of players using a character
            # print(str(char) + ": " + str(len(players_chars[phase][char])))
            if total > 0:
                appears[phase][char]["percent"] = round(
                    appears[phase][char]["flat"] / total, 2
                )
            else:
                appears[phase][char]["percent"] = 0.00
            if appears[phase][char]["flat"] > 0:
                appears[phase][char]["avg_round"] = round(
                    appears[phase][char]["round"] / appears[phase][char]["flat"], 2
                )
            else:
                appears[phase][char]["avg_round"] = 0.00

            # if (chambers == ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2", "5-1", "5-2", "6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2"]):
            appears[phase][char]["sample"] = len(players_chars[phase][char])

            # Calculate constellations
            app_flat = appears[phase][char]["owned"] / 100.0
            if owns[phase][char]["flat"] > 0:
                if appears[phase][char]["owned"] > 0:
                    appears[phase][char]["cons_avg"] /= appears[phase][char]["owned"]
                for cons in appears[phase][char]["cons_freq"]:
                    if appears[phase][char]["cons_freq"][cons]["flat"] > 0:
                        appears[phase][char]["cons_freq"][cons]["percent"] = round(
                            appears[phase][char]["cons_freq"][cons]["flat"] / app_flat, 2
                        )
                        appears[phase][char]["cons_freq"][cons]["avg_round"] = round(
                            appears[phase][char]["cons_freq"][cons]["round"] / appears[phase][char]["cons_freq"][cons]["flat"], 2
                        )
                    else:
                        appears[phase][char]["cons_freq"][cons]["percent"] = 0.00
                        appears[phase][char]["cons_freq"][cons]["avg_round"] = 0.00

            # Calculate weapons
            sorted_weapons = (sorted(
                appears[phase][char]["weap_freq"].items(),
                key = operator.itemgetter(1),
                reverse=True
            ))
            appears[phase][char]["weap_freq"] = {k: v for k, v in sorted_weapons}
            for weapon in appears[phase][char]["weap_freq"]:
                # If a gear appears >15 times, include it
                # Because there might be 1* gears
                # If it's for character infographic, include all gears
                if appears[phase][char]["weap_freq"][weapon] > gear_app_threshold or info_char:
                    appears[phase][char]["weap_freq"][weapon] = round(
                        appears[phase][char]["weap_freq"][weapon] / app_flat, 2
                    )
                else:
                    appears[phase][char]["weap_freq"][weapon] = "-"

            # Remove flex artifacts
            appears[phase][char]["arti_freq"]["Flex"] = 0
            # Calculate artifacts
            sorted_arti = (sorted(
                appears[phase][char]["arti_freq"].items(),
                key = operator.itemgetter(1),
                reverse=True
            ))
            appears[phase][char]["arti_freq"] = {k: v for k, v in sorted_arti}
            for arti in appears[phase][char]["arti_freq"]:
                # If a gear appears >15 times, include it
                # Because there might be 1* gears
                # If it's for character infographic, include all gears
                if (appears[phase][char]["arti_freq"][arti] > gear_app_threshold or info_char) and arti != "Flex":
                    appears[phase][char]["arti_freq"][arti] = round(
                        appears[phase][char]["arti_freq"][arti] / app_flat, 2
                    )
                else:
                    appears[phase][char]["arti_freq"][arti] = "-"

            # Remove flex artifacts
            appears[phase][char]["planar_freq"]["Flex"] = 0
            # Calculate artifacts
            sorted_planars = (sorted(
                appears[phase][char]["planar_freq"].items(),
                key = operator.itemgetter(1),
                reverse=True
            ))
            appears[phase][char]["planar_freq"] = {k: v for k, v in sorted_planars}
            for planar in appears[phase][char]["planar_freq"]:
                # If a gear appears >15 times, include it
                # Because there might be 1* gears
                # If it's for character infographic, include all gears
                if (appears[phase][char]["planar_freq"][planar] > gear_app_threshold or info_char) and planar != "Flex":
                    appears[phase][char]["planar_freq"][planar] = round(
                        appears[phase][char]["planar_freq"][planar] / app_flat, 2
                    )
                else:
                    appears[phase][char]["planar_freq"][planar] = "-"
    return appears

def usages(owns, appears, past_phase, filename, chambers=ROOMS, offset=1):
    uses = {}

    try:
        with open("../char_results/" + past_phase + "/" + filename + ".csv") as stats:
            # uid_freq_comp will help detect duplicate UIDs
            reader = csv.reader(stats)
            col_names = next(reader)
            past_usage = {}
            past_rounds = {}

            # Append lines and check for duplicate UIDs by checking if
            # there are exactly 12 entries (1 for each chamber) for a UID
            for line in reader:
                past_usage[line[0]] = float(line[1].strip('%'))
                try:
                    past_rounds[line[0]] = float(line[2])
                except:
                    pass
    except:
        past_usage = {}
        past_rounds = {}

    for phase in owns:
        uses[phase] = {}
        rates = []
        for char in owns[phase]:
            uses[phase][char] = {
                "app": appears[phase][char]["percent"],
                "app_flat": appears[phase][char]["flat"],
                "round": appears[phase][char]["avg_round"],
                "own": owns[phase][char]["percent"],
                "usage" : 0,
                "diff": "-",
                "diff_rounds": "-",
                "rarity": CHARACTERS[char]["availability"],
                "weapons" : {},
                "artifacts" : {},
                "planars" : {},
                "cons_usage": {},
                "cons_avg": appears[phase][char]["cons_avg"],
                "sample": appears[phase][char]["sample"]
            }
            if owns[phase][char]["flat"] > 0:
                rate = round(appears[phase][char]["flat"] / (owns[phase][char]["flat"] * offset / 100.0), 2)
                rates.append(uses[phase][char]["app"])

                if char in past_usage:
                    uses[phase][char]["diff"] = round(appears[phase][char]["percent"] - past_usage[char], 2)
                if char in past_rounds:
                    uses[phase][char]["diff_rounds"] = round(appears[phase][char]["avg_round"] - past_rounds[char], 2)

                # if (chambers == ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2", "5-1", "5-2", "6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2"]):
                for i in range (7):
                    uses[phase][char]["cons_usage"][i] = {
                        "app": "-",
                        "own": "-",
                        "usage": "-",
                    }

                weapons = list(appears[phase][char]["weap_freq"])
                i = 0
                while i < 20:
                    if i >= len(weapons):
                        uses[phase][char]["weapons"][i] = "-"
                    else:
                        uses[phase][char]["weapons"][weapons[i]] = appears[phase][char]["weap_freq"][weapons[i]]
                    i += 1

                artifacts = list(appears[phase][char]["arti_freq"])
                i = 0
                while i < 10:
                    if i >= len(artifacts):
                        uses[phase][char]["artifacts"][i] = "-"
                    else:
                        uses[phase][char]["artifacts"][artifacts[i]] = appears[phase][char]["arti_freq"][artifacts[i]]
                    i += 1

                planars = list(appears[phase][char]["planar_freq"])
                i = 0
                while i < 10:
                    if i >= len(planars):
                        uses[phase][char]["planars"][i] = "-"
                    else:
                        uses[phase][char]["planars"][planars[i]] = appears[phase][char]["planar_freq"][planars[i]]
                    i += 1

                for i in range (7):
                    uses[phase][char]["cons_usage"][i]["app"] = appears[phase][char]["cons_freq"][i]["percent"]
                    uses[phase][char]["cons_usage"][i]["round"] = appears[phase][char]["cons_freq"][i]["avg_round"]
                    # uses[phase][char]["cons_usage"][i]["own"] = owns[phase][char]["cons_freq"][i]["percent"]
                    # if "Trailblazer" in char:
                    #     uses[phase][char]["cons_usage"][i]["usage"] = round(
                    #         appears[phase][char]["cons_freq"][i]["flat"]  / (owns[phase][char]["cons_freq"][i]["flat"] * (
                    #                 owns[phase][char]["flat"] / owns[phase][char]["cons_freq"][i]["flat"]
                    #             ) * offset / 100.0), 2
                    #     )
                    # else:
                    #     uses[phase][char]["cons_usage"][i]["usage"] = round(
                    #         appears[phase][char]["cons_freq"][i]["flat"] / (owns[phase][char]["cons_freq"][i]["flat"] * offset / 100.0), 2
                    #     )
        rates.sort(reverse=True)
        for char in uses[phase]:
            if owns[phase][char]["flat"] > 0:
                uses[phase][char]["rank"] = rates.index(uses[phase][char]["app"]) + 1
    return uses
