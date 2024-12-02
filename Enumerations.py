
from enum import Enum

# Enum to represent types of activities (e.g., GAME, PRACTICE)
class ActivityType(Enum):
    GAME = "GAME"      # Represents a game activity
    PRACTICE = "PRACTICE"  # Represents a practice activity


# Enum to represent weekdays (MO, TU, FR for Monday, Tuesday, Friday)
class Weekday(Enum):
    MO = "MO"  # Monday
    TU = "TU"  # Tuesday
    FR = "FR"  # Friday


# Class containing mappings from Enum values to Enum objects for easy lookups
class EnumValueToObjMaps:
    # Map to associate activity type strings with their respective ActivityType Enum
    ACTIVITY_TYPES = {activity_type.value: activity_type for activity_type in ActivityType}

    # Map to associate weekday strings with their respective Weekday Enum
    WEEKDAYS = {weekday.value: weekday for weekday in Weekday}