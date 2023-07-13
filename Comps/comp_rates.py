import csv
import operator
from itertools import permutations
from composition import Composition
from player_phase import PlayerPhase
import char_usage as cu
import pygsheets
from comp_rates_config import *

def main():
    global sample_size
    sample_size = {}
    print("start")

    client = pygsheets.authorize()

    # Open the spreadsheet and the first sheet.
    sh = client.open('Memory of Chaos Stats Form (Responses)')
    wks = sh.sheet1

    global self_uids
    ranges = wks.get_values_batch( ['B1:B', 'D1:D'] )
    self_uids = ranges[0][1:]
    self_uids = [i[0] for i in self_uids]

    print("done sheets")

    with open("../data/compositions.csv") as stats:
        # uid_freq_comp will help detect duplicate UIDs
        reader = csv.reader(stats)
        col_names_comps = next(reader)
        comp_table = []
        uid_freq_comp = {}
        self_freq_comp = {}
        last_uid = "0"

        for line in reader:
            # if line[0] in self_uids:
            #     continue
            if line[0] != last_uid:
                skip_uid = False
                # if line[0] in uid_freq_comp or int(line[2].split("-")[0]) > 1:
                if line[0] in uid_freq_comp:
                    skip_uid = True
                    # print("duplicate UID in comp: " + line[0])
                else:
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

    with open("../data/phase_characters.csv") as stats:
        # uid_freq_char and last_uid will help detect duplicate UIDs
        reader = csv.reader(stats)
        col_names = next(reader)
        player_table = []
        uid_freq_char = []
        last_uid = "0"

        # Append lines
        for line in reader:
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
        print("done csv")

    csv_writer = csv.writer(open("../char_results/uids.csv", 'w', newline=''))
    for uid in uid_freq_comp.keys():
        csv_writer.writerow([uid])
    # print(uid_freq_comp)
    # exit()

    all_comps = form_comps(col_names_comps, comp_table, alt_comps)
    all_players = form_players(player_table, all_comps, [RECENT_PHASE])
    print("done form")

    if "Char usages all stages" in run_commands:
        global usage
        usage = char_usages(all_players, archetype, past_phase, filename="all", floor=True)
        duo_usages(all_comps, all_players, usage, archetype)
        print("done char")

    if "Char usages for each stage" in run_commands:
        for room in ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2", "5-1", "5-2", "6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2"]:
            char_usages(all_players, archetype, past_phase, rooms=[room], filename=room, offset=2)
        print("done char stage")

    if "Char usages for each stage (combined)" in run_commands:
        for room in [["1-1", "1-2"], ["2-1", "2-2"], ["3-1", "3-2"], ["4-1", "4-2"], ["5-1", "5-2"], ["6-1", "6-2"], ["7-1", "7-2"], ["8-1", "8-2"], ["9-1", "9-2"], ["10-1", "10-2"]]:
            char_usages(all_players, archetype, past_phase, rooms=room, filename=room[0].split('-')[0])
        print("done char stage (combine)")

    if "Comp usage all stages overall" in run_commands:
        comp_usages(all_comps, all_players, whaleCheck, whaleSigWeap, sigWeaps, rooms=["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2", "5-1", "5-2", "6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2"], filename="all", floor=True)
        print("done comp all")

    if "Comp usages for each stage" in run_commands:
        for room in ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2", "5-1", "5-2", "6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2"]:
            comp_usages(all_comps, all_players, whaleCheck, whaleSigWeap, sigWeaps, rooms=[room], filename=room, offset=2)
        with open("../char_results/demographic.json", "w") as out_file:
            out_file.write(json.dumps(sample_size,indent=4))
        print("done comp stage")

    if "Character specific infographics" in run_commands:
        comp_usages(all_comps, all_players, whaleCheck, whaleSigWeap, sigWeaps, filename=char, info_char=True, floor=True)
        print("done char infographics")

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
    # comp_owned(players, comps_dict, whaleCheck, whaleSigWeap, sigWeaps, owns_offset=offset)
    rank_usages(comps_dict, owns_offset=offset)
    comp_usages_write(comps_dict, filename, floor, info_char)

def used_comps(players, comps, rooms, filename, whaleCheck, whaleSigWeap, sigWeaps, phase=RECENT_PHASE, floor=False, offset=1):
    # Returns the dictionary of all the comps used and how many times they were used
    comps_dict = [{},{},{},{},{}]
    error_uids = []
    # deepwoodTighnari = 0
    # deepwoodEquipChars = {}
    # meltGanyu = 0
    # meltGanyuWeap = {}
    # meltGanyuArti = {}
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

        if whaleCheck:
            whaleComp = False
            for char in range (4):
                if (
                    players[phase][comp.player].owned[comp_tuple[char]]["cons"] != 0
                    and CHARACTERS[comp_tuple[char]]["availability"] in ["Limited 5*"]
                ) or (
                    whaleSigWeap and players[phase][comp.player].owned[comp_tuple[char]]["weapon"] in sigWeaps
                ):
                    whaleComp = True
            if whaleComp:
                whaleCount += 1
                continue

        for star_threshold in range(0,5):
            if star_threshold != 4 and comp.star_num != star_threshold:
                continue
            if comp_tuple not in comps_dict[star_threshold]:
                comps_dict[star_threshold][comp_tuple] = {
                    "uses": 1,
                    "owns": 0,
                    "5* count": comp.fivecount,
                    "comp_name": comp.comp_name,
                    "alt_comp_name": comp.alt_comp_name,
                    "star_num": comp.star_num,
                    "deepwood": 0,
                    "players": [comp.player]
                }
                # if floor:
                #     # deepwood = False
                #     # melt = False
                #     # deepwoodEquip = ""
                #     for char in range (4):
                #         # if char in ["Thoma","Yoimiya","Yanfei","Hu Tao","Xinyan","Diluc","Amber","Xiangling","Klee","Bennett"]:
                #         #     melt = True
                #         # "weapon" and "artifacts" stores dictionary of
                #         # used gear, key is the name of the gear, value is the app#
                #         comps_dict[star_threshold][comp_tuple][comp_tuple[char]] = {
                #             "weapon" : {},
                #             "artifacts" : {},
                #             "cons": []
                #         }
                #         try:
                #             comps_dict[star_threshold][comp_tuple][comp_tuple[char]]["weapon"][players[phase][comp.player].owned[comp_tuple[char]]["weapon"]] = 1
                #             if players[phase][comp.player].owned[comp_tuple[char]]["artifacts"] != "":
                #                 comps_dict[star_threshold][comp_tuple][comp_tuple[char]]["artifacts"][players[phase][comp.player].owned[comp_tuple[char]]["artifacts"]] = 1
                #                 # if players[phase][comp.player].owned[comp_tuple[char]]["artifacts"] == "Deepwood Memories":
                #                 #     deepwood = True
                #                 #     deepwoodEquip = comp_tuple[char]
                #         except Exception as e:
                #             if ('{}: {}'.format(comp.player, e)) not in error_uids:
                #                 error_uids.append('{}: {}'.format(comp.player, e))
                #     # if deepwood:
                #     #     comps_dict[star_threshold][comp_tuple]["deepwood"] += 1
                #     #     if ("Tighnari" in comp_tuple):
                #     #         deepwoodTighnari += 1
                #     #         if deepwoodEquip in deepwoodEquipChars:
                #     #             deepwoodEquipChars[deepwoodEquip] += 1
                #     #         else:
                #     #             deepwoodEquipChars[deepwoodEquip] = 1
                #     # if melt and "Ganyu" in comp_tuple:
                #     #     meltGanyu += 1
            else:
                comps_dict[star_threshold][comp_tuple]["uses"] +=1
                if comp.player not in comps_dict[star_threshold][comp_tuple]["players"]:
                    comps_dict[star_threshold][comp_tuple]["players"].append(comp.player)
                # if floor:
                #     # deepwood = False
                #     # deepwoodEquip = ""
                #     for i in range(4):
                #         try:
                #             if players[phase][comp.player].owned[comp_tuple[i]]["weapon"] in comps_dict[star_threshold][comp_tuple][comp_tuple[i]]["weapon"]:
                #                 comps_dict[star_threshold][comp_tuple][comp_tuple[i]]["weapon"][players[phase][comp.player].owned[comp_tuple[i]]["weapon"]] += 1
                #             else:
                #                 comps_dict[star_threshold][comp_tuple][comp_tuple[i]]["weapon"][players[phase][comp.player].owned[comp_tuple[i]]["weapon"]] = 1
                #             # if players[phase][comp.player].owned[comp_tuple[i]]["artifacts"] != "":
                #                 if players[phase][comp.player].owned[comp_tuple[i]]["artifacts"] in comps_dict[star_threshold][comp_tuple][comp_tuple[i]]["artifacts"]:
                #                     comps_dict[star_threshold][comp_tuple][comp_tuple[i]]["artifacts"][players[phase][comp.player].owned[comp_tuple[i]]["artifacts"]] += 1
                #                 else:
                #                     comps_dict[star_threshold][comp_tuple][comp_tuple[i]]["artifacts"][players[phase][comp.player].owned[comp_tuple[i]]["artifacts"]] = 1
                #                 # if players[phase][comp.player].owned[comp_tuple[i]]["artifacts"] == "Deepwood Memories":
                #                 #     deepwood = True
                #                 #     deepwoodEquip = comp_tuple[i]
                #         except Exception as e:
                #             if ('{}: {}'.format(comp.player, e)) not in error_uids:
                #                 error_uids.append('{}: {}'.format(comp.player, e))
                #     # if deepwood:
                #     #     comps_dict[star_threshold][comp_tuple]["deepwood"] += 1
                #     #     if ("Tighnari" in comp_tuple):
                #     #         deepwoodTighnari += 1
                #     #         if deepwoodEquip in deepwoodEquipChars:
                #     #             deepwoodEquipChars[deepwoodEquip] += 1
                #     #         else:
                #     #             deepwoodEquipChars[deepwoodEquip] = 1
    # if floor:
    #     for comp in comps_dict:
    #         for char in comp:
    #             sorted_weapons = (sorted(
    #                 comps_dict[comp][char]["weapon"].items(),
    #                 key = operator.itemgetter(1),
    #                 reverse=True
    #             ))
    #             if(len(sorted_weapons) > 1):
    #                 maxWeapon = sorted_weapons[0][1]
    #                 sortWeapons = [sorted_weapons[0]]
    #                 for i in range (1, len(sorted_weapons)):
    #                     if sorted_weapons[i][1] == maxWeapon:
    #                         # print(i)
    #                         # print(sorted_weapons)
    #                         # print(maxWeapon)
    #                         sortWeapons.append(sorted_weapons[i])
    #                     else:
    #                         break
    #                 if len(sortWeapons) > 1:
    #                     foundWeapon = False
    #                     # print()
    #                     # print(list(usage[RECENT_PHASE][char]["weapons"]))
    #                     # print(sorted_weapons)
    #                     for charWeapon in (list(usage[RECENT_PHASE][char]["weapons"])):
    #                         for compCharWeapon in sortWeapons:
    #                             if compCharWeapon[0] == charWeapon:
    #                                 foundWeapon = True
    #                                 maxWeapon = compCharWeapon
    #                         if foundWeapon:
    #                             break
    #                     if not(foundWeapon):
    #                         print(char)
    #                         print(list(usage[RECENT_PHASE][char]["weapons"]))
    #                         print(sorted_weapons)
    #                     if foundWeapon:
    #                         sorted_weapons.remove(maxWeapon)
    #                         sorted_weapons.insert(0, maxWeapon)
    #                     # print(sorted_weapons)
    #             comps_dict[comp][char]["weapon"] = {k: v for k, v in sorted_weapons}

    #             sorted_artifacts = (sorted(
    #                 comps_dict[comp][char]["artifacts"].items(),
    #                 key = operator.itemgetter(1),
    #                 reverse=True
    #             ))
    #             if(len(sorted_artifacts) > 1):
    #                 maxArtifact = sorted_artifacts[0][1]
    #                 sortArtifacts = [sorted_artifacts[0]]
    #                 for i in range (1, len(sorted_artifacts)):
    #                     if sorted_artifacts[i][1] == maxArtifact:
    #                         # print(i)
    #                         # print(sorted_artifacts)
    #                         # print(maxArtifact)
    #                         sortArtifacts.append(sorted_artifacts[i])
    #                     else:
    #                         break
    #                 if len(sortArtifacts) > 1:
    #                     foundArtifact = False
    #                     # print()
    #                     # print(list(usage[RECENT_PHASE][char]["artifacts"]))
    #                     # print(sorted_artifacts)
    #                     for charArtifact in (list(usage[RECENT_PHASE][char]["artifacts"])):
    #                         for compCharArtifact in sortArtifacts:
    #                             if compCharArtifact[0] == charArtifact:
    #                                 foundArtifact = True
    #                                 maxArtifact = compCharArtifact
    #                         if foundArtifact:
    #                             break
    #                     # if not(foundArtifact):
    #                     #     print(char)
    #                     #     print(list(usage[RECENT_PHASE][char]["artifacts"]))
    #                     #     print(sorted_artifacts)
    #                     if foundArtifact:
    #                         sorted_artifacts.remove(maxArtifact)
    #                         sorted_artifacts.insert(0, maxArtifact)
    #                     # print(sorted_artifacts)
    #             comps_dict[comp][char]["artifacts"] = {k: v for k, v in sorted_artifacts}
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

# def comp_owned(players, comps_dict, whaleCheck, whaleSigWeap, sigWeaps, phase=RECENT_PHASE, owns_offset=1):
#     # For every comp that is used, calculate the ownership rate,
#     # i.e. how many players own all four characters in the comp
#     for player in players[phase].values():
#         for comp in comps_dict:
#             if player.chars_owned(comp):
#                 if whaleCheck:
#                     whaleComp = False
#                     for char in comp:
#                         if char not in CHARACTERS:
#                             continue
#                         # if player.owned[char] == None:
#                         #     if whaleSigWeap:
#                         #         for trav in ["Traveler-A", "Traveler-G", "Traveler-E", "Traveler-D"]:
#                         #             if player.owned[trav] != None:
#                         #                 if player.owned[trav]["weapon"] in sigWeaps:
#                         #                     whaleComp = True
#                         #     continue
#                         if (
#                             player.owned[char]["cons"] != 0
#                             and CHARACTERS[char]["availability"] in ["Limited 5*"]
#                         ) or (
#                             whaleSigWeap and player.owned[char]["weapon"] in sigWeaps
#                         ):
#                             whaleComp = True
#                     if whaleComp:
#                         continue
#                 comps_dict[comp]["owns"] += owns_offset

def rank_usages(comps_dict, owns_offset=1):
    # Calculate the usage rate and sort the comps according to it
    for star_threshold in range(0,5):
        rates = []
        for comp in comps_dict[star_threshold]:
            app = int(100.0 * comps_dict[star_threshold][comp]["uses"] / (total_comps * owns_offset) * 200 + .5) / 100.0
            comps_dict[star_threshold][comp]["app_rate"] = app
            # rate = int(100.0 * comps_dict[star_threshold][comp]["uses"] / comps_dict[star_threshold][comp]["owns"] * 100 + .5) / 100.0
            comps_dict[star_threshold][comp]["usage_rate"] = 0
            # own = int(100.0 * comps_dict[star_threshold][comp]["owns"] / (total_comps * owns_offset) * 100 + .5) / 100.0
            comps_dict[star_threshold][comp]["own_rate"] = 0
            # deepwood = int(100.0 * comps_dict[star_threshold][comp]["deepwood"] / comps_dict[star_threshold][comp]["uses"] * 100 + .5) / 100.0
            # comps_dict[star_threshold][comp]["deepwood_rate"] = deepwood
            rates.append(app)
        rates.sort(reverse=True)
        for comp in comps_dict[star_threshold]:
            comps_dict[star_threshold][comp]["app_rank"] = rates.index(comps_dict[star_threshold][comp]["app_rate"]) + 1

        # # To check the list of weapons and artifacts for a comp
        # comp_tuple = ("Tighnari","Yae Miko","Fischl","Zhongli")
        # print(comp_tuple)
        # print("   App: " + str(comps_dict[star_threshold][comp_tuple]["app_rate"]))
        # print("   Own: " + str(comps_dict[star_threshold][comp_tuple]["own_rate"]))
        # print("   Usage: " + str(comps_dict[star_threshold][comp_tuple]["usage_rate"]))
        # print("   5* Count: " + str(comps_dict[star_threshold][comp_tuple]["5* count"]))
        # print("   Deepwood Holders: " + str(comps_dict[star_threshold][comp_tuple]["deepwood"]))
        # print("   Deepwood Rate: " + str(comps_dict[star_threshold][comp_tuple]["deepwood_rate"]))
        # if comps_dict[star_threshold][comp_tuple]["5* count"] <= 1:
        #     print("   F2P App: " + str(comps_dict[star_threshold][comp_tuple]["app_rate"]))
        # print()
        # for i in comp_tuple:
        #     print(i + ": ")
        #     for weapon in comps_dict[star_threshold][comp_tuple][i]["weapon"]:
        #         print("   " + weapon + ": " + str(comps_dict[star_threshold][comp_tuple][i]["weapon"][weapon]))
        #     print()
        #     for artifacts in comps_dict[star_threshold][comp_tuple][i]["artifacts"]:
        #         print("   " + artifacts + ": " + str(comps_dict[star_threshold][comp_tuple][i]["artifacts"][artifacts]))
        #     print()

def duo_usages(comps,
                players,
                usage,
                archetype,
                rooms=["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2", "5-1", "5-2", "6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2"],
                filename="duo_usages"):
    duos_dict = used_duos(players, comps, rooms, usage, archetype)
    duo_write(duos_dict, usage, filename, archetype)

def used_duos(players, comps, rooms, usage, archetype, phase=RECENT_PHASE):
    # Returns dictionary of all the duos used and how many times they were used
    duos_dict = {}

    for comp in comps:
        if len(comp.characters) < 2 or comp.room not in rooms:
            continue

        # foundPyro = False
        # foundHydro = False
        # foundDendro = False
        # foundNilou = False
        # foundOnField = False

        # testChar = 0
        # while not foundPyro and testChar < len(pyroChars):
        #     if comp.char_presence[pyroChars[testChar]]:
        #         foundPyro = True
        #     testChar += 1

        # testChar = 0
        # while not foundHydro and testChar < len(hydroChars):
        #     if comp.char_presence[hydroChars[testChar]]:
        #         foundHydro = True
        #     testChar += 1

        # testChar = 0
        # while not foundDendro and testChar < len(dendroChars):
        #     if comp.char_presence[dendroChars[testChar]]:
        #         foundDendro = True
        #     testChar += 1

        # testChar = 0
        # while not foundOnField and testChar < len(onField):
        #     if comp.char_presence[onField[testChar]]:
        #         foundOnField = True
        #     testChar += 1

        # if comp.char_presence["Nilou"]:
        #     foundNilou = True

        match archetype:
            case "Nilou":
                if not (foundNilou):
                    continue
            case "dendro":
                if not (foundDendro):
                    continue
            case "nondendro":
                if not (not foundDendro):
                    continue
            case "off-field":
                if not (not foundOnField and not foundNilou):
                    continue
            case "on-field":
                if not (foundOnField and not foundNilou):
                    continue
            case "melt":
                if not (foundPyro):
                    continue
            case "freeze":
                if not (not foundPyro and foundHydro):
                    continue
            case _:
                pass

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
        if usage[phase][duo[0]]["app_flat"] > 0:
            # Calculate the appearance rate of the duo by dividing the appearance count
            # of the duo with the appearance count of the first character
            duos_dict[duo] = round(duos_dict[duo] * 100 / usage[phase][duo[0]]["app_flat"], 2)
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
    own = cu.ownership(players, chambers = rooms)
    app = cu.appearances(players, own, archetype, chambers = rooms, offset = offset, info_char = info_char)
    chars_dict = cu.usages(own, app, past_phase, filename, chambers = rooms, offset = offset)
    # # Print the list of weapons and artifacts used for a character
    # if floor:
    #     print(app[RECENT_PHASE][filename])
    char_usages_write(chars_dict[RECENT_PHASE], filename, floor, archetype)
    return chars_dict

def comp_usages_write(comps_dict, filename, floor, info_char):
    out_json = []
    out_comps = []
    outvar_comps = []
    var_comps = []
    exc_comps = []
    variations = {}

    # Sort the comps according to their usage rate
    for star_threshold in range(0,5):
        comps_dict[star_threshold] = dict(sorted(comps_dict[star_threshold].items(), key=lambda t: t[1]["app_rate"], reverse=True))
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
                    if comps_dict[star_threshold][comp]["app_rate"] > app_rate_threshold or (info_char and comps_dict[star_threshold][comp]["app_rate"] > char_app_rate_threshold):
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
                            "app_rate": str(comps_dict[star_threshold][comp]["app_rate"]) + "%",
                            "app_flat": str(len(comps_dict[star_threshold][comp]["players"])),
                            # "own_rate": str(comps_dict[star_threshold][comp]["own_rate"]) + "%",
                            # "usage_rate": str(comps_dict[star_threshold][comp]["usage_rate"]) + "%"
                        }
                        j = 1
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
                                out_comps.append(out_comps_append)
                            else:
                                variations[comp_name] += 1
                                out_comps_append["variation"] = variations[comp_name]
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
                            "app_rate": str(comps_dict[star_threshold][comp]["app_rate"]) + "%",
                            # "own_rate": str(comps_dict[star_threshold][comp]["own_rate"]) + "%",
                            # "usage_rate": str(comps_dict[star_threshold][comp]["usage_rate"]) + "%",
                        }
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
                        "app_rate": str(comps_dict[star_threshold][comp]["app_rate"]) + "%",
                        # "own_rate": str(comps_dict[star_threshold][comp]["own_rate"]) + "%",
                        # "usage_rate": str(comps_dict[star_threshold][comp]["usage_rate"]) + "%"
                    }
                    outvar_comps.append(outvar_comps_append)
            if not info_char:
                out = name_filter(comp, mode="out")
                out_json.append({
                    "char_one": out[0],
                    "char_two": out[1],
                    "char_three": out[2],
                    "char_four": out[3],
                    "app_rate": comps_dict[star_threshold][comp]["app_rate"],
                    "rank": comps_dict[star_threshold][comp]["app_rank"],
                    "star_num": str(star_threshold)
                })

    if info_char:
        out_comps += var_comps

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

    if not info_char:
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
        if usage[RECENT_PHASE][char]["app_flat"] > 20:
            out_duos_append = {
                "char": char,
                "app_rate": usage[RECENT_PHASE][char]["app_flat"],
            }
            for i in range(8):
                if i < len(duos_dict[char]):
                    out_duos_append["app_rate_" + str(i + 1)] = str(duos_dict[char][i][1]) + "%"
                    out_duos_append["char_" + str(i + 1)] = duos_dict[char][i][0]
                else:
                    out_duos_append["app_rate_" + str(i + 1)] = "0%"
                    out_duos_append["char_" + str(i + 1)] = "-"
            out_duos.append(out_duos_append)
    out_duos = sorted(out_duos, key=lambda t: t["app_rate"], reverse = True)

    if archetype != "all":
        filename = filename + "_" + archetype
    csv_writer = csv.writer(open("../comp_results/" + filename + ".csv", 'w', newline=''))
    for duos in out_duos:
        csv_writer.writerow(duos.values())

def char_usages_write(chars_dict, filename, floor, archetype):
    out_chars = []
    weap_len = 10
    arti_len = 10
    planar_len = 5
    chars_dict = dict(sorted(chars_dict.items(), key=lambda t: t[1]["app"], reverse=True))
    for char in chars_dict:
        out_chars_append = {
            "char": char,
            "app_rate": str(chars_dict[char]["app"]) + "%",
            # "usage_rate": str(chars_dict[char]["usage"]) + "%",
            # "own_rate": str(chars_dict[char]["own"]) + "%",
            "rarity": chars_dict[char]["rarity"],
            "diff": str(chars_dict[char]["diff"]) + "%"
        }
        for i in ["app_rate","diff"]:
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

def comp_chars(row, cols):
    comp = []
    for i in range(5, 5 + len(CHARACTERS)):
        if row[i] == '1':
            comp.append(cols[i])
    return comp

def form_comps(col_names, table, info_char):
    round_num = col_names.index('round_num')
    star_num = col_names.index('star_num')
    room = col_names.index('room')
    phase = col_names.index('phase')
    comps = []

    for row in table:
        comp = Composition(row[0], comp_chars(row, col_names), row[phase], row[round_num], row[star_num], row[room], info_char)
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
