from Activity import Activity
from Enumerations import ActivityType, Weekday
from ActivitySlot import ActivitySlot

# Represents a practice activity
class Practice(Activity):
    # Specifies the type of activity as practice
    ACTIVITY_TYPE = ActivityType.PRACTICE

    def __init__(self, id: str, association: str, age: str, tier: str, division: int, practice_num: int):
        """
        Initializes a Practice object.

        Parameters:
        - id (str): Unique identifier for the practice.
        - association (str): The organization or group hosting the practice.
        - age (str): Age group involved in the practice.
        - tier (str): The competitive tier for the practice group.
        - division (int): Division within the tier.
        - practice_num (int): Practice sequence number or count.
        """
        self.id = id
        self.association = association
        self.age = age
        self.tier = tier
        self.division = division
        self.practice_num = practice_num  # Number of practices assigned or planned

    def get_id(self):
        """Returns the unique identifier for the practice."""
        return self.id

    def get_association(self):
        """Returns the association hosting the practice."""
        return self.association

    def get_age(self):
        """Returns the age group of the practice."""
        return self.age

    def get_tier(self):
        """Returns the competitive tier of the practice."""
        return self.tier

    def get_division(self):
        """Returns the division for the practice."""
        return self.division


# Represents a time slot for a practice
class PracticeSlot(ActivitySlot):
    # Specifies the type of activity slot as practice
    ACTIVITY_TYPE = ActivityType.PRACTICE

    def __init__(self, weekday: Weekday, start_time: str, end_time: str, is_evening_slot: bool, practicemax: int, practicemin: int):
        """
        Initializes a PracticeSlot object.

        Parameters:
        - weekday (Weekday): Day of the week for the practice slot.
        - start_time (str): Start time of the practice in HH:MM format.
        - end_time (str): End time of the practice in HH:MM format.
        - is_evening_slot (bool): Indicates if the slot is in the evening.
        - practicemax (int): Maximum number of participants allowed in the slot.
        - practicemin (int): Minimum number of participants required for the slot.
        """
        self.weekday = weekday
        self.id = (self.ACTIVITY_TYPE, weekday, start_time)  # Unique identifier for the slot
        self.start_time = start_time
        self.end_time = end_time
        self.is_evening_slot = is_evening_slot
        self.practicemax = practicemax
        self.practicemin = practicemin
        self.overlaps = set()  # Set to track overlapping slots
