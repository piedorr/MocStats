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
        self.round_num = round_num
        self.star_num = int(star_num)
        self.char_structs(comp_chars)
        self.name_structs(self.characters, info_char)
        # self.comp_elements()

    def char_structs(self, comp_chars):
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
        for character in comp_chars:
            self.char_presence[character] = True
            if CHARACTERS[character]["availability"] in ["Limited 5*", "5*"]:
                fives.append(character)

            if character in ["Seele", "Yanqing", "Dan Heng", "Hook", "Jing Yuan", "Kafka", "Blade"]:
                dps.insert(0, character)
            elif character in ["Qingque", "Serval", "Arlan", "Clara", "Sushang", "Physical Trailblazer", "Himeko", "Sampo", "Herta"]:
                sub.insert(0, character)
            elif character in ["Bronya", "Silver Wolf", "Asta", "Tingyun", "Welt", "Pela", "Yukong"]:
                anemo.append(character)
            elif character in ["Natasha", "Luocha", "Bailu"]:
                healer.insert(0, character)
            elif character in ["March 7th", "Gepard", "Fire Trailblazer"]:
                healer.append(character)
            # else:
            #     temp.append(character)
        # for character in temp:
        #     if character in ["Xingqiu", "Yelan"]:
        #         # If Childe is DPS, Xingqiu is ahead of Xiangling
        #         if "Tartaglia" in dps:
        #             dps.insert(1, character)
        #             temp_remove.append(character)
        #             continue
        #         else:
        #             sub.insert(0, character)
        #             temp_remove.append(character)
        #             continue
        #     elif character in ["Zhongli"]:
        #         # For Xiao Succ Benny Dong
        #         if (
        #             "Sucrose" in temp or
        #             "Jean" in temp or
        #             "Kaedehara Kazuha" in anemo or
        #             "Venti" in anemo or
        #             "Faruzan" in temp
        #         ) and "Bennett" in healer and "Xiao" in dps:
        #             healer.append(character)
        #             temp_remove.append(character)
        #             continue
        #         else:
        #             healer.insert(0, character)
        #             temp_remove.append(character)
        #             continue
        #     elif character in ["Faruzan"]:
        #         if "Wanderer" in dps or "Xiao" in dps:
        #             dps.append(character)
        #             temp_remove.append(character)
        #             continue
        #         else:
        #             sub.append(character)
        #             temp_remove.append(character)
        #             continue
        #     elif character in ["Nilou"]:
        #         if "Nahida" in sub or "Kaveh" in dps:
        #             sub.append(character)
        #             temp_remove.append(character)
        #             continue
        #         else:
        #             dps.insert(0, character)
        #             temp_remove.append(character)
        #             continue
        #     elif character in ["Albedo"]:
        #         if "Zhongli" in temp:
        #             anemo.append(character)
        #             temp_remove.append(character)
        #             continue
        #         else:
        #             sub.append(character)
        #             temp_remove.append(character)
        #             continue
        #     elif character in ["Yae Miko"]:
        #         if "Raiden Shogun" in dps:
        #             dps.append(character)
        #             temp_remove.append(character)
        #             continue
        #         else:
        #             sub.insert(0, character)
        #             temp_remove.append(character)
        #             continue
        #     elif character in ["Barbara"]:
        #         if healer:
        #             sub.append(character)
        #             temp_remove.append(character)
        #             continue
        #         else:
        #             healer.append(character)
        #             temp_remove.append(character)
        #             continue

        #     if dps:
        #         if "Dehya" in dps and character in ["Ganyu"]:
        #             dps.insert(0, character)
        #             temp_remove.append(character)
        #             continue
        #         elif character in ["Ningguang","Ganyu","Kamisato Ayato"]:
        #             sub.insert(0, character)
        #             temp_remove.append(character)
        #             continue
        #         elif character in ["Yanfei"]:
        #             healer.insert(0, character)
        #             temp_remove.append(character)
        #             continue
        #     elif character in ["Ningguang","Yanfei","Ganyu","Kamisato Ayato"]:
        #         dps.append(character)
        #         temp_remove.append(character)
        #         continue
        # if "Nahida" in sub:
        #     if not(dps):
        #         sub.remove("Nahida")
        #         dps.append("Nahida")
        #     elif "Raiden Shogun" in dps and ("Yae Miko" in dps or len(dps) == 1):
        #         sub.remove("Nahida")
        #         dps.insert(0, "Nahida")
        #         dps.remove("Raiden Shogun")
        #         sub.insert(0, "Raiden Shogun")
        #         if "Kamisato Ayato" in sub:
        #             sub.remove("Kamisato Ayato")
        #             dps.insert(0, "Kamisato Ayato")
        # for character in temp_remove:
        #     temp.remove(character)
        # temp_remove = []
        # for character in temp:
        #     if character in ["Xiangling"]:
        #         if "Kamisato Ayato" in sub:
        #             sub.insert(1, character)
        #             temp_remove.append(character)
        #             continue
        #         else:
        #             sub.insert(0, character)
        #             temp_remove.append(character)
        #             continue

        #     if "Xiao" in dps:
        #         if character in ["Jean","Sucrose"]:
        #             dps.append(character)
        #             temp_remove.append(character)
        #             continue
        #     elif character in ["Jean"]:
        #         anemo.insert(0, character)
        #         temp_remove.append(character)
        #         continue

        #     if dps:
        #         if character in ["Sucrose"]:
        #             # For Sukokomon, where Kokomi is DPS and Xiangling+Fischl is sub
        #             if "Fischl" in sub and "Xiangling" in temp:
        #                 dps.append(character)
        #                 temp_remove.append(character)
        #                 continue
        #             else:
        #                 anemo.append(character)
        #                 temp_remove.append(character)
        #                 continue
        #         if healer and "Zhongli" not in healer:
        #             if character in ["Sangonomiya Kokomi","Lisa"]:
        #                 sub.append(character)
        #                 temp_remove.append(character)
        #                 continue
        #         else:
        #             if character in ["Sangonomiya Kokomi","Lisa"]:
        #                 sub.append(character)
        #                 temp_remove.append(character)
        #                 continue
        #     else:
        #         if character in ["Sangonomiya Kokomi","Lisa"]:
        #             if "Yae Miko" in sub:
        #                 sub.append(character)
        #                 temp_remove.append(character)
        #                 continue
        #             else:
        #                 dps.insert(0, character)
        #                 temp_remove.append(character)
        #                 continue

        # for character in temp_remove:
        #     temp.remove(character)
        # for character in temp:
        #     if character in ["Sucrose"]:
        #         if "Xiangling" in sub or "Yae Miko" in sub:
        #             anemo.insert(0, character)
        #             temp_remove.append(character)
        #             continue
        #         else:
        #             dps.insert(0, character)
        #             temp_remove.append(character)
        #             continue
        #     elif character in ["Traveler"]:
        #         sub.insert(0, character)
        #         temp_remove.append(character)
        #         continue
        #     else:
        #         print("dps: " + str(dps) + ", sub: " + str(sub) + ", anemo: " + str(anemo) + ", healer: " + str(healer))
        #         print("not included: " + str(temp))
        self.fivecount = len(fives)
        self.characters = dps + sub + anemo + healer

    def name_structs(self, characters, info_char):
        """Name structure creator.
        """
        comp_names = {
            "Clara Dual Carry": [
                ["Clara","Serval","Tingyun","Natasha"]
            ],
            "Clara Hypercarry": [
                ["Clara","Pela","Tingyun","Natasha"],
                ["Clara","Silver Wolf","Natasha","Fire Trailblazer"],
                ["Clara","Silver Wolf","Natasha","Gepard"],
                ["Clara","Silver Wolf","Natasha","March 7th"],
                ["Clara","Silver Wolf","Tingyun","Bailu"],
                ["Clara","Silver Wolf","Tingyun","Natasha"],
                ["Clara","Pela","Natasha","March 7th"],
                ["Clara","Pela","Tingyun","March 7th"],
                ["Clara","Tingyun","Bailu","March 7th"],
                ["Clara","Tingyun","Luocha","March 7th"],
                ["Clara","Tingyun","Gepard","Fire Trailblazer"],
                ["Clara","Tingyun","Natasha","Fire Trailblazer"],
                ["Clara","Tingyun","Natasha","March 7th"],
                ["Clara","Welt","Bronya","Natasha"]
            ],
            "Dan Heng Hypercarry": [
                ["Dan Heng","Asta","Natasha","Fire Trailblazer"],
                ["Dan Heng","Asta","Bailu","Fire Trailblazer"],
                ["Dan Heng","Bronya","Pela","Natasha"],
                ["Dan Heng","Bronya","Bailu","Fire Trailblazer"],
                ["Dan Heng","Bronya","Natasha","Fire Trailblazer"],
                ["Dan Heng","Silver Wolf","Asta","Bailu"],
                ["Dan Heng","Silver Wolf","Natasha","Fire Trailblazer"],
                ["Dan Heng","Silver Wolf","Natasha","Gepard"],
                ["Dan Heng","Silver Wolf","Pela","Gepard"],
                ["Dan Heng","Silver Wolf","Tingyun","Bailu"],
                ["Dan Heng","Silver Wolf","Tingyun","Gepard"],
                ["Dan Heng","Silver Wolf","Bailu","Fire Trailblazer"],
                ["Dan Heng","Pela","Tingyun","Gepard"],
                ["Dan Heng","Tingyun","Bailu","Fire Trailblazer"],
                ["Dan Heng","Tingyun","Bailu","Gepard"],
                ["Dan Heng","Tingyun","Bailu","March 7th"],
                ["Dan Heng","Tingyun","Natasha","Fire Trailblazer"],
                ["Dan Heng","Tingyun","Natasha","March 7th"],
                ["Dan Heng","Tingyun","March 7th","Fire Trailblazer"],
                ["Dan Heng","Welt","Pela","Gepard"],
                ["Dan Heng","Welt","Asta","Natasha"],
                ["Dan Heng","Welt","March 7th","Fire Trailblazer"],
                ["Dan Heng","Welt","Natasha","March 7th"],
                ["Dan Heng","Welt","Pela","Bailu"],
                ["Dan Heng","Welt","Pela","Natasha"],
                ["Dan Heng","Welt","Silver Wolf","Natasha"],
                ["Dan Heng","Welt","Tingyun","Gepard"],
                ["Dan Heng","Welt","Tingyun","Natasha"],
                ["Dan Heng","Welt","Bronya","Gepard"],
                ["Dan Heng","Welt","Natasha","Fire Trailblazer"],
            ],
            "Dan Heng Dual Carry": [
                ["Dan Heng","Clara","Bailu","March 7th"],
                ["Dan Heng","Clara","Tingyun","Natasha"],
                ["Dan Heng","Clara","Natasha","March 7th"],
                ["Dan Heng","Clara","Silver Wolf","March 7th"],
                ["Dan Heng","Clara","Silver Wolf","Natasha"],
                ["Dan Heng","Himeko","Natasha","Fire Trailblazer"],
                ["Dan Heng","Serval","Silver Wolf","Gepard"],
                ["Dan Heng","Serval","Natasha","Fire Trailblazer"],
                ["Dan Heng","Sushang","Natasha","Fire Trailblazer"]
            ],
            "Himeko Hypercarry": [
                ["Himeko","Silver Wolf","Natasha","Fire Trailblazer"],
                ["Himeko","Asta","March 7th","Fire Trailblazer"],
                ["Himeko","Asta","Natasha","Fire Trailblazer"]
            ],
            "Hook Hypercarry": [
                ["Hook","Asta","Bailu","Fire Trailblazer"],
                ["Hook","Asta","Natasha","Fire Trailblazer"],
                ["Hook","Silver Wolf","Natasha","Fire Trailblazer"],
                ["Hook","Tingyun","Natasha","Fire Trailblazer"]
            ],
            "Hook Dual Carry": [
                ["Hook","Seele","Natasha","Fire Trailblazer"],
                ["Hook","Qingque","Natasha","Gepard"]
            ],
            "Jing Yuan Hypercarry": [
                ["Jing Yuan","Asta","Bailu","Fire Trailblazer"],
                ["Jing Yuan","Asta","Natasha","Fire Trailblazer"],
                ["Jing Yuan","Asta","Tingyun","Bailu"],
                ["Jing Yuan","Asta","Tingyun","Gepard"],
                ["Jing Yuan","Asta","Tingyun","Natasha"],
                ["Jing Yuan","Asta","Tingyun","Fire Trailblazer"],
                ["Jing Yuan","Asta","Tingyun","Luocha"],
                ["Jing Yuan","Bronya","Bailu","Gepard"],
                ["Jing Yuan","Bronya","Tingyun","Luocha"],
                ["Jing Yuan","Bronya","Bailu","Fire Trailblazer"],
                ["Jing Yuan","Bronya","Natasha","Fire Trailblazer"],
                ["Jing Yuan","Bronya","Natasha","Gepard"],
                ["Jing Yuan","Bronya","Tingyun","Fire Trailblazer"],
                ["Jing Yuan","Bronya","Tingyun","Gepard"],
                ["Jing Yuan","Bronya","Tingyun","Bailu"],
                ["Jing Yuan","Bronya","Tingyun","Natasha"],
                ["Jing Yuan","Pela","Natasha","Fire Trailblazer"],
                ["Jing Yuan","Pela","Tingyun","Fire Trailblazer"],
                ["Jing Yuan","Pela","Tingyun","Bailu"],
                ["Jing Yuan","Pela","Tingyun","Gepard"],
                ["Jing Yuan","Pela","Tingyun","March 7th"],
                ["Jing Yuan","Pela","Tingyun","Natasha"],
                ["Jing Yuan","Pela","Tingyun","Luocha"],
                ["Jing Yuan","Silver Wolf","Luocha","Gepard"],
                ["Jing Yuan","Silver Wolf","Tingyun","Luocha"],
                ["Jing Yuan","Silver Wolf","Asta","Gepard"],
                ["Jing Yuan","Silver Wolf","Bailu","Fire Trailblazer"],
                ["Jing Yuan","Silver Wolf","Bailu","Gepard"],
                ["Jing Yuan","Silver Wolf","Bailu","March 7th"],
                ["Jing Yuan","Silver Wolf","Bronya","Bailu"],
                ["Jing Yuan","Silver Wolf","Bronya","Gepard"],
                ["Jing Yuan","Silver Wolf","Bronya","Natasha"],
                ["Jing Yuan","Silver Wolf","March 7th","Gepard"],
                ["Jing Yuan","Silver Wolf","Natasha","Fire Trailblazer"],
                ["Jing Yuan","Silver Wolf","Natasha","Gepard"],
                ["Jing Yuan","Silver Wolf","Pela","Bailu"],
                ["Jing Yuan","Silver Wolf","Pela","Gepard"],
                ["Jing Yuan","Silver Wolf","Tingyun","Fire Trailblazer"],
                ["Jing Yuan","Silver Wolf","Tingyun","March 7th"],
                ["Jing Yuan","Silver Wolf","Tingyun","Natasha"],
                ["Jing Yuan","Silver Wolf","Tingyun","Gepard"],
                ["Jing Yuan","Tingyun","Bailu","Fire Trailblazer"],
                ["Jing Yuan","Tingyun","Bailu","Gepard"],
                ["Jing Yuan","Tingyun","Bailu","March 7th"],
                ["Jing Yuan","Tingyun","March 7th","Fire Trailblazer"],
                ["Jing Yuan","Tingyun","March 7th","Gepard"],
                ["Jing Yuan","Tingyun","Natasha","Fire Trailblazer"],
                ["Jing Yuan","Tingyun","Natasha","Gepard"],
                ["Jing Yuan","Tingyun","Natasha","March 7th"],
                ["Jing Yuan","Tingyun","Gepard","Fire Trailblazer"],
                ["Jing Yuan","Tingyun","Luocha","Fire Trailblazer"],
                ["Jing Yuan","Tingyun","Luocha","Gepard"],
                ["Jing Yuan","Tingyun","Luocha","March 7th"],
                ["Jing Yuan","Tingyun","Yukong","Luocha"],
                ["Jing Yuan","Welt","Silver Wolf","Luocha"],
                ["Jing Yuan","Welt","Tingyun","Luocha"],
                ["Jing Yuan","Welt","Bailu","Fire Trailblazer"],
                ["Jing Yuan","Welt","Bronya","Bailu"],
                ["Jing Yuan","Welt","Bronya","Natasha"],
                ["Jing Yuan","Welt","Natasha","Fire Trailblazer"],
                ["Jing Yuan","Welt","Natasha","Gepard"],
                ["Jing Yuan","Welt","Silver Wolf","Bailu"],
                ["Jing Yuan","Welt","Silver Wolf","Fire Trailblazer"],
                ["Jing Yuan","Welt","Silver Wolf","Gepard"],
                ["Jing Yuan","Welt","Silver Wolf","Natasha"],
                ["Jing Yuan","Welt","Tingyun","Bailu"],
                ["Jing Yuan","Welt","Tingyun","Fire Trailblazer"],
                ["Jing Yuan","Welt","Tingyun","March 7th"],
                ["Jing Yuan","Welt","Tingyun","Gepard"],
                ["Jing Yuan","Welt","Tingyun","Natasha"]
            ],
            "Jing Yuan Dual Carry": [
                ["Jing Yuan","Clara","Bailu","March 7th"],
                ["Jing Yuan","Clara","Natasha","March 7th"],
                ["Jing Yuan","Clara","Pela","March 7th"],
                ["Jing Yuan","Clara","Silver Wolf","Bailu"],
                ["Jing Yuan","Clara","Silver Wolf","Natasha"],
                ["Jing Yuan","Clara","Tingyun","Bailu"],
                ["Jing Yuan","Clara","Tingyun","Gepard"],
                ["Jing Yuan","Clara","Tingyun","March 7th"],
                ["Jing Yuan","Clara","Tingyun","Natasha"],
                ["Jing Yuan","Clara","Welt","Bailu"],
                ["Jing Yuan","Clara","Welt","Natasha"],
                ["Jing Yuan","Clara","Tingyun","Luocha"],
                ["Jing Yuan","Dan Heng","Natasha","Fire Trailblazer"],
                ["Jing Yuan","Dan Heng","Tingyun","Bailu"],
                ["Jing Yuan","Dan Heng","Tingyun","Gepard"],
                ["Jing Yuan","Dan Heng","Tingyun","Natasha"],
                ["Jing Yuan","Dan Heng","Welt","Gepard"],
                ["Jing Yuan","Himeko","Natasha","Fire Trailblazer"],
                ["Jing Yuan","Seele","Silver Wolf","Bailu"],
                ["Jing Yuan","Seele","Natasha","Fire Trailblazer"],
                ["Jing Yuan","Serval","Tingyun","Natasha"],
                ["Jing Yuan","Serval","Tingyun","Natasha"],
                ["Jing Yuan","Sushang","Tingyun","Gepard"],
                ["Jing Yuan","Sushang","Tingyun","Natasha"]
            ],
            "Phys MC Dual Carry": [
                ["Physical Trailblazer","Clara","Welt","Bailu"]
            ],
            "Qingque Hypercarry": [
                ["Qingque","Bronya","Tingyun","Gepard"],
                ["Qingque","Silver Wolf","Asta","Bailu"],
                ["Qingque","Silver Wolf","Asta","Fire Trailblazer"],
                ["Qingque","Silver Wolf","Bailu","Fire Trailblazer"],
                ["Qingque","Silver Wolf","Natasha","Fire Trailblazer"],
                ["Qingque","Welt","Silver Wolf","Gepard"]
            ],
            "Qingque Dual Carry": [
                ["Qingque","Clara","Natasha","March 7th"],
                ["Qingque","Clara","Silver Wolf","Natasha"]
            ],
            "Sampo Hypercarry": [
                ["Sampo","Pela","Natasha","Fire Trailblazer"],
                ["Sampo","Silver Wolf","Pela","Bailu"]
            ],
            "Seele Hypercarry": [
                ["Seele","Asta","Bailu","Fire Trailblazer"],
                ["Seele","Asta","Bronya","Bailu"],
                ["Seele","Asta","Bronya","Fire Trailblazer"],
                ["Seele","Asta","Bronya","Natasha"],
                ["Seele","Asta","March 7th","Fire Trailblazer"],
                ["Seele","Asta","Natasha","Fire Trailblazer"],
                ["Seele","Asta","Tingyun","Bailu"],
                ["Seele","Asta","Tingyun","Fire Trailblazer"],
                ["Seele","Asta","Tingyun","Gepard"],
                ["Seele","Asta","Tingyun","Natasha"],
                ["Seele","Asta","Bailu","March 7th"],
                ["Seele","Asta","Bronya","Gepard"],
                ["Seele","Asta","Bronya","March 7th"],
                ["Seele","Asta","Bronya","Tingyun"],
                ["Seele","Asta","Gepard","Fire Trailblazer"],
                ["Seele","Asta","Natasha","Gepard"],
                ["Seele","Asta","Natasha","March 7th"],
                ["Seele","Asta","Pela","Gepard"],
                ["Seele","Asta","Tingyun","March 7th"],
                ["Seele","Bronya","Bailu","Gepard"],
                ["Seele","Bronya","March 7th","Gepard"],
                ["Seele","Bronya","Pela","Bailu"],
                ["Seele","Bronya","Pela","Fire Trailblazer"],
                ["Seele","Bronya","Pela","Gepard"],
                ["Seele","Bronya","Tingyun","March 7th"],
                ["Seele","Bronya","Bailu","Fire Trailblazer"],
                ["Seele","Bronya","Bailu","March 7th"],
                ["Seele","Bronya","Gepard","Fire Trailblazer"],
                ["Seele","Bronya","March 7th","Fire Trailblazer"],
                ["Seele","Bronya","Natasha","Fire Trailblazer"],
                ["Seele","Bronya","Natasha","Gepard"],
                ["Seele","Bronya","Natasha","March 7th"],
                ["Seele","Bronya","Pela","Natasha"],
                ["Seele","Bronya","Tingyun","Bailu"],
                ["Seele","Bronya","Tingyun","Fire Trailblazer"],
                ["Seele","Bronya","Tingyun","Gepard"],
                ["Seele","Bronya","Tingyun","Natasha"],
                ["Seele","Bronya","Luocha","Fire Trailblazer"],
                ["Seele","Bronya","Pela","March 7th"],
                ["Seele","Natasha","March 7th","Fire Trailblazer"],
                ["Seele","Pela","March 7th","Fire Trailblazer"],
                ["Seele","Pela","Tingyun","Fire Trailblazer"],
                ["Seele","Pela","Tingyun","Gepard"],
                ["Seele","Pela","Natasha","Fire Trailblazer"],
                ["Seele","Pela","Tingyun","Bailu"],
                ["Seele","Pela","Tingyun","March 7th"],
                ["Seele","Pela","Tingyun","Natasha"],
                ["Seele","Silver Wolf","Bronya","Luocha"],
                ["Seele","Silver Wolf","Luocha","Fire Trailblazer"],
                ["Seele","Silver Wolf","Yukong","Luocha"],
                ["Seele","Silver Wolf","Asta","Bailu"],
                ["Seele","Silver Wolf","Asta","March 7th"],
                ["Seele","Silver Wolf","Bailu","Gepard"],
                ["Seele","Silver Wolf","Bailu","March 7th"],
                ["Seele","Silver Wolf","Bronya","March 7th"],
                ["Seele","Silver Wolf","Gepard","Fire Trailblazer"],
                ["Seele","Silver Wolf","March 7th","Gepard"],
                ["Seele","Silver Wolf","Natasha","March 7th"],
                ["Seele","Silver Wolf","Pela","Bailu"],
                ["Seele","Silver Wolf","Pela","Fire Trailblazer"],
                ["Seele","Silver Wolf","Pela","March 7th"],
                ["Seele","Silver Wolf","Pela","Natasha"],
                ["Seele","Silver Wolf","Tingyun","March 7th"],
                ["Seele","Silver Wolf","Asta","Fire Trailblazer"],
                ["Seele","Silver Wolf","Asta","Gepard"],
                ["Seele","Silver Wolf","Asta","Natasha"],
                ["Seele","Silver Wolf","Bailu","Fire Trailblazer"],
                ["Seele","Silver Wolf","Bronya","Bailu"],
                ["Seele","Silver Wolf","Bronya","Fire Trailblazer"],
                ["Seele","Silver Wolf","Bronya","Gepard"],
                ["Seele","Silver Wolf","Bronya","Natasha"],
                ["Seele","Silver Wolf","March 7th","Fire Trailblazer"],
                ["Seele","Silver Wolf","Natasha","Fire Trailblazer"],
                ["Seele","Silver Wolf","Natasha","Gepard"],
                ["Seele","Silver Wolf","Pela","Gepard"],
                ["Seele","Silver Wolf","Tingyun","Bailu"],
                ["Seele","Silver Wolf","Tingyun","Fire Trailblazer"],
                ["Seele","Silver Wolf","Tingyun","Gepard"],
                ["Seele","Silver Wolf","Tingyun","Natasha"],
                ["Seele","Tingyun","Bailu","Fire Trailblazer"],
                ["Seele","Tingyun","Bailu","March 7th"],
                ["Seele","Tingyun","Gepard","Fire Trailblazer"],
                ["Seele","Tingyun","March 7th","Fire Trailblazer"],
                ["Seele","Tingyun","Natasha","Fire Trailblazer"],
                ["Seele","Tingyun","Natasha","Gepard"],
                ["Seele","Tingyun","Natasha","March 7th"],
                ["Seele","Tingyun","March 7th","Gepard"],
                ["Seele","Welt","Bronya","Bailu"],
                ["Seele","Welt","Bronya","Gepard"],
                ["Seele","Welt","Natasha","March 7th"],
                ["Seele","Welt","Silver Wolf","Bailu"],
                ["Seele","Welt","Silver Wolf","Fire Trailblazer"],
                ["Seele","Welt","Silver Wolf","Gepard"],
                ["Seele","Welt","Silver Wolf","Bronya"],
                ["Seele","Welt","Silver Wolf","Luocha"],
                ["Seele","Welt","Tingyun","Bailu"],
                ["Seele","Welt","Tingyun","Gepard"],
                ["Seele","Welt","Tingyun","Natasha"],
                ["Seele","Welt","Asta","Fire Trailblazer"],
                ["Seele","Welt","Bronya","Fire Trailblazer"],
                ["Seele","Welt","Bronya","March 7th"],
                ["Seele","Welt","Bronya","Natasha"],
                ["Seele","Welt","Gepard","Fire Trailblazer"],
                ["Seele","Welt","March 7th","Fire Trailblazer"],
                ["Seele","Welt","Natasha","Fire Trailblazer"],
                ["Seele","Welt","Natasha","Gepard"],
                ["Seele","Welt","Pela","Fire Trailblazer"],
                ["Seele","Welt","Silver Wolf","Natasha"],
                ["Seele","Welt","Tingyun","Fire Trailblazer"]
            ],
            "Seele Dual Carry": [
                ["Seele","Clara","Bronya","Bailu"],
                ["Seele","Clara","Bronya","March 7th"],
                ["Seele","Clara","Bronya","Natasha"],
                ["Seele","Clara","Natasha","March 7th"],
                ["Seele","Clara","Pela","Natasha"],
                ["Seele","Clara","Silver Wolf","Natasha"],
                ["Seele","Clara","Silver Wolf","Luocha"],
                ["Seele","Clara","Tingyun","Natasha"],
                ["Seele","Clara","Asta","Fire Trailblazer"],
                ["Seele","Clara","Asta","Natasha"],
                ["Seele","Clara","Bronya","Fire Trailblazer"],
                ["Seele","Clara","Bronya","Gepard"],
                ["Seele","Clara","March 7th","Fire Trailblazer"],
                ["Seele","Clara","Natasha","Fire Trailblazer"],
                ["Seele","Clara","Natasha","Gepard"],
                ["Seele","Clara","Silver Wolf","Bailu"],
                ["Seele","Clara","Silver Wolf","Fire Trailblazer"],
                ["Seele","Clara","Silver Wolf","Gepard"],
                ["Seele","Clara","Silver Wolf","March 7th"],
                ["Seele","Clara","Tingyun","Bailu"],
                ["Seele","Clara","Tingyun","March 7th"],
                ["Seele","Dan Heng","Silver Wolf","Natasha"],
                ["Seele","Dan Heng","Natasha","Fire Trailblazer"],
                ["Seele","Herta","Asta","Bailu"],
                ["Seele","Himeko","Bronya","Gepard"],
                ["Seele","Himeko","Silver Wolf","Bailu"],
                ["Seele","Himeko","Silver Wolf","Fire Trailblazer"],
                ["Seele","Himeko","Silver Wolf","Natasha"],
                ["Seele","Himeko","Tingyun","Bailu"],
                ["Seele","Himeko","Natasha","Fire Trailblazer"],
                ["Seele","Sampo","March 7th","Fire Trailblazer"],
                ["Seele","Sampo","Natasha","Fire Trailblazer"],
                ["Seele","Sampo","Silver Wolf","Fire Trailblazer"],
                ["Seele","Physical Trailblazer","Natasha","March 7th"],
                ["Seele","Physical Trailblazer","Silver Wolf","Natasha"],
                ["Seele","Serval","Natasha","Fire Trailblazer"],
                ["Seele","Serval","Silver Wolf","Bailu"],
                ["Seele","Serval","Tingyun","Bailu"],
                ["Seele","Sushang","March 7th","Fire Trailblazer"],
                ["Seele","Sushang","Silver Wolf","Natasha"],
                ["Seele","Sushang","Tingyun","Fire Trailblazer"],
                ["Seele","Sushang","Tingyun","Natasha"],
                ["Seele","Sushang","Bronya","Natasha"],
                ["Seele","Sushang","Natasha","Fire Trailblazer"]
            ],
            "Serval Hypercarry": [
                ["Serval","Asta","Natasha","Fire Trailblazer"],
                ["Serval","Arlan","Bronya","Bailu"],
                ["Serval","Pela","Tingyun","Natasha"],
                ["Serval","Silver Wolf","Bailu","March 7th"],
                ["Serval","Silver Wolf","Natasha","Fire Trailblazer"],
                ["Serval","Silver Wolf","Natasha","Gepard"],
                ["Serval","Tingyun","Bailu","March 7th"],
                ["Serval","Tingyun","Natasha","Fire Trailblazer"],
                ["Serval","Tingyun","Natasha","Gepard"],
                ["Serval","Tingyun","Bailu","Fire Trailblazer"],
                ["Serval","Welt","Tingyun","Gepard"]
            ],
            "Silver Wolf Hypercarry": [
                ["Silver Wolf","Bronya","Natasha","Fire Trailblazer"],
                ["Silver Wolf","Pela","Natasha","Gepard"]
            ],
            "Sushang Hypercarry": [
                ["Sushang","Asta","Natasha","Fire Trailblazer"],
                ["Sushang","Asta","Tingyun","Natasha"],
                ["Sushang","Bronya","Natasha","Gepard"],
                ["Sushang","Bronya","Pela","March 7th"],
                ["Sushang","Bronya","March 7th","Gepard"],
                ["Sushang","Bronya","Natasha","Fire Trailblazer"],
                ["Sushang","Pela","March 7th","Fire Trailblazer"],
                ["Sushang","Pela","Natasha","Gepard"],
                ["Sushang","Silver Wolf","Natasha","Fire Trailblazer"],
                ["Sushang","Silver Wolf","Natasha","Gepard"],
                ["Sushang","Silver Wolf","Pela","March 7th"],
                ["Sushang","Silver Wolf","Pela","Gepard"],
                ["Sushang","Silver Wolf","Bronya","Bailu"],
                ["Sushang","Silver Wolf","Bronya","Natasha"],
                ["Sushang","Silver Wolf","Natasha","March 7th"],
                ["Sushang","Tingyun","Bailu","Fire Trailblazer"],
                ["Sushang","Tingyun","Natasha","Gepard"],
                ["Sushang","Tingyun","Natasha","Fire Trailblazer"],
                ["Sushang","Tingyun","Natasha","March 7th"],
                ["Sushang","Welt","March 7th","Fire Trailblazer"],
                ["Sushang","Welt","Pela","Natasha"],
                ["Sushang","Welt","Silver Wolf","Bailu"],
                ["Sushang","Welt","Silver Wolf","Gepard"],
                ["Sushang","Welt","Silver Wolf","Natasha"],
                ["Sushang","Welt","Tingyun","Natasha"],
                ["Sushang","Welt","Natasha","Fire Trailblazer"],
                ["Sushang","Welt","Natasha","March 7th"]
            ],
            "Sushang Dual Carry": [
                ["Sushang","Clara","Natasha","March 7th"],
                ["Sushang","Clara","Natasha","Fire Trailblazer"],
                ["Sushang","Clara","Silver Wolf","Bailu"],
                ["Sushang","Clara","Tingyun","Natasha"],
                ["Sushang","Jing Yuan","Tingyun","Gepard"],
                ["Sushang","Jing Yuan","Tingyun","Natasha"],
                ["Sushang","Qingque","Silver Wolf","Natasha"],
                ["Sushang","Qingque","Natasha","Fire Trailblazer"],
                ["Sushang","Seele","Bronya","Natasha"],
                ["Sushang","Seele","Natasha","Fire Trailblazer"],
                ["Sushang","Serval","Natasha","Fire Trailblazer"],
                ["Sushang","Serval","Bailu","Fire Trailblazer"],
                ["Sushang","Serval","March 7th","Fire Trailblazer"],
                ["Sushang","Serval","Pela","Gepard"],
                ["Sushang","Serval","Tingyun","Natasha"],
                ["Sushang","Serval","Welt","Natasha"]
            ],
            "Welt Hypercarry": [
                ["Welt","Asta","Tingyun","Gepard"],
                ["Welt","Bronya","Natasha","Fire Trailblazer"],
                ["Welt","Pela","Natasha","Fire Trailblazer"],
                ["Welt","Pela","Natasha","March 7th"],
                ["Welt","Silver Wolf","Natasha","Gepard"],
                ["Welt","Silver Wolf","Natasha","Fire Trailblazer"],
                ["Welt","Silver Wolf","Pela","Bailu"],
                ["Welt","Silver Wolf","Tingyun","Bailu"]
            ],
            "Yanqing Hypercarry": [
                ["Yanqing","Asta","Natasha","Fire Trailblazer"],
                ["Yanqing","Bronya","Natasha","Gepard"],
                ["Yanqing","Bronya","Pela","Gepard"],
                ["Yanqing","Pela","March 7th","Fire Trailblazer"],
                ["Yanqing","Pela","Natasha","March 7th"],
                ["Yanqing","Pela","Natasha","Fire Trailblazer"],
                ["Yanqing","Pela","Tingyun","Gepard"],
                ["Yanqing","Silver Wolf","Asta","Gepard"],
                ["Yanqing","Silver Wolf","Bronya","Natasha"],
                ["Yanqing","Silver Wolf","March 7th","Fire Trailblazer"],
                ["Yanqing","Silver Wolf","Natasha","Fire Trailblazer"],
                ["Yanqing","Silver Wolf","Natasha","Gepard"],
                ["Yanqing","Silver Wolf","Natasha","March 7th"],
                ["Yanqing","Silver Wolf","Pela","Natasha"],
                ["Yanqing","Silver Wolf","Tingyun","Gepard"],
                ["Yanqing","Tingyun","Bailu","Gepard"],
                ["Yanqing","Tingyun","Natasha","Gepard"],
                ["Yanqing","Tingyun","Natasha","March 7th"],
                ["Yanqing","Tingyun","Bailu","Fire Trailblazer"],
                ["Yanqing","Tingyun","Natasha","Fire Trailblazer"],
                ["Yanqing","Welt","March 7th","Fire Trailblazer"],
                ["Yanqing","Welt","Natasha","Fire Trailblazer"],
                ["Yanqing","Welt","Natasha","March 7th"],
                ["Yanqing","Welt","Pela","Gepard"],
                ["Yanqing","Welt","Silver Wolf","Bailu"],
                ["Yanqing","Welt","Silver Wolf","Gepard"],
                ["Yanqing","Welt","Silver Wolf","Natasha"],
                ["Yanqing","Welt","Tingyun","Bailu"],
                ["Yanqing","Welt","Tingyun","Gepard"],
                ["Yanqing","Welt","Tingyun","March 7th"],
                ["Yanqing","Welt","Tingyun","Natasha"],
                ["Yanqing","Welt","Natasha","Gepard"]
            ],
            "Yanqing Dual Carry": [
                ["Yanqing","Clara","Silver Wolf","March 7th"],
                ["Yanqing","Clara","Silver Wolf","Natasha"],
                ["Yanqing","Clara","Natasha","March 7th"],
                ["Yanqing","Clara","Pela","March 7th"],
                ["Yanqing","Clara","Pela","Natasha"],
                ["Yanqing","Clara","Tingyun","March 7th"],
                ["Yanqing","Clara","Tingyun","Natasha"],
                ["Yanqing","Jing Yuan","Tingyun","Gepard"],
                ["Yanqing","Jing Yuan","Silver Wolf","Gepard"],
                ["Yanqing","Jing Yuan","Tingyun","Bailu"],
                ["Yanqing","Seele","Natasha","Fire Trailblazer"],
                ["Yanqing","Seele","Tingyun","Gepard"],
                ["Yanqing","Seele","Tingyun","Natasha"],
                ["Yanqing","Serval","Silver Wolf","Gepard"],
                ["Yanqing","Serval","Natasha","Fire Trailblazer"],
                ["Yanqing","Sushang","Natasha","Fire Trailblazer"]
            ],
            "Faux-Mono Lightning": [
                ["Jing Yuan","Silver Wolf","Tingyun","Bailu"],
                ["Serval","Silver Wolf","Tingyun","Bailu"]
            ],
            "Faux-Mono Fire": [
                ["Himeko","Silver Wolf","Asta","Fire Trailblazer"]
            ],
            "Faux-Mono Physical": [
                ["Sushang","Clara","Silver Wolf","Natasha"]
            ],
            "Faux-Mono Ice": [
                ["Yanqing","Silver Wolf","Pela","Gepard"],
                ["Yanqing","Silver Wolf","Pela","March 7th"]
            ]
        }
        alt_comp_names = {}
        self.comp_name = "-"
        self.alt_comp_name = "-"
        for comp_name in comp_names:
            if characters in comp_names[comp_name]:
                self.comp_name = comp_name
                break
        for alt_comp_name in alt_comp_names:
            if characters in alt_comp_names[alt_comp_name]:
                self.alt_comp_name = alt_comp_name
                if info_char:
                    self.comp_name = alt_comp_name
                break

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
