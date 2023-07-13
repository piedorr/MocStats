import json
import csv

f = open('../data/relics.json')
relics_data = json.load(f)
f = open('../data/characters.json')
characters = json.load(f)

trailblazer_ids = []
for char in characters.values():
	if char["name"] == "{NICKNAME}":
		trailblazer_ids.append(char["id"])

# uids = []
with open("data/uids.csv", 'r', encoding='UTF8') as f:
    reader = csv.reader(f, delimiter=',')
    uids = list(reader)
uids = [uid[0] for uid in uids]
uids = list(dict.fromkeys(uids))
