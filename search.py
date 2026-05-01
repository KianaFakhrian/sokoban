import time
import collections

def bfs_solve(game):
    start_state = game.get_initial_state()

    # Queue stores tuples of: (current_state, path_list, cost)
    queue = collections.deque([(start_state, [], 0)])

    # Set to keep track of visited states.
    # We use a tuple of (player_pos, sorted_boxes) as the key because State objects might not be hashable.
    visited = set()
    # مرتب کردن جعبه ها براساس مختصات ایکس و بعد وای
    visited.add((start_state.player, tuple(sorted(start_state.boxes))))

    while queue:
        current_state, path, cost = queue.popleft()

        # Check if goal is reached
        if game.is_goal(current_state):
            return path

        # Get all possible successor states
        # تولید حالت‌های بعدی (Successors
        successors = game.get_successors(current_state)

        for action, next_state, step_cost in successors:

            next_key = (next_state.player, next_state.boxes)

            if next_key not in visited:
                visited.add(next_key)
                new_path = path + [action]
                new_cost = cost + step_cost
                #adding new state to the end of queue
                queue.append((next_state, new_path, new_cost))

    return None  # No solution found

def ids_solve(game):
    """
    Uses Depth-Limited Search (DLS) with increasing depth limits.
    Returns: List of actions (strings) to reach the goal.
    """
    start_state = game.get_initial_state()
    # Start with depth 0 and increase gradually
    depth = 0
    max_depth = 100 #depth limit

    while depth <= max_depth:
        # checking all the states after depth moves
        result = dls_solve(game, start_state, depth, [])
        if result is not None:
            return result
        depth += 1

    return None  # No solution found within max_depth


def dls_solve(game, current_state, limit, path):
    # Check if goal is reached
    if game.is_goal(current_state):
        return path

    # If limit is reached, stop this branch
    if limit <= 0:
        return None

     # find all the possible moves from the current state
    successors = game.get_successors(current_state)
    #next-state : state after the move, path : list of all actions from start to current state
    for action, next_state, step_cost in successors:
        new_path = path + [action]
        # decrease depth limit for the next step and analysing whether there is a solution
        result = dls_solve(game, next_state, limit - 1, new_path)
        if result is not None:
            return result

    return None


def ucs_solve(game):
    start_state = game.get_initial_state()

    # Your code goes here
    # this function should return actions


def astar_solve(game):
    def heuristic():
        pass

    start_state = game.get_initial_state()

    # Your code goes here
    # this function should return actions




