import json

with open('../data/characters.json') as char_file:
    CHARACTERS = json.load(char_file)

RECENT_PHASE = "1.4.2"
past_phase = "1.4.1"
char_infographics = ["Topaz and Numby", "Guinaifen", "Sushang", "Luka"]
char_infographics = char_infographics[3]

# threshold for comps, not inclusive
global app_rate_threshold
global app_rate_threshold_round
global f2p_app_rate_threshold
app_rate_threshold = 0.15
app_rate_threshold_round = 0.2
json_threshold = 0.1
f2p_app_rate_threshold = 0.1
skew_num = 0.8

# threshold for comps in character infographics
global char_app_rate_threshold
char_app_rate_threshold = 0.1

skip_self = False
skip_random = False
archetype = "all"
whaleCheck = False
whaleSigWeap = False
sigWeaps = []
standWeaps = []

# Char infographics should be separated from overall comp rankings
run_commands = [
    "Char usages 8 - 10",
    # "Comp usage 8 - 10",
    # "Char usages for each stage",
    # "Char usages for each stage (combined)",
    # "Comp usages for each stage",
    # "Character specific infographics",
    # "Char usages all stages",
    # "Comp usage all stages",
]



alt_comps = "Character specific infographics" in run_commands
if alt_comps and char_app_rate_threshold > app_rate_threshold:
    app_rate_threshold = char_app_rate_threshold