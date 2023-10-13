import json

with open('../data/characters.json') as char_file:
    CHARACTERS = json.load(char_file)

RECENT_PHASE = "1.3.3"
past_phase = "1.3.2"
char_infographics = ["Fu Xuan"]
char_infographics = char_infographics[0]

# threshold for comps, not inclusive
global app_rate_threshold
global app_rate_threshold_round
global f2p_app_rate_threshold
app_rate_threshold = 0.4
app_rate_threshold_round = 0.4
json_threshold = 0.1
f2p_app_rate_threshold = 0.1

# threshold for comps in character infographics
global char_app_rate_threshold
char_app_rate_threshold = 0.4


skip_self = False
archetype = "all"
whaleCheck = False
whaleSigWeap = False
sigWeaps = []
standWeaps = []

# Char infographics should be separated from overall comp rankings
run_commands = [
    "Char usages 6 - 10",
    # "Char usages for each stage",
    # "Comp usage 6 - 10",
    # "Comp usages for each stage",
    # "Char usages for each stage (combined)",
    "Character specific infographics",
    # "Char usages all stages",
    # "Comp usage all stages",
]

alt_comps = "Character specific infographics" in run_commands