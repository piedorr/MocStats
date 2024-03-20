import json

with open('../data/characters.json') as char_file:
    CHARACTERS = json.load(char_file)

with open('../data/light_cones.json') as char_file:
    LIGHT_CONES = json.load(char_file)

RECENT_PHASE = "2.0.4"
past_phase = "2.0.2"
global pf_mode
pf_mode = False
char_infographics = ["Sushang", "Hook", "Natasha", "Dr. Ratio", "Kafka"]
char_infographics = char_infographics[3]

# threshold for comps in character infographics, non-inclusive
global char_app_rate_threshold
char_app_rate_threshold = 0.25

# threshold for comps, not inclusive
global app_rate_threshold
global app_rate_threshold_round
global f2p_app_rate_threshold
app_rate_threshold = 0.1
app_rate_threshold_round = 0
json_threshold = 0.1
f2p_app_rate_threshold = 0.1
skew_num = 0.8
duo_dict_len = 30
duo_dict_len_print = 10

skip_self = False
skip_random = False
archetype = "all"
whaleCheck = False
whaleSigWeap = False

# Char infographics should be separated from overall comp rankings
run_commands = [
    # "Duos check",
    # "Char usages 8 - 10",
    # "Char usages for each stage",
    # "Char usages for each stage (combined)",
    # "Comp usage 8 - 10",
    "Comp usages for each stage",
    # "Character specific infographics",
    # "Char usages all stages",
    # "Comp usage all stages",
]


sigWeaps = []
standWeaps = ["Night on the Milky Way", "Something Irreplaceable", "But the Battle Isn't Over", "In the Name of the World", "Moment of Victory", "Time Waits for No One", "Sleep Like the Dead"]
for light_cone in LIGHT_CONES:
    if light_cone[:2] == "23":
        if LIGHT_CONES[light_cone]["name"] not in standWeaps:
            sigWeaps += [LIGHT_CONES[light_cone]["name"]]

alt_comps = "Character specific infographics" in run_commands
if alt_comps and char_app_rate_threshold > app_rate_threshold:
    app_rate_threshold = char_app_rate_threshold