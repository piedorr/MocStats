import json
import re

moc_phase = "2.3.3"
pf_phase = "2.3.2"
as_phase = "2.3.1"

with open('../data/characters.json') as char_file:
    CHARACTERS = json.load(char_file)
with open("../char_results/" + moc_phase + "/all2.json") as stats:
    moc_dict = json.load(stats)
with open("../char_results/" + pf_phase + "_pf/all2.json") as stats:
    pf_dict = json.load(stats)
with open("../char_results/" + as_phase + "_as/all2.json") as stats:
    as_dict = json.load(stats)

uses = []
uses_moc = {}
uses_pf = {}
uses_as = {}
stats_len = {
    "weapons": 10,
    "artifacts": 10,
    "planars": 5,
    "body_stats": 3,
    "feet_stats": 3,
    "sphere_stats": 3,
    "rope_stats": 3,
}

for char in moc_dict:
    uses_moc[char["char"]] = char.copy()
    uses_moc[char["char"]]["weapons"] = {}
    uses_moc[char["char"]]["artifacts"] = {}
    uses_moc[char["char"]]["planars"] = {}
    uses_moc[char["char"]]["body_stats"] = {}
    uses_moc[char["char"]]["feet_stats"] = {}
    uses_moc[char["char"]]["sphere_stats"] = {}
    uses_moc[char["char"]]["rope_stats"] = {}
    for stat in char:
        for stat_name in ["weapon", "artifact", "planar", "body_stats", "feet_stats", "sphere_stats", "rope_stats"]:
            if re.sub(r'\d', '', stat) == stat_name + "_" and char[stat] != "" and char[stat] != "-":
                temp_dict = {}
                if stat_name == "artifact":
                    temp_dict["1"] = char[stat + "_1"]
                    temp_dict["2"] = char[stat + "_2"]
                temp_dict["app"] = char[stat + "_app"]
                if stat_name in ["weapon", "artifact", "planar"]:
                    temp_dict["round_moc"] = char[stat + "_round"]
                    temp_dict["round_pf"] = 0.0
                    temp_dict["round_as"] = 0.0
                else:
                    stat_name = stat_name[:-1]
                uses_moc[char["char"]][stat_name + "s"][char[stat]] = temp_dict
for char in pf_dict:
    uses_pf[char["char"]] = char.copy()
    uses_pf[char["char"]]["weapons"] = {}
    uses_pf[char["char"]]["artifacts"] = {}
    uses_pf[char["char"]]["planars"] = {}
    uses_pf[char["char"]]["body_stats"] = {}
    uses_pf[char["char"]]["feet_stats"] = {}
    uses_pf[char["char"]]["sphere_stats"] = {}
    uses_pf[char["char"]]["rope_stats"] = {}
    for stat in char:
        for stat_name in ["weapon", "artifact", "planar", "body_stats", "feet_stats", "sphere_stats", "rope_stats"]:
            if re.sub(r'\d', '', stat) == stat_name + "_" and char[stat] != "" and char[stat] != "-":
                temp_dict = {}
                if stat_name == "artifact":
                    temp_dict["1"] = char[stat + "_1"]
                    temp_dict["2"] = char[stat + "_2"]
                temp_dict["app"] = char[stat + "_app"]
                if stat_name in ["weapon", "artifact", "planar"]:
                    temp_dict["round_moc"] = 99.99
                    temp_dict["round_pf"] = char[stat + "_round"]
                    temp_dict["round_as"] = 0.0
                else:
                    stat_name = stat_name[:-1]
                uses_pf[char["char"]][stat_name + "s"][char[stat]] = temp_dict
for char in as_dict:
    uses_as[char["char"]] = char.copy()
    uses_as[char["char"]]["weapons"] = {}
    uses_as[char["char"]]["artifacts"] = {}
    uses_as[char["char"]]["planars"] = {}
    uses_as[char["char"]]["body_stats"] = {}
    uses_as[char["char"]]["feet_stats"] = {}
    uses_as[char["char"]]["sphere_stats"] = {}
    uses_as[char["char"]]["rope_stats"] = {}
    for stat in char:
        for stat_name in ["weapon", "artifact", "planar", "body_stats", "feet_stats", "sphere_stats", "rope_stats"]:
            if re.sub(r'\d', '', stat) == stat_name + "_" and char[stat] != "" and char[stat] != "-":
                temp_dict = {}
                if stat_name == "artifact":
                    temp_dict["1"] = char[stat + "_1"]
                    temp_dict["2"] = char[stat + "_2"]
                temp_dict["app"] = char[stat + "_app"]
                if stat_name in ["weapon", "artifact", "planar"]:
                    temp_dict["round_moc"] = 99.99
                    temp_dict["round_pf"] = 0.0
                    temp_dict["round_as"] = char[stat + "_round"]
                else:
                    stat_name = stat_name[:-1]
                uses_as[char["char"]][stat_name + "s"][char[stat]] = temp_dict

for char in CHARACTERS:
    uses_temp = {
        "char": char,
        "app_rate_moc": uses_moc.get(char, {}).get("app_rate", 0),
        "avg_round_moc": uses_moc.get(char, {}).get("avg_round", 0),
        "sample_moc": uses_moc.get(char, {}).get("sample", 0),
        "sample_size_players_moc": uses_moc.get(char, {}).get("sample_size_players", 0),
        "app_rate_pf": uses_pf.get(char, {}).get("app_rate", 0),
        "avg_round_pf": uses_pf.get(char, {}).get("avg_round", 0),
        "sample_pf": uses_pf.get(char, {}).get("sample", 0),
        "sample_size_players_pf": uses_pf.get(char, {}).get("sample_size_players", 0),
        "app_rate_as": uses_as.get(char, {}).get("app_rate", 0),
        "avg_round_as": uses_as.get(char, {}).get("avg_round", 0),
        "sample_as": uses_as.get(char, {}).get("sample", 0),
        "sample_size_players_as": uses_as.get(char, {}).get("sample_size_players", 0),
        "app_0": 0,
        "round_0_moc": uses_moc.get(char, {}).get("round_0", 0),
        "round_0_pf": uses_pf.get(char, {}).get("round_0", 0),
        "round_0_as": uses_as.get(char, {}).get("round_0", 0),
        "app_1": 0,
        "round_1_moc": uses_moc.get(char, {}).get("round_1", 0),
        "round_1_pf": uses_pf.get(char, {}).get("round_1", 0),
        "round_1_as": uses_as.get(char, {}).get("round_1", 0),
        "app_2": 0,
        "round_2_moc": uses_moc.get(char, {}).get("round_2", 0),
        "round_2_pf": uses_pf.get(char, {}).get("round_2", 0),
        "round_2_as": uses_as.get(char, {}).get("round_2", 0),
        "app_3": 0,
        "round_3_moc": uses_moc.get(char, {}).get("round_3", 0),
        "round_3_pf": uses_pf.get(char, {}).get("round_3", 0),
        "round_3_as": uses_as.get(char, {}).get("round_3", 0),
        "app_4": 0,
        "round_4_moc": uses_moc.get(char, {}).get("round_4", 0),
        "round_4_pf": uses_pf.get(char, {}).get("round_4", 0),
        "round_4_as": uses_as.get(char, {}).get("round_4", 0),
        "app_5": 0,
        "round_5_moc": uses_moc.get(char, {}).get("round_5", 0),
        "round_5_pf": uses_pf.get(char, {}).get("round_5", 0),
        "round_5_as": uses_as.get(char, {}).get("round_5", 0),
        "app_6": 0,
        "round_6_moc": uses_moc.get(char, {}).get("round_6", 0),
        "round_6_pf": uses_pf.get(char, {}).get("round_6", 0),
        "round_6_as": uses_as.get(char, {}).get("round_6", 0),
        "cons_avg": 0,
        "weapons": uses_moc.get(char, {}).get("weapons", {}),
        "artifacts": uses_moc.get(char, {}).get("artifacts", {}),
        "planars": uses_moc.get(char, {}).get("planars", {}),
        "body_stats": uses_moc.get(char, {}).get("body_stats", {}),
        "feet_stats": uses_moc.get(char, {}).get("feet_stats", {}),
        "sphere_stats": uses_moc.get(char, {}).get("sphere_stats", {}),
        "rope_stats": uses_moc.get(char, {}).get("rope_stats", {}),
    }

    rate_moc = uses_temp["app_rate_moc"] if (uses_temp["app_rate_moc"] == 0) == (uses_temp["sample_size_players_moc"] == 0) else 0
    rate_pf = uses_temp["app_rate_pf"] if (uses_temp["app_rate_pf"] == 0) == (uses_temp["sample_size_players_pf"] == 0) else 0
    rate_as = uses_temp["app_rate_as"] if (uses_temp["app_rate_as"] == 0) == (uses_temp["sample_size_players_as"] == 0) else 0
    rate_combine = rate_moc + rate_pf + rate_as
    rate_combine = rate_combine if rate_combine else 1

    for stat in stats_len:
        for item in uses_temp[stat]:
            uses_temp[stat][item]["app"] = round(uses_temp[stat][item]["app"] * rate_moc / rate_combine, 2)
        for item in uses_pf.get(char, {}).get(stat, {}):
            if item != "" and item != "-":
                if item in uses_temp[stat]:
                    uses_temp[stat][item]["app"] = round(uses_temp[stat][item]["app"] + uses_pf[char][stat][item]["app"] * rate_pf / rate_combine, 2)
                    if stat in ["weapons", "artifacts", "planars"]:
                        uses_temp[stat][item]["round_pf"] = uses_pf[char][stat][item]["round_pf"]
                else:
                    uses_temp[stat][item] = uses_pf[char][stat][item].copy()
                    uses_temp[stat][item]["app"] = round(uses_temp[stat][item]["app"] * rate_pf / rate_combine, 2)
        for item in uses_as.get(char, {}).get(stat, {}):
            if item != "" and item != "-":
                if item in uses_temp[stat]:
                    uses_temp[stat][item]["app"] = round(uses_temp[stat][item]["app"] + uses_as[char][stat][item]["app"] * rate_as / rate_combine, 2)
                    if stat in ["weapons", "artifacts", "planars"]:
                        uses_temp[stat][item]["round_as"] = uses_as[char][stat][item]["round_as"]
                else:
                    uses_temp[stat][item] = uses_as[char][stat][item].copy()
                    uses_temp[stat][item]["app"] = round(uses_temp[stat][item]["app"] * rate_as / rate_combine, 2)

        sorted_items = (sorted(
            uses_temp[stat].items(),
            key = lambda t: t[1]["app"],
            reverse=True
        ))
        uses_temp[stat] = {k: v for k, v in sorted_items}

        for i in range(stats_len[stat]):
            if i < len(list(uses_temp[stat])):
                uses_temp[stat + "_" + str(i + 1)] = list(uses_temp[stat])[i]
                if stat == "artifacts":
                    uses_temp[stat + "_" + str(i + 1) + "_1"] = list(uses_temp[stat].values())[i]["1"]
                    uses_temp[stat + "_" + str(i + 1) + "_2"] = list(uses_temp[stat].values())[i]["2"]
                uses_temp[stat + "_" + str(i + 1) + "_app"] = list(uses_temp[stat].values())[i]["app"]
                if stat in ["weapons", "artifacts", "planars"]:
                    uses_temp[stat + "_" + str(i + 1) + "_round_moc"] = list(uses_temp[stat].values())[i]["round_moc"]
                    uses_temp[stat + "_" + str(i + 1) + "_round_pf"] = list(uses_temp[stat].values())[i]["round_pf"]
                    uses_temp[stat + "_" + str(i + 1) + "_round_as"] = list(uses_temp[stat].values())[i]["round_as"]
            else:
                uses_temp[stat + "_" + str(i + 1)] = ""
                if stat == "artifacts":
                    uses_temp[stat + "_" + str(i + 1) + "_1"] = ""
                    uses_temp[stat + "_" + str(i + 1) + "_2"] = ""
                uses_temp[stat + "_" + str(i + 1) + "_app"] = 0.0
                if stat in ["weapons", "artifacts", "planars"]:
                    uses_temp[stat + "_" + str(i + 1) + "_round_moc"] = 99.99
                    uses_temp[stat + "_" + str(i + 1) + "_round_pf"] = 0.0
                    uses_temp[stat + "_" + str(i + 1) + "_round_as"] = 0.0
        del uses_temp[stat]

    stats_iter = ["app_0", "app_1", "app_2", "app_3", "app_4", "app_5", "app_6", "cons_avg", "char_lvl", "light_cone_lvl", "attack_lvl", "skill_lvl", "ultimate_lvl", "talent_lvl", "max_hp", "atk", "dfns", "speed", "crate", "cdmg", "dmg_boost", "heal_boost", "energy_regen", "effect_res", "effect_rate", "break_effect", "spd_sub", "hp_sub", "atk_sub", "def_sub", "crate_sub", "cdmg_sub", "res_sub", "ehr_sub", "break_sub"]
    for stat in stats_iter:
        stat_moc = uses_moc.get(char, {}).get(stat)
        stat_pf = uses_pf.get(char, {}).get(stat)
        stat_as = uses_as.get(char, {}).get(stat)
        uses_temp[stat] = round((((stat_moc * rate_moc) if stat_moc != None else 0) + ((stat_pf * rate_pf) if stat_pf != None else 0) + ((stat_as * rate_as) if stat_as != None else 0)) / rate_combine, 2)
    uses.append(uses_temp)

with open("../char_results/builds.json", "w") as out_file:
    out_file.write(json.dumps(uses,indent=2))
