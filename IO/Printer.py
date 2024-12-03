#   This class prints out the generated schedule at the end of our search process.

from Schedule import Schedule

class Printer:

    #Constructor
    def __init__(self) -> None:
        pass

    @staticmethod
    def print_schedule(schedule: Schedule):
        #schedule = schedule.get_copy() <- not sure if need this
        buffer_space = 30

        print("Eval-value: " + str(schedule.get_eval()))
        for activity_id in schedule.slot_of_each_activity:
            slot_id = schedule.slot_of_each_activity[activity_id]
            activity_type, weekday, start_time = slot_id

            num_spaces = buffer_space - len(activity_id)

            print(
                activity_id + " " * num_spaces + ": " +
                weekday.value + ", " + start_time
            )
