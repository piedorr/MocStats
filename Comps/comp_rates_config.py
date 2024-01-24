import json

with open('../data/characters.json') as char_file:
    CHARACTERS = json.load(char_file)

RECENT_PHASE = "1.6.2"
past_phase = "1"
global pf_mode
pf_mode = True
char_infographics = ["Ruan Mei", "Blade", "March 7th", "Xueyi", "Tingyun"]
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
sigWeaps = ["Night on the Milky Way", "In the Night", "Something Irreplaceable", "But the Battle Isn't Over", "In the Name of the World", "Moment of Victory", "Patience Is All You Need", "Incessant Rain", "Echoes of the Coffin", "The Unreachable Side", "Before Dawn", "She Already Shut Her Eyes", "Sleep Like the Dead", "Time Waits for No One", "I Shall Be My Own Sword", "Brighter Than the Sun", "Worrisome, Blissful", "Night of Fright", "An Instant Before A Gaze", "Past Self in Mirror", "Baptism of Pure Thought", "Earthly Escapade", "Reforged Remembrance"]
standWeaps = []

# Char infographics should be separated from overall comp rankings
run_commands = [
    "Char usages 8 - 10",
    # "Char usages for each stage",
    # "Char usages for each stage (combined)",
    # "Comp usage 8 - 10",
    # "Comp usages for each stage",
    # "Character specific infographics",
    # "Char usages all stages",
    # "Comp usage all stages",
    # "Duos check",
]



alt_comps = "Character specific infographics" in run_commands
if alt_comps and char_app_rate_threshold > app_rate_threshold:
    app_rate_threshold = char_app_rate_threshold