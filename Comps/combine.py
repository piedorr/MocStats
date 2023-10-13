import json

with open('../char_results/all.json') as char_file:
    CHARACTERS = json.load(char_file)
with open('../mihomo/results_real/chars.json') as char_file:
    STATS = json.load(char_file)

temp_char_list = []
for i in range(len(CHARACTERS)):
    if STATS[i]["name"] == CHARACTERS[i]["char"]:
        del STATS[i]["name"]
    else:
        print(STATS[i]["name"])
    temp_char_list.append(CHARACTERS[i] | STATS[i])
CHARACTERS = temp_char_list

with open("../char_results/all2.json", "w") as out_file:
    out_file.write(json.dumps(CHARACTERS,indent=4))