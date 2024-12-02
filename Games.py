from Enumerations import ActivityType, Weekday
from Activity import Activity
from ActivitySlot import ActivitySlot

# Represents a game activity
class Game(Activity):
    # Specifies the type of activity as a game
    ACTIVITY_TYPE = ActivityType.GAME

    def __init__(self, id: str, association: str, age: str, tier: str, division: int):
        """
        Initializes a Game object.

        Parameters:
        - id (str): Unique identifier for the game.
        - association (str): The association or organization hosting the game.
        - age (str): The age group participating in the game.
        - tier (str): The competitive tier of the game.
        - division (int): The division within the tier.
        """
        self.id = id
        self.association = association
        self.age = age
        self.tier = tier
        self.division = division

    def get_id(self):
        """Returns the unique identifier of the game."""
        return self.id

    def get_association(self):
        """Returns the association hosting the game."""
        return self.association

    def get_age(self):
        """Returns the age group of the game."""
        return self.age

    def get_tier(self):
        """Returns the competitive tier of the game."""
        return self.tier

    def get_division(self):
        """Returns the division of the game."""
        return self.division


# Represents a time slot for a game
class GameSlot(ActivitySlot):
    # Specifies the type of activity as a game slot
    ACTIVITY_TYPE = ActivityType.GAME

    def __init__(self, weekday: Weekday, start_time: str, end_time: str, is_evening_slot: bool, gamemax: int, gamemin: int):
        """
        Initializes a GameSlot object.

        Parameters:
        - weekday (Weekday): The day of the week for the slot.
        - start_time (str): The start time of the slot in HH:MM format.
        - end_time (str): The end time of the slot in HH:MM format.
        - is_evening_slot (bool): Indicates if the slot is in the evening.
        - gamemax (int): Maximum number of players allowed in the slot.
        - gamemin (int): Minimum number of players required for the slot.
        """
        self.weekday = weekday
        self.id = (self.ACTIVITY_TYPE, weekday, start_time)  # Unique identifier for the slot
        self.start_time = start_time
        self.end_time = end_time
        self.is_evening_slot = is_evening_slot
        self.gamemax = gamemax
        self.gamemin = gamemin
        self.overlaps = set()  # Tracks other slots that overlap with this one

