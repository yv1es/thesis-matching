#!/usr/bin/env python3
import argparse
import numpy as np
from solve_lsap import solve_lsap
from solve_lbap import solve_lbap


def parse_topics(path):
    topics = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            topics.append(line)
    return topics


def parse_priorities(path):
    students = []
    prefs = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if ":" not in line:
                raise ValueError(f"Bad format in priorities file: {line!r}")
            student, rest = line.split(":", 1)
            student = student.strip()
            # split on commas into integers
            nums = [int(x.strip()) for x in rest.split(",") if x.strip()]
            # check for duplicate priorities
            if len(nums) != len(set(nums)):
                raise ValueError(
                    f"Duplicate priorities for student {student!r}: {nums}"
                )
            students.append(student)
            prefs.append(nums)
    return students, prefs


def build_cost_matrix(preferences, num_topics):
    n = len(preferences)
    C = np.full((n, num_topics), np.inf)
    for i, prefs in enumerate(preferences):
        for rank, topic_no in enumerate(prefs, start=1):
            j = topic_no - 1
            if j < 0 or j >= num_topics:
                raise IndexError(f"Preference {topic_no} out of range (1–{num_topics})")
            C[i, j] = rank
    return C


def compute_metrics(C, assignment):
    ranks = np.array([C[i, j] for i, j in enumerate(assignment)])
    return ranks.mean(), ranks.max()


def main():
    p = argparse.ArgumentParser(
        prog="main.py", description="Assign topics to students via LSAP & LBAP"
    )
    p.add_argument("topics_file", help="one topic per line")
    p.add_argument("priorities_file", help="lines like 'Name: 1, 2, 3'")
    p.add_argument(
        "-o",
        "--output",
        help="output file to write results to (default: stdout)",
        type=str,
        default=None,
    )
    args = p.parse_args()

    # Parse input files
    topics = parse_topics(args.topics_file)
    students, preferences = parse_priorities(args.priorities_file)

    # ensure all students have the same number of priorities
    if preferences:
        expected = len(preferences[0])
        for student, prefs in zip(students, preferences):
            if len(prefs) != expected:
                raise ValueError(
                    f"Student {student!r} has {len(prefs)} priorities; expected {expected}."
                )

    # Build cost matrix and solve
    C = build_cost_matrix(preferences, len(topics))
    lsap_assign, _ = solve_lsap(C)
    lbap_assign, _ = solve_lbap(C)

    # Collect output lines
    lines = []
    # LSAP
    lines.append("=== LSAP Assignment ===")
    lsap_avg, lsap_max = compute_metrics(C, lsap_assign)
    for i, student in enumerate(students):
        t = lsap_assign[i]
        lines.append(f"  {student:10s} → {topics[t]:10s}   (prio {int(C[i, t])})")
    lines.append(f"Avg prio: {lsap_avg:.2f}, Max prio: {lsap_max}")
    lines.append("")
    # LBAP
    lines.append("=== LBAP Assignment ===")
    lbap_avg, lbap_max = compute_metrics(C, lbap_assign)
    for i, student in enumerate(students):
        t = lbap_assign[i]
        lines.append(f"  {student:10s} → {topics[t]:10s}   (prio {int(C[i, t])})")
    lines.append(f"Avg prio: {lbap_avg:.2f}, Max prio: {lbap_max}")

    # Output to file or stdout
    if args.output:
        with open(args.output, "w") as f:
            for line in lines:
                f.write(line + "\n")
                print(line)
    else:
        for line in lines:
            print(line)


if __name__ == "__main__":
    main()
