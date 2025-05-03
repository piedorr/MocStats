from csv import writer as csvwriter
from statistics import mean, stdev
from warnings import filterwarnings

from comp_rates_config import (
    RECENT_PHASE,
    f2pOnly,
    load,
    pf_mode,
    sigWeaps,
    whaleOnly,
)
from line_profiler import profile
from pandas import read_csv  # type: ignore
from percentile import calculate_percentile
from player_phase import PlayerPhase
from scipy.stats import skew, trim_mean  # type: ignore

filterwarnings("ignore", category=RuntimeWarning)
ROOMS = (
    ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2"]
    if pf_mode
    else [
        "1-1",
        "1-2",
        "2-1",
        "2-2",
        "3-1",
        "3-2",
        "4-1",
        "4-2",
        "5-1",
        "5-2",
        "6-1",
        "6-2",
        "7-1",
        "7-2",
        "8-1",
        "8-2",
        "9-1",
        "9-2",
        "10-1",
        "10-2",
        "11-1",
        "11-2",
        "12-1",
        "12-2",
    ]
)
global gear_app_threshold
gear_app_threshold = 0
DEFAULT_VALUE: float = 0 if pf_mode else 99.99
DEFAULT_ROUND: int = 0 if pf_mode else 2
SINGLE_CHAMBER: list[str] = ["4-1", "4-2"] if pf_mode else ["12-1", "12-2"]
with open("../data/characters.json") as char_file:
    CHARACTERS: dict[str, dict[str, str | int | None]] = load(char_file)


class RoundApp:
    def __init__(self) -> None:
        self.app_flat: int = 0
        self.app: float = 0
        self.round_list = {str(i): list[int]() for i in range(1, 13)}
        self.round: float = 0


class CharApp(RoundApp):
    def __init__(self) -> None:
        super().__init__()
        self.app_flat_exclude: int = 0
        self.app_exclude: float = 0
        self.owned: int = 0
        self.std_dev_round: float = 0
        self.q1_round: float = 0
        self.weap_freq: dict[str, RoundApp] = {}
        self.arti_freq: dict[str, RoundApp] = {}
        self.planar_freq: dict[str, RoundApp] = {}
        self.cons_avg: float = 0
        self.sample: int = 0
        self.sample_app_flat: int = 0
        self.cons_freq = {i: RoundApp() for i in range(7)}


@profile
def appearances(
    users: dict[str, dict[str, PlayerPhase]],
    chambers: list[str] = ROOMS,
    offset: int = 1,
    info_char: bool = False,
) -> dict[int, dict[str, CharApp]]:
    app: dict[str, CharApp] = {}
    user_chars: dict[str, set[str]] = {}

    all_uids = set[str]()
    comp_error = False
    error_comps = []

    for char in CHARACTERS:
        user_chars[char] = set[str]()
        app[char] = CharApp()

    for user in users[RECENT_PHASE].values():
        for chamber in user.chambers:
            cur_chamber = list(str(chamber).split("-"))[0]
            if chamber not in chambers:
                continue
            all_uids.add(user.player)
            # foundchar = resetfind()
            whale_comp = False
            giga_whale = False
            f2p_comp = True
            sustainCount = 0

            for char in user.chambers[chamber].characters:
                if (
                    CHARACTERS[char]["availability"] == "Limited 5*"
                    and user.chambers[chamber].char_cons
                    and user.chambers[chamber].char_cons[char] > 0
                ):
                    whale_comp = True
                    if user.chambers[chamber].char_cons[char] > 2:
                        giga_whale = True
                if char in user.owned and user.owned[char].weapon in sigWeaps:
                    f2p_comp = False
                if CHARACTERS[char]["role"] == "Sustain":
                    sustainCount += 1

            if not (pf_mode):
                side_chamber = chamber[:-1] + ("2" if chamber[-1] == "1" else "1")
                for char in user.chambers[side_chamber].characters:
                    if (
                        CHARACTERS[char]["availability"] == "Limited 5*"
                        and user.chambers[side_chamber].char_cons
                        and user.chambers[side_chamber].char_cons[char] > 0
                    ):
                        whale_comp = True
                        if user.chambers[side_chamber].char_cons[char] > 2:
                            giga_whale = True
                    if char in user.owned and user.owned[char].weapon in sigWeaps:
                        f2p_comp = False

            if (whaleOnly and (giga_whale or not whale_comp)) or (
                f2pOnly and (not f2p_comp or whale_comp)
            ):
                continue

            for char in user.chambers[chamber].characters:
                user_round = user.chambers[chamber].round_num
                # to print the amount of players using a character,
                # for char infographics
                if chambers == SINGLE_CHAMBER:
                    user_chars[char].add(user.player)

                app[char].app_flat += 1
                if whale_comp == whaleOnly and (not f2pOnly or f2p_comp):
                    app[char].app_flat_exclude += 1

                if (
                    whale_comp == whaleOnly
                    and (not f2pOnly or f2p_comp)
                    and (sustainCount <= 1)
                ):
                    app[char].round_list[cur_chamber].append(user_round)

                if user.chambers[chamber].char_cons and chambers == SINGLE_CHAMBER:
                    char_con = user.chambers[chamber].char_cons[char]
                    app[char].cons_freq[char_con].app_flat += 1
                    if sustainCount <= 1:
                        app[char].cons_freq[char_con].round_list[cur_chamber].append(
                            user_round
                        )
                    app[char].cons_avg += char_con
                if chambers != (SINGLE_CHAMBER):
                    continue
                if char not in user.owned:
                    continue

                user_char = user.owned[char]
                app[char].owned += 1

                if user_char.weapon != "":
                    if user_char.weapon not in app[char].weap_freq:
                        app[char].weap_freq[user_char.weapon] = RoundApp()
                    app[char].weap_freq[user_char.weapon].app_flat += 1
                    if not whale_comp and (sustainCount <= 1):
                        app[char].weap_freq[user_char.weapon].round_list[
                            cur_chamber
                        ].append(user_round)

                if user_char.artifacts != "":
                    if user_char.artifacts not in app[char].arti_freq:
                        app[char].arti_freq[user_char.artifacts] = RoundApp()
                    app[char].arti_freq[user_char.artifacts].app_flat += 1
                    if not whale_comp and (sustainCount <= 1):
                        app[char].arti_freq[user_char.artifacts].round_list[
                            cur_chamber
                        ].append(user_round)

                if user_char.planars != "":
                    if user_char.planars not in app[char].planar_freq:
                        app[char].planar_freq[user_char.planars] = RoundApp()
                    app[char].planar_freq[user_char.planars].app_flat += 1
                    if not whale_comp and (sustainCount <= 1):
                        app[char].planar_freq[user_char.planars].round_list[
                            cur_chamber
                        ].append(user_round)

    if comp_error:
        df_char = read_csv("../data/phase_characters.csv")
        df_spiral = read_csv("../data/compositions.csv")
        df_char = df_char[~df_char["uid"].isin(error_comps)]
        df_spiral = df_spiral[~df_spiral["uid"].isin(error_comps)]
        df_char.to_csv("phase_characters.csv", index=False)
        df_spiral.to_csv("compositions.csv", index=False)
        raise ValueError("There are missing comps from character data.")

    total = len(all_uids) / 100.0
    all_rounds: dict[str, dict[int, dict[int, int]]] = {}
    for char in app:
        all_rounds[char] = {}
        # # to print the amount of players using a character
        # print(str(char) + ": " + str(len(players_chars[char])))
        if total > 0:
            app[char].app = round(app[char].app_flat / total, 2)
            app[char].app_exclude = round(app[char].app_flat_exclude / total, 2)
        else:
            app[char].app = 0.00
        if app[char].app_flat_exclude >= 8:
            avg_round: list[float] = []
            std_dev_round: list[float] = []
            q1_round: list[float] = []
            uses_room: dict[int, int] = {}

            for room_num in range(1, 13):
                if room_num >= 10:
                    all_rounds[char][room_num] = {}
                    for i in range(41):
                        all_rounds[char][room_num][i] = 0
                if app[char].round_list[str(room_num)]:
                    if room_num >= 10:
                        for round_num_iter in app[char].round_list[str(room_num)]:
                            all_rounds[char][room_num][round_num_iter] += 1
                    uses_room[room_num] = len(app[char].round_list[str(room_num)])
                    if len(app[char].round_list[str(room_num)]) > 10:
                        std_dev_round.append(stdev(app[char].round_list[str(room_num)]))
                        q1_round.append(
                            calculate_percentile(
                                app[char].round_list[str(room_num)],
                                75 if pf_mode else 25,
                            )
                        )
                        skewness = skew(
                            app[char].round_list[str(room_num)],
                            axis=0,
                            bias=True,
                        )
                        if abs(skewness) > 0.8:
                            avg_round.append(
                                trim_mean(
                                    app[char].round_list[str(room_num)],
                                    0.25,
                                )
                            )
                        else:
                            avg_round.append(mean(app[char].round_list[str(room_num)]))
                    else:
                        std_dev_round.append(0)
                        q1_round.append(0)
                        avg_round.append(mean(app[char].round_list[str(room_num)]))

            is_count_cycles = True
            if not uses_room:
                is_count_cycles = False
            elif chambers == SINGLE_CHAMBER:
                app[char].sample_app_flat = uses_room[4 if pf_mode else 12]
                if len(uses_room) != len(chambers) / 2:
                    is_count_cycles = False
            for room_num in uses_room:
                if uses_room[room_num] < 10:
                    is_count_cycles = False
                    break

            # if avg_round:
            if is_count_cycles:
                app[char].round = round(mean(avg_round), DEFAULT_ROUND)
                app[char].std_dev_round = round(mean(std_dev_round), DEFAULT_ROUND)
                app[char].q1_round = round(mean(q1_round), DEFAULT_ROUND)
            else:
                app[char].round = DEFAULT_VALUE
                app[char].q1_round = DEFAULT_VALUE
        else:
            app[char].round = DEFAULT_VALUE
            app[char].q1_round = DEFAULT_VALUE

        app[char].sample = len(user_chars[char])

        if chambers != SINGLE_CHAMBER:
            continue
        # Calculate constellations
        if app[char].app_flat > 0:
            app[char].cons_avg = round(
                app[char].cons_avg / app[char].app_flat,
                2,
            )
        for cons in app[char].cons_freq:
            if app[char].cons_freq[cons].app_flat > 0:
                app[char].cons_freq[cons].app = round(
                    app[char].cons_freq[cons].app_flat / app[char].app_flat * 100, 2
                )
                avg_round = []
                for room_num in range(1, 13):
                    if app[char].cons_freq[cons].round_list[str(room_num)]:
                        if app[char].cons_freq[cons].app_flat > 10:
                            skewness = skew(
                                app[char].cons_freq[cons].round_list[str(room_num)],
                                axis=0,
                                bias=True,
                            )
                            if abs(skewness) > 0.8:
                                avg_round.append(
                                    trim_mean(
                                        app[char]
                                        .cons_freq[cons]
                                        .round_list[str(room_num)],
                                        0.25,
                                    )
                                )
                            else:
                                avg_round.append(
                                    mean(
                                        app[char]
                                        .cons_freq[cons]
                                        .round_list[str(room_num)]
                                    )
                                )
                        else:
                            avg_round.append(
                                mean(
                                    app[char].cons_freq[cons].round_list[str(room_num)]
                                )
                            )
                if avg_round:
                    app[char].cons_freq[cons].round = round(
                        mean(avg_round), DEFAULT_ROUND
                    )
                else:
                    app[char].cons_freq[cons].round = DEFAULT_VALUE
            else:
                app[char].cons_freq[cons].app = 0.00
                app[char].cons_freq[cons].round = DEFAULT_VALUE

        app_flat = app[char].owned / 100.0
        # Calculate weapons
        sorted_weapons = sorted(
            app[char].weap_freq.items(),
            key=lambda t: t[1].app_flat,
            reverse=True,
        )
        app[char].weap_freq = {k: v for k, v in sorted_weapons}
        for weapon in app[char].weap_freq:
            # If a gear appears >15 times, include it
            # Because there might be 1* gears
            # If it's for character infographic, include all gears
            if (
                app[char].weap_freq[weapon].app_flat > gear_app_threshold
                or info_char
                or (app[char].weap_freq[weapon].app_flat / app_flat) > 20
            ):
                app[char].weap_freq[weapon].app = round(
                    app[char].weap_freq[weapon].app_flat / app_flat,
                    2,
                )
                avg_round = []
                for room_num in range(1, 13):
                    if app[char].weap_freq[weapon].round_list[str(room_num)]:
                        if app[char].weap_freq[weapon].app_flat > 10:
                            skewness = skew(
                                app[char].weap_freq[weapon].round_list[str(room_num)],
                                axis=0,
                                bias=True,
                            )
                            if abs(skewness) > 0.8:
                                avg_round.append(
                                    trim_mean(
                                        app[char]
                                        .weap_freq[weapon]
                                        .round_list[str(room_num)],
                                        0.25,
                                    )
                                )
                            else:
                                avg_round.append(
                                    mean(
                                        app[char]
                                        .weap_freq[weapon]
                                        .round_list[str(room_num)]
                                    )
                                )
                        else:
                            avg_round.append(
                                mean(
                                    app[char]
                                    .weap_freq[weapon]
                                    .round_list[str(room_num)]
                                )
                            )
                if avg_round:
                    app[char].weap_freq[weapon].round = round(
                        mean(avg_round), DEFAULT_ROUND
                    )
                else:
                    app[char].weap_freq[weapon].round = DEFAULT_VALUE
            else:
                app[char].weap_freq[weapon].app = 0
                app[char].weap_freq[weapon].round = DEFAULT_VALUE

        # Remove flex artifacts
        if "Flex" in app[char].arti_freq:
            del app[char].arti_freq["Flex"]
        # Calculate artifacts
        sorted_arti = sorted(
            app[char].arti_freq.items(),
            key=lambda t: t[1].app_flat,
            reverse=True,
        )
        app[char].arti_freq = {k: v for k, v in sorted_arti}
        for arti in app[char].arti_freq:
            # If a gear appears >15 times, include it
            # Because there might be 1* gears
            # If it's for character infographic, include all gears
            if (
                app[char].arti_freq[arti].app_flat > gear_app_threshold or info_char
            ) and arti != "Flex":
                app[char].arti_freq[arti].app = round(
                    app[char].arti_freq[arti].app_flat / app_flat, 2
                )
                avg_round = []
                for room_num in range(1, 13):
                    if app[char].arti_freq[arti].round_list[str(room_num)]:
                        if app[char].arti_freq[arti].app_flat > 10:
                            skewness = skew(
                                app[char].arti_freq[arti].round_list[str(room_num)],
                                axis=0,
                                bias=True,
                            )
                            if abs(skewness) > 0.8:
                                avg_round.append(
                                    trim_mean(
                                        app[char]
                                        .arti_freq[arti]
                                        .round_list[str(room_num)],
                                        0.25,
                                    )
                                )
                            else:
                                avg_round.append(
                                    mean(
                                        app[char]
                                        .arti_freq[arti]
                                        .round_list[str(room_num)]
                                    )
                                )
                        else:
                            avg_round.append(
                                mean(
                                    app[char].arti_freq[arti].round_list[str(room_num)]
                                )
                            )
                if avg_round:
                    app[char].arti_freq[arti].round = round(
                        mean(avg_round), DEFAULT_ROUND
                    )
                else:
                    app[char].arti_freq[arti].round = DEFAULT_VALUE
            else:
                app[char].arti_freq[arti].app = 0
                app[char].arti_freq[arti].round = DEFAULT_VALUE

        # Remove flex artifacts
        if "Flex" in app[char].planar_freq:
            del app[char].planar_freq["Flex"]
        # Calculate artifacts
        sorted_planars = sorted(
            app[char].planar_freq.items(),
            key=lambda t: t[1].app_flat,
            reverse=True,
        )
        app[char].planar_freq = {k: v for k, v in sorted_planars}
        for planar in app[char].planar_freq:
            # If a gear appears >15 times, include it
            # Because there might be 1* gears
            # If it's for character infographic, include all gears
            if (
                app[char].planar_freq[planar].app_flat > gear_app_threshold or info_char
            ) and planar != "Flex":
                app[char].planar_freq[planar].app = round(
                    app[char].planar_freq[planar].app_flat / app_flat,
                    2,
                )
                avg_round = []
                for room_num in range(1, 13):
                    if app[char].planar_freq[planar].round_list[str(room_num)]:
                        if app[char].planar_freq[planar].app_flat > 1:
                            skewness = skew(
                                app[char].planar_freq[planar].round_list[str(room_num)],
                                axis=0,
                                bias=True,
                            )
                            if abs(skewness) > 0.8:
                                avg_round.append(
                                    trim_mean(
                                        app[char]
                                        .planar_freq[planar]
                                        .round_list[str(room_num)],
                                        0.25,
                                    )
                                )
                            else:
                                avg_round.append(
                                    mean(
                                        app[char]
                                        .planar_freq[planar]
                                        .round_list[str(room_num)]
                                    )
                                )
                        else:
                            avg_round.append(
                                mean(
                                    app[char]
                                    .planar_freq[planar]
                                    .round_list[str(room_num)]
                                )
                            )
                if avg_round:
                    app[char].planar_freq[planar].round = round(
                        mean(avg_round), DEFAULT_ROUND
                    )
                else:
                    app[char].planar_freq[planar].round = DEFAULT_VALUE
            else:
                app[char].planar_freq[planar].app = 0
                app[char].planar_freq[planar].round = DEFAULT_VALUE
    if chambers == ["12-1", "12-2"]:
        csv_writer = csvwriter(open("../char_results/all_rounds.csv", "w", newline=""))
        for char in all_rounds:
            for room_num in all_rounds[char]:
                for round_num_iter in all_rounds[char][room_num]:
                    csv_writer.writerow(
                        [
                            "2/21/2024",
                            char,
                            room_num,
                            round_num_iter,
                            all_rounds[char][room_num][round_num_iter],
                        ]
                    )
    return {4: app}


class CharUsageData(CharApp):
    def __init__(self, char_app: CharApp, char: str) -> None:
        super().__init__()
        self.__dict__.update(char_app.__dict__)
        self.usage = 0
        self.diff = "-"
        self.diff_rounds = "-"
        self.role = str(CHARACTERS[char]["role"])
        self.rarity = str(CHARACTERS[char]["availability"])
        self.weapons: dict[str, RoundApp] = {}
        self.weapons_round: dict[str, RoundApp] = {}
        self.artifacts: dict[str, RoundApp] = {}
        self.artifacts_round: dict[str, RoundApp] = {}
        self.planars: dict[str, RoundApp] = {}
        self.cons_usage = {i: dict[str, str]() for i in range(7)}
        self.rank: int


@profile
def usages(
    app: dict[int, dict[str, CharApp]],
    past_phase: str,
    chambers: list[str] = ROOMS,
) -> dict[int, dict[str, CharUsageData]]:
    uses: dict[int, dict[str, CharUsageData]] = {}
    past_usage: dict[str, dict[str, dict[str, dict[str, float]]]] = {}
    past_rounds: dict[str, dict[str, dict[str, dict[str, float]]]] = {}

    try:
        with open("../char_results/" + past_phase + "/appearance.json") as stats:
            past_usage = load(stats)
        with open("../char_results/" + past_phase + "/rounds.json") as stats:
            past_rounds = load(stats)
    except Exception:
        pass

    for star_num in app:
        uses[star_num] = {}
        rates: list[float] = []
        for char in app[4]:
            uses[star_num][char] = CharUsageData(app[4][char], char)
            rates.append(uses[star_num][char].app)

            if chambers == SINGLE_CHAMBER:
                stage = "all"
            else:
                stage = chambers[0]

            if char in past_usage[stage][str(star_num)]:
                uses[star_num][char].diff = str(
                    round(
                        app[4][char].app
                        - past_usage[stage][str(star_num)][char]["app"],
                        2,
                    )
                )

            if char in past_rounds[stage][str(star_num)]:
                uses[star_num][char].diff_rounds = str(
                    round(
                        app[4][char].round
                        - past_rounds[stage][str(star_num)][char]["round"],
                        2,
                    )
                )

            for i in range(7):
                uses[star_num][char].cons_usage[i] = {
                    "app": "-",
                    "own": "-",
                    "usage": "-",
                }

            if chambers != SINGLE_CHAMBER or star_num != 4:
                continue

            weapons = list(app[4][char].weap_freq)
            for i in range(len(weapons)):
                uses[star_num][char].weapons[weapons[i]] = app[4][char].weap_freq[
                    weapons[i]
                ]

            artifacts = list(app[4][char].arti_freq)
            for i in range(len(artifacts)):
                uses[star_num][char].artifacts[artifacts[i]] = app[4][char].arti_freq[
                    artifacts[i]
                ]

            planars = list(app[4][char].planar_freq)
            for i in range(len(planars)):
                uses[star_num][char].planars[planars[i]] = app[4][char].planar_freq[
                    planars[i]
                ]

            for i in range(7):
                uses[star_num][char].cons_usage[i]["app"] = str(
                    app[4][char].cons_freq[i].app
                )
                uses[star_num][char].cons_usage[i]["round"] = str(
                    app[4][char].cons_freq[i].round
                )
        rates.sort(reverse=True)
        for char in uses[star_num]:
            # if owns[star_num][char]["flat"] > 0:
            uses[star_num][char].rank = rates.index(uses[star_num][char].app) + 1
    return uses
