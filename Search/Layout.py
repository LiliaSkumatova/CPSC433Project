"""
This class represents the environment which will store user input, configuration, and search parameters.
It acts as a central repository for data such as schedules, slots, constraints, and preferences, which are
necessary for the scheduling algorithm to function.
"""
import logging
import pprint
from contextlib import redirect_stdout

from Enumerations import ActivityType, Weekday
from Games import Game
from Practices import Practice
from Games import GameSlot
from Practices import PracticeSlot

class Layout:
    # Counter for the number of leaves encountered during the search
    leaves_encountered = 0

    # Pre-parser initialization variables (these are set before parsing input files)
    SPECIAL_BOOKINGS = {
        # Assign special activities (like practices) directly to specific time slots
        "CMSA U12T1S": (ActivityType.PRACTICE, Weekday.TU, "18:00"),
        "CMSA U13T1S": (ActivityType.PRACTICE, Weekday.TU, "18:00")
    }

    # Mapping slot IDs to corresponding slot objects
    SLOT_ID_TO_OBJ = {}
    PRACTICE_SLOT_ID_TO_OBJ = {}
    GAME_SLOT_ID_TO_OBJ = {}

    # Penalty values to evaluate the quality of schedules
    W_MINFILLED = 0
    W_PREF = 0
    W_PAIR = 0
    W_SECDIFF = 0
    PEN_GAMEMIN = 0
    PEN_PRACTICEMIN = 0
    PEN_NOTPAIRED = 0
    PEN_SECTION = 0

    # During-parser initialization variables
    NAME = ""  # Name of the schedule or environment
    ACTIVITY_ID_TO_OBJ = {}  # Maps activity IDs to their instances
    GAME_ID_TO_OBJ = {}  # Maps game IDs to game instances
    PRACTICE_ID_TO_OBJ = {}  # Maps practice IDs to practice instances
    NOT_COMPATIBLE = {}  # Stores incompatible activities
    UNWANTED = {}  # Activities that cannot be assigned to specific slots
    PREFERENCES = {}  # Slot preferences for activities
    PAIR = {}  # Pairs of activities that must be scheduled together
    PARTASSIGN = {}  # Activities with predefined slot assignments

    # Post-parser initialization variables
    ACTIVITY_IDS = set()  # Set of all activity IDs
    GAME_IDS = set()  # Set of game IDs
    PRACTICE_IDS = set()  # Set of practice IDs
    ALL_SLOT_IDS = set()  # Set of all slot IDs
    PRACTICE_SLOT_IDS = set()  # Set of practice slot IDs
    GAME_SLOT_IDS = set()  # Set of game slot IDs

    # Slot categorization by day and type
    MO_G_SLOTS_IDS = set()
    TU_G_SLOT_IDS = set()
    MO_P_SLOTS_IDS = set()
    TU_P_SLOT_IDS = set()
    FR_P_SLOT_IDS = set()


    @staticmethod
    def display_parsed_data():
        """
        Displays parsed data for debugging and verification purposes.
        Prints game IDs, practice IDs, and constraints such as incompatibilities and preferences.
        """
        print("Game IDs: " + str(Layout.GAME_IDS))
        print("Practice IDs: " + str(Layout.PRACTICE_IDS))
        print("\nNot compatible: " + str(Layout.NOT_COMPATIBLE))
        print("\nUnwanted: " + str(Layout.UNWANTED))
        print("\nPreferences: " + str(Layout.PREFERENCES))
        print("\nPair: " + str(Layout.PAIR))
        print("\nPartial assignments: " + str(Layout.PARTASSIGN))


    @staticmethod
    def pre_parser_initialization():

        MO_GAME_SLOT_SHORTCUTS = [
            "8:00-9:00", "9:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00",
            "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00", "17:00-18:00",
            "18:00-19:00", "19:00-20:00", "20:00-21:00"
        ]
        TU_GAME_SLOT_SHORTCUTS = [
            "8:00-9:30", "9:30-11:00", "11:00-12:30", "12:30-14:00", "14:00-15:30",
            "15:30-17:00", "17:00-18:30", "18:30-20:00"
        ]
        MO_PRACTICE_SLOT_SHORTCUTS = [
            "8:00-9:00", "9:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00",
            "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00", "17:00-18:00",
            "18:00-19:00", "19:00-20:00", "20:00-21:00"
        ]
        TU_PRACTICE_SLOT_SHORTCUTS = [
            "8:00-9:00", "9:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-13:00",
            "13:00-14:00", "14:00-15:00", "15:00-16:00", "16:00-17:00", "17:00-18:00",
            "18:00-19:00", "19:00-20:00", "20:00-21:00"
        ]
        FR_PRACTICE_SLOT_SHORTCUTS = [
            "8:00-10:00", "10:00-12:00", "12:00-14:00", "14:00-16:00", "16:00-18:00",
            "18:00-20:00"
        ]


        def time_str_to_int(time_str: str) -> int:
            try:
                hours, mins = (int(e) for e in time_str.strip().split(":"))
            except ValueError:
                raise ValueError(f"invalid time string: {time_str}")

            return hours * 60 + mins


        def decide_if_evening_slot(time_str: str) -> bool:
            time_int = time_str_to_int(time_str)
            return time_int >= 1080 # 18:00 - 18 * 60 = 1080


        def params(shortcut: str):
            start_time, end_time = shortcut.split("-")
            is_evening_slot = decide_if_evening_slot(start_time)
            return start_time, end_time, is_evening_slot, 0, 0

        MO_GAME_SLOTS = [GameSlot(Weekday.MO, *params(shortcut)) for shortcut in MO_GAME_SLOT_SHORTCUTS]
        TU_GAME_SLOTS = [GameSlot(Weekday.TU, *params(shortcut)) for shortcut in TU_GAME_SLOT_SHORTCUTS]
        MO_PRACTICE_SLOTS = [PracticeSlot(Weekday.MO, *params(shortcut)) for shortcut in MO_PRACTICE_SLOT_SHORTCUTS]
        TU_PRACTICE_SLOTS = [PracticeSlot(Weekday.TU, *params(shortcut)) for shortcut in TU_PRACTICE_SLOT_SHORTCUTS]
        FR_PRACTICE_SLOTS = [PracticeSlot(Weekday.FR, *params(shortcut)) for shortcut in FR_PRACTICE_SLOT_SHORTCUTS]

        ACTIVITY_SLOTS = MO_GAME_SLOTS + TU_GAME_SLOTS + MO_PRACTICE_SLOTS + TU_PRACTICE_SLOTS + FR_PRACTICE_SLOTS
        Layout.SLOT_ID_TO_OBJ = {slot.id: slot for slot in ACTIVITY_SLOTS}

        Layout.GAME_SLOT_ID_TO_OBJ = {slot_id: Layout.SLOT_ID_TO_OBJ[slot_id] for slot_id in
                                      filter(lambda id: id[0] == ActivityType.GAME, Layout.SLOT_ID_TO_OBJ)
                                      }

        Layout.PRACTICE_SLOT_ID_TO_OBJ = {slot_id: Layout.SLOT_ID_TO_OBJ[slot_id] for slot_id in
                                          filter(lambda id: id[0] == ActivityType.PRACTICE, Layout.SLOT_ID_TO_OBJ)
                                          }

        Layout.ALL_SLOT_IDS = {slot_id for slot_id in Layout.SLOT_ID_TO_OBJ}
        Layout.PRACTICE_SLOT_IDS = {slot_id for slot_id in Layout.PRACTICE_SLOT_ID_TO_OBJ}
        Layout.GAME_SLOT_IDS = {slot_id for slot_id in Layout.GAME_SLOT_ID_TO_OBJ}

        Layout.MO_G_SLOTS_IDS = {slot_id for slot_id in
                                 filter(lambda id: id[0] == ActivityType.GAME
            and id[1] == Weekday.MO, Layout.ALL_SLOT_IDS)
                                 }
        Layout.TU_G_SLOT_IDS = {slot_id for slot_id in
                                filter(lambda id: id[0] == ActivityType.GAME
            and id[1] == Weekday.TU, Layout.ALL_SLOT_IDS)
                                }
        Layout.MO_P_SLOTS_IDS = {slot_id for slot_id in
                                 filter(lambda id: id[0] == ActivityType.PRACTICE
            and id[1] == Weekday.MO, Layout.ALL_SLOT_IDS)
                                 }
        Layout.TU_P_SLOT_IDS = {slot_id for slot_id in
                                filter(lambda id: id[0] == ActivityType.PRACTICE
            and id[1] == Weekday.TU, Layout.ALL_SLOT_IDS)
                                }
        Layout.FR_P_SLOT_IDS = {slot_id for slot_id in
                                filter(lambda id: id[0] == ActivityType.PRACTICE
            and id[1] == Weekday.FR, Layout.ALL_SLOT_IDS)
                                }

        # Calculate overlaps between slots (slots with overlapping time on the same day)
        for slot_a_id in Layout.ALL_SLOT_IDS:
            slot_a_obj = Layout.SLOT_ID_TO_OBJ[slot_a_id]
            slot_a_start = time_str_to_int(slot_a_obj.start_time)
            slot_a_end = time_str_to_int(slot_a_obj.end_time)

            for slot_b_id in Layout.ALL_SLOT_IDS:
                slot_b_obj = Layout.SLOT_ID_TO_OBJ[slot_b_id]
                slot_b_start = time_str_to_int(slot_b_obj.start_time)
                slot_b_end = time_str_to_int(slot_b_obj.end_time)

                # Check if slots overlap
                if (
                        slot_a_obj.weekday == slot_b_obj.weekday
                        and not (slot_a_start >= slot_b_end or slot_a_end <= slot_b_start)
                ):
                    slot_a_obj.overlaps.add(slot_b_id)
                    slot_b_obj.overlaps.add(slot_a_id)

    @staticmethod
    def post_parser_initialization():
        """
        Perform additional setup after parsing input files. This includes updating constraints and
        settings for specific slots, as well as logging environment data for debugging purposes.
        """

        # Example admin meeting constraints
        slot_a_id = (ActivityType.GAME, Weekday.TU, "11:00")
        slot_b_id = (ActivityType.PRACTICE, Weekday.TU, "11:00")
        slot_c_id = (ActivityType.PRACTICE, Weekday.TU, "12:00")

        slot_a = Layout.SLOT_ID_TO_OBJ[slot_a_id]
        slot_b = Layout.SLOT_ID_TO_OBJ[slot_b_id]
        slot_c = Layout.SLOT_ID_TO_OBJ[slot_c_id]

        # Set these slots to have zero games
        slot_a.gamemin = 0
        slot_a.gamemax = 0
        slot_b.gamemin = 0
        slot_b.gamemax = 0
        slot_c.gamemin = 0
        slot_c.gamemax = 0

        # Log environment data for debugging
        logging.debug("\n" * 5)
        logging.debug("<environment data>")
        with open('program_log.log', 'a') as f:
            with redirect_stdout(f):
                pprint.pprint(vars(Layout))
        logging.debug("</environment data>")
        logging.debug("\n" * 5)

    class Adders:
        """
        Inner class providing methods to add activities, constraints, and preferences
        to the environment during parsing or initialization.
        """

        @staticmethod
        def update_name(name: str):
            """
            Update the name of the environment (e.g., the schedule's name).
            """
            Layout.NAME = name

        @staticmethod
        def add_game(game: Game):
            """
            Add a game to the environment, updating relevant mappings and sets.
            """
            Layout.ACTIVITY_ID_TO_OBJ[game.id] = game
            Layout.ACTIVITY_IDS.add(game.id)
            Layout.GAME_ID_TO_OBJ[game.id] = game
            Layout.GAME_IDS.add(game.id)
            Layout.NOT_COMPATIBLE[game.id] = set()

        @staticmethod
        def add_practice(practice: Practice):
            """
            Add a practice to the environment, updating relevant mappings and sets.
            """
            Layout.ACTIVITY_ID_TO_OBJ[practice.id] = practice
            Layout.ACTIVITY_IDS.add(practice.id)
            Layout.PRACTICE_ID_TO_OBJ[practice.id] = practice
            Layout.PRACTICE_IDS.add(practice.id)
            Layout.NOT_COMPATIBLE[practice.id] = set()

        @staticmethod
        def add_not_compatible(activity1_id: str, activity2_id: str):
            """
            Add a constraint indicating that two activities cannot be scheduled together.
            """
            Layout.NOT_COMPATIBLE[activity1_id].add(activity2_id)
            Layout.NOT_COMPATIBLE[activity2_id].add(activity1_id)

        @staticmethod
        def add_unwanted(activity_id: str, slot_id: "tuple[ActivityType, Weekday, str]"):
            """
            Add a constraint preventing an activity from being scheduled in a specific slot.
            """
            if activity_id not in Layout.UNWANTED:
                Layout.UNWANTED[activity_id] = set()
            Layout.UNWANTED[activity_id].add(slot_id)

        @staticmethod
        def add_preference(preference: "tuple[str, tuple[ActivityType, Weekday, str], int]"):
            """
            Add a preference for an activity to be scheduled in a specific slot with a given value.
            """
            activity_id, slot_id, pref_value = preference
            if activity_id not in Layout.PREFERENCES:
                Layout.PREFERENCES[activity_id] = set()
            Layout.PREFERENCES[activity_id].add((slot_id, pref_value))

        @staticmethod
        def add_pair(pair: "tuple[str, str]"):
            """
            Add a pairing constraint, ensuring two activities are scheduled at the same time.
            """
            activity_a, activity_b = pair
            if activity_a not in Layout.PAIR:
                Layout.PAIR[activity_a] = set()
            if activity_b not in Layout.PAIR:
                Layout.PAIR[activity_b] = set()
            Layout.PAIR[activity_a].add(activity_b)
            Layout.PAIR[activity_b].add(activity_a)

        @staticmethod
        def add_partassign(partassign: "tuple[str, tuple[ActivityType, Weekday, str]]"):
            """
            Add a hard constraint assigning an activity to a specific slot.
            """
            activity_id, slot_id = partassign
            Layout.PARTASSIGN[activity_id] = slot_id
