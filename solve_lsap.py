import numpy as np
from scipy.optimize import linear_sum_assignment


def solve_lsap(C: np.ndarray):
    """
    Solve the Linear Sum Assignment Problem (minimize the sum of ranks) using SciPy.

    Parameters
    ----------
    C : np.ndarray, shape (n, m)
        Cost matrix where C[i, j] is the rank (1…K) that student i assigns to topic j,
        or np.inf if topic j is not in student i's preference list.

    Returns
    -------
    assignment : np.ndarray, shape (n,)
        For each student i, the index j of the assigned topic.
    total_cost : float
        The total sum of ranks over all students.
    """
    row_ind, col_ind = linear_sum_assignment(C)
    total_cost = C[row_ind, col_ind].sum()
    assignment = col_ind
    return assignment, total_cost
