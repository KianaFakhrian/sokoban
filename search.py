import collections
from queue import PriorityQueue
from script import assignment_min_cost


def bfs_solve(game):
    """
    Breadth‑First Search (unweighted).
    Guarantees the shortest path in terms of number of actions.
    """
    start_state = game.get_initial_state()

    # Queue elements: (current_state, action_list, total_cost)
    queue = collections.deque([(start_state, [], 0)])

    # Visited set holds (player_pos, frozenset_of_boxes) to detect duplicates.
    # Using the combination of player position and box positions (as a frozenset)
    # uniquely identifies a state, even if State objects are not hashable.
    visited = set()
    visited.add((start_state.player, start_state.boxes))

    while queue:
        current_state, path, cost = queue.popleft()

        if game.is_goal(current_state):
            return path

        for action, next_state, step_cost in game.get_successors(current_state):
            next_key = (next_state.player, next_state.boxes)

            if next_key not in visited:
                visited.add(next_key)
                queue.append((next_state, path + [action], cost + step_cost))

    return None   # No solution found


def ids_solve(game):
    """
    Iterative Deepening Search (IDS).
    Calls Depth‑Limited Search (DLS) with increasing depth limits.
    Guarantees the shallowest solution (fewest actions), uses O(d) memory.
    """
    start_state = game.get_initial_state()
    max_depth = 100   # safety cap to avoid infinite loops if no solution exists

    for depth in range(max_depth + 1):
        # visited dict: state → highest remaining depth explored for that state.
        # It is fresh for each depth iteration to preserve optimality.
        visited = {}
        result = dls_solve(game, start_state, depth, [], set(), visited)
        if result is not None:
            return result

    return None   # no solution found within max_depth


def dls_solve(game, state, limit, path, on_path, visited):
    """
    Depth‑Limited Search (recursive) with two pruning mechanisms:
      1. `visited` – transposition table recording the maximum remaining depth
         for which a state has already been fully searched. If we see the same
         state with an equal or smaller remaining depth, we skip it.
      2. `on_path` – set of states currently in the recursion stack. This
         prevents cycles inside the current branch, avoiding infinite recursion.
    """
    if game.is_goal(state):
        return path
    if limit <= 0:               # depth cutoff – no more moves allowed
        return None

    # Prune using depth‑aware visited table
    prev_limit = visited.get(state, -1)
    if prev_limit >= limit:
        return None
    visited[state] = limit

    # Cycle detection within the current path
    on_path.add(state)

    for action, next_state, step_cost in game.get_successors(state):
        if next_state in on_path:
            continue             # would create a cycle, skip this branch
        # Recurse with one less allowed move
        result = dls_solve(game, next_state, limit - 1, path + [action],
                           on_path, visited)
        if result is not None:
            on_path.remove(state)   # clean up before returning success
            return result

    on_path.remove(state)           # backtrack: remove from current path
    return None


def ucs_solve(game):
    """
    Uniform‑Cost Search.
    Expands nodes in order of increasing path cost.
    Optimal for any step costs, but memory‑intensive.
    """
    start_state = game.get_initial_state()

    pq = PriorityQueue()
    tiebreak = 0                     # unique tie‑breaker to avoid comparing states
    pq.put((0, tiebreak, start_state, []))
    tiebreak += 1

    best_cost = {start_state: 0}     # best known cost to reach each state
    visited = set()                  # states that have already been expanded

    while not pq.empty():
        cost, _, state, actions = pq.get()

        # Skip if this state was already expanded (its optimal cost was found earlier)
        if state in visited:
            continue
        visited.add(state)

        if game.is_goal(state):
            return actions

        for action, next_state, step_cost in game.get_successors(state):
            new_cost = cost + step_cost
            # Only enqueue if we found a cheaper path to next_state
            if next_state not in best_cost or new_cost < best_cost[next_state]:
                best_cost[next_state] = new_cost
                pq.put((new_cost, tiebreak, next_state, actions + [action]))
                tiebreak += 1

    return None


def astar_solve(game):
    """
    A* search using an externally provided admissible heuristic.
    `heuristic_func(state, game)` should return an estimated cost‑to‑go.
    Uses a PriorityQueue with tie‑breaking and re‑opens nodes when a cheaper
    path is found (required for optimality with inconsistent heuristics).
    """

    def heuristic(state):
        """
        Admissible heuristic for Sokoban‑like puzzles.
        Assumptions:
        - Moving the player costs 1 per step.
        - Pushing a box costs 5 per step (the box moves one cell at cost 5).
        The heuristic computes:
        1. Minimum‑cost assignment of boxes to targets (push cost part).
        2. Minimum player moves to become adjacent to any unsolved box.
        Both are lower bounds, so the total is admissible.
        """
        player = state.get_player_pos()
        boxes = state.get_boxes()          # list / frozenset of (x, y)
        targets = game.get_targets()       # list of (x, y)

        n = len(boxes)
        if n == 0:
            return 0

        # Build cost matrix: 5 * Manhattan distance for each box → target pair.
        # If a box is already on a target, its distance is 0, which is correct.
        cost_matrix = []
        for bx, by in boxes:
            row = [5 * (abs(bx - tx) + abs(by - ty)) for tx, ty in targets]
            cost_matrix.append(row)

        # Solve the assignment problem to get the minimal total push cost.
        assignment = assignment_min_cost(cost_matrix)
        push_cost = sum(cost_matrix[i][assignment[i]] for i in range(n))

        # Player must at some point stand next to a box to push it.
        # The distance to that pushable cell is at least max(0, Manhattan_distance_to_box - 1).
        unsolved = [b for b in boxes if b not in targets]
        if not unsolved:
            return push_cost   # all boxes are already on targets

        player_moves = min(
            max(0, abs(player[0] - bx) + abs(player[1] - by) - 1)
            for bx, by in unsolved
        )

        # Total admissible estimate = push cost + player moves
        return push_cost + player_moves


    start_state = game.get_initial_state()
    start_h = heuristic(start_state)

    pq = PriorityQueue()
    tiebreak = 0
    # Tuple: (f_value, tiebreak, state, g_value, action_list)
    pq.put((start_h, tiebreak, start_state, 0, []))
    tiebreak += 1

    best_g = {start_state: 0}   # best known g‑value for each state

    while not pq.empty():
        f, _, state, g, actions = pq.get()

        # If we already know a cheaper way to reach this state, skip this entry.
        if g > best_g.get(state, float('inf')):
            continue

        if game.is_goal(state):
            return actions

        for action, next_state, step_cost in game.get_successors(state):
            new_g = g + step_cost
            if new_g < best_g.get(next_state, float('inf')):
                best_g[next_state] = new_g
                new_f = new_g + heuristic(next_state)
                pq.put((new_f, tiebreak, next_state, new_g, actions + [action]))
                tiebreak += 1

    return None   # no solution