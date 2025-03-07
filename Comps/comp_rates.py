import csv
import time
import char_usage as cu
import statistics
import os
from scipy.stats import skew, trim_mean
from itertools import permutations
from plyer import notification
from composition import Composition
from player_phase import PlayerPhase
from slugify import slugify
from comp_rates_config import (
    RECENT_PHASE,
    CHARACTERS,
    json,
    as_mode,
    pf_mode,
    skip_random,
    skip_self,
    alt_comps,
    run_commands,
    archetype,
    past_phase,
    whaleOnly,
    f2pOnly,
    sigWeaps,
    char_infographics,
    app_rate_threshold,
    app_rate_threshold_round,
    char_app_rate_threshold,
    json_threshold,
    duo_dict_len,
)
from archetypes import find_archetype, resetfind, findchars

with open("prydwen-slug.json") as slug_file:
    slug = json.load(slug_file)


def main():
    for make_path in [
        "../comp_results",
        "../comp_results/json",
        "../mihomo/results_real",
        "../char_results",
        "../rogue_results",
    ]:
        if not os.path.exists(make_path):
            os.makedirs(make_path)

    start_time = time.time()
    print("start")

    global self_uids
    if os.path.isfile("../../uids.csv"):
        with open("../../uids.csv", "r", encoding="UTF8") as f:
            reader = csv.reader(f, delimiter=",")
            self_uids = list(reader)[0]
    else:
        self_uids = []

    pf_filename = ""
    if as_mode:
        pf_filename = "_as"
    elif pf_mode:
        pf_filename = "_pf"
    if os.path.exists("../data/raw_csvs_real/"):
        stats = open("../data/raw_csvs_real/" + RECENT_PHASE + pf_filename + ".csv")
    else:
        stats = open("../data/raw_csvs/" + RECENT_PHASE + pf_filename + ".csv")

    # uid_freq_comp will help detect duplicate UIDs
    reader = csv.reader(stats)
    next(reader)
    all_comps = []
    if pf_mode:
        all_chambers = ["1", "2", "3", "4"]
    else:
        all_chambers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
    three_star_sample = {}
    for chamber_num in all_chambers:
        three_star_sample[chamber_num] = 0
    uid_freq_comp = {}
    self_freq_comp = {}
    # dps_freq_comp = {}
    last_uid = "0"

    for line in reader:
        if skip_self and line[0] in self_uids:
            continue
        if skip_random and line[0] not in self_uids:
            continue
        if line[0] != last_uid:
            skip_uid = False
            if line[0] in uid_freq_comp:
                skip_uid = True
                # print("duplicate UID in comp: " + line[0])
            elif (
                not pf_mode
                and int("".join(filter(str.isdigit, line[1]))) > 11
                and int(line[4]) == 3
            ) or (
                pf_mode
                and int("".join(filter(str.isdigit, line[1]))) > 3
                and int(line[4]) == 3
            ):
                uid_freq_comp[line[0]] = 1
                if line[0] in self_uids:
                    self_freq_comp[line[0]] = 1
            else:
                skip_uid = True
        # else:
        #     uid_freq_comp[line[0]] += 1
        last_uid = line[0]
        if not skip_uid:
            stage = "".join(filter(str.isdigit, line[1]))
            comp_chars_temp = []
            for i in range(5, 9):
                if line[i] != "":
                    if "Imbibitor" in line[i]:
                        line[i] = "Dan Heng • Imbibitor Lunae"
                    elif "Topaz and Numby" == line[i]:
                        line[i] = "Topaz & Numby"
                    elif "March 7th" == line[i]:
                        line[i] = "Ice March 7th"
                    comp_chars_temp.append(line[i])
            cons_chars_temp = []
            if len(line) > 10:
                for i in range(9, 13):
                    if line[i] != "":
                        cons_chars_temp.append(line[i])
                pf_buff = line[13] if pf_mode else ""
            else:
                pf_buff = line[9] if pf_mode else ""
            if comp_chars_temp:
                comp = Composition(
                    line[0],
                    comp_chars_temp,
                    RECENT_PHASE,
                    line[3],
                    line[4],
                    stage + "-" + str(line[2]),
                    alt_comps,
                    pf_buff,
                    cons_chars_temp,
                )
                # if int(stage) > 7:
                #     if line[0] not in dps_freq_comp:
                #         dps_freq_comp[line[0]] = set()
                #     if comp.dps == []:
                #         if comp.sub != []:
                #             dps_freq_comp[line[0]].add(frozenset([comp.sub[0]]))
                #     else:
                #         dps_freq_comp[line[0]].add(frozenset([comp.dps[0]]))
                all_comps.append(comp)
                if int(line[4]) == 3:
                    three_star_sample[stage] += 1

    # len_dps_freq_comp = {}
    # for i in dps_freq_comp:
    #     if len(dps_freq_comp[i]) not in len_dps_freq_comp:
    #         len_dps_freq_comp[len(dps_freq_comp[i])] = 0
    #     len_dps_freq_comp[len(dps_freq_comp[i])] += 1
    #     if len(dps_freq_comp[i]) == 1:
    #         print(str(i) + ": " + str(dps_freq_comp[i]))
    # print(len_dps_freq_comp)
    # exit()

    global sample_size
    sample_size = {}
    for chamber_num in all_chambers:
        sample_size[chamber_num] = {}
    global avg_round_stage
    avg_round_stage = {}
    for chamber_num in all_chambers:
        avg_round_stage[chamber_num] = []
    global valid_duo_dps
    if os.path.exists("../char_results/duo_check.csv"):
        with open("../char_results/duo_check.csv", "r") as f:
            valid_duo_dps = list(csv.reader(f, delimiter=","))
    else:
        valid_duo_dps = []
    # max_weight = 0
    sample_size["all"] = {
        "total": len(uid_freq_comp),
        "self_report": len(self_freq_comp),
        "random": len(uid_freq_comp) - len(self_freq_comp),
    }

    # global stage_weight
    # stage_weight = {}
    # for stage in avg_round_stage:
    #     stage_weight[stage] = max_weight / sample_size[stage]["avg_round_stage"]
    #     sample_size[stage]["weight"] = stage_weight[stage]

    if os.path.exists("../data/raw_csvs_real/"):
        stats = open("../data/raw_csvs_real/" + RECENT_PHASE + "_char.csv")
    else:
        stats = open("../data/raw_csvs/" + RECENT_PHASE + "_char.csv")

    # uid_freq_char and last_uid will help detect duplicate UIDs
    reader = csv.reader(stats)
    next(reader)
    all_players = {}
    all_players[RECENT_PHASE] = {}
    last_uid = "0"
    player = PlayerPhase(last_uid, RECENT_PHASE)
    uid_freq_char = []

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
            if not skip_uid:
                if line[0] != last_uid:
                    all_players[RECENT_PHASE][last_uid] = player
                    last_uid = line[0]
                    player = PlayerPhase(last_uid, RECENT_PHASE)
                if "Imbibitor" in line[2]:
                    line[2] = "Dan Heng • Imbibitor Lunae"
                elif "Topaz and Numby" == line[2]:
                    line[2] = "Topaz & Numby"
                elif "March 7th" == line[2]:
                    line[2] = "Ice March 7th"
                player.add_character(
                    line[2], line[3], line[4], line[5], line[6], line[7], line[8]
                )
    all_players[RECENT_PHASE][last_uid] = player

    for comp in all_comps:
        if comp.player not in all_players[comp.phase]:
            all_players[comp.phase][comp.player] = PlayerPhase(comp.player, comp.phase)
        all_players[comp.phase][comp.player].add_comp(comp)

    csv_writer = csv.writer(open("../char_results/uids.csv", "w", newline=""))
    for uid in uid_freq_comp.keys():
        csv_writer.writerow([uid])

    cur_time = time.time()
    print("done csv: ", (cur_time - start_time), "s")

    global usage
    if pf_mode:
        three_stages = ["4-1", "4-2"]
        three_double_stages = [["4-1", "4-2"]]
        one_stage = ["4-1", "4-2"]
        all_stages = ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2"]
        # all_double_stages = [
        #     ["1-1", "1-2"],
        #     ["2-1", "2-2"],
        #     ["3-1", "3-2"],
        #     ["4-1", "4-2"],
        # ]
    else:
        three_stages = ["10-1", "10-2", "11-1", "11-2", "12-1", "12-2"]
        three_double_stages = [["10-1", "10-2"], ["11-1", "11-2"], ["12-1", "12-2"]]
        one_stage = ["12-1", "12-2"]
        all_stages = [
            "1-1",
            "1-2",
            "2-1",
            "2-2",
            "3-1",
            "3-2",
            "4-1",
            "4-2",
            "5-1",
            "5-2",
            "6-1",
            "6-2",
            "7-1",
            "7-2",
            "8-1",
            "8-2",
            "9-1",
            "9-2",
            "10-1",
            "10-2",
            "11-1",
            "11-2",
            "12-1",
            "12-2",
        ]
        # all_double_stages = [
        #     ["1-1", "1-2"],
        #     ["2-1", "2-2"],
        #     ["3-1", "3-2"],
        #     ["4-1", "4-2"],
        #     ["5-1", "5-2"],
        #     ["6-1", "6-2"],
        #     ["7-1", "7-2"],
        #     ["8-1", "8-2"],
        #     ["9-1", "9-2"],
        #     ["10-1", "10-2"],
        #     ["11-1", "11-2"],
        #     ["12-1", "12-2"],
        # ]

        # three_stages = ["8-1", "8-2", "9-1", "9-2", "10-1", "10-2"]
        # three_double_stages = [["8-1", "8-2"], ["9-1", "9-2"], ["10-1", "10-2"]]
        # one_stage = ["10-1", "10-2"]
        # all_stages = ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2", "5-1", "5-2", "6-1", "6-2", "7-1", "7-2", "8-1", "8-2", "9-1", "9-2", "10-1", "10-2"]
        # all_double_stages = [["1-1", "1-2"], ["2-1", "2-2"], ["3-1", "3-2"], ["4-1", "4-2"], ["5-1", "5-2"], ["6-1", "6-2"], ["7-1", "7-2"], ["8-1", "8-2"], ["9-1", "9-2"], ["10-1", "10-2"]]

    if "Char usages all stages" in run_commands:
        char_usages(
            all_players, archetype, past_phase, all_stages, filename="all", floor=True
        )
        cur_time = time.time()
        print("done char: ", (cur_time - start_time), "s")

    if "Duos check" in run_commands:
        usage = char_usages(
            all_players, archetype, past_phase, three_stages, filename="all", floor=True
        )
        duo_usages(
            all_comps, all_players, usage, archetype, three_stages, check_duo=True
        )

    if "Char usages 8 - 10" in run_commands:
        usage = char_usages(
            all_players, archetype, past_phase, one_stage, filename="all", floor=True
        )
        if not whaleOnly and not f2pOnly:
            duo_usages(
                all_comps, all_players, usage, archetype, one_stage, check_duo=False
            )
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
        #         if usage[star_num][char]["round"] == 0:
        #             continue
        #         rounds[star_num][char] = {
        #             "round": usage[star_num][char]["round"],
        #             "rarity": usage[star_num][char]["rarity"],
        #             "diff": usage[star_num][char]["diff_rounds"]
        #         }
        # with open("../char_results/appearance_top.json", "w") as out_file:
        #     out_file.write(json.dumps(appearances,indent=2))
        # with open("../char_results/rounds_top.json", "w") as out_file:
        #     out_file.write(json.dumps(rounds,indent=2))
        cur_time = time.time()
        print("done char 8 - 10: ", (cur_time - start_time), "s")

    if "Char usages for each stage" in run_commands:
        char_chambers = {"all": {}}
        for star_num in usage:
            char_chambers["all"][star_num] = usage[star_num].copy()
        # for room in all_stages:
        for room in three_stages:
            char_chambers[room] = char_usages(
                all_players, archetype, past_phase, [room], filename=room, offset=2
            )
        appearances = {}
        rounds = {}
        for room in char_chambers:
            appearances[room] = {}
            rounds[room] = {}
            for star_num in char_chambers[room]:
                appearances[room][star_num] = dict(
                    sorted(
                        char_chambers[room][star_num].items(),
                        key=lambda t: t[1]["app"],
                        reverse=True,
                    )
                )
                if pf_mode:
                    rounds[room][star_num] = dict(
                        sorted(
                            char_chambers[room][star_num].items(),
                            key=lambda t: t[1]["round"],
                            reverse=True,
                        )
                    )
                else:
                    rounds[room][star_num] = dict(
                        sorted(
                            char_chambers[room][star_num].items(),
                            key=lambda t: t[1]["round"],
                            reverse=False,
                        )
                    )
                for char in char_chambers[room][star_num]:
                    appearances[room][star_num][char] = {
                        "app": char_chambers[room][star_num][char]["app"],
                        "rarity": char_chambers[room][star_num][char]["rarity"],
                        "diff": char_chambers[room][star_num][char]["diff"],
                    }
                    if char_chambers[room][star_num][char]["round"] == 0:
                        continue
                    rounds[room][star_num][char] = {
                        "round": char_chambers[room][star_num][char]["round"],
                        # "prev_round": prev_chambers[room][str(star_num)][char],
                        "rarity": char_chambers[room][star_num][char]["rarity"],
                        "diff": char_chambers[room][star_num][char]["diff_rounds"],
                    }
        if not whaleOnly and not f2pOnly:
            with open("../char_results/appearance.json", "w") as out_file:
                out_file.write(json.dumps(appearances, indent=2))
            with open("../char_results/rounds.json", "w") as out_file:
                out_file.write(json.dumps(rounds, indent=2))
        cur_time = time.time()
        print("done char stage: ", (cur_time - start_time), "s")

    if "Char usages for each stage (combined)" in run_commands:
        char_chambers = {"all": {}}
        for star_num in usage:
            char_chambers["all"][star_num] = usage[star_num].copy()
        # for room in all_double_stages:
        for room in three_double_stages:
            char_chambers[room[0]] = char_usages(
                all_players, archetype, past_phase, room, filename=room[0].split("-")[0]
            )
        appearances = {}
        rounds = {}
        for room in char_chambers:
            appearances[room] = {}
            rounds[room] = {}
            for star_num in char_chambers[room]:
                appearances[room][star_num] = dict(
                    sorted(
                        char_chambers[room][star_num].items(),
                        key=lambda t: t[1]["app"],
                        reverse=True,
                    )
                )
                if pf_mode:
                    rounds[room][star_num] = dict(
                        sorted(
                            char_chambers[room][star_num].items(),
                            key=lambda t: t[1]["round"],
                            reverse=True,
                        )
                    )
                else:
                    rounds[room][star_num] = dict(
                        sorted(
                            char_chambers[room][star_num].items(),
                            key=lambda t: t[1]["round"],
                            reverse=False,
                        )
                    )
                for char in char_chambers[room][star_num]:
                    appearances[room][star_num][char] = {
                        "app": char_chambers[room][star_num][char]["app"],
                        "rarity": char_chambers[room][star_num][char]["rarity"],
                        "diff": char_chambers[room][star_num][char]["diff"],
                    }
                    if char_chambers[room][star_num][char]["round"] == 0:
                        continue
                    rounds[room][star_num][char] = {
                        "round": char_chambers[room][star_num][char]["round"],
                        # "prev_round": prev_chambers[room][str(star_num)][char],
                        "rarity": char_chambers[room][star_num][char]["rarity"],
                        "diff": char_chambers[room][star_num][char]["diff_rounds"],
                    }
        if not whaleOnly and not f2pOnly:
            with open("../char_results/appearance_combine.json", "w") as out_file:
                out_file.write(json.dumps(appearances, indent=2))
            with open("../char_results/rounds_combine.json", "w") as out_file:
                out_file.write(json.dumps(rounds, indent=2))
        cur_time = time.time()
        print("done char stage (combine): ", (cur_time - start_time), "s")

    global all_comps_json
    all_comps_json = {}
    if "Comp usage all stages" in run_commands:
        comp_usages(all_comps, all_players, all_stages, filename="all", floor=True)
        cur_time = time.time()
        print("done comp all: ", (cur_time - start_time), "s")

    if "Comp usage 8 - 10" in run_commands:
        comp_usages(all_comps, all_players, one_stage, filename="top", floor=True)
        cur_time = time.time()
        print("done comp 8 - 10: ", (cur_time - start_time), "s")

    if "Comp usages for each stage" in run_commands:
        # for room in all_stages:
        for room in three_stages:
            comp_usages(all_comps, all_players, [room], filename=room, offset=2)

        if not whaleOnly and not f2pOnly:
            with open("../char_results/demographic.json", "w") as out_file:
                out_file.write(json.dumps(sample_size, indent=2))
        cur_time = time.time()
        print("done comp stage: ", (cur_time - start_time), "s")

    if "Character specific infographics" in run_commands:
        comp_usages(
            all_comps,
            all_players,
            one_stage,
            filename=char_infographics,
            info_char=True,
            floor=True,
        )
        cur_time = time.time()
        print("done char infographics: ", (cur_time - start_time), "s")

    if (
        "Comp usage 8 - 10" in run_commands
        and "Comp usages for each stage" in run_commands
        and not whaleOnly
        and not f2pOnly
    ):
        with open("../comp_results/json/all_comps.json", "w") as out_file:
            out_file.write(json.dumps(all_comps_json, indent=2))

    if __name__ == "__main__":
        notification.notify(
            title="Finished",
            message="Finished executing comp_rates",
            # displaying time
            timeout=2,
        )  # type: ignore
        # waiting time
        time.sleep(2)


def comp_usages(
    comps,
    players,
    rooms,
    filename="comp_usages",
    offset=1,
    info_char=False,
    floor=False,
):
    global top_comps_app
    top_comps_app = {}
    comps_dict = used_comps(players, comps, rooms, filename, floor=floor, offset=offset)
    rank_usages(comps_dict, rooms, owns_offset=offset)
    comp_usages_write(comps_dict, filename, floor, info_char, True)
    comp_usages_write(comps_dict, filename, floor, info_char, False)


def used_comps(
    players, comps, rooms, filename, phase=RECENT_PHASE, floor=False, offset=1
):
    # Returns the dictionary of all the comps used and how many times they were used
    comps_dict = [{}, {}, {}, {}, {}]
    # error_uids = []
    # lessFour = []
    # lessFourComps = {}
    global total_comps
    total_comps = 0
    total_self_comps = 0
    whale_count = 0
    f2p_count = 0
    # dual_dps = {}
    # total_char_comps = {}

    # For storing the prev and next comps
    comp_iter = 0
    side_comp = None
    for comp in comps:
        if comp_iter - 1 > len(comps):
            if comps[comp_iter - 1].player == comp.player:
                side_comp = comps[comp_iter - 1]
        elif not side_comp and comp_iter + 1 < len(comps):
            if comps[comp_iter + 1].player == comp.player:
                side_comp = comps[comp_iter + 1]
        comp_iter += 1

        comp_tuple = tuple(comp.characters)
        if side_comp:
            side_comp_tuple = tuple(side_comp.characters)
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
            if len(side_comp_tuple) < 4:
                continue

            whale_comp = False
            f2p_comp = True
            sustain_count = 0
            dps_count = 0
            for char in range(4):
                if CHARACTERS[comp_tuple[char]]["availability"] == "Limited 5*":
                    if comp.char_cons:
                        if comp.char_cons[comp_tuple[char]] > 0:
                            whale_comp = True
                    if comp_tuple[char] in players[phase][comp.player].owned:
                        if (
                            players[phase][comp.player].owned[comp_tuple[char]]["cons"]
                            > 0
                            # ) or (
                            #     players[phase][comp.player].owned[comp_tuple[char]]["weapon"] in sigWeaps
                        ):
                            whale_comp = True
                        if (
                            players[phase][comp.player].owned[comp_tuple[char]][
                                "weapon"
                            ]
                            not in sigWeaps
                        ):
                            f2p_comp = False
                elif (
                    CHARACTERS[side_comp_tuple[char]]["availability"] == "Limited 5*"
                    and not whale_comp
                    and side_comp
                    and not pf_mode
                    and not as_mode
                ):
                    if side_comp.char_cons:
                        if side_comp.char_cons[side_comp_tuple[char]] > 0:
                            whale_comp = True
                    elif (
                        side_comp_tuple[char] in players[phase][side_comp.player].owned
                    ):
                        if (
                            players[phase][side_comp.player].owned[
                                side_comp_tuple[char]
                            ]["cons"]
                            > 0
                            # ) or (
                            #     whaleSigWeap and players[phase][side_comp.player].owned[comp_tuple[char]]["weapon"] in sigWeaps
                        ):
                            whale_comp = True
                # if comp_tuple[char] not in total_char_comps:
                #     total_char_comps[comp_tuple[char]] = 0
                # total_char_comps[comp_tuple[char]] += 1
                if CHARACTERS[comp_tuple[char]]["role"] == "Sustain":
                    sustain_count += 1
                if CHARACTERS[comp_tuple[char]]["role"] == "Damage Dealer":
                    dps_count += 1
                for duo_dps in valid_duo_dps:
                    if set(duo_dps).issubset(comp_tuple):
                        dps_count = 1
                        break

            if whale_comp:
                whale_count += 1
            if whaleOnly and not whale_comp:
                continue
            if f2p_comp:
                f2p_count += 1
            if f2pOnly and (not f2p_comp or whale_comp):
                continue

            for star_threshold in range(0, 5):
                if star_threshold != 4 and comp.star_num != star_threshold:
                    continue
                if comp_tuple not in comps_dict[star_threshold]:
                    comps_dict[star_threshold][comp_tuple] = {
                        "uses": 0,
                        "owns": 0,
                        "5* count": comp.fivecount,
                        "comp_name": comp.comp_name,
                        "alt_comp_name": comp.alt_comp_name,
                        "dual_comp_name": comp.dual_comp_name,
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
                            "11": [],
                            "12": [],
                        },
                        "whale_count": set(),
                        "players": set(),
                    }
                    for char in range(4):
                        comps_dict[star_threshold][comp_tuple][comp_tuple[char]] = {
                            "weapon": {},
                            "artifacts": {},
                            "cons": {},
                        }
                        for i in range(7):
                            comps_dict[star_threshold][comp_tuple][comp_tuple[char]][
                                "cons"
                            ][str(i)] = 0
                comps_dict[star_threshold][comp_tuple]["uses"] += 1
                # comps_dict[star_threshold][comp_tuple]["round_num"][list(str(comp.room).split("-"))[0]].append(comp.round_num)
                comps_dict[star_threshold][comp_tuple]["players"].add(comp.player)
                if whale_comp:
                    comps_dict[star_threshold][comp_tuple]["whale_count"].add(
                        comp.player
                    )
                if whale_comp == whaleOnly and (not f2pOnly or f2p_comp):
                    for i in range(4):
                        if comp_tuple[i] in players[phase][comp.player].owned:
                            if (
                                players[phase][comp.player].owned[comp_tuple[i]][
                                    "weapon"
                                ]
                                in comps_dict[star_threshold][comp_tuple][
                                    comp_tuple[i]
                                ]["weapon"]
                            ):
                                comps_dict[star_threshold][comp_tuple][comp_tuple[i]][
                                    "weapon"
                                ][
                                    players[phase][comp.player].owned[comp_tuple[i]][
                                        "weapon"
                                    ]
                                ] += 1
                            else:
                                comps_dict[star_threshold][comp_tuple][comp_tuple[i]][
                                    "weapon"
                                ][
                                    players[phase][comp.player].owned[comp_tuple[i]][
                                        "weapon"
                                    ]
                                ] = 1
                            if (
                                players[phase][comp.player].owned[comp_tuple[i]][
                                    "artifacts"
                                ]
                                != ""
                            ):
                                if (
                                    players[phase][comp.player].owned[comp_tuple[i]][
                                        "artifacts"
                                    ]
                                    in comps_dict[star_threshold][comp_tuple][
                                        comp_tuple[i]
                                    ]["artifacts"]
                                ):
                                    comps_dict[star_threshold][comp_tuple][
                                        comp_tuple[i]
                                    ]["artifacts"][
                                        players[phase][comp.player].owned[
                                            comp_tuple[i]
                                        ]["artifacts"]
                                    ] += 1
                                else:
                                    comps_dict[star_threshold][comp_tuple][
                                        comp_tuple[i]
                                    ]["artifacts"][
                                        players[phase][comp.player].owned[
                                            comp_tuple[i]
                                        ]["artifacts"]
                                    ] = 1
                            comps_dict[star_threshold][comp_tuple][comp_tuple[i]][
                                "cons"
                            ][
                                str(
                                    players[phase][comp.player].owned[comp_tuple[i]][
                                        "cons"
                                    ]
                                )
                            ] += 1
                    comps_dict[star_threshold][comp_tuple]["round_num"][
                        list(str(comp.room).split("-"))[0]
                    ].append(comp.round_num)
                    if star_threshold == 4 and sustain_count <= 1:
                        avg_round_stage[list(str(comp.room).split("-"))[0]].append(
                            comp.round_num
                        )
                        if pf_mode:
                            if (
                                "buff_" + comp.buff
                                not in sample_size[list(str(comp.room).split("-"))[0]]
                            ):
                                sample_size[list(str(comp.room).split("-"))[0]][
                                    "buff_" + comp.buff
                                ] = 0
                            sample_size[list(str(comp.room).split("-"))[0]][
                                "buff_" + comp.buff
                            ] += 1

    for stage in avg_round_stage:
        sample_size[stage]["avg_round"] = round(
            statistics.mean(avg_round_stage[stage] if avg_round_stage[stage] else [0]),
            2,
        )
        # "3_star": three_star_sample[stage]
        # if sample_size[stage]["avg_round_stage"] > max_weight:
        #     max_weight = sample_size[stage]["avg_round_stage"]

    chamber_num = list(str(filename).split("-"))
    if len(chamber_num) > 1:
        if chamber_num[1] == "1":
            sample_size[chamber_num[0]]["total"] = total_comps
            sample_size[chamber_num[0]]["self_report"] = total_self_comps
            sample_size[chamber_num[0]]["random"] = total_comps - total_self_comps
        # if total_comps == 0:
        #     del sample_size[chamber_num[0]]
    if whaleOnly:
        print("Whale percentage: " + str(whale_count / total_comps))
    return comps_dict


def rank_usages(comps_dict, rooms, owns_offset=1):
    # Calculate the usage rate and sort the comps according to it
    for star_threshold in range(0, 5):
        rates = []
        # rounds = []
        for comp in comps_dict[star_threshold]:
            avg_round = []
            uses_room = {}

            for room_num in range(1, 13):
                if comps_dict[star_threshold][comp]["round_num"][str(room_num)]:
                    uses_room[room_num] = len(
                        comps_dict[star_threshold][comp]["round_num"][str(room_num)]
                    )
                    if comps_dict[star_threshold][comp]["uses"] > 1:
                        skewness = skew(
                            comps_dict[star_threshold][comp]["round_num"][
                                str(room_num)
                            ],
                            axis=0,
                            bias=True,
                        )
                        if abs(skewness) > 0.8:
                            avg_round.append(
                                trim_mean(
                                    comps_dict[star_threshold][comp]["round_num"][
                                        str(room_num)
                                    ],
                                    0.25,
                                )
                            )
                        else:
                            avg_round.append(
                                statistics.mean(
                                    comps_dict[star_threshold][comp]["round_num"][
                                        str(room_num)
                                    ]
                                )
                            )
                    else:
                        avg_round.append(
                            statistics.mean(
                                comps_dict[star_threshold][comp]["round_num"][
                                    str(room_num)
                                ]
                            )
                        )
                    # avg_round.append(statistics.mean(comps_dict[star_threshold][comp]["round_num"][str(room_num)]))
                    # avg_round += comps_dict[star_threshold][comp]["round_num"][str(room_num)]

            comps_dict[star_threshold][comp]["is_count_round"] = True
            comps_dict[star_threshold][comp]["is_count_round_print"] = True
            if (rooms == ["12-1", "12-2"]) or pf_mode and rooms == ["4-1", "4-2"]:
                for room_num in uses_room:
                    if whaleOnly:
                        if uses_room[room_num] < 10:
                            comps_dict[star_threshold][comp]["is_count_round"] = False
                    elif uses_room[room_num] < 15:
                        comps_dict[star_threshold][comp]["is_count_round"] = False
                    if uses_room[room_num] < 2:
                        comps_dict[star_threshold][comp]["is_count_round_print"] = False
            elif len(rooms) == 1:
                if whaleOnly:
                    if comps_dict[star_threshold][comp]["uses"] < 10:
                        comps_dict[star_threshold][comp]["is_count_round"] = False
                elif comps_dict[star_threshold][comp]["uses"] < 15:
                    comps_dict[star_threshold][comp]["is_count_round"] = False
                if comps_dict[star_threshold][comp]["uses"] < 2:
                    comps_dict[star_threshold][comp]["is_count_round_print"] = False

            if avg_round:
                avg_round = round(statistics.mean(avg_round), 2)
                if pf_mode:
                    avg_round = round(avg_round)
            else:
                avg_round = 99.99
                if pf_mode:
                    avg_round = 0

            app = (
                int(
                    100.0
                    * comps_dict[star_threshold][comp]["uses"]
                    / (total_comps * owns_offset)
                    * 200
                    + 0.5
                )
                / 100.0
            )
            comps_dict[star_threshold][comp]["app_rate"] = app
            comps_dict[star_threshold][comp]["round"] = avg_round
            # rate = int(100.0 * comps_dict[star_threshold][comp]["uses"] / comps_dict[star_threshold][comp]["owns"] * 100 + .5) / 100.0
            comps_dict[star_threshold][comp]["usage_rate"] = 0
            # own = int(100.0 * comps_dict[star_threshold][comp]["owns"] / (total_comps * owns_offset) * 100 + .5) / 100.0
            comps_dict[star_threshold][comp]["own_rate"] = 0
            rates.append(app)
            # rounds.append(avg_round)
        rates.sort(reverse=True)
        # rounds.sort(reverse=False)
        for comp in comps_dict[star_threshold]:
            comps_dict[star_threshold][comp]["app_rank"] = (
                rates.index(comps_dict[star_threshold][comp]["app_rate"]) + 1
            )
            # comps_dict[star_threshold][comp]["round_rank"] = rounds.index(comps_dict[star_threshold][comp]["round"]) + 1

    # # To check the list of weapons and artifacts for a comp
    # comp_tuples = [('Kafka', 'Asta', 'Tingyun', 'Luocha'), ('Kafka', 'Asta', 'Tingyun', 'Bailu')]
    # for comp_tuple in comp_tuples:
    #     print(comp_tuple)
    #     print("   App: " + str(comps_dict[4][comp_tuple]["app_rate"]))
    #     print("   Own: " + str(comps_dict[4][comp_tuple]["own_rate"]))
    #     print("   Usage: " + str(comps_dict[4][comp_tuple]["usage_rate"]))
    #     print("   5* Count: " + str(comps_dict[4][comp_tuple]["5* count"]))
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
    #         for cons in comps_dict[4][comp_tuple][i]["cons"]:
    #             print("   " + cons + ": " + str(comps_dict[4][comp_tuple][i]["cons"][cons]))
    #         print()


def duo_usages(
    comps, players, usage, archetype, rooms, check_duo=False, filename="duo_usages"
):
    duos_dict = used_duos(players, comps, rooms, usage, check_duo, archetype)
    duo_write(duos_dict, usage, filename, archetype, check_duo)


def used_duos(players, comps, rooms, usage, archetype, check_duo, phase=RECENT_PHASE):
    # Returns dictionary of all the duos used and how many times they were used
    duos_dict = {}

    for comp in comps:
        if len(comp.characters) < 2 or comp.room not in rooms:
            continue

        foundchar = resetfind()
        whale_comp = False
        sustain_count = 0
        for char in comp.characters:
            findchars(char, foundchar)
            if CHARACTERS[char]["availability"] == "Limited 5*":
                if comp.char_cons:
                    if comp.char_cons[char] > 0:
                        whale_comp = True
                elif char in players[phase][comp.player].owned:
                    if players[phase][comp.player].owned[char]["cons"] > 0:
                        whale_comp = True
            if CHARACTERS[char]["role"] == "Sustain":
                sustain_count += 1
        if not find_archetype(foundchar):
            continue

        # Permutate the duos, for example if Ganyu and Xiangling are used,
        # two duos are used, Ganyu/Xiangling and Xiangling/Ganyu
        duos = list(permutations(comp.characters, 2))
        for duo in duos:
            is_triple_dps = False
            # comp_diff_duo = list(set(comp.characters) - set(duo))
            # for char_diff_duo in comp_diff_duo:
            #     if CHARACTERS[char_diff_duo]["role"] == "Damage Dealer" or char_diff_duo in ["Sampo", "Black Swan", "Luka", "Guinaifen", "Ruan Mei"]:
            #         is_triple_dps = True
            #         break

            if duo not in duos_dict:
                duos_dict[duo] = {
                    "app_flat": 0,
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
                        "11": [],
                        "12": [],
                    },
                }
            duos_dict[duo]["app_flat"] += 1

            if is_triple_dps and check_duo:
                continue
            if (not whale_comp) and sustain_count <= 1:
                duos_dict[duo]["round_num"][list(str(comp.room).split("-"))[0]].append(
                    comp.round_num
                )

    sorted_duos = sorted(
        duos_dict.items(), key=lambda t: t[1]["app_flat"], reverse=True
    )
    duos_dict = {k: v for k, v in sorted_duos}

    sorted_duos = {}
    for duo in duos_dict:
        if usage[4][duo[0]]["app_flat"] > 0:
            # Calculate the appearance rate of the duo by dividing the appearance count
            # of the duo with the appearance count of the first character
            duos_dict[duo]["uses"] = round(
                duos_dict[duo]["app_flat"] * 100 / usage[4][duo[0]]["app_flat"], 2
            )
            duos_dict[duo]["app_flat"] = 0
            avg_round = []
            for room_num in range(1, 13):
                if duos_dict[duo]["round_num"][str(room_num)]:
                    duos_dict[duo]["app_flat"] += len(
                        duos_dict[duo]["round_num"][str(room_num)]
                    )
                    if len(duos_dict[duo]["round_num"][str(room_num)]) > 1:
                        skewness = skew(
                            duos_dict[duo]["round_num"][str(room_num)],
                            axis=0,
                            bias=True,
                        )
                        if abs(skewness) > 0.8:
                            avg_round.append(
                                trim_mean(
                                    duos_dict[duo]["round_num"][str(room_num)], 0.25
                                )
                            )
                        else:
                            avg_round.append(
                                statistics.mean(
                                    duos_dict[duo]["round_num"][str(room_num)]
                                )
                            )
                    else:
                        avg_round.append(
                            statistics.mean(duos_dict[duo]["round_num"][str(room_num)])
                        )
                    # avg_round.append(statistics.mean(duos_dict[duo]["round_num"][str(room_num)]))
                    # avg_round += duos_dict[duo]["round_num"][str(room_num)]
            if avg_round:
                duos_dict[duo]["round_num"] = round(statistics.mean(avg_round), 2)
                if pf_mode:
                    duos_dict[duo]["round_num"] = round(duos_dict[duo]["round_num"])
            else:
                duos_dict[duo]["round_num"] = 99.99
                if pf_mode:
                    duos_dict[duo]["round_num"] = 0
            if duo[0] not in sorted_duos:
                sorted_duos[duo[0]] = []
            sorted_duos[duo[0]].append(
                [
                    duo[1],
                    duos_dict[duo]["uses"],
                    duos_dict[duo]["round_num"],
                    duos_dict[duo]["app_flat"],
                ]
            )

    return sorted_duos


def char_usages(
    players,
    archetype,
    past_phase,
    rooms,
    filename="char_usages",
    offset=1,
    info_char=False,
    floor=False,
):
    # own = cu.ownership(players, chambers = rooms)
    own = {}
    app = cu.appearances(
        players, own, archetype, chambers=rooms, offset=offset, info_char=info_char
    )
    chars_dict = cu.usages(
        own, app, past_phase, filename, chambers=rooms, offset=offset
    )
    # # Print the list of weapons and artifacts used for a character
    # if floor:
    #     print(app[RECENT_PHASE][filename])
    if (not pf_mode and rooms == ["12-1", "12-2"]) or (
        pf_mode and rooms == ["4-1", "4-2"]
    ):
        char_usages_write(chars_dict[4], filename, floor, archetype)
    return chars_dict


def comp_usages_write(comps_dict, filename, floor, info_char, sort_app):
    out_json = []
    out_comps = []
    outvar_comps = []
    var_comps = []
    # exc_comps = []
    variations = {}
    if sort_app:
        threshold = app_rate_threshold
    else:
        threshold = app_rate_threshold_round

    # Sort the comps according to their usage rate
    for star_threshold in range(0, 5):
        if sort_app:
            comps_dict[star_threshold] = dict(
                sorted(
                    comps_dict[star_threshold].items(),
                    key=lambda t: t[1]["app_rate"],
                    reverse=True,
                )
            )
        else:
            if pf_mode:
                comps_dict[star_threshold] = dict(
                    sorted(
                        comps_dict[star_threshold].items(),
                        key=lambda t: t[1]["round"],
                        reverse=True,
                    )
                )
            else:
                comps_dict[star_threshold] = dict(
                    sorted(
                        comps_dict[star_threshold].items(),
                        key=lambda t: t[1]["round"],
                        reverse=False,
                    )
                )
        comp_names = []
        dual_comp_names = []

        for comp in comps_dict[star_threshold]:
            if info_char and filename not in comp:
                continue
            if star_threshold == 4:
                comp_name = comps_dict[star_threshold][comp]["comp_name"]
                dual_comp_name = comps_dict[star_threshold][comp]["dual_comp_name"]
                alt_comp_name = comps_dict[star_threshold][comp]["alt_comp_name"]
                # Only one variation of each comp name is included,
                # unless if it's used for a character's infographic
                if (
                    (
                        comp_name not in comp_names
                        and comp_name not in dual_comp_names
                        and dual_comp_name not in comp_names
                        and alt_comp_name not in comp_names
                        and comps_dict[star_threshold][comp]["round"] != 99.99
                        and comps_dict[star_threshold][comp]["round"] != 0
                    )
                    or comp_name == "-"
                    or info_char
                ):
                    if sort_app:
                        top_comps_app[comp_name] = comps_dict[star_threshold][comp][
                            "app_rate"
                        ]
                    elif comp_name in top_comps_app:
                        if (
                            comps_dict[star_threshold][comp]["is_count_round"]
                            and comps_dict[star_threshold][comp]["app_rate"]
                            < top_comps_app[comp_name] / 5
                        ):
                            continue
                    if comps_dict[star_threshold][comp]["is_count_round"] and (
                        comps_dict[star_threshold][comp]["app_rate"] >= threshold
                        or (
                            info_char
                            and comps_dict[star_threshold][comp]["app_rate"]
                            > char_app_rate_threshold
                        )
                    ):
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
                            "app_rate": str(
                                comps_dict[star_threshold][comp]["app_rate"]
                            )
                            + "%",
                            "avg_round": str(comps_dict[star_threshold][comp]["round"]),
                            # "own_rate": str(comps_dict[star_threshold][comp]["own_rate"]) + "%",
                            # "usage_rate": str(comps_dict[star_threshold][comp]["usage_rate"]) + "%"
                        }

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

                        out_comps_append["whale_count"] = str(
                            len(comps_dict[star_threshold][comp]["whale_count"])
                        )
                        out_comps_append["app_flat"] = str(
                            len(comps_dict[star_threshold][comp]["players"])
                        )
                        out_comps_append["uses"] = str(
                            comps_dict[star_threshold][comp]["uses"]
                        )

                        if info_char:
                            if comp_name not in comp_names:
                                out_comps.append(out_comps_append)
                            else:
                                var_comps.append(out_comps_append)
                        else:
                            out_comps.append(out_comps_append)

                        if comp_name != "-":
                            comp_names.append(comp_name)
                        if dual_comp_name != "-":
                            dual_comp_names.append(dual_comp_name)
                        if alt_comp_name != "-":
                            comp_names.append(alt_comp_name)

                    # elif floor:
                    #     temp_comp_name = "-"
                    #     if alt_comp_name != "-":
                    #         temp_comp_name = alt_comp_name
                    #     else:
                    #         temp_comp_name = comp_name
                    #     exc_comps_append = {
                    #         "comp_name": temp_comp_name,
                    #         "char_1": comp[0],
                    #         "char_2": comp[1],
                    #         "char_3": comp[2],
                    #         "char_4": comp[3],
                    #         # "own_rate": str(comps_dict[star_threshold][comp]["own_rate"]) + "%",
                    #         # "usage_rate": str(comps_dict[star_threshold][comp]["usage_rate"]) + "%",
                    #     }
                    #     exc_comps_append["app_rate"] = str(comps_dict[star_threshold][comp]["app_rate"]) + "%"
                    #     exc_comps_append["avg_round"] = str(comps_dict[star_threshold][comp]["round"])
                    #     exc_comps.append(exc_comps_append)
                elif comp_name in comp_names:
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
                    outvar_comps_append["app_rate"] = (
                        str(comps_dict[star_threshold][comp]["app_rate"]) + "%"
                    )
                    outvar_comps_append["avg_round"] = str(
                        comps_dict[star_threshold][comp]["round"]
                    )
                    outvar_comps.append(outvar_comps_append)
                if not info_char and (
                    # comps_dict[star_threshold][comp]["app_rate"] >= json_threshold or pf_mode or (not pf_mode and filename not in ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2", "5-1", "5-2"])
                    comps_dict[star_threshold][comp]["is_count_round_print"]
                    and (comps_dict[star_threshold][comp]["app_rate"] >= json_threshold)
                ):
                    out = name_filter(comp, mode="out")
                    for i in range(0, 4):
                        out[i] = slugify(out[i])
                        if out[i] in slug:
                            out[i] = slug[out[i]]
                    out_json_dict = {
                        "char_one": out[0],
                        "char_two": out[1],
                        "char_three": out[2],
                        "char_four": out[3],
                    }
                    out_json_dict["app_rate"] = comps_dict[star_threshold][comp][
                        "app_rate"
                    ]
                    out_json_dict["rank"] = comps_dict[star_threshold][comp]["app_rank"]
                    out_json_dict["avg_round"] = comps_dict[star_threshold][comp][
                        "round"
                    ]
                    out_json_dict["star_num"] = str(star_threshold)
                    # out_json_dict["rank"] = comps_dict[star_threshold][comp]["round_rank"]
                    out_json.append(out_json_dict)

    if info_char:
        out_comps += var_comps

    if archetype != "all":
        filename = filename + "_" + archetype

    if not (sort_app):
        filename = filename + "_rounds"

    if whaleOnly:
        filename = filename + "_C1"
    elif f2pOnly:
        filename = filename + "_E0S0"

    # if floor and not info_char:
    #     # csv_writer = csv.writer(open("../comp_results/f2p_app_" + filename + ".csv", 'w', newline=''))
    #     # for comps in f2p_comps:
    #     #     csv_writer.writerow(comps.values())
    #     with open("../comp_results/var_" + filename + ".json", "w") as out_file:
    #         out_file.write(json.dumps(outvar_comps,indent=2))

    if floor:
        csv_writer = csv.writer(
            open("../comp_results/comps_usage_" + filename + ".csv", "w", newline="")
        )
        for comps in out_comps:
            csv_writer.writerow(comps.values())
        # with open("../comp_results/exc_" + filename + ".json", "w") as out_file:
        #     out_file.write(json.dumps(exc_comps,indent=2))

    if not info_char and sort_app:
        # csv_writer = csv.writer(open("../comp_results/csv/" + filename + ".csv", 'w', newline=''))
        # csv_writer.writerow(out_json[0].keys())
        # for comps in out_json:
        #     csv_writer.writerow(comps.values())

        # with open("../comp_results/exc_" + filename + ".json", "w") as out_file:
        #     out_file.write(json.dumps(exc_comps,indent=2))

        all_comps_json[filename] = out_json.copy()
        with open("../comp_results/json/" + filename + ".json", "w") as out_file:
            out_file.write(json.dumps(out_json, indent=2))


def duo_write(duos_dict, usage, filename, archetype, check_duo):
    out_duos = []
    for char in duos_dict:
        if usage[4][char]["app_flat"] > 0:
            out_duos_append = {
                "char": char,
                "app": usage[4][char]["app"],
            }
            for i in range(duo_dict_len):
                if i < len(duos_dict[char]):
                    out_duos_append["char_" + str(i + 1)] = duos_dict[char][i][0]
                    out_duos_append["app_rate_" + str(i + 1)] = (
                        str(duos_dict[char][i][1]) + "%"
                    )
                    out_duos_append["avg_round_" + str(i + 1)] = duos_dict[char][i][2]
                    out_duos_append["app_flat_" + str(i + 1)] = duos_dict[char][i][3]
                else:
                    out_duos_append["char_" + str(i + 1)] = "-"
                    out_duos_append["app_rate_" + str(i + 1)] = "0.00%"
                    out_duos_append["avg_round_" + str(i + 1)] = 0.00
                    out_duos_append["app_flat_" + str(i + 1)] = 0
            out_duos.append(out_duos_append)
    out_duos = sorted(out_duos, key=lambda t: t["app"], reverse=True)

    if archetype != "all":
        filename = filename + "_" + archetype
    csv_writer = csv.writer(
        open("../char_results/" + filename + ".csv", "w", newline="")
    )
    count = 0
    out_duos_check = {}
    out_duos_exclu = {}
    for duos in out_duos:
        out_duos_check[duos["char"]] = {}
        out_duos_exclu[duos["char"]] = {}
        if count == 0:
            # csv_writer.writerow(duos.keys())
            temp_duos = ["char", "app"]
            for i in range(10):
                temp_duos += [
                    "char_" + str(i + 1),
                    "app_rate_" + str(i + 1),
                    "avg_round_" + str(i + 1),
                ]
            csv_writer.writerow(temp_duos)
            count += 1
        # csv_writer.writerow(duos.values())
        temp_duos = [
            duos["char"],
            duos["app"],
        ]
        for i in range(10):
            temp_duos += [
                duos["char_" + str(i + 1)],
                duos["app_rate_" + str(i + 1)],
                duos["avg_round_" + str(i + 1)],
            ]
        csv_writer.writerow(temp_duos)

        if check_duo:
            for i in range(duo_dict_len):
                duos["app_rate_" + str(i + 1)] = float(
                    duos["app_rate_" + str(i + 1)][:-1]
                )
                if (
                    duos["app_rate_" + str(i + 1)] >= 1
                    and duos["app_flat_" + str(i + 1)] >= 10
                    and (
                        (
                            duos["avg_round_" + str(i + 1)]
                            < usage[4][duos["char_" + str(i + 1)]]["round"]
                        )
                        or (
                            duos["avg_round_" + str(i + 1)]
                            < usage[4][duos["char"]]["round"]
                        )
                    )
                    and usage[4][duos["char_" + str(i + 1)]]["round"] != 99.99
                    and usage[4][duos["char_" + str(i + 1)]]["round"] != 0
                ):
                    # out_duos_exclu[duos["char"]][duos["char_" + str(i + 1)]] = {
                    #     "app": duos["app_rate_" + str(i + 1)],
                    #     "avg_round": duos["avg_round_" + str(i + 1)]
                    # }
                    # duos.pop("char_" + str(i + 1))
                    # duos.pop("app_rate_" + str(i + 1))
                    # duos.pop("avg_round_" + str(i + 1))
                    # continue
                    out_duos_check[duos["char"]][duos["char_" + str(i + 1)]] = {
                        "app": duos["app_rate_" + str(i + 1)],
                        "avg_round": duos["avg_round_" + str(i + 1)],
                    }
    if check_duo:
        char_names = list(CHARACTERS.keys())
        out_dd = {}
        out_dd_list = []
        csv_writer = csv.writer(open("../char_results/duo_check.csv", "w", newline=""))
        for char_i in char_names:
            for char_j in char_names:
                is_char_i_dps = CHARACTERS[char_i]["role"] == "Damage Dealer"
                is_char_j_dps = CHARACTERS[char_j]["role"] == "Damage Dealer"
                if is_char_i_dps and is_char_j_dps:
                    if char_j not in out_duos_check:
                        continue
                    if char_i not in out_duos_check:
                        continue
                    if char_i in out_duos_check[char_j]:
                        out_dd_list.append([char_j, char_i])
                        if char_j in out_duos_check[char_i]:
                            out_dd[frozenset([char_i, char_j])] = {
                                "char_i": char_i,
                                "char_i_app": str(
                                    out_duos_check[char_i][char_j]["app"]
                                ),
                                "char_j": char_j,
                                "char_j_app": str(
                                    out_duos_check[char_j][char_i]["app"]
                                ),
                                "avg_round": str(
                                    out_duos_check[char_i][char_j]["avg_round"]
                                ),
                            }
                        elif char_j in out_duos_exclu[char_i]:
                            out_dd[frozenset([char_i, char_j])] = {
                                "char_i": char_i,
                                "char_i_app": str(
                                    out_duos_exclu[char_i][char_j]["app"]
                                ),
                                "char_j": char_j,
                                "char_j_app": str(
                                    out_duos_check[char_j][char_i]["app"]
                                ),
                                "avg_round": str(
                                    out_duos_exclu[char_i][char_j]["avg_round"]
                                ),
                            }

        sorted_out_dd = sorted(
            out_dd.items(), key=lambda t: t[1]["char_i"], reverse=True
        )
        out_dd = {k: v for k, v in sorted_out_dd}

        for out_dd_print in out_dd_list:
            csv_writer.writerow(out_dd_print)
            # print(out_dd_print)
        for out_dd_print in out_dd:
            print(
                out_dd[out_dd_print]["char_i"]
                + ", "
                + out_dd[out_dd_print]["char_i_app"]
                + ", "
                + out_dd[out_dd_print]["char_j"]
                + ", "
                + out_dd[out_dd_print]["char_j_app"]
                + ", "
                + out_dd[out_dd_print]["avg_round"]
            )
        if __name__ == "__main__":
            notification.notify(
                title="Finished",
                message="Finished executing comp_rates",
                # displaying time
                timeout=2,
            )  # type: ignore
            # waiting time
            time.sleep(1)
        exit()

    for i in range(len(out_duos)):
        for duo_value in ["char"] + [f"char_{i}" for i in range(1, 31)]:
            if out_duos[i][duo_value]:
                out_duos[i][duo_value] = slugify(out_duos[i][duo_value])
                if out_duos[i][duo_value] in slug:
                    out_duos[i][duo_value] = slug[out_duos[i][duo_value]]
    with open("../char_results/" + filename + ".json", "w") as out_file:
        out_file.write(json.dumps(out_duos, indent=2))


def char_usages_write(chars_dict, filename, floor, archetype):
    out_chars = []
    out_chars_csv = []
    weap_len = 10
    arti_len = 10
    planar_len = 5
    chars_dict = dict(
        sorted(chars_dict.items(), key=lambda t: t[1]["app"], reverse=True)
    )
    for char in chars_dict:
        out_chars_append = {
            "char": char,
            "app_rate": str(chars_dict[char]["app"]) + "%",
            "app_rate_e0": str(chars_dict[char]["app_exclude"]) + "%",
            "avg_round": str(chars_dict[char]["round"]),
            # "prev_avg_round": str(prev_round.get(char, 99.99)),
            "std_dev_round": str(chars_dict[char]["std_dev_round"]),
            "q1_round": str(chars_dict[char]["q1_round"]),
            # "usage_rate": str(chars_dict[char]["usage"]) + "%",
            # "own_rate": str(chars_dict[char]["own"]) + "%",
            "role": chars_dict[char]["role"],
            "rarity": chars_dict[char]["rarity"],
            "diff": str(chars_dict[char]["diff"]) + "%",
            "diff_rounds": str(chars_dict[char]["diff_rounds"]),
        }
        for i in ["app_rate", "app_rate_e0", "diff", "diff_rounds"]:
            if out_chars_append[i] == "-%":
                out_chars_append[i] = "-"
        if list(chars_dict[char]["weapons"]):
            for i in range(weap_len):
                if i < len(list(chars_dict[char]["weapons"])):
                    out_chars_append["weapon_" + str(i + 1)] = list(
                        chars_dict[char]["weapons"]
                    )[i]
                    out_chars_append["weapon_" + str(i + 1) + "_app"] = (
                        str(list(chars_dict[char]["weapons"].values())[i]["percent"])
                        + "%"
                    )
                    out_chars_append["weapon_" + str(i + 1) + "_round"] = str(
                        list(chars_dict[char]["weapons"].values())[i]["avg_round"]
                    )
                else:
                    out_chars_append["weapon_" + str(i + 1)] = ""
                    out_chars_append["weapon_" + str(i + 1) + "_app"] = "0.0"
                    out_chars_append["weapon_" + str(i + 1) + "_round"] = "99.99"
                    if pf_mode:
                        out_chars_append["weapon_" + str(i + 1) + "_round"] = "0.0"
            for i in range(arti_len):
                if i < len(list(chars_dict[char]["artifacts"])):
                    arti_name = list(chars_dict[char]["artifacts"])[i]
                    out_chars_append["artifact_" + str(i + 1)] = arti_name
                    arti_name = (
                        arti_name.replace("Watchmaker,", "Watchmaker")
                        .replace("Sigonia,", "Sigonia")
                        .replace("Duran,", "Duran")
                        .split(", ")
                    )
                    out_chars_append["artifact_" + str(i + 1) + "_1"] = (
                        arti_name[0]
                        .replace("Watchmaker", "Watchmaker,")
                        .replace("Sigonia", "Sigonia,")
                        .replace("Duran", "Duran,")
                    )
                    if len(arti_name) > 1:
                        out_chars_append["artifact_" + str(i + 1) + "_2"] = (
                            arti_name[1]
                            .replace("Watchmaker", "Watchmaker,")
                            .replace("Sigonia", "Sigonia,")
                            .replace("Duran", "Duran,")
                        )
                    else:
                        out_chars_append["artifact_" + str(i + 1) + "_2"] = ""
                    out_chars_append["artifact_" + str(i + 1) + "_app"] = (
                        str(list(chars_dict[char]["artifacts"].values())[i]["percent"])
                        + "%"
                    )
                    out_chars_append["artifact_" + str(i + 1) + "_round"] = str(
                        list(chars_dict[char]["artifacts"].values())[i]["avg_round"]
                    )
                else:
                    out_chars_append["artifact_" + str(i + 1)] = ""
                    out_chars_append["artifact_" + str(i + 1) + "_1"] = ""
                    out_chars_append["artifact_" + str(i + 1) + "_2"] = ""
                    out_chars_append["artifact_" + str(i + 1) + "_app"] = "0.0"
                    out_chars_append["artifact_" + str(i + 1) + "_round"] = "99.99"
                    if pf_mode:
                        out_chars_append["artifact_" + str(i + 1) + "_round"] = "0.0"
            for i in range(planar_len):
                if i < len(list(chars_dict[char]["planars"])):
                    out_chars_append["planar_" + str(i + 1)] = list(
                        chars_dict[char]["planars"]
                    )[i]
                    out_chars_append["planar_" + str(i + 1) + "_app"] = (
                        str(list(chars_dict[char]["planars"].values())[i]["percent"])
                        + "%"
                    )
                    out_chars_append["planar_" + str(i + 1) + "_round"] = str(
                        list(chars_dict[char]["planars"].values())[i]["avg_round"]
                    )
                else:
                    out_chars_append["planar_" + str(i + 1)] = ""
                    out_chars_append["planar_" + str(i + 1) + "_app"] = "0.0"
                    out_chars_append["planar_" + str(i + 1) + "_round"] = "99.99"
                    if pf_mode:
                        out_chars_append["planar_" + str(i + 1) + "_round"] = "0.0"
            # for i in range(7):
            #     out_chars_append["use_" + str(i)] = str(list(list(chars_dict[char]["cons_usage"].values())[i].values())[2]) + "%"
            #     if out_chars_append["use_" + str(i)] == "-%":
            #         out_chars_append["use_" + str(i)] = "-"
            #     out_chars_append["own_" + str(i)] = str(list(list(chars_dict[char]["cons_usage"].values())[i].values())[1]) + "%"
            #     if out_chars_append["own_" + str(i)] == "-%":
            #         out_chars_append["own_" + str(i)] = "-"
            for i in range(7):
                out_chars_append["app_" + str(i)] = (
                    str(
                        list(list(chars_dict[char]["cons_usage"].values())[i].values())[
                            0
                        ]
                    )
                    + "%"
                )
                out_chars_append["round_" + str(i)] = str(
                    list(list(chars_dict[char]["cons_usage"].values())[i].values())[3]
                )
                if out_chars_append["app_" + str(i)] == "-%":
                    out_chars_append["app_" + str(i)] = "-"
            out_chars_append["cons_avg"] = chars_dict[char]["cons_avg"]
            out_chars_append["sample"] = chars_dict[char]["sample"]
            out_chars_append["sample_app_flat"] = chars_dict[char]["sample_app_flat"]
        else:
            for i in range(weap_len):
                out_chars_append["weapon_" + str(i + 1)] = ""
                out_chars_append["weapon_" + str(i + 1) + "_app"] = "0.0"
                out_chars_append["weapon_" + str(i + 1) + "_round"] = "99.99"
                if pf_mode:
                    out_chars_append["weapon_" + str(i + 1) + "_round"] = "0.0"
            for i in range(arti_len):
                out_chars_append["artifact_" + str(i + 1)] = ""
                out_chars_append["artifact_" + str(i + 1) + "_1"] = ""
                out_chars_append["artifact_" + str(i + 1) + "_2"] = ""
                out_chars_append["artifact_" + str(i + 1) + "_app"] = "0.0"
                out_chars_append["artifact_" + str(i + 1) + "_round"] = "99.99"
                if pf_mode:
                    out_chars_append["artifact_" + str(i + 1) + "_round"] = "0.0"
            for i in range(planar_len):
                out_chars_append["planar_" + str(i + 1)] = ""
                out_chars_append["planar_" + str(i + 1) + "_app"] = "0.0"
                out_chars_append["planar_" + str(i + 1) + "_round"] = "99.99"
                if pf_mode:
                    out_chars_append["planar_" + str(i + 1) + "_round"] = "0.0"
            # for i in range(7):
            #     out_chars_append["use_" + str(i)] = str(list(list(chars_dict[char]["cons_usage"].values())[i].values())[2]) + "%"
            #     if out_chars_append["use_" + str(i)] == "-%":
            #         out_chars_append["use_" + str(i)] = "-"
            #     out_chars_append["own_" + str(i)] = str(list(list(chars_dict[char]["cons_usage"].values())[i].values())[1]) + "%"
            #     if out_chars_append["own_" + str(i)] == "-%":
            #         out_chars_append["own_" + str(i)] = "-"
            for i in range(7):
                out_chars_append["app_" + str(i)] = "0.0%"
                out_chars_append["round_" + str(i)] = "99.99"
                if pf_mode:
                    out_chars_append["round_" + str(i)] = "0.0"
            out_chars_append["cons_avg"] = chars_dict[char]["cons_avg"]
            out_chars_append["sample"] = chars_dict[char]["sample"]
            out_chars_append["sample_app_flat"] = chars_dict[char]["sample_app_flat"]
        out_chars.append(out_chars_append)
        out_chars_csv.append(out_chars_append.copy())
        if char == filename:
            break

    if archetype != "all":
        filename = filename + "_" + archetype
    if whaleOnly:
        filename = filename + "_C1"
    elif f2pOnly:
        filename = filename + "_E0S0"

    iterate_value_app = ["app_rate", "app_rate_e0", "diff"]
    iterate_value_round = ["avg_round", "std_dev_round", "q1_round", "diff_rounds"]
    iterate_name_arti = []
    for i in range(weap_len):
        iterate_value_app.append("weapon_" + str(i + 1) + "_app")
        iterate_value_round.append("weapon_" + str(i + 1) + "_round")
    for i in range(arti_len):
        iterate_value_app.append("artifact_" + str(i + 1) + "_app")
        iterate_value_round.append("artifact_" + str(i + 1) + "_round")
    for i in range(planar_len):
        iterate_value_app.append("planar_" + str(i + 1) + "_app")
        iterate_value_round.append("planar_" + str(i + 1) + "_round")
    for i in range(7):
        iterate_value_app.append("app_" + str(i))
        iterate_value_round.append("round_" + str(i))

    for i in range(len(out_chars)):
        # for i in range(7):
        out_chars[i]["char"] = slugify(out_chars[i]["char"])
        if out_chars[i]["char"] in slug:
            out_chars[i]["char"] = slug[out_chars[i]["char"]]
        for value in iterate_value_app:
            if out_chars[i][value][:-1].replace(".", "").replace("-", "").isnumeric():
                out_chars[i][value] = float(out_chars[i][value][:-1])
            else:
                out_chars[i][value] = 0.00
        for value in iterate_value_round:
            if out_chars[i][value].replace(".", "").replace("-", "").isnumeric():
                out_chars[i][value] = (
                    round(float(out_chars[i][value]))
                    if pf_mode
                    else float(out_chars[i][value])
                )
            else:
                out_chars[i][value] = 99.99
                if pf_mode:
                    out_chars[i][value] = 0
        for value in iterate_name_arti:
            if out_chars[i][value]:
                out_chars[i][value] = (
                    out_chars[i][value].replace(".", "").replace("-", "")
                )
            else:
                out_chars[i][value] = 99.99
                if pf_mode:
                    out_chars[i][value] = 0
    with open("../char_results/" + filename + ".json", "w") as out_file:
        out_file.write(json.dumps(out_chars, indent=2))

    csv_writer = csv.writer(
        open("../char_results/" + filename + ".csv", "w", newline="")
    )
    count = 0
    for chars in out_chars_csv:
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


main()
