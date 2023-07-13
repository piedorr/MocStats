import json

# This var needs to change every time
RECENT_PHASE = "2.2b"

with open('../data/characters.json') as char_file:
    CHARACTERS = json.load(char_file)

past_phase = "1.1.2"
char = "Seele"

# threshold for comps, not inclusive
global app_rate_threshold
global f2p_app_rate_threshold
app_rate_threshold = 0.15
f2p_app_rate_threshold = 0.1

# threshold for comps in character infographics
global char_app_rate_threshold
char_app_rate_threshold = 0.07

archetype = "all"
alt_comps = False
whaleCheck = False
whaleSigWeap = True
sigWeaps = []
standWeaps = []

run_commands = [
    "Char usages all stages",
    "Comp usages for each stage"
]

commands = [
    "Char usages for each stage",
    "Char usages for each stage (combined)",
    "Comp usage all stages overall",
    "Character specific infographics"
]