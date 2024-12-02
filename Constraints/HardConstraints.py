"""
This class contains methods to verify if a generated schedule satisfies the hard constraints of the scheduling problem.
Schedules that fail to meet the hard constraints will be rejected and not added to the search tree.
"""

# Constraint checks will take as input a current schedule and a new game or practice slot assignment to make.

from Enumerations import ActivityType, Weekday
from Search.Layout import Layout
from Activity import Activity
from Schedule import Schedule
from Games import Game
from Practices import Practice
from ActivitySlot import ActivitySlot
from Enumerations import ActivityType
from IO.Parser import Parser


class HardConstraints:
    # Class variables to track the number of failures for various constraints
    generalFails = 0  # Tracks general constraint failures
    cityFails = 0  # Tracks city constraint failures

    gameMaxFails = 0  # Tracks failures related to game slot limits
    practiceMaxFails = 0  # Tracks failures related to practice slot limits
    sameSlotFails = 0  # Tracks failures due to overlapping games and practices
    notCompatibleFails = 0  # Tracks failures due to incompatible activities
    partAssignFails = 0  # Tracks failures in partial assignments
    unwantedFails = 0  # Tracks failures caused by assigning to unwanted slots

    @staticmethod
    def check_constraints(schedule: Schedule, assignment: tuple):
        """
        Evaluates whether an activity can be assigned to a slot while adhering to all constraints.

        Args:
            schedule (Schedule): The current schedule being evaluated.
            assignment (tuple): A tuple containing the activity ID and slot ID.

        Returns:
            bool: True if the assignment satisfies all constraints; False otherwise.
        """
        # Extract the activity type from the slot ID
        activity_type = assignment[1][0]

        # Ensure the activity type is valid (either GAME or PRACTICE)
        if not (activity_type == ActivityType.GAME or activity_type == ActivityType.PRACTICE):
            raise TypeError("Activity must be of type 'Game' or 'Practice'.")

        # Check general and city-specific constraints
        general = HardConstraints.GeneralConstraints.check_general_constraints(schedule, assignment)
        city = HardConstraints.CityConstraints.check_city_constraints(schedule, assignment)

        # Increment failure counters if constraints are violated
        if not general:
            HardConstraints.generalFails += 1
        if not city:
            HardConstraints.cityFails += 1

        # Return True only if all constraints are satisfied
        return general and city


    class GeneralConstraints:
        @staticmethod
        def check_general_constraints(schedule: Schedule, assignment: tuple) -> bool:
            """
            Evaluates all general constraints for the given assignment.

            Args:
                schedule (Schedule): The current schedule being evaluated.
                assignment (tuple): A tuple containing the activity ID and slot ID.

            Returns:
                bool: True if the assignment satisfies all general constraints; False otherwise.
            """
            activity_type = assignment[1][0]

            # Check constraints specific to games or practices
            if activity_type == ActivityType.GAME:
                game_max = HardConstraints.GeneralConstraints.game_max(schedule, assignment)
                if not game_max:
                    HardConstraints.gameMaxFails += 1
                passes = game_max
            else:
                practice_max = HardConstraints.GeneralConstraints.practice_max(schedule, assignment)
                if not practice_max:
                    HardConstraints.practiceMaxFails += 1
                passes = practice_max

            # Evaluate additional general constraints
            same_slot = HardConstraints.GeneralConstraints.gp_same_slot(schedule, assignment)
            not_compatible = HardConstraints.GeneralConstraints.not_compatible(schedule, assignment)
            part_assign = HardConstraints.GeneralConstraints.part_assign(schedule, assignment)
            unwanted = HardConstraints.GeneralConstraints.unwanted(schedule, assignment)

            # Increment failure counters for violated constraints
            HardConstraints.sameSlotFails += not same_slot
            HardConstraints.notCompatibleFails += not not_compatible
            HardConstraints.partAssignFails += not part_assign
            HardConstraints.unwantedFails += not unwanted

            return passes and same_slot and not_compatible and part_assign and unwanted



        @staticmethod
        def game_max(schedule: Schedule, assignment: tuple) -> bool:
            """
            Checks if the number of games in a slot exceeds the maximum allowed.

            Args:
                schedule (Schedule): The current schedule.
                assignment (tuple): A tuple containing the activity ID and slot ID.

            Returns:
                bool: True if the number of games does not exceed the maximum; False otherwise.
            """
            activity_id, slot_id = assignment
            activity_type = slot_id[0]
            slot_obj = Layout.SLOT_ID_TO_OBJ[slot_id]
            if activity_type != ActivityType.GAME:
                return True
            if len(schedule.assignments[slot_id]) >= slot_obj.gamemax:
                return False
            return True


        @staticmethod
        def practice_max(schedule: Schedule, assignment: tuple) -> bool:
            """
            Checks if the number of practices in a slot exceeds the maximum allowed.

            Args:
                schedule (Schedule): The current schedule.
                assignment (tuple): A tuple containing the activity ID and slot ID.

            Returns:
                bool: True if the number of practices does not exceed the maximum; False otherwise.
            """
            activity_id, slot_id = assignment
            activity_type = slot_id[0]
            slot_obj = Layout.SLOT_ID_TO_OBJ[slot_id]
            if activity_type != ActivityType.PRACTICE:
                return True
            if len(schedule.assignments[slot_id]) >= slot_obj.practicemax:
                return False
            return True


        # Game/practice same slot assignment
        @staticmethod
        def gp_same_slot(schedule: Schedule, assignment: tuple) -> bool:
            """
           Ensures that games and practices for the same division do not overlap.

           Args:
               schedule (Schedule): The current schedule.
               assignment (tuple): A tuple containing the activity ID and slot ID.

           Returns:
               bool: True if no overlapping occurs; False otherwise.
           """
            activity_id, slot_id = assignment
            slot_obj = Layout.SLOT_ID_TO_OBJ[slot_id]
            overlapping_slots = slot_obj.overlaps
            activity_obj = Layout.ACTIVITY_ID_TO_OBJ[activity_id]
            type_a = activity_obj.ACTIVITY_TYPE

            for overlapping_slot in overlapping_slots:
                for act_id in schedule.assignments[overlapping_slot]:
                    act_obj = Layout.ACTIVITY_ID_TO_OBJ[act_id]
                    type_b = act_obj.ACTIVITY_TYPE
                    if type_a == ActivityType.PRACTICE and type_b == ActivityType.PRACTICE:
                        continue

                    # TODO unsure of which implementation is correct
                    # implementation version 1
                    same_assoc = (activity_obj.association == act_obj.association)
                    same_age = (activity_obj.age == act_obj.age)
                    same_tier = (activity_obj.tier == act_obj.tier)
                    same_division = (activity_obj.division == act_obj.division)
                    if same_assoc and same_age and same_tier and same_division:
                        return False

            return True


        # Not compatible assignment
        @staticmethod
        def not_compatible(schedule: Schedule, assignment: tuple) -> bool:
            """
            Ensures that incompatible activities are not scheduled in the same slot.

            Args:
                schedule (Schedule): The current schedule.
                assignment (tuple): A tuple containing the activity ID and slot ID.

            Returns:
                bool: True if no incompatibility exists; False otherwise.
            """
            activity_id, slot_id = assignment
            for id in schedule.assignments[slot_id]:
                if id in Layout.NOT_COMPATIBLE[activity_id]:
                    return False
            return True


        # Partial assignment
        @staticmethod
        def part_assign(schedule: Schedule, assignment: tuple) -> bool:
            """
            Ensures that partially assigned activities are placed in their required slots.

            Args:
                schedule (Schedule): The current schedule.
                assignment (tuple): A tuple containing the activity ID and slot ID.

            Returns:
                bool: True if the assignment respects partial assignments; False otherwise.
            """
            activity_id, slot_id = assignment
            if activity_id not in Layout.PARTASSIGN:
                return True
            return slot_id == Layout.PARTASSIGN[activity_id]


        # Unwanted assignment
        @staticmethod
        def unwanted(schedule: Schedule, assignment: tuple) -> bool:
            """
            Ensures that activities are not assigned to unwanted slots.

            Args:
                schedule (Schedule): The current schedule.
                assignment (tuple): A tuple containing the activity ID and slot ID.

            Returns:
                bool: True if the slot is not unwanted; False otherwise.
            """
            activity_id, slot_id = assignment
            for slot in Layout.UNWANTED[activity_id]:
                if slot_id == slot:
                    return False

            return True


    class CityConstraints:

        @staticmethod
        def check_city_constraints(schedule: Schedule, assignment: tuple) -> bool:
            """
            Evaluates all city-specific constraints for the given assignment.

            Args:
                schedule (Schedule): The current schedule being evaluated.
                assignment (tuple): A tuple containing the activity ID and slot ID.

            Returns:
                bool: True if all city-specific constraints are satisfied; False otherwise.
            """
            activity_id, slot_id = assignment
            activity_type = slot_id[0]

            if (activity_type == ActivityType.GAME): # activity is a game
                passes = (
                    HardConstraints.CityConstraints.age_group_constraint(schedule, assignment) and
                    # HardConstraints.CityConstraints.meeting_constraint(schedule, assignment) and
                    HardConstraints.CityConstraints.special_bookings_constraint(schedule, assignment)
                )
            else: # activity is a practice
                passes = True

            if Layout.ACTIVITY_ID_TO_OBJ[activity_id].division is not None:
                passes = passes and HardConstraints.CityConstraints.evening_slot_constraint(schedule, assignment)

            # The additional constraints below are checked whether the activity is a game or a practice
            return passes


        @staticmethod
        def evening_slot_constraint(schedule: Schedule, assignment: tuple) -> bool:
            """
            Ensures that division 9 activities are assigned only to evening slots.

            Args:
                schedule (Schedule): The current schedule.
                assignment (tuple): A tuple containing the activity ID and slot ID.

            Returns:
                bool: True if the activity is assigned to an evening slot; False otherwise.
            """
            activity_id, slot_id = assignment
            activity_obj = Layout.ACTIVITY_ID_TO_OBJ[activity_id]
            if (str(activity_obj.division)[0] == '9'): # TODO may not only be division 9, but divisions that start with 9
                return Parser.decide_if_evening_slot(slot_id[2])
            else:
                return True


        @staticmethod
        def age_group_constraint(schedule: Schedule, assignment: tuple) -> bool:
            """
            Ensures that games for age groups U15 through U19 do not overlap.

            Args:
                schedule (Schedule): The current schedule.
                assignment (tuple): A tuple containing the activity ID and slot ID.

            Returns:
                bool: True if no overlap exists between the specified age groups; False otherwise.
            """
            MUTEX_AGES = {"U15", "U16", "U17", "U19"}

            activity_id, slot_id = assignment
            activity_type = slot_id[0]
            if activity_type != ActivityType.GAME:
                return True # this hard constraint only involves games

            age_a = Layout.GAME_ID_TO_OBJ[activity_id].age
            if age_a not in MUTEX_AGES:
                return True

            for act_id in schedule.assignments[slot_id]:
                if act_id == activity_id:
                    continue

                age_b = Layout.GAME_ID_TO_OBJ[act_id].age
                if age_b in MUTEX_AGES:
                    return False

            return True

        @staticmethod
        def special_bookings_constraint(schedule: Schedule, assignment: tuple) -> bool:
            """
            Ensures that special games (e.g., CMSA U12T1S, CMSA U13T1S) are assigned correctly.

            Args:
                schedule (Schedule): The current schedule.
                assignment (tuple): A tuple containing the activity ID and slot ID.

            Returns:
                bool: True if the special booking rules are satisfied; False otherwise.
            """
            activity_id, slot_id = assignment
            act_obj = Layout.ACTIVITY_ID_TO_OBJ[activity_id]

            if act_obj.ACTIVITY_TYPE != ActivityType.GAME:
                return True # this constraint doesn't apply to practices

            association, age, tier = act_obj.association, act_obj.age, act_obj.tier

            if association != "CMSA" or age not in {"U12", "U13"} or tier != "T1":
                return True # constraint doesn't apply to this given game


            if activity_id in Layout.SPECIAL_BOOKINGS:
                if slot_id == Layout.SPECIAL_BOOKINGS[activity_id]:
                    return True

                return False

            if age == "U12":
                if "CMSA U12T1S" in schedule.assignments[slot_id]:
                    return False
                return True
            elif age == "U13":
                if "CMSA U13T1S" in schedule.assignments[slot_id]:
                    return False
                return True
            else:
                raise Exception("age should be one of U12 or U13 at this point in the hard constraint check")

