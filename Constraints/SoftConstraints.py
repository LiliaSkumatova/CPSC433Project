"""
The methods placed herein evaluate schedules for compliance with soft constraints and assign penalty scores.
Penalty scores are used to quantify how well a schedule satisfies soft constraints as it is generated.
"""

from Search.Layout import Layout
from Schedule import Schedule
from Enumerations import ActivityType


class SoftConstraints:
    """
    This class contains methods to evaluate soft constraints and calculate penalty scores for schedules.
    """

    @staticmethod
    def get_delta_eval(schedule: Schedule, latest_assignment: tuple) -> int:
        """
        Calculates the change in penalty score caused by the latest assignment.

        Args:
            schedule (Schedule): The current schedule being evaluated.
            latest_assignment (tuple): The most recent activity-slot assignment.

        Returns:
            int: The total change in penalty score.
        """
        # Calculate penalties for each soft constraint and weight them
        delta_eval_minfilled_games = (
            SoftConstraints.GeneralConstraints.game_min(schedule, latest_assignment)
            * Layout.W_MINFILLED
        )
        delta_eval_minfilled_practices = (
            SoftConstraints.GeneralConstraints.practice_min(schedule, latest_assignment)
            * Layout.W_MINFILLED
        )
        delta_eval_pref = (
            SoftConstraints.GeneralConstraints.preference(schedule, latest_assignment)
            * Layout.W_PREF
        )
        delta_eval_pair = (
            SoftConstraints.GeneralConstraints.pair(schedule, latest_assignment)
            * Layout.W_PAIR
        )
        delta_eval_secdiff = (
            SoftConstraints.check_city_constraint(schedule, latest_assignment)
            * Layout.W_SECDIFF
        )

        # Sum all penalties and return the total delta
        return sum(
            [
                delta_eval_minfilled_games,
                delta_eval_minfilled_practices,
                delta_eval_pref,
                delta_eval_pair,
                delta_eval_secdiff,
            ]
        )

    class GeneralConstraints:
        """
        This nested class contains methods to evaluate general soft constraints, such as game and practice minimums,
        preferences, and activity pairing.
        """

        @staticmethod
        def game_min(schedule: Schedule, latest_assignment: tuple) -> int:
            """
            Evaluates the penalty for failing to meet the minimum number of games in a slot.

            Args:
                schedule (Schedule): The current schedule.
                latest_assignment (tuple): The most recent activity-slot assignment.

            Returns:
                int: The penalty reduction for meeting the minimum games requirement.
            """
            _, slot_id = latest_assignment
            activity_type = slot_id[0]

            # Skip if the activity is not a game
            if activity_type == ActivityType.PRACTICE:
                return 0

            # Check if the slot meets the minimum games requirement
            slot_obj = Layout.GAME_SLOT_ID_TO_OBJ[slot_id]
            penalty_included = len(schedule.assignments.get(slot_id, [])) < slot_obj.gamemin

            # Return penalty reduction if the minimum is met
            return -Layout.PEN_GAMEMIN if penalty_included else 0

        @staticmethod
        def practice_min(schedule: Schedule, latest_assignment: tuple) -> int:
            """
            Evaluates the penalty for failing to meet the minimum number of practices in a slot.

            Args:
                schedule (Schedule): The current schedule.
                latest_assignment (tuple): The most recent activity-slot assignment.

            Returns:
                int: The penalty reduction for meeting the minimum practices requirement.
            """
            _, slot_id = latest_assignment
            activity_type = slot_id[0]

            # Skip if the activity is not a practice
            if activity_type == ActivityType.GAME:
                return 0

            # Check if the slot meets the minimum practices requirement
            slot_obj = Layout.PRACTICE_SLOT_ID_TO_OBJ[slot_id]
            penalty_included = len(schedule.assignments.get(slot_id, [])) < slot_obj.practicemin

            # Return penalty reduction if the minimum is met
            return -Layout.PEN_PRACTICEMIN if penalty_included else 0

        @staticmethod
        def preference(schedule: Schedule, latest_assignment: tuple) -> int:
            """
            Evaluates the penalty for assigning an activity to a non-preferred slot.

            Args:
                schedule (Schedule): The current schedule.
                latest_assignment (tuple): The most recent activity-slot assignment.

            Returns:
                int: The penalty reduction for assigning to a preferred slot.
            """
            activity_id, slot_id = latest_assignment
            delta_penalty = 0

            # Check if the slot matches any preferences for the activity
            for preference in Layout.PREFERENCES.get(activity_id, []):
                pref_slot_id, pref_value = preference
                if slot_id == pref_slot_id:
                    delta_penalty -= pref_value  # Reduce penalty by the preference value

            return delta_penalty

        @staticmethod
        def pair(schedule: Schedule, latest_assignment: tuple) -> int:
            """
            Evaluates the penalty for failing to schedule paired activities in the same slot.

            Args:
                schedule (Schedule): The current schedule.
                latest_assignment (tuple): The most recent activity-slot assignment.

            Returns:
                int: The penalty increase for failing to pair activities.
            """
            activity_id, slot_id = latest_assignment
            delta_penalty = 0

            # Check if the activity has paired activities
            if activity_id in Layout.PAIR:
                paired_activities = Layout.PAIR[activity_id]
                for paired_activity in paired_activities:
                    # Skip activities that have not yet been assigned
                    if (
                        paired_activity in schedule.remaining_games
                        or paired_activity in schedule.remaining_practices
                    ):
                        continue
                    # Penalize if the paired activity is not in the same slot
                    if paired_activity not in schedule.assignments.get(slot_id, []):
                        delta_penalty += Layout.PEN_NOTPAIRED

            return delta_penalty

    @staticmethod
    def check_city_constraint(schedule: Schedule, latest_assignment: tuple) -> int:
        """
        Evaluates the penalty for failing to meet city-specific constraints, such as association and tier rules.

        Args:
            schedule (Schedule): The current schedule.
            latest_assignment (tuple): The most recent activity-slot assignment.

        Returns:
            int: The penalty increase for violating city constraints.
        """
        activity_id, slot_id = latest_assignment
        activity_type = slot_id[0]

        # Skip if the activity is not a game
        if activity_type != ActivityType.GAME:
            return 0

        delta_penalty = 0
        activity_obj = Layout.GAME_ID_TO_OBJ[activity_id]

        # Compare the attributes of the activity with others in the same slot
        for act_id in schedule.assignments.get(slot_id, []):
            act_obj = Layout.GAME_ID_TO_OBJ[act_id]
            if (
                activity_obj.age == act_obj.age
                and activity_obj.tier == act_obj.tier
                and activity_obj.association == act_obj.association
            ):
                delta_penalty += Layout.PEN_SECTION  # Penalize for overlapping attributes

        return delta_penalty
