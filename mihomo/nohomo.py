import _thread
import time
import asyncio
import traceback

from mihomo import Language, MihomoAPI, StarrailInfoParsed
from nohomo_config import json, os, csv, uids, filename, trailblazer_ids, relics_data

client = MihomoAPI(Language.EN)

print(len(uids))


def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


def input_thread(input_list):
    input()
    input_list.append(True)


async def v1():
    if not os.path.exists("results_real"):
        os.makedirs("results_real")

    # error_uids = []
    header = [
        "uid",
        "player_level",
        "character",
        "char_level",
        "path",
        "light_cone",
        "light_cone_level",
        "attack_lvl",
        "skill_lvl",
        "ultimate_lvl",
        "talent_lvl",
        "HP",
        "ATK",
        "DEF",
        "SPD",
        "CRIT Rate",
        "CRIT DMG",
        "DMG Boost",
        "Outgoing Healing Boost",
        "Energy Regeneration Rate",
        "Effect RES",
        "Effect Hit Rate",
        "Break Effect",
        "SPD sub",
        "HP sub",
        "ATK sub",
        "DEF sub",
        "CRIT Rate sub",
        "CRIT DMG sub",
        "Effect RES sub",
        "Effect Hit Rate sub",
        "Break Effect sub",
        "Body",
        "Feet",
        "Sphere",
        "Rope",
        "relic",
        "ornament",
    ]
    writer = csv.writer(open(filename + ".csv", "w", encoding="UTF8", newline=""))
    writer.writerow(header)

    header = [
        "uid",
        "phase",
        "name",
        "level",
        "cons",
        "weapon",
        "element",
        "artifacts",
        "relics",
    ]
    writer_chars = csv.writer(
        open(filename + "_char.csv", "w", encoding="UTF8", newline="")
    )
    writer_chars.writerow(header)

    input_list = []
    _thread.start_new_thread(input_thread, (input_list,))
    uid_iter = -1
    while not input_list and uid_iter < len(uids):
        uid_iter += 1
        uid = uids[uid_iter]

        i: int = -1
        while i < 5:
            i += 1
            if i == 5:
                print("error")
            try:
                print("{} / {} : {}, {}".format(uid_iter + 1, len(uids), uid, i))
                data: StarrailInfoParsed = await client.fetch_user(uid)
                for character in data.characters:
                    line = []
                    line_chars = []
                    line.append(uid)
                    line_chars.append(uid)
                    line_chars.append("2.2b")
                    line.append(data.player.level)
                    if str(character.id) in trailblazer_ids:
                        if "March 7th" in character.name:
                            line.append("March 7th")
                            line_chars.append("March 7th")
                        else:
                            line.append("Trailblazer")
                            line_chars.append("Trailblazer")
                    else:
                        line.append(character.name)
                        line_chars.append(character.name)
                    line.append(character.level)
                    line_chars.append(character.level)
                    line_chars.append(character.eidolon)
                    line.append(character.element.name)
                    if character.light_cone is not None:
                        line.append(character.light_cone.name)
                        line_chars.append(character.light_cone.name)
                        line.append(character.light_cone.level)
                    else:
                        line.append("")
                        line_chars.append("")
                        line.append("")
                    line_chars.append(character.element.name)

                    skills = {"Basic ATK": 0, "Skill": 0, "Ultimate": 0, "Talent": 0}
                    skill_ids = {}
                    for skill in character.traces:
                        if skill.type_text in skills and skill.max_level > 1:
                            skill_ids[str(character.id) + "0" + str(skill.id)[-2:]] = (
                                skill.type_text
                            )
                    # print(json.dumps(skill_ids, indent = 2))
                    for skill in character.trace_tree:
                        if str(skill.id) in skill_ids:
                            # print(skill_ids[str(skill.id)] + ": " + str(skill.level))
                            skills[skill_ids[str(skill.id)]] = skill.level
                    # print(json.dumps(skills, indent = 2))
                    for skill in skills.values():
                        line.append(skill)

                    desired_stats = {
                        "HP": 0.00,
                        "ATK": 0.00,
                        "DEF": 0.00,
                        "SPD": 0.00,
                        "CRIT Rate": 0.00,
                        "CRIT DMG": 0.00,
                        str(character.element.name) + " DMG Boost": 0.00,
                        "Outgoing Healing Boost": 0.00,
                        "Energy Regeneration Rate": 0.00,
                        "Effect RES": 0.00,
                        "Effect Hit Rate": 0.00,
                        "Break Effect": 0.00,
                    }

                    for stat in character.attributes:
                        if stat.name in desired_stats:
                            if stat.is_percent:
                                desired_stats[stat.name] = stat.value * 100
                            else:
                                desired_stats[stat.name] = stat.value

                    for stat in character.additions:
                        if stat.name in desired_stats:
                            if stat.is_percent:
                                desired_stats[stat.name] += stat.value * 100
                            else:
                                desired_stats[stat.name] += stat.value

                    for stat in desired_stats.values():
                        line.append(round(stat, 3))

                    mainstats = {
                        "HEAD": "",
                        "HAND": "",
                        "BODY": "",
                        "FOOT": "",
                        "NECK": "",
                        "OBJECT": "",
                    }
                    substats = {
                        "Flat HP": 0.00,
                        "Flat ATK": 0.00,
                        "Flat DEF": 0.00,
                        "Flat SPD": 0.00,
                        "HP": 0.00,
                        "ATK": 0.00,
                        "DEF": 0.00,
                        "CRIT Rate": 0.00,
                        "CRIT DMG": 0.00,
                        "Effect RES": 0.00,
                        "Effect Hit Rate": 0.00,
                        "Break Effect": 0.00,
                    }
                    artifacts = {}
                    ornaments = {}
                    for relic in character.relics:
                        mainstats[relics_data[str(relic.id)]["type"]] = (
                            relic.main_affix.name
                        )
                        if relics_data[str(relic.id)]["type"] in ["OBJECT", "NECK"]:
                            if relic.set_name not in ornaments:
                                ornaments[relic.set_name] = 1
                            else:
                                ornaments[relic.set_name] += 1
                        else:
                            if relic.set_name not in artifacts:
                                artifacts[relic.set_name] = 1
                            else:
                                artifacts[relic.set_name] += 1
                        for stat in relic.sub_affixes:
                            if stat.is_percent:
                                substats[stat.name] += stat.value * 100
                            else:
                                substats["Flat " + stat.name] += stat.value

                    for stat_key in list(substats.keys())[3:]:
                        line.append(round(substats[stat_key], 3))

                    for stat_key in list(mainstats.keys())[2:]:
                        line.append(mainstats[stat_key])

                    char_set = None
                    for set in artifacts:
                        if artifacts[set] == 2 or artifacts[set] == 4:
                            if char_set is not None:
                                if set < char_set:
                                    char_set = set + ", " + char_set
                                else:
                                    char_set += ", " + set
                            else:
                                char_set = set
                        elif artifacts[set] == 3:
                            char_set = set + ", Flex"
                    if len(artifacts) > 2:
                        if char_set is not None:
                            char_set += ", Flex"
                        else:
                            char_set = "Flex"
                    line.append(char_set)
                    line_chars.append(char_set)

                    char_set = None
                    for set in ornaments:
                        if ornaments[set] == 2:
                            char_set = set
                    line.append(char_set)
                    line_chars.append(char_set)

                    writer.writerow(line)
                    writer_chars.writerow(line_chars)
                break
            except asyncio.exceptions.TimeoutError:
                print("timeout")
                time.sleep(1)
            except AttributeError:
                print("{}: {}".format(uid, traceback.format_exc()))
                # print(str(uid) + " Too Many Requests")
                time.sleep(1)
            except Exception as e:
                if str(e) == "[429] Too Many Requests":
                    print("[429] Too Many Requests")
                    time.sleep(3)
                elif "Cannot connect" in str(e):
                    print("Cannot connect")
                    i = 0
                    time.sleep(1)
                elif str(e) == "User not found.":
                    print("User not found.")
                    break
                else:
                    print("{}: {}".format(uid, traceback.format_exc()))
                    # exit()
                    break

    print("\nFinished")

    # if len(error_uids):
    # 	print('Error with UIDs:')
    # 	for i in error_uids:
    # 		print(i)


asyncio.run(v1())
