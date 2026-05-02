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