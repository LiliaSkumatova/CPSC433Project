"""
The 'ActivitySlot' class serves as the base class for all scheduling slots.
It is an abstract class meant to represent time slots in a schedule, including games and practices.
Specific slot types (e.g., GameSlot, PracticeSlot) inherit from this class and add their unique attributes.
"""
from abc import ABC

class ActivitySlot(ABC):
    pass
