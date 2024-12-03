
import logging

# Importing required modules for layout/environment setup, schedule maker, parser, and constraint handling
from Search.Layout import Layout
from ScheduleMaker import ScheduleMaker
from IO.Parser import Parser
from IO.Printer import Printer


class Main:
    """
    Main driver class that initializes and runs the scheduling process.
    It creates a schedule maker object, processes the input using a parser,
    and finds the optimal solution.
    """

    @staticmethod
    def main():
        """
        The main method of the program. It initializes the logging, processes input data,
        initializes the schedule maker, and performs the search for the optimal solution.
        """
        # Clear the log file at the beginning of the execution
        Main.clear_log()

        # Set up logging to a file for debugging purposes with DEBUG level logging
        logging.basicConfig(filename="program_log.log", level=logging.DEBUG)

        # Pre-parser initialization to set up the environment (like slot definitions)
        Layout.pre_parser_initialization()

        # Initialize the parser and parse the input data
        parser = Parser()
        parser.parse()

        # Post-parser initialization to finalize the environment setup
        Layout.post_parser_initialization()

        # Initialize the Schedule maker with the current environment
        ScheduleMaker.initialize()

        # Perform the search to find the optimal schedule
        optimal_solution = ScheduleMaker.search()

        # Check if a solution was found and print the result
        if optimal_solution is None:
            print("No solution was found!")  # Inform the user if no solution exists
        else:
            # If a solution is found, print the details of the schedule
            print("Search has ended! Here is the solution found: ")
            Printer.print_schedule(optimal_solution.pr)  # Print the schedule assignments

    @staticmethod
    def clear_log():
        """
        Clears the content of the log file to prepare for a new execution.
        """
        with open("program_log.log", "w"):  # Open the log file in write mode to clear it
            pass

# Entry point of the program, starts the main method if this script is executed directly
if __name__ == "__main__":
    Main.main()
