def axis_free(game, x, y, axis):
    """
    Returns True if a box at (x,y) can be pushed along the given axis.
    axis = 0 → horizontal (left/right), axis = 1 → vertical (up/down)
    A box can only move on an axis if both immediate neighbours in that
    direction are free (not walls and inside the grid).
    """
    width  = game.get_grid_width()
    height = game.get_grid_height()
    if axis == 0:          # horizontal
        left  = x - 1
        right = x + 1
        left_ok  = (left >= 0) and not game.is_wall((left, y))
        right_ok = (right < width) and not game.is_wall((right, y))
        return left_ok and right_ok
    else:                  # vertical
        up   = y - 1
        down = y + 1
        up_ok    = (up >= 0) and not game.is_wall((x, up))
        down_ok  = (down < height) and not game.is_wall((x, down))
        return up_ok and down_ok


def is_deadlocked(box, targets, game):
    """
    Simple deadlock detection for a single box.
    Returns True if the box is stuck and cannot reach any target.
    """
    x, y = box

    # A box already on a target is never deadlocked
    if (x, y) in targets:
        return False

    # Check if the box can move at all (in either axis)
    can_move_horiz = axis_free(game, x, y, 0)
    can_move_vert  = axis_free(game, x, y, 1)

    # If both axes are blocked → box is frozen and not on target → dead
    if not can_move_horiz and not can_move_vert:
        return True

    # Optional: add more patterns here if needed (wall line deadlocks, etc.)
    # For now, the simple freeze check catches most common deadlocks.

    return False

def assignment_min_cost(cost_matrix):
    """
    Hungarian algorithm (Kuhn‑Munkres) for minimum‑cost perfect matching
    on a square cost matrix.

    input:  cost_matrix – list of lists, cost_matrix[i][j] is the cost
            of assigning row i to column j.
    returns: assignment list `a` where `a[i] = j` means row i is matched
             to column j, giving the minimum total cost.

    Time complexity: O(n³), where n = len(cost_matrix).
    """
    n = len(cost_matrix)
    u = [0] * (n + 1)          # potentials for rows
    v = [0] * (n + 1)          # potentials for columns
    p = [0] * (n + 1)          # p[j] = row currently assigned to column j
    way = [0] * (n + 1)        # backtracking pointers

    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = [float('inf')] * (n + 1)
        used = [False] * (n + 1)

        # Dijkstra‑like step to find an augmenting path
        while True:
            used[j0] = True
            i0 = p[j0]
            delta = float('inf')
            j1 = 0
            for j in range(1, n + 1):
                if not used[j]:
                    cur = cost_matrix[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta:
                        delta = minv[j]
                        j1 = j

            # Update potentials
            for j in range(n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta

            j0 = j1
            if p[j0] == 0:
                break

        # Augment the matching
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break

    # Build the resulting assignment (0‑based indices)
    assignment = [0] * n
    for j in range(1, n + 1):
        if p[j] != 0:
            assignment[p[j] - 1] = j - 1
    return assignment