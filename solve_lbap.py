import numpy as np
import networkx as nx


def solve_lbap(C: np.ndarray):
    """
    Solve the Linear Bottleneck Assignment Problem (minimize the worst rank)
    via binary search + Hopcroft–Karp matching (NetworkX).

    Parameters
    ----------
    C : np.ndarray, shape (n, m)
        Cost matrix where C[i, j] is the rank (1…K) that student i assigns to topic j,
        or np.inf if topic j is not in student i’s preference list.

    Returns
    -------
    assignment : np.ndarray, shape (n,)
        For each student i, the index j of the assigned topic.
    worst_rank : int
        The minimal achievable maximum rank across all students.
    """
    n, m = C.shape
    k_max = int(np.nanmax(C[np.isfinite(C)]))
    C_int = np.where(np.isinf(C), k_max + 1, C).astype(int)

    def feasible(T: int):
        """
        Check if there exists a perfect matching using only edges with cost <= T.
        """
        G = nx.Graph()
        # Add student nodes (0…n-1) and topic nodes (n…n+m-1)
        G.add_nodes_from(range(n), bipartite=0)
        G.add_nodes_from(range(n, n + m), bipartite=1)
        # Add edges for every (i, j) with cost <= T
        rows, cols = np.where(C_int <= T)
        edges = ((i, j + n) for i, j in zip(rows, cols))
        G.add_edges_from(edges)

        matching = nx.algorithms.bipartite.matching.maximum_matching(
            G, top_nodes=range(n)
        )
        return (len(matching) // 2 == n), matching

    # Binary search for the smallest T allowing a perfect matching
    lo, hi, best_match = 1, k_max, None
    while lo < hi:
        mid = (lo + hi) // 2
        ok, match = feasible(mid)
        if ok:
            hi, best_match = mid, match
        else:
            lo = mid + 1

    assignment = np.full(n, -1, dtype=int)
    for u, v in best_match.items():
        if u < n:
            assignment[u] = v - n

    return assignment, hi
