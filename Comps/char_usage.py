import json
import pandas as pd
import operator
import csv
import statistics
from archetypes import *
from comp_rates_config import RECENT_PHASE

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
    appears = {}
    players_chars = {}

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
                "round": {
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
                appears[star_num][character]["cons_freq"][i] = {
                    "flat": 0,
                    "round": {
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
                # for char in player.chambers[chamber].characters:
                #     findchars(char, foundchar)
                # if find_archetype(foundchar):
                if True:
                    for char in player.chambers[chamber].characters:
                        # to print the amount of players using a character, for char infographics
                        if len(chambers) > 2:
                            players_chars[star_num][char].add(player.player)

                        char_name = char
                        appears[star_num][char_name]["flat"] += 1
                        appears[star_num][char_name]["round"][list(str(chamber).split("-"))[0]].append(player.chambers[chamber].round_num)
                        # In case of character in comp data missing from character data
                        if len(chambers) < 5:
                            continue
                        if char not in player.owned or star_num != 4:
                            # print("Comp data missing from character data: " + str(player.player) + ", " + str(char))
                            # if player.player not in error_comps:
                            #     error_comps.append(player.player)
                            # comp_error = True
                            continue
                        appears[star_num][char_name]["owned"] += 1
                        appears[star_num][char_name]["cons_freq"][player.owned[char]["cons"]]["flat"] += 1
                        appears[star_num][char_name]["cons_freq"][player.owned[char]["cons"]]["round"][list(str(chamber).split("-"))[0]].append(player.chambers[chamber].round_num)
                        appears[star_num][char_name]["cons_avg"] += player.owned[char]["cons"]

                        if player.owned[char]["weapon"] != "":
                            if player.owned[char]["weapon"] in appears[star_num][char_name]["weap_freq"]:
                                appears[star_num][char_name]["weap_freq"][player.owned[char]["weapon"]] += 1
                            else:
                                appears[star_num][char_name]["weap_freq"][player.owned[char]["weapon"]] = 1

                        if player.owned[char]["artifacts"] != "":
                            if player.owned[char]["artifacts"] in appears[star_num][char_name]["arti_freq"]:
                                appears[star_num][char_name]["arti_freq"][player.owned[char]["artifacts"]] += 1
                            else:
                                appears[star_num][char_name]["arti_freq"][player.owned[char]["artifacts"]] = 1

                        if player.owned[char]["planars"] != "":
                            if player.owned[char]["planars"] in appears[star_num][char_name]["planar_freq"]:
                                appears[star_num][char_name]["planar_freq"][player.owned[char]["planars"]] += 1
                            else:
                                appears[star_num][char_name]["planar_freq"][player.owned[char]["planars"]] = 1

        if comp_error:
            df_char = pd.read_csv('../data/phase_characters.csv')
            df_spiral = pd.read_csv('../data/compositions.csv')
            df_char = df_char[~df_char['uid'].isin(error_comps)]
            df_spiral = df_spiral[~df_spiral['uid'].isin(error_comps)]
            df_char.to_csv("phase_characters.csv", index=False)
            df_spiral.to_csv("compositions.csv", index=False)
            raise ValueError("There are missing comps from character data.")

        total = total_battle * offset/200.0
        for char in appears[star_num]:
            # # to print the amount of players using a character
            # print(str(char) + ": " + str(len(players_chars[star_num][char])))
            if total > 0:
                appears[star_num][char]["percent"] = round(
                    appears[star_num][char]["flat"] / total, 2
                )
            else:
                appears[star_num][char]["percent"] = 0.00
            if appears[star_num][char]["flat"] > 0:
                avg_round = []
                for room_num in range(1,11):
                    if (appears[star_num][char]["round"][str(room_num)]):
                        # avg_round.append(statistics.mean(appears[star_num][char]["round"][str(room_num)]))
                        avg_round += appears[star_num][char]["round"][str(room_num)]
                # if star_num == 4:
                #     print(char + " " + str(avg_round))
                appears[star_num][char]["avg_round"] = round(statistics.mean(avg_round), 2)
            else:
                appears[star_num][char]["avg_round"] = 99.99

            # if (chambers == ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2", "5-1", "5-2", "6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2"]):
            appears[star_num][char]["sample"] = len(players_chars[star_num][char])

            if len(chambers) < 5:
                continue
            if star_num != 4:
                continue
            # Calculate constellations
            app_flat = appears[star_num][char]["owned"] / 100.0
            # if owns[star_num][char]["flat"] > 0:
            if appears[star_num][char]["owned"] > 0:
                appears[star_num][char]["cons_avg"] /= appears[star_num][char]["owned"]
            for cons in appears[star_num][char]["cons_freq"]:
                if appears[star_num][char]["cons_freq"][cons]["flat"] > 0:
                    appears[star_num][char]["cons_freq"][cons]["percent"] = round(
                        appears[star_num][char]["cons_freq"][cons]["flat"] / app_flat, 2
                    )
                    avg_round = []
                    for room_num in range(1,11):
                        if (appears[star_num][char]["cons_freq"][cons]["round"][str(room_num)]):
                            avg_round.append(statistics.mean(appears[star_num][char]["cons_freq"][cons]["round"][str(room_num)]))
                    appears[star_num][char]["cons_freq"][cons]["avg_round"] = round(statistics.mean(avg_round), 2)
                else:
                    appears[star_num][char]["cons_freq"][cons]["percent"] = 99.99
                    appears[star_num][char]["cons_freq"][cons]["avg_round"] = 99.99

            # Calculate weapons
            sorted_weapons = (sorted(
                appears[star_num][char]["weap_freq"].items(),
                key = operator.itemgetter(1),
                reverse=True
            ))
            appears[star_num][char]["weap_freq"] = {k: v for k, v in sorted_weapons}
            for weapon in appears[star_num][char]["weap_freq"]:
                # If a gear appears >15 times, include it
                # Because there might be 1* gears
                # If it's for character infographic, include all gears
                if appears[star_num][char]["weap_freq"][weapon] > gear_app_threshold or info_char:
                    appears[star_num][char]["weap_freq"][weapon] = round(
                        appears[star_num][char]["weap_freq"][weapon] / app_flat, 2
                    )
                else:
                    appears[star_num][char]["weap_freq"][weapon] = "-"

            # Remove flex artifacts
            appears[star_num][char]["arti_freq"]["Flex"] = 0
            # Calculate artifacts
            sorted_arti = (sorted(
                appears[star_num][char]["arti_freq"].items(),
                key = operator.itemgetter(1),
                reverse=True
            ))
            appears[star_num][char]["arti_freq"] = {k: v for k, v in sorted_arti}
            for arti in appears[star_num][char]["arti_freq"]:
                # If a gear appears >15 times, include it
                # Because there might be 1* gears
                # If it's for character infographic, include all gears
                if (appears[star_num][char]["arti_freq"][arti] > gear_app_threshold or info_char) and arti != "Flex":
                    appears[star_num][char]["arti_freq"][arti] = round(
                        appears[star_num][char]["arti_freq"][arti] / app_flat, 2
                    )
                else:
                    appears[star_num][char]["arti_freq"][arti] = "-"

            # Remove flex artifacts
            appears[star_num][char]["planar_freq"]["Flex"] = 0
            # Calculate artifacts
            sorted_planars = (sorted(
                appears[star_num][char]["planar_freq"].items(),
                key = operator.itemgetter(1),
                reverse=True
            ))
            appears[star_num][char]["planar_freq"] = {k: v for k, v in sorted_planars}
            for planar in appears[star_num][char]["planar_freq"]:
                # If a gear appears >15 times, include it
                # Because there might be 1* gears
                # If it's for character infographic, include all gears
                if (appears[star_num][char]["planar_freq"][planar] > gear_app_threshold or info_char) and planar != "Flex":
                    appears[star_num][char]["planar_freq"][planar] = round(
                        appears[star_num][char]["planar_freq"][planar] / app_flat, 2
                    )
                else:
                    appears[star_num][char]["planar_freq"][planar] = "-"
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
                # "own": owns[star_num][char]["percent"],
                "own": 0,
                "usage" : 0,
                "diff": "-",
                "diff_rounds": "-",
                "rarity": CHARACTERS[char]["availability"],
                "weapons" : {},
                "artifacts" : {},
                "planars" : {},
                "cons_usage": {},
                "cons_avg": appears[star_num][char]["cons_avg"],
                "sample": appears[star_num][char]["sample"]
            }
            # rate = round(appears[star_num][char]["flat"] / (owns[star_num][char]["flat"] * offset / 100.0), 2)
            rates.append(uses[star_num][char]["app"])

            if len(chambers) > 2:
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

            if len(chambers) < 5:
                continue
            if star_num != 4:
                continue

            weapons = list(appears[star_num][char]["weap_freq"])
            i = 0
            while i < 20:
                if i >= len(weapons):
                    uses[star_num][char]["weapons"][i] = "-"
                else:
                    uses[star_num][char]["weapons"][weapons[i]] = appears[star_num][char]["weap_freq"][weapons[i]]
                i += 1

            artifacts = list(appears[star_num][char]["arti_freq"])
            i = 0
            while i < 10:
                if i >= len(artifacts):
                    uses[star_num][char]["artifacts"][i] = "-"
                else:
                    uses[star_num][char]["artifacts"][artifacts[i]] = appears[star_num][char]["arti_freq"][artifacts[i]]
                i += 1

            planars = list(appears[star_num][char]["planar_freq"])
            i = 0
            while i < 10:
                if i >= len(planars):
                    uses[star_num][char]["planars"][i] = "-"
                else:
                    uses[star_num][char]["planars"][planars[i]] = appears[star_num][char]["planar_freq"][planars[i]]
                i += 1

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
