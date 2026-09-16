import argparse
from itertools import combinations

class ArgumentationFramework:
    def __init__(self, file_path):
        # Initialize the framework by reading arguments and attacks from the file
        self.arguments, self.attacks = self._read_graph(file_path)

    def _read_graph(self, file_path):
        """
        Reads the argumentation framework from a file.

        Args:
            file_path (str): Path to the file.

        Returns:
            tuple: A tuple containing a list of arguments and a list of attacks.
        """
        arguments = set()  # Use a set to avoid duplicate arguments
        attacks = []  # Store attacks as tuples (source, target)
        try:
            with open(file_path) as file:
                for line in file:
                    if "arg" in line:
                        arg = self._extract_content(line)  # Extract argument name
                        arguments.add(arg)
                    elif "att" in line:
                        src, tgt = self._extract_content(line).split(',')  # Extract attack pair
                        if src == tgt:
                            raise ValueError("Self-attack detected: an argument cannot attack itself.")
                        attacks.append((src, tgt))
            return list(arguments), attacks
        except FileNotFoundError:
            raise ValueError(f"File not found: {file_path}")  # Handle missing file errors
        except Exception as e:
            raise ValueError(f"Error parsing the file: {e}")  # Handle other errors

    @staticmethod
    def _extract_content(line):
        # Extract content within parentheses in a line (e.g., "arg(A)")
        start_idx = line.find('(')
        end_idx = line.find(')')
        return line[start_idx + 1:end_idx]

    @staticmethod
    def _powerset(iterable):
        """
        Generates all possible subsets of a given iterable.

        Args:
            iterable (iterable): The iterable to generate subsets from.

        Yields:
            tuple: A subset.
        """
        s = list(iterable)
        # Use combinations to generate subsets of all possible sizes
        return (subset for r in range(len(s) + 1) for subset in combinations(s, r))

    def _is_conflict_free(self, subset):
        """
        Checks if a given subset is conflict-free.

        Args:
            subset (list): A subset of arguments.

        Returns:
            bool: True if the subset is conflict-free, False otherwise.
        """
        # Ensure no pair of arguments in the subset attacks each other
        return all((arg1, arg2) not in self.attacks for arg1 in subset for arg2 in subset)

    def _attacks_all_remaining(self, subset, remaining_args):
        """
        Checks if a subset attacks all remaining arguments.

        Args:
            subset (list): The subset to check.
            remaining_args (list): The remaining arguments.

        Returns:
            bool: True if the subset attacks all remaining arguments, False otherwise.
        """
        # Track which remaining arguments are attacked
        attacked = {arg: False for arg in remaining_args}
        for arg in subset:
            for remaining_arg in remaining_args:
                if (arg, remaining_arg) in self.attacks:
                    attacked[remaining_arg] = True  # Mark as attacked
        return all(attacked.values())  # Check if all are attacked

    def _get_attackers(self, argument):
        """
        Retrieves all attackers of a given argument.

        Args:
            argument (str): The argument to find attackers for.

        Returns:
            list: A list of attackers.
        """
        # Find all arguments that attack the given argument
        return [attacker for attacker, target in self.attacks if target == argument]

    def _is_argument_defended(self, argument, subset):
        """
        Checks if an individual argument is defended by a subset.

        Args:
            argument (str): An argument.
            subset (list): A subset of arguments.

        Returns:
            bool: True if the argument is defended by the subset, False otherwise.
        """
        attackers = self._get_attackers(argument)  # Get attackers of the argument
        # Check if each attacker is counter-attacked by any defender in the subset
        return all(any((defender, attacker) in self.attacks for defender in subset) for attacker in attackers)

    def _is_defended(self, subset):
        """
        Checks if all arguments in a subset are defended.

        Args:
            subset (list): A subset of arguments.

        Returns:
            bool: True if all arguments are defended, False otherwise.
        """
        # Verify that each argument in the subset is defended
        return all(self._is_argument_defended(arg, subset) for arg in subset)

    def _is_complete_extension(self, candidate_set):
        """
        Checks if a candidate set is a complete extension.

        Args:
            candidate_set (list): The candidate set to check.

        Returns:
            bool: True if the candidate set is a complete extension, False otherwise.
        """
        # A complete extension must be conflict-free, defend all its elements,
        # and include all arguments it can defend
        return (
            self._is_conflict_free(candidate_set) and
            self._is_defended(candidate_set) and
            all(
                arg in candidate_set
                for arg in self.arguments
                if self._is_argument_defended(arg, candidate_set)
            )
        )

    def find_stable_extensions(self):
        """
        Finds all stable extensions.

        Returns:
            list: A list of all stable extensions.
        """
        stable_extensions = []
        for subset in self._powerset(self.arguments):
            remaining_args = set(self.arguments) - set(subset)
            # Stable extensions must be conflict-free and attack all remaining arguments
            if self._is_conflict_free(subset) and self._attacks_all_remaining(subset, remaining_args):
                stable_extensions.append(list(subset))
        return stable_extensions

    def find_complete_extensions(self):
        """
        Finds all complete extensions.

        Returns:
            list: A list of all complete extensions.
        """
        # Filter subsets to include only those that qualify as complete extensions
        return [list(subset) for subset in self._powerset(self.arguments) if self._is_complete_extension(subset)]

    def is_credulously_accepted(self, arg, extensions):
        """
        Checks if an argument is credulously accepted.

        Args:
            arg (str): The argument to check.
            extensions (list): The extensions to consider.

        Returns:
            str: "YES" if the argument is credulously accepted, "NO" otherwise.
        """
        # An argument is credulously accepted if it appears in at least one extension
        return "YES" if any(arg in ext for ext in extensions) else "NO"

    def is_skeptically_accepted(self, arg, extensions):
        """
        Checks if an argument is skeptically accepted.

        Args:
            arg (str): The argument to check.
            extensions (list): The extensions to consider.

        Returns:
            str: "YES" if the argument is skeptically accepted, "NO" otherwise.
        """
        # An argument is skeptically accepted if it appears in all extensions
        return "YES" if all(arg in ext for ext in extensions) else "NO"


def main():
    parser = argparse.ArgumentParser(description="Argumentation Framework Analyzer")
    parser.add_argument("-p", choices=['SE-CO', 'SE-ST', 'DC-CO', 'DS-CO', 'DC-ST', 'DS-ST'],
                        required=True, help="Specify the type of analysis to perform")
    parser.add_argument("-f", required=True, help="Path to the text file describing the Argumentation Framework")
    parser.add_argument("-a", required=False, help="Query argument or list of arguments")

    args = parser.parse_args()

    if args.p in ['DC-CO', 'DS-CO', 'DC-ST', 'DS-ST'] and not args.a:
        parser.error("The '-a' argument is required when using the options: DC-CO, DS-CO, DC-ST, DS-ST")

    af = ArgumentationFramework(args.f)

    if args.p in ['SE-CO', 'SE-ST']:
        extensions = (af.find_complete_extensions() if args.p == 'SE-CO'
                      else af.find_stable_extensions())
        # Print extensions or "NO" if no extensions are found
        print(str(extensions).replace("'", "") if extensions else "NO")
    elif args.p in ['DC-CO', 'DS-CO', 'DC-ST', 'DS-ST']:
        query_argument = args.a
        extensions = (af.find_complete_extensions() if 'CO' in args.p
                      else af.find_stable_extensions())
        result = (af.is_credulously_accepted(query_argument, extensions) if 'DC' in args.p
                  else af.is_skeptically_accepted(query_argument, extensions))
        # Print the result of the query
        print(result)
    else:
        print("Invalid command")


if __name__ == "__main__":
    main()
