# Combined Python Script

from Schedule import Schedule
from Constraints.HardConstraints import HardConstraints
from Constraints.SoftConstraints import SoftConstraints
from Search.Layout import Layout


# ----------------------
# Part 1: SearchModel
# ----------------------

class SearchModel:
    @staticmethod
    def div(schedule: Schedule):
        """
        Input: A schedule to expand.
        Output: A list of all possible schedules produced by assigning a single game or practice to any available slot, where that assignment does not violate hard constraints.
        Note that we will never generate a new schedule (we only produce copies).
            Therefore, the only schedule 'initialized' is the very first empty schedule.
            In this way, the integrity of the 'remaining_games' and 'remaining_practices' variables is preserved.
            Game and practice are removed from their respective 'remaining' lists in a schedule upon being assigned to the schedule.
        """
        assignments = []  # list of tuples, where each represents an assignment

        # Generating possible assignments for games
        for game_id in schedule.remaining_games:
            if game_id in Layout.SPECIAL_BOOKINGS:
                assignment = (game_id, Layout.SPECIAL_BOOKINGS[game_id])
                if HardConstraints.check_constraints(schedule, assignment):
                    assignments.append(assignment)
            else:
                for game_slot_id in schedule.vacant_game_slots:
                    assignment = (game_id, game_slot_id)
                    if HardConstraints.check_constraints(schedule, assignment):
                        assignments.append(assignment)

        # Generating possible assignments for practices
        for practice_id in schedule.remaining_practices:
            for practice_slot_id in schedule.vacant_practice_slots:
                assignment = (practice_id, practice_slot_id)
                if HardConstraints.check_constraints(schedule, assignment):
                    assignments.append(assignment)

        # Generating and returning new Schedule objects for each of these new assignments
        return SearchModel.generate_schedules(schedule, assignments)

    @staticmethod
    def generate_schedules(schedule: Schedule, assignments):
        """
        Input: List of assignments, where each assignment is represented by a 2-tuple containing an activity ID and a slot ID
        Output: List of Schedule objects, where each corresponds to the addition of one of the new assignments given as input
        """
        schedules = []

        for assign in assignments:
            new_schedule = schedule.get_copy()
            activity_id, slot_id = assign
            new_schedule.eval = new_schedule.eval + SoftConstraints.get_delta_eval(new_schedule, assign)
            new_schedule.assign_activity(activity_id, slot_id)
            new_schedule.latest_assignment = assign
            schedules.append(new_schedule)

        return schedules


# ----------------------
# Part 2: Tree and Node
# ----------------------


class Node:
    def __init__(self, parent, pr: Schedule, sol: bool):
        self.parent = parent
        self.pr = pr
        self.sol = sol
        self.children = []
        self.opt = None
        if self.parent is not None:
            self.compute_opt()

    def check_sol(self):
        if self.parent is None: return

        if not self.is_leaf():
            sol = True
            for child in self.children:
                sol = sol and child.sol  # if any child is False, the parent is False

            if sol:
                self.sol = True
                self.parent.check_sol()

        # If node is a leaf, we must check if its schedule is complete
        else:
            if (len(self.pr.remaining_games) == 0) and (len(self.pr.remaining_practices) == 0):
                self.sol = True
                self.parent.check_sol()

    def compute_opt(self):
        latest_id, latest_slot_id = self.pr.latest_assignment

        # We want to make assignments that fulfill hard constraints first, so we give those assignments infinitely negative values (else, we assign eval())
        if (latest_id in Layout.PARTASSIGN) and (latest_slot_id == Layout.PARTASSIGN[latest_id]):
            self.opt = float('-inf')
        elif (latest_id in Layout.SPECIAL_BOOKINGS) and (
                latest_slot_id == Layout.SPECIAL_BOOKINGS[latest_id]):
            self.opt = float('-inf')
        else:
            self.opt = self.eval()

    def eval(self):
        return self.pr.eval + SoftConstraints.get_delta_eval(self.pr, self.pr.latest_assignment)

    def add_child(self, parent, pr, sol):
        self.children.append(Node(parent, pr, sol))

    def is_leaf(self):
        is_leaf = len(self.children) == 0
        if is_leaf: Layout.leaves_encountered = Layout.leaves_encountered + 1
        return is_leaf


class Tree:
    def __init__(self) -> None:
        self.root = Node(None, Schedule(), False)
    @staticmethod
    def expand(parent_node: Node):
        for schedule in SearchModel.div(parent_node.pr):
            parent_node.add_child(parent_node, schedule, False)
    @staticmethod
    def fleaf(parent_node: Node):
        if not (len(parent_node.children) > 0):
            raise (RuntimeError("fleaf attempting to choose child from parent with no children"))

        # Sorting children by Opt values
        # Note that it is sorting in reverse order (using -)
        parent_node.children.sort(key=lambda x: x.opt, reverse=True)
