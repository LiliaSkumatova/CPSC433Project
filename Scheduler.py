"""
This class is the container for the scheduling AI. It calls the methods in order to parse an input file and returns a
completed schedule at the end of the evaluation process.
"""

import time
from Schedule import Schedule
from Constraints.HardConstraints import HardConstraints
from IO.Parser import Parser
from Search.Layout import Layout
from Search.AndTreeSearch import SearchModel, Tree, Node
from IO.Printer import Printer


class Scheduler:
    # Class-level variables
    tree = None  # The Tree object representing the search space
    stack = []  # Stack used for depth-first search
    current_best = None  # Stores the best schedule found so far
    last_print_time = time.time()  # Tracks the last time the schedule was printed

    @staticmethod
    def initialize():
        """
        Initializes the scheduler by creating the root node of the search tree
        and pushing it onto the stack.
        """
        Scheduler.tree = Tree()
        Scheduler.stack.append(Scheduler.tree.root)

    @staticmethod
    def search():
        """
        The main method that starts and executes the search process. It iterates through the nodes
        in the stack, expands them, evaluates their feasibility, and updates the current best solution.
        """
        print("Search has started.")

        # Check if the problem is solvable before proceeding
        solvable = Scheduler.detect_solvable()
        if not solvable:
            print("Instance doesn't appear to be solvable!")
            return None

        # Continue searching while there are nodes in the stack
        while len(Scheduler.stack) > 0:
            node: Node = Scheduler.stack.pop()  # Get the next node to process

            # Calculate the number of remaining activities
            total_activities = len(Layout.ACTIVITY_IDS)
            remaining_activities = len(node.pr.remaining_games) + len(node.pr.remaining_practices)

            # Expand the current node by generating its children
            Scheduler.tree.expand(node)
            node.check_sol()  # Check if the current node's schedule is a solution

            # Update the current best schedule if applicable
            if node.sol:
                if Scheduler.current_best is None or node.pr.eval < Scheduler.current_best.pr.eval:
                    Scheduler.current_best = node

            # Sort children of the current node by their "opt" values (highest priority first)
            if node.children:
                Scheduler.tree.fleaf(node)

            # Add children nodes to the stack for further processing
            for child in node.children:
                Scheduler.stack.append(child)

            # Display the current optimization status periodically
            Scheduler.display_current_opt()

        return Scheduler.current_best

    @staticmethod
    def display_current_opt():
        """
        Displays the current state of the optimization process every 4 seconds.
        It shows general constraint failures and prints the current best schedule if available.
        """
        if time.time() - Scheduler.last_print_time > 4:
            Scheduler.last_print_time = time.time()

            total_fails = HardConstraints.generalFails + HardConstraints.cityFails
            if Scheduler.current_best:
                Printer.print_schedule(Scheduler.current_best.pr)
            else:
                print(
                    f"\nNo solution yet among {Layout.leaves_encountered} leaves encountered. "
                    "Keep waiting!\n"
                )

    @staticmethod
    def detect_solvable():
        """
        Determines if the scheduling problem is solvable based on the total capacity of available slots
        and the number of games and practices to be scheduled.
        """
        total_gamemax = sum(x.gamemax for x in Layout.GAME_SLOT_ID_TO_OBJ.values())
        total_practicemax = sum(x.practicemax for x in Layout.PRACTICE_SLOT_ID_TO_OBJ.values())
        num_games = len(Layout.GAME_IDS)
        num_practices = len(Layout.PRACTICE_IDS)

        # Check if there are more practices than the available practice slots
        if num_practices > total_practicemax:
            return False

        # Allow two extra games for special bookings, else check slot sufficiency
        if num_games > total_gamemax + 2:
            return False

        return True
