import json

# Set class constants in initialization
# Load the list of characters from their file
with open("../data/characters.json") as char_file:
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

    def __init__(
        self,
        uid,
        comp_chars,
        phase,
        round_num,
        star_num,
        room,
        info_char,
        buff,
        comp_chars_cons,
    ):
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
        self.char_structs(comp_chars, info_char, comp_chars_cons)
        self.buff = buff
        # self.comp_elements()

    def char_structs(self, comp_chars, info_char, comp_chars_cons):
        """Character structure creator.
        Makes a presence dict that maps character names to bools, and
        a list (alphabetically ordered) of the character names.
        """
        self.char_presence = {}
        self.char_cons = {}
        fives = []
        self.dps = []
        self.subdps = []
        self.anemo = []
        self.healer = []
        self.dot = []
        self.fua = []
        self.super_break = []
        len_element = {
            "Ice": 0,
            "Wind": 0,
            "Fire": 0,
            "Imaginary": 0,
            "Quantum": 0,
            "Lightning": 0,
            "Physical": 0,
        }
        if comp_chars_cons:
            for char_iter in range(len(comp_chars)):
                self.char_cons[comp_chars[char_iter]] = int(comp_chars_cons[char_iter])
        comp_chars.sort()
        for character in comp_chars:
            if "Imbibitor" in character:
                character = "Dan Heng • Imbibitor Lunae"
            if "Topaz and Numby" == character:
                character = "Topaz & Numby"
            if "March 7th" == character:
                character = "Ice March 7th"
            self.char_presence[character] = True
            if CHARACTERS[character]["availability"] in ["Limited 5*", "5*"]:
                fives.append(character)

            if character in [
                "Seele",
                "Yanqing",
                "Hook",
                "Jing Yuan",
                "Dan Heng • Imbibitor Lunae",
                "Argenti",
                "Dr. Ratio",
                "Acheron",
                "Boothill",
                "Firefly",
                "Jade",
                "Feixiao",
                "Rappa",
                "The Herta",
                "Aglaea",
                "Mydei",
            ]:
                self.dps.insert(0, character)
            elif character in [
                "Kafka",
                "Qingque",
                "Arlan",
                "Dan Heng",
                "Sushang",
                "Jingliu",
                "Himeko",
            ]:
                self.dps.append(character)
            elif character in [
                "Clara",
                "Yunli",
                "Blade",
                "Xueyi",
                "Misha",
                "Black Swan",
            ]:
                self.subdps.insert(0, character)
            elif character in [
                "Imaginary March 7th",
                "Moze",
                "Welt",
                "Serval",
                "Physical Trailblazer",
                "Herta",
                "Topaz & Numby",
            ]:
                self.subdps.append(character)
            elif character in ["Sampo", "Luka", "Guinaifen"]:
                self.anemo.insert(0, character)
            elif character in [
                "Bronya",
                "Silver Wolf",
                "Asta",
                "Tingyun",
                "Pela",
                "Yukong",
                "Hanya",
                "Ruan Mei",
                "Sparkle",
                "Robin",
                "Imaginary Trailblazer",
                "Jiaoqiu",
                "Sunday",
                "Fugue",
                "Ice Trailblazer",
                "Tribbie",
            ]:
                self.anemo.append(character)
            elif character in [
                "Natasha",
                "Luocha",
                "Bailu",
                "Lynx",
                "Huohuo",
                "Gallagher",
            ]:
                self.healer.insert(0, character)
            elif character in [
                "Ice March 7th",
                "Gepard",
                "Fire Trailblazer",
                "Fu Xuan",
                "Aventurine",
                "Lingsha",
            ]:
                self.healer.append(character)

            if character in [
                "Kafka",
                "Black Swan",
                "Serval",
                "Sampo",
                "Luka",
                "Guinaifen",
            ]:
                self.dot.append(character)
            if character in [
                "Topaz & Numby",
                "Dr. Ratio",
                "Clara",
                "Yunli",
                "Jing Yuan",
                "Himeko",
                "Kafka",
                "Blade",
                "Herta",
                "Xueyi",
                "Jade",
                "Feixiao",
                "Moze",
            ]:
                self.fua.append(character)
            if character in ["Imaginary Trailblazer", "Fugue"]:
                self.super_break.append(character)

            if CHARACTERS[character]["element"] == "Ice":
                len_element["Ice"] += 1
            if CHARACTERS[character]["element"] == "Wind":
                len_element["Wind"] += 1
            if CHARACTERS[character]["element"] == "Fire":
                len_element["Fire"] += 1
            if CHARACTERS[character]["element"] == "Imaginary":
                len_element["Imaginary"] += 1
            if CHARACTERS[character]["element"] == "Quantum":
                len_element["Quantum"] += 1
            if CHARACTERS[character]["element"] == "Thunder":
                len_element["Lightning"] += 1
            if CHARACTERS[character]["element"] == "Physical":
                len_element["Physical"] += 1

        if (not self.dps and not self.subdps) and "Lingsha" in self.healer:
            self.dps.insert(0, "Lingsha")

        self.fivecount = len(fives)
        self.characters = self.dps + self.subdps + self.anemo + self.healer

        if (
            "Acheron" in self.dps or "Kafka" in self.dps
        ) and "Black Swan" in self.subdps:
            self.subdps.remove("Black Swan")
            self.anemo.insert(0, "Black Swan")

        """Name structure creator.
        """
        # comp_names = {
        # }
        self.comp_name = "-"
        self.alt_comp_name = "-"
        self.dual_comp_name = "-"
        # for comp_name in comp_names:
        #     if self.characters in comp_names[comp_name]:
        #         self.comp_name = comp_name
        #         break

        if self.comp_name == "-":
            if len(self.dot) >= 1:
                if len(self.dot) > 2:
                    self.alt_comp_name = self.characters[0] + " Triple DoT"
                elif len(self.dot) > 1:
                    self.alt_comp_name = self.characters[0] + " Dual DoT"
                # elif len(self.dps) + len(self.subdps) == 1:
                #     self.alt_comp_name = self.characters[0] + " Solo DoT"
            elif len(self.fua) > 1:
                self.alt_comp_name = self.characters[0] + " Follow-Up"

            # if len_element["Quantum"] == 4:
            #     self.alt_comp_name = "Mono Quantum"
            #     self.dual_comp_name = "Mono Quantum"
            # for elem in len_element:
            #     if len_element[elem] == 4:
            #         self.comp_name = "Mono " + elem
            # if self.comp_name == "-" and "Silver Wolf" in self.characters:
            #     for elem in len_element:
            #         if len_element[elem] == 3 and elem != "Quantum":
            #             self.comp_name = "Faux-Mono " + elem
            # if self.comp_name == "-":
            archetype = ""
            if len(self.healer) == 0:
                archetype = " No Sustain"
                self.alt_comp_name = self.characters[0] + " No Sustain"
            elif len(self.super_break) >= 1:
                archetype = " Super Break"
            elif len(self.dps) + len(self.subdps) > 1:
                if (
                    len(self.dps) + len(self.subdps) > 2
                    and "Follow-Up" not in self.alt_comp_name
                ):
                    archetype = " Triple Carry"
                else:
                    archetype = " Dual Carry"
                self.dual_comp_name = self.characters[1] + archetype
            else:
                if len(self.healer) > 1:
                    archetype = " Dual Sustain"
                elif len(self.anemo) > 0:
                    archetype = " Hypercarry"

            if self.dps or self.subdps or self.anemo:
                self.comp_name = self.characters[0] + archetype
            else:
                self.comp_name = "Full Sustain"

    # def comp_elements(self):
    #     """Composition elements tracker.
    #     Creates a dict that maps elements to number of chars with that element,
    #     and a dict that maps the resonance(s) the comp has to booleans.
    #     """
    #     self.elements = dict.fromkeys(ELEMENTS, 0)
    #     for char in self.characters:
    #         self.elements[CHARACTERS[char]["element"]] += 1

    #     # self.resonance = dict.fromkeys(ELEMENTS, False)

    #     # # Add the unique resonance to the list of element resonances,
    #     # # and set it as the default. Technically there's the edge case for
    #     # # if there's < 4 characters, it should be false I think?
    #     # self.resonance['Unique'] = len(self.characters) == 4
    #     # for ele in ELEMENTS:
    #     #     if self.elements[ele] >= 2:
    #     #         self.resonance[ele] = True
    #     #         self.resonance['Unique'] = False

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
