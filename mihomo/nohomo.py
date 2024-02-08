import requests
import asyncio
import genshin
import inspect
import pickle
import msvcrt
import time
import _thread

from mihomo import Language, MihomoApi, FormattedApiInfo
from nohomo_config import *

client = MihomoApi()

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

	cpt = 1
	error_uids = []
	header = ['uid', 'player_level', 'character', 'char_level', 'path', 'light_cone', 'light_cone_level', 'attack_lvl', 'skill_lvl', 'ultimate_lvl', 'talent_lvl', 'HP', 'ATK', 'DEF', 'SPD', 'CRIT Rate', 'CRIT DMG', 'DMG Boost', 'Outgoing Healing Boost', 'Energy Regeneration Rate', 'Effect RES', 'Effect Hit Rate', 'Break Effect', 'SPD sub', 'HP sub', 'ATK sub', 'DEF sub', 'CRIT Rate sub', 'CRIT DMG sub', 'Effect RES sub', 'Effect Hit Rate sub', 'Break Effect sub', 'Body', 'Feet', 'Sphere', 'Rope', 'relic', 'ornament']
	writer = csv.writer(open(filename + '.csv', 'w', encoding='UTF8', newline=''))
	writer.writerow(header)

	for uid in uids:
		cpt += 1

		for i in range(20):
			try:
				print('{} / {} : {}, {}'.format(cpt, len(uids), uid, i), end="\r")
				data: FormattedApiInfo = await client.get_parsed_api_data(str(uid))
				for character in data.characters:
					line = []
					line.append(uid)
					line.append(data.player.level)
					if (str(character.id) in trailblazer_ids):
						line.append("Trailblazer")
					else:
						line.append(character.name)
					line.append(character.level)
					line.append(character.element.name)
					if character.light_cone != None:
						line.append(character.light_cone.name)
						line.append(character.light_cone.level)
					else:
						line.append("")
						line.append("")

					skills = {
						"Basic ATK": 0,
						"Skill": 0,
						"Ultimate": 0,
						"Talent": 0
					}
					for skill in character.skills:
						if skill.type_text in skills and skill.max_level > 1:
							skills[skill.type_text] = skill.level
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
						"Break Effect": 0.00
					}

					for stat in character.attributes:
						if stat.name in desired_stats:
							if stat.percent:
								desired_stats[stat.name] = stat.value*100
							else:
								desired_stats[stat.name] = stat.value

					for stat in character.additions:
						if stat.name in desired_stats:
							if stat.percent:
								desired_stats[stat.name] += stat.value*100
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
						"OBJECT": ""
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
						"Break Effect": 0.00
					}
					artifacts = {}
					ornaments = {}
					for relic in character.relics:
						mainstats[relics_data[str(relic.id)]["type"]] = relic.main_affix.name
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
						for stat in relic.sub_affix:
							if stat.percent:
								substats[stat.name] += stat.value*100
							else:
								substats["Flat " + stat.name] += stat.value

					for i in list(substats.keys())[3:]:
						line.append(round(substats[i], 3))

					for i in list(mainstats.keys())[2:]:
						line.append(mainstats[i])

					char_set = None
					for set in artifacts:
						if artifacts[set] == 2 or artifacts[set] == 4:
							if char_set != None:
								if set < char_set:
									char_set = set + ", " + char_set
								else:
									char_set += ", " + set
							else:
								char_set = set
						elif artifacts[set] == 3:
							char_set = set + ", Flex"
					if len(artifacts) > 2:
						if char_set != None:
							char_set += ", Flex"
						else:
							char_set = "Flex"
					line.append(char_set)

					char_set = None
					for set in ornaments:
						if ornaments[set] == 2:
							char_set = set
					line.append(char_set)

					writer.writerow(line)
				time.sleep(0.5)
				break
			except asyncio.exceptions.TimeoutError as e:
				time.sleep(20)
				pass
			except Exception as e:
				if str(e) == "[429] Too Many Requests":
					print("[429] Too Many Requests")
					time.sleep(60)
					pass
				elif str(e) == "Cannot connect to host api.mihomo.me:443 ssl:default [getaddrinfo failed]":
					print("Cannot connect")
					time.sleep(10)
					pass
				elif str(e) == "User not found.":
					break
				else:
					# error_uids.append('{}: {}'.format(uid, e))
					print('{}: {}, {}'.format(uid, e, type(e)))
					# exit()
					break

	print('\nFinished')

	# if len(error_uids):
	# 	print('Error with UIDs:')
	# 	for i in error_uids:
	# 		print(i)

asyncio.run(v1())
