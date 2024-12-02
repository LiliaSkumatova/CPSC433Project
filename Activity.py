"""
The base class for all game and practice activities.

This abstract class defines shared behavior and properties that can be
inherited and customized by specific activity types (e.g., Game, Practice).
Since it is abstract, no constructor is required, and subclasses are expected
to define their own specific implementations.
"""
from abc import ABC, abstractmethod


class Activity(ABC):

    ACTIVITY_TYPE = None



