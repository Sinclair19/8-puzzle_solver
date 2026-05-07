import heapq
from itertools import count


PUZZLE_SIZE = 3
BLANK_TILE = 0

OPERATORS = [
    ("Up", -1, 0),
    ("Down", 1, 0),
    ("Left", 0, -1),
    ("Right", 0, 1),
]

GOAL_PUZZLE = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0],
]

GOAL_POSITIONS = {
    tile: (row_index, column_index)
    for row_index, row in enumerate(GOAL_PUZZLE)
    for column_index, tile in enumerate(row)
}

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


class SearchNode:
    def __init__(self, state, parent=None, move=None, g_cost=0, h_cost=0):
        self.state = copy_puzzle(state)
        self.parent = parent
        self.move = move
        self.g_cost = g_cost
        self.h_cost = h_cost

    def f_cost(self):
        return self.g_cost + self.h_cost


def main():
    print("Welcome to my 8-Puzzle Solver.")
    puzzle = get_initial_puzzle()
    algorithm_choice = get_algorithm_choice()
    show_trace = get_trace_choice()
    heuristic_function = get_heuristic_function(algorithm_choice)

    print("\nInitial puzzle:")
    print_puzzle(puzzle)
    print(f"Selected algorithm: {ALGORITHMS[algorithm_choice]}")

    solution_node, nodes_expanded, max_queue_size = general_search(
        puzzle,
        heuristic_function,
        show_trace,
    )

    if solution_node is None:
        print("\nNo solution was found.")
        print(f"Number of nodes expanded: {nodes_expanded}")
        print(f"Max queue size: {max_queue_size}")
        return

    print("\nGoal state!")
    print(f"Solution depth was {solution_node.g_cost}")
    print(f"Number of nodes expanded: {nodes_expanded}")
    print(f"Max queue size: {max_queue_size}")
    print_solution_path(solution_node)


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
    tiles = flatten_puzzle(puzzle)
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


def get_trace_choice():
    print("\nShow every expanded state?")
    print("Press Enter for no, or type 'y' to show the full trace.")
    choice = input("Show trace? ").strip().lower()
    return choice == "y" or choice == "yes"


def print_puzzle(puzzle):
    for row in puzzle:
        print(row)


def copy_puzzle(puzzle):
    return [row[:] for row in puzzle]


def flatten_puzzle(puzzle):
    tiles = []
    for row in puzzle:
        tiles.extend(row)
    return tiles


def puzzle_to_tuple(puzzle):
    return tuple(flatten_puzzle(puzzle))


def is_goal_puzzle(puzzle):
    return puzzle == GOAL_PUZZLE


def general_search(initial_state, heuristic_function, show_trace=False):
    nodes = make_queue(make_initial_node(initial_state, heuristic_function))
    best_g_cost_by_state = {
        puzzle_to_tuple(initial_state): 0,
    }
    explored_states = set()
    nodes_expanded = 0
    max_queue_size = len(nodes["heap"])

    while True:
        if is_queue_empty(nodes):
            return None, nodes_expanded, max_queue_size

        node = remove_front(nodes)
        state_key = puzzle_to_tuple(node.state)

        if state_key in explored_states:
            continue

        if show_trace:
            print_expanded_node(node)

        if is_goal_puzzle(node.state):
            return node, nodes_expanded, max_queue_size

        explored_states.add(state_key)
        nodes_expanded += 1
        child_nodes = expand_node(node, heuristic_function)
        queueing_function(nodes, child_nodes, best_g_cost_by_state, explored_states)
        max_queue_size = max(max_queue_size, len(nodes["heap"]))


def make_queue(initial_node):
    nodes = {
        "heap": [],
        "tie_breaker": count(),
    }
    add_node_to_queue(nodes, initial_node)
    return nodes


def is_queue_empty(nodes):
    return len(nodes["heap"]) == 0


def add_node_to_queue(nodes, node):
    heapq.heappush(
        nodes["heap"],
        (node.f_cost(), node.g_cost, next(nodes["tie_breaker"]), node),
    )


def remove_front(nodes):
    priority, g_cost, tie_breaker, node = heapq.heappop(nodes["heap"])
    return node


def queueing_function(nodes, child_nodes, best_g_cost_by_state, explored_states):
    for child_node in child_nodes:
        child_key = puzzle_to_tuple(child_node.state)

        if child_key in explored_states:
            continue

        best_known_g_cost = best_g_cost_by_state.get(child_key)
        if best_known_g_cost is not None and best_known_g_cost <= child_node.g_cost:
            continue

        best_g_cost_by_state[child_key] = child_node.g_cost
        add_node_to_queue(nodes, child_node)


def make_initial_node(initial_state, heuristic_function):
    return SearchNode(
        state=initial_state,
        h_cost=heuristic_function(initial_state),
    )


def make_child_node(parent_node, move_name, child_state, heuristic_function):
    return SearchNode(
        state=child_state,
        parent=parent_node,
        move=move_name,
        g_cost=parent_node.g_cost + 1,
        h_cost=heuristic_function(child_state),
    )


def expand_node(node, heuristic_function):
    child_nodes = []

    for move_name, child_state in expand_puzzle(node.state):
        child_nodes.append(
            make_child_node(node, move_name, child_state, heuristic_function)
        )

    return child_nodes


def print_node_costs(node):
    print(
        f"g(n) = {node.g_cost}, "
        f"h(n) = {node.h_cost}, "
        f"f(n) = {node.f_cost()}"
    )


def print_expanded_node(node):
    print(
        "\nThe best state to expand with "
        f"g(n) = {node.g_cost} and h(n) = {node.h_cost} is:"
    )
    print_puzzle(node.state)


def get_solution_path(solution_node):
    path = []
    current_node = solution_node

    while current_node is not None:
        path.append(current_node)
        current_node = current_node.parent

    path.reverse()
    return path


def print_solution_path(solution_node):
    path = get_solution_path(solution_node)

    print("\nSolution path:")
    for index, node in enumerate(path):
        if node.move is None:
            print(f"\nStep {index}: initial state")
        else:
            print(f"\nStep {index}: move blank {node.move}")

        print_puzzle(node.state)


def get_heuristic_function(algorithm_choice):
    if algorithm_choice == "1":
        return uniform_cost_heuristic
    if algorithm_choice == "2":
        return misplaced_tile_heuristic
    if algorithm_choice == "3":
        return manhattan_distance_heuristic

    raise ValueError(f"Unknown algorithm choice: {algorithm_choice}")


def uniform_cost_heuristic(puzzle):
    return 0


def misplaced_tile_heuristic(puzzle):
    misplaced_tiles = 0

    for row_index in range(PUZZLE_SIZE):
        for column_index in range(PUZZLE_SIZE):
            tile = puzzle[row_index][column_index]
            if tile != BLANK_TILE and tile != GOAL_PUZZLE[row_index][column_index]:
                misplaced_tiles += 1

    return misplaced_tiles


def manhattan_distance_heuristic(puzzle):
    total_distance = 0

    for row_index in range(PUZZLE_SIZE):
        for column_index in range(PUZZLE_SIZE):
            tile = puzzle[row_index][column_index]
            if tile == BLANK_TILE:
                continue

            goal_row, goal_column = GOAL_POSITIONS[tile]
            row_distance = abs(row_index - goal_row)
            column_distance = abs(column_index - goal_column)
            total_distance += row_distance + column_distance

    return total_distance


def find_blank_tile(puzzle):
    for row_index in range(PUZZLE_SIZE):
        for column_index in range(PUZZLE_SIZE):
            if puzzle[row_index][column_index] == BLANK_TILE:
                return row_index, column_index

    raise ValueError("Puzzle does not contain a blank tile.")


def is_inside_puzzle(row_index, column_index):
    return (
        0 <= row_index < PUZZLE_SIZE
        and 0 <= column_index < PUZZLE_SIZE
    )


def move_blank_tile(puzzle, row_change, column_change):
    blank_row, blank_column = find_blank_tile(puzzle)
    new_blank_row = blank_row + row_change
    new_blank_column = blank_column + column_change

    if not is_inside_puzzle(new_blank_row, new_blank_column):
        return None

    new_puzzle = copy_puzzle(puzzle)
    new_puzzle[blank_row][blank_column] = new_puzzle[new_blank_row][new_blank_column]
    new_puzzle[new_blank_row][new_blank_column] = BLANK_TILE
    return new_puzzle


def expand_puzzle(puzzle):
    children = []

    for move_name, row_change, column_change in OPERATORS:
        child_puzzle = move_blank_tile(puzzle, row_change, column_change)
        if child_puzzle is not None:
            children.append((move_name, child_puzzle))

    return children


if __name__ == "__main__":
    main()
