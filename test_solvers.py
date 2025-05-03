import numpy as np

from solve_lsap import solve_lsap
from solve_lbap import solve_lbap

# np.random.seed(42)

test_matrices = {
    # everyone has a distinct first choice
    "distinct_first_choice": np.array(
        [
            [1, 3, np.inf, 2, 5, np.inf, 4],
            [2, 1, 4, np.inf, 3, np.inf, 5],
            [np.inf, 2, 1, 4, np.inf, 3, 5],
            [3, np.inf, 2, 1, 4, np.inf, 5],
            [np.inf, 4, 2, 5, 1, 3, np.inf],
        ]
    ),
    # two students share the same first choice
    "shared_top_choice": np.array(
        [
            [2, 3, np.inf, 1, 5, np.inf, 4],
            [1, 2, 4, np.inf, 3, np.inf, 5],
            [np.inf, 2, 1, 4, np.inf, 3, 5],
            [3, np.inf, 2, 1, 4, np.inf, 5],
            [np.inf, 4, 2, 5, 1, 3, np.inf],
        ]
    ),
    # tiny: 2 students, 3 topics
    "tiny_2x3": np.array(
        [
            [1, np.inf, 2],
            [np.inf, 1, 2],
        ]
    ),
    # reversed preferences: each student ranks topics in reverse order
    "reverse_5x7": np.array(
        [
            [7, 6, 5, 4, 3, 2, 1],
            [7, 6, 5, 4, 3, 2, 1],
            [7, 6, 5, 4, 3, 2, 1],
            [7, 6, 5, 4, 3, 2, 1],
            [7, 6, 5, 4, 3, 2, 1],
        ],
        dtype=float,
    ),
    # sparse preferences: many topics not listed
    "sparse_6x6": np.array(
        [
            [1, np.inf, np.inf, 4, np.inf, 2],
            [np.inf, 1, np.inf, np.inf, 3, np.inf],
            [np.inf, np.inf, 1, np.inf, np.inf, 2],
            [4, np.inf, np.inf, 1, np.inf, np.inf],
            [np.inf, 3, np.inf, np.inf, 1, np.inf],
            [np.inf, np.inf, 2, np.inf, np.inf, 1],
        ]
    ),
    # random test: 8 students, 10 topics, ranks 1–5, ~20% unlisted
    "random_8x10": (
        lambda C: (
            C := np.random.randint(1, 6, size=(8, 10)).astype(float),
            mask := (np.random.rand(8, 10) < 0.2),
            C.__setitem__(mask, np.inf),
            C,
        )[-1]
    )(None),
}


def main():
    for name, C in test_matrices.items():
        lsap_assign, _ = solve_lsap(C)
        lbap_assign, _ = solve_lbap(C)

        lsap_avg, lsap_max = compute_metrics(C, lsap_assign)
        lbap_avg, lbap_max = compute_metrics(C, lbap_assign)

        print(f"\n=== {name} instance ===")
        print("LSAP → assignment:", lsap_assign)
        print(f"       avg rank = {lsap_avg:.2f}, max rank = {lsap_max}")
        print("LBAP → assignment:", lbap_assign)
        print(f"       avg rank = {lbap_avg:.2f}, max rank = {lbap_max}")

        print(f"\nCost Matrix: \n{C}")


def compute_metrics(C: np.ndarray, assignment: np.ndarray):
    """
    Given cost matrix C and an assignment array (topic index per student),
    return (average_rank, max_rank) over the students.
    """
    ranks = np.array([C[i, j] for i, j in enumerate(assignment)])
    return ranks.mean(), ranks.max()


if __name__ == "__main__":
    main()
