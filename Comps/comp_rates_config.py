import json

with open('../data/characters.json') as char_file:
    CHARACTERS = json.load(char_file)

RECENT_PHASE = "1.1.3"
past_phase = "1.1.2.2"
char_infographics = "Seele"

# threshold for comps, not inclusive
global app_rate_threshold
global f2p_app_rate_threshold
app_rate_threshold = 0.15
f2p_app_rate_threshold = 0.1

# threshold for comps in character infographics
global char_app_rate_threshold
char_app_rate_threshold = 0.07


archetype = "all"
whaleCheck = False
whaleSigWeap = False
sigWeaps = []
standWeaps = []

# Char infographics should be separated from overall comp rankings
run_commands = [
    "Char usages all stages",
    "Char usages for each stage",
    "Comp usage all stages",
    "Comp usages for each stage"
]

alt_comps = "Character specific infographics" in run_commands

commands = [
    "Character specific infographics",
    "Char usages for each stage (combined)"
]