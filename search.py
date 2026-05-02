import time
import collections
from queue import PriorityQueue

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
    Iterative Deepening Search (IDS):
    Repeatedly calls Depth-Limited Search (DLS) with increasing depth limits,
    guaranteeing the shallowest goal is found first while using O(d) memory.
    Returns: List of actions (strings) to reach the goal, or None if unsolvable.
    """
    start_state = game.get_initial_state()
    depth = 0
    max_depth = 100  # safety cap to avoid infinite loops if no solution exists

    while depth <= max_depth:
        # visited dict: state → highest remaining depth explored for that state
        # Fresh for each depth iteration to preserve optimality.
        visited = {}
        result = dls_solve(game, start_state, depth, [], set(), visited)
        if result is not None:
            return result
        depth += 1

    return None  # no solution found within max_depth


def dls_solve(game, state, limit, path, on_path, visited):
    """
    Depth-Limited Search with two pruning mechanisms:
      1. 'visited' : prunes states already seen with at least as much remaining depth.
      2. 'on_path'  : prevents cycles within the current recursion branch.

    Returns: action list if goal found, else None.
    """
    if game.is_goal(state):
        return path
    if limit <= 0:           # depth cutoff – stop and backtrack
        return None

    # --- Prune using the depth-aware visited table ---
    # If we already explored this state with a remaining depth ≥ current limit,
    # the current search cannot discover any new solution – skip it.
    prev_limit = visited.get(state, -1)
    if prev_limit >= limit:
        return None
    visited[state] = limit   # mark this as the best depth we've explored it

    # --- Cycle detection within the current path ---
    on_path.add(state)

    for action, next_state, step_cost in game.get_successors(state):
        if next_state in on_path:
            continue          # would create a cycle, skip
        # Recurse with one less move allowed
        result = dls_solve(game, next_state, limit - 1, path + [action], on_path, visited)
        if result is not None:
            on_path.remove(state)   # clean up before returning
            return result

    on_path.remove(state)            # backtrack: remove from current path
    return None


def ucs_solve(game):
    start_state = game.get_initial_state()

    pq = PriorityQueue()
    tiebreak = 0
    pq.put((0, tiebreak, start_state, []))
    tiebreak += 1

    best_cost = {start_state: 0}     # best known cost to reach a state
    visited = set()                  # already expanded states

    while not pq.empty():
        cost, _, state, actions = pq.get()

        # If this state was already expanded, skip
        if state in visited:
            continue

        # Mark as visited
        visited.add(state)

        if game.is_goal(state):
            return actions

        for action, next_state, step_cost in game.get_successors(state):
            new_cost = cost + step_cost
            # If we found a better path, or the state hasn't been seen yet
            if next_state not in best_cost or new_cost < best_cost[next_state]:
                best_cost[next_state] = new_cost
                pq.put((new_cost, tiebreak, next_state, actions + [action]))
                tiebreak += 1

    return None


def astar_solve(game):
    def heuristic():
        pass

    start_state = game.get_initial_state()

    # Your code goes here
    # this function should return actions




