#   This class prints out the generated schedule at the end of our search process.

from Schedule import Schedule
from Games import Game
from Practices import Practice
from Games import GameSlot
from Practices import PracticeSlot
from Activity import Activity
from Enumerations import ActivityType
from Enumerations import Weekday
from Search.Layout import Layout




class Printer():

    #Constructor
    def __init__(self) -> None:
        pass

    def print_schedule(schedule: Schedule):
        #schedule = schedule.get_copy() <- not sure if need this
        BUFFER_SPACE = 30

        print("Eval-value: " + str(schedule.getEval()))
        for activity_id in schedule.slot_of_each_activity:
            activity = Layout.ACTIVITY_ID_TO_OBJ[activity_id]
            slot_id = schedule.slot_of_each_activity[activity_id]
            activity_type, weekday, start_time = slot_id

            num_spaces = BUFFER_SPACE - len(activity_id)

            print(
                activity_id + " " * num_spaces + ": " +
                weekday.value + ", " + start_time
            )
