PUZZLE_SIZE = 3
BLANK_TILE = 0

DEFAULT_PUZZLES = {
    "1": (
        "Trivial",
        [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 0],
        ],
    ),
    "2": (
        "Very Easy",
        [
            [1, 2, 3],
            [4, 5, 6],
            [7, 0, 8],
        ],
    ),
    "3": (
        "Easy",
        [
            [1, 2, 0],
            [4, 5, 3],
            [7, 8, 6],
        ],
    ),
    "4": (
        "Doable",
        [
            [0, 1, 2],
            [4, 5, 3],
            [7, 8, 6],
        ],
    ),
    "5": (
        "Hard",
        [
            [8, 7, 1],
            [6, 0, 2],
            [5, 4, 3],
        ],
    ),
}

ALGORITHMS = {
    "1": "Uniform Cost Search",
    "2": "A* with the Misplaced Tile heuristic",
    "3": "A* with the Manhattan Distance heuristic",
}


def main():
    print("Welcome to my 8-Puzzle Solver.")
    puzzle = get_initial_puzzle()
    algorithm_choice = get_algorithm_choice()

    print("\nInitial puzzle:")
    print_puzzle(puzzle)
    print(f"Selected algorithm: {ALGORITHMS[algorithm_choice]}")


def get_initial_puzzle():
    while True:
        print("\nType '1' to use a default puzzle, or '2' to create your own.")
        choice = input("Choice: ").strip()

        if choice == "1":
            return get_default_puzzle()
        if choice == "2":
            return get_custom_puzzle()

        print("Please enter either 1 or 2.")


def get_default_puzzle():
    print("\nChoose a default puzzle:")
    for key, (name, puzzle) in DEFAULT_PUZZLES.items():
        print(f"{key}. {name}")
        print_puzzle(puzzle)

    while True:
        choice = input("Default puzzle number: ").strip()
        if choice in DEFAULT_PUZZLES:
            name, puzzle = DEFAULT_PUZZLES[choice]
            print(f"Selected {name}.")
            return copy_puzzle(puzzle)

        print(f"Please enter a number from 1 to {len(DEFAULT_PUZZLES)}.")


def get_custom_puzzle():
    print("\nEnter your puzzle, using 0 to represent the blank.")
    print("Enter each row as three numbers separated by spaces.")

    while True:
        puzzle = []
        puzzle.append(read_puzzle_row("first"))
        puzzle.append(read_puzzle_row("second"))
        puzzle.append(read_puzzle_row("third"))

        if is_valid_puzzle(puzzle):
            return puzzle

        print("\nInvalid puzzle. Use each number from 0 through 8 exactly once.")
        print("Please enter the whole puzzle again.")


def read_puzzle_row(row_name):
    while True:
        raw_row = input(f"Enter the {row_name} row: ").strip()
        pieces = raw_row.split()

        if len(pieces) != PUZZLE_SIZE:
            print("Each row must contain exactly three numbers.")
            continue

        try:
            return [int(piece) for piece in pieces]
        except ValueError:
            print("Rows may only contain numbers.")


def is_valid_puzzle(puzzle):
    tiles = []
    for row in puzzle:
        tiles.extend(row)

    expected_tiles = list(range(PUZZLE_SIZE * PUZZLE_SIZE))
    return sorted(tiles) == expected_tiles


def get_algorithm_choice():
    print("\nSelect algorithm:")
    for key, name in ALGORITHMS.items():
        print(f"{key}. {name}")

    while True:
        choice = input("Algorithm number: ").strip()
        if choice in ALGORITHMS:
            return choice

        print("Please enter 1, 2, or 3.")


def print_puzzle(puzzle):
    for row in puzzle:
        print(row)


def copy_puzzle(puzzle):
    return [row[:] for row in puzzle]


if __name__ == "__main__":
    main()
