import json

# Set class constants in initialization
# Load the list of characters from their file
with open('../data/characters.json') as char_file:
    CHARACTERS = json.load(char_file)

# # Load the list of elements from the reactions file
# with open('../data/reaction.json') as react_file:
#     ELEMENTS = list(json.load(react_file).keys())

class Composition:
    """An object that stores information about a particular composition. Has:
        player: a string for the player who used this comp.
        phase: a string for the phase this composition was used in.
        room: a string in the form XX-X-X for the room this comp was used in.
        char_presence: a string --> boolean dict for chars in this comp.
        characters: a list of strings for the names of the chars in this comp.
        elements: a string --> int dict for the num of chars for each element.
        resonance: a string --> boolean dict for which resonances are active.
        
        Additional methods are:
        resonance_string: returns the resonances active as a string.
        on_res_chars: returns the list of characters activating the resonance.
        char_elemeent_list: returns the list of character's elements.
    """

    def __init__(self, uid, comp_chars, phase, round_num, star_num, room, info_char):
        """Composition constructor. Takes in:
            A player, as a UID string
            A composition, as a length-four list of character strings
            A phase, as a string
            A room, as a string
        """
        self.player = str(uid)
        self.phase = phase
        self.room = room
        self.round_num = int(round_num)
        self.star_num = int(star_num)
        self.char_structs(comp_chars, info_char)
        # self.comp_elements()

    def char_structs(self, comp_chars, info_char):
        """Character structure creator.
        Makes a presence dict that maps character names to bools, and
        a list (alphabetically ordered) of the character names.
        """
        self.char_presence = {}
        fives = []
        dps = []
        sub = []
        anemo = []
        healer = []
        temp = []
        temp_remove = []
        comp_chars.sort()
        for character in comp_chars:
            self.char_presence[character] = True
            if CHARACTERS[character]["availability"] in ["Limited 5*", "5*"]:
                fives.append(character)

            if character in ["Seele", "Yanqing", "Hook", "Jing Yuan", "Kafka"]:
                dps.insert(0, character)
            elif character in ["Qingque", "Arlan", "Himeko", "Dan Heng", "Sushang"]:
                dps.append(character)
            elif character in ["Clara", "Blade"]:
                sub.insert(0, character)
            elif character in ["Welt", "Serval", "Physical Trailblazer", "Sampo", "Herta", "Luka"]:
                sub.append(character)
            elif character in ["Bronya", "Silver Wolf", "Asta", "Tingyun", "Pela", "Yukong"]:
                anemo.append(character)
            elif character in ["Natasha", "Luocha", "Bailu"]:
                healer.insert(0, character)
            elif character in ["March 7th", "Gepard", "Fire Trailblazer"]:
                healer.append(character)
        self.fivecount = len(fives)
        self.characters = dps + sub + anemo + healer

        """Name structure creator.
        """
        comp_names = {
            "Faux-Mono Lightning": [
                ["Jing Yuan","Tingyun","Silver Wolf","Bailu"],
                ["Jing Yuan","Silver Wolf","Tingyun","Bailu"],
                ["Serval","Silver Wolf","Tingyun","Bailu"],
            ],
            "Faux-Mono Fire": [
                ["Himeko","Asta","Silver Wolf","Fire Trailblazer"],
            ],
            "Faux-Mono Physical": [
                ["Clara","Sushang","Silver Wolf","Natasha"],
                ["Sushang","Clara","Silver Wolf","Natasha"],
            ],
            "Faux-Mono Ice": [
                ["Yanqing","Pela","Silver Wolf","Gepard"],
                ["Yanqing","Silver Wolf","Pela","Gepard"],
                ["Yanqing","Silver Wolf","Pela","March 7th"],
            ],
            "Faux-Mono Imaginary": [
                ["Welt","Silver Wolf","Yukong","Luocha"],
            ]
        }
        self.comp_name = "-"
        self.alt_comp_name = "-"
        for comp_name in comp_names:
            if self.characters in comp_names[comp_name]:
                self.comp_name = comp_name
                break

        if self.comp_name == "-":
            archetype = ""
            if len(dps) + len(sub) > 2:
                archetype = " Triple Carry"
            elif len(dps) + len(sub) > 1:
                archetype = " Dual Carry"
            elif len(dps) + len(sub) == 1:
                if len(anemo) > 1:
                    archetype = " Hypercarry"
                elif len(healer) > 1:
                    archetype = " Dual Sustain"
            if dps:
                self.comp_name = dps[0] + archetype
            elif sub:
                self.comp_name = sub[0] + archetype
            elif anemo:
                self.comp_name = anemo[0] + archetype
            else:
                self.comp_name = "Full Sustain"

    def comp_elements(self):
        """Composition elements tracker.
        Creates a dict that maps elements to number of chars with that element,
        and a dict that maps the resonance(s) the comp has to booleans.
        """
        self.elements = dict.fromkeys(ELEMENTS, 0)
        for char in self.characters:
            self.elements[CHARACTERS[char]["element"]] += 1
        
        # self.resonance = dict.fromkeys(ELEMENTS, False)

        # # Add the unique resonance to the list of element resonances,
        # # and set it as the default. Technically there's the edge case for
        # # if there's < 4 characters, it should be false I think?
        # self.resonance['Unique'] = len(self.characters) == 4
        # for ele in ELEMENTS:
        #     if self.elements[ele] >= 2:
        #         self.resonance[ele] = True
        #         self.resonance['Unique'] = False
    
    # def resonance_string(self):
    #     """Returns the resonance of the composition. Two resos are joined by a ,"""
    #     resos = []
    #     for reso in self.resonance.keys():
    #         if self.resonance[reso]:
    #             resos.append(reso)
    #     return ", ".join(resos)
    
    # def on_res_chars(self):
    #     """Returns the list of characters who match the composition's resonance."""
    #     chars = []
    #     for char in self.characters:
    #         if self.resonance[CHARACTERS[char]["element"]] or self.resonance["Unique"]:
    #             chars.append(char)
    #     return chars

    # def char_element_list(self):
    #     """Returns the characters' elements as a list"""
    #     return [ CHARACTERS[char]['element'] for char in self.characters ]

    def contains_chars(self, chars):
        """Returns a bool whether this comp contains all the chars in included list."""
        for char in chars:
            if not self.char_presence[char]:
                return False
        return True
