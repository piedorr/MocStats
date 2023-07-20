import csv
import json
from comp_rates_config import archetype

with open('../data/characters.json') as char_file:
    CHARACTERS = json.load(char_file)

def find_archetype(foundchar):
    match archetype:
        # case "spread":
        #     return(foundchar["foundElectro"] and foundchar["foundDendro"] and not foundchar["foundHydro"])
        case _:
            return(True)

elementChars = {
    # "Pyro": []
}
# for char in CHARACTERS:
#     if CHARACTERS[char]["element"] == "Pyro":
#         elementChars["Pyro"] += [char]

def resetfind():
    foundchar = {
        # "foundPyro": False,
        "found": False
    }
    return foundchar

def findchars(char, foundchar):
    pass
    # foundchar["foundPyro"] = char in elementChars["Pyro"] or foundchar["foundPyro"]