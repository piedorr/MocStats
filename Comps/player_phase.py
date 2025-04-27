import json

from composition import Composition

# Set class constants in initialization
# Load the list of characters from their file
with open("../data/characters.json") as char_file:
    CHARACTERS: dict[str, dict[str, str | int | None]] = json.load(char_file)
with open("../data/relic_affixes.json") as relic_file:
    articombinations: dict[str, dict[str, str | int | None]] = json.load(relic_file)


class OwnedChars:
    def __init__(
        self,
        level: str,
        cons: str,
        weapon: str,
        element: str,
        artifacts: str,
        planars: str,
    ) -> None:
        self.level: int = int(level)
        self.cons: int = int(cons)
        self.weapon: str = weapon
        self.element: str = element
        self.artifacts: str = artifacts
        self.planars: str = planars


class PlayerPhase:
    """
    An object that stores information about a player on a phase. Has:
    player: a string for this player.
    phase: a string for the phase.
    chambers: a string->composition dict for the comps they used.
    owned: a string->dict (character) dict for the characters they owned:
        None if they don't own the character.
    """

    def __init__(self, player: str, phase: str) -> None:
        """
        Composition constructor. Takes in:
        A player, as a string
        A phase, as a string
        """
        self.player = player
        self.phase = phase
        self.chambers: dict[str, Composition] = {}
        self.owned: dict[str, OwnedChars] = {}

    def add_character(
        self,
        name: str,
        level: str,
        cons: str,
        weapon: str,
        element: str,
        artifacts: str,
        planars: str,
    ) -> None:
        """
        Adds in a character to the owned characters dict.
        """
        for arti in articombinations:
            articom = []
            comarti = []
            for artiset in articombinations[arti]:
                articom.append(artiset + ", ")
                comarti.append(", " + artiset)
            for i in articom:
                if i in artifacts:
                    artifacts = artifacts.replace(i, arti + ", ")
            for i in comarti:
                if i in artifacts:
                    artifacts = artifacts.replace(i, "")
                    artifacts = arti + ", " + artifacts

        self.owned[name] = OwnedChars(level, cons, weapon, element, artifacts, planars)

    def add_comp(self, composition: Composition) -> None:
        """Adds a composition to the chambers dict."""
        if composition.phase != self.phase or composition.player != self.player:
            return
        if composition.room in self.chambers:
            return
        self.chambers[composition.room] = composition

    def chars_owned(self, characters: list[str]) -> bool:
        """Takes in an iter of character names,
        and returns true if the player owned them all."""
        for char in characters:
            if not self.owned[char]:
                return False
        return True

    def chars_used(self, characters: list[str]) -> bool:
        """Takes in an iter of character names,
        and returns true if the player used them all."""
        if not self.chars_owned(characters):
            return False
        for char in characters:
            if not self.char_used(char):
                return False
        return True

    def no_chars_owned(self, characters: list[str]) -> bool:
        """Takes in a list of character names,
        and returns true if the player owns none of them."""
        for char in characters:
            if self.owned[char]:
                return False
        return True

    def no_chars_used(self, characters: list[str]) -> bool:
        """Takes in an iter of character names,
        and returns true if the player used none of them."""
        for char in characters:
            if self.char_used(char):
                return False
        return True

    def char_used(self, character: str) -> bool:
        """Takes in a character name, and returns true if the player used them."""
        if not self.owned[character]:
            return False
        for chamber in self.chambers.values():
            if chamber.char_presence[character]:
                return True
        return False

    def chars_placement(self, characters: list[str]) -> None | dict:
        """
        Takes in an iter of character names, and if the player owns them all,
        returns a dict of which chambers each was used in.
        """
        if not self.chars_owned(characters):
            return None
        chambers = {
            "1-1": [],
            "1-2": [],
            "2-1": [],
            "2-2": [],
            "3-1": [],
            "3-2": [],
            "4-1": [],
            "4-2": [],
            "5-1": [],
            "5-2": [],
            "6-1": [],
            "6-2": [],
            "7-1": [],
            "7-2": [],
            "8-1": [],
            "8-2": [],
            "9-1": [],
            "9-2": [],
            "10-1": [],
            "10-2": [],
            "11-1": [],
            "11-2": [],
            "12-1": [],
            "12-2": [],
        }
        for char in characters:
            for chamber in chambers:
                if self.chambers[chamber].char_presence[char]:
                    chambers[chamber].append(char)
        return chambers

    # def floor_twelve(self):
    #     """Returns the comps used on floor 12."""
    #     return [c[1] for c in self.chambers.items() if c[0][:2] == "12"]
