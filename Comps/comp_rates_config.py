import json
import argparse
import os
from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--all", action="store_true")
parser.add_argument("-ca", "--comps_all", action="store_true")
parser.add_argument("-d", "--duos", action="store_true")
parser.add_argument("-t", "--top", action="store_true")
parser.add_argument("-ct", "--comps_top", action="store_true")
parser.add_argument("-w", "--whale", action="store_true")
parser.add_argument("-f", "--f2p", action="store_true")

# # Unused for now
# parser.add_argument("-MOC", action = "store_true")
# parser.add_argument("-PF", action = "store_true")
# parser.add_argument("-AS", action = "store_true")
# parser.add_argument("-p", "--past")
# parser.add_argument("-r", "--recent")

args = parser.parse_args()

with open(str(os.getenv("REPO_PATH")) + "/data/characters.json") as char_file:
    CHARACTERS = json.load(char_file)

with open(str(os.getenv("REPO_PATH")) + "/data/light_cones.json") as char_file:
    LIGHT_CONES = json.load(char_file)

# don't add underscore, i.e. 2.2.1"_pf"
RECENT_PHASE = "2.7.3"

# if no past phase, leave blank
# add underscore, i.e. 2.2.1"_pf"
past_phase = "2.6.3"
global pf_mode
global as_mode
# if as: pf_mode = True
pf_mode = False
as_mode = False

run_all_chars = False
run_chars_name = ["Aglaea", "Boothill", "Robin", "Silver Wolf"]
char_infographics = run_chars_name[1]

# threshold for comps in character infographics, non-inclusive
global char_app_rate_threshold
char_app_rate_threshold = 0.25

# threshold for comps, not inclusive
global app_rate_threshold
global app_rate_threshold_round
global f2p_app_rate_threshold
app_rate_threshold = 0.1
app_rate_threshold_round = 0
json_threshold = 0
f2p_app_rate_threshold = 0.1
skew_num = 0.8
duo_dict_len = 30
duo_dict_len_print = 10

skip_self = False
skip_random = False
archetype = "all"
whaleOnly = args.whale
f2pOnly = args.f2p

# Char infographics should be separated from overall comp rankings
run_commands = [
    # "Duos check",
    "Char usages 8 - 10",
    # "Char usages for each stage",
    # "Char usages for each stage (combined)",
    # "Comp usage 8 - 10",
    # "Comp usages for each stage",
    # "Character specific infographics",
    # "Char usages all stages",
    # "Comp usage all stages",
]

if args.whale or args.top or args.f2p:
    run_commands = [
        "Char usages 8 - 10",
        "Comp usage 8 - 10",
    ]

elif args.comps_top:
    run_commands = [
        "Comp usage 8 - 10",
    ]

elif args.all:
    run_commands = [
        "Char usages 8 - 10",
        "Char usages for each stage",
        "Char usages for each stage (combined)",
        "Comp usage 8 - 10",
        "Comp usages for each stage",
    ]

elif args.comps_all:
    run_commands = [
        "Comp usage 8 - 10",
        "Comp usages for each stage",
    ]

elif args.duos:
    run_commands = [
        "Duos check",
    ]

sigWeaps = []
standWeaps = [
    "Night on the Milky Way",
    "Something Irreplaceable",
    "But the Battle Isn't Over",
    "In the Name of the World",
    "Moment of Victory",
    "Time Waits for No One",
    "Sleep Like the Dead",
    "On the Fall of an Aeon",
    "Cruising in the Stellar Sea",
    "Texture of Memories",
    "Solitary Healing",
    "Eternal Calculus",
]
for light_cone in LIGHT_CONES:
    if (
        LIGHT_CONES[light_cone]["rarity"] == 5
        and LIGHT_CONES[light_cone]["name"] not in standWeaps
    ):
        sigWeaps += [LIGHT_CONES[light_cone]["name"]]

alt_comps = "Character specific infographics" in run_commands
if alt_comps and char_app_rate_threshold > app_rate_threshold:
    app_rate_threshold = char_app_rate_threshold
