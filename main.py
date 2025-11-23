#!/usr/bin/env python3
import argparse
import csv
import numpy as np
from solve_lsap import solve_lsap
from solve_lbap import solve_lbap


def parse_topics(path):
    """
    Parse topics from a CSV file with header:

        id,name,capacity

    - id:       unique integer topic ID
    - name:     string, required
    - capacity: integer, optional; defaults to 1 if empty/missing

    Returns:
        topic_ids   : list[int]
        topics      : list[str]
        capacities  : list[int]
    """
    topic_ids = []
    topics = []
    capacities = []
    seen_ids = set()

    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        if "id" not in reader.fieldnames or "name" not in reader.fieldnames:
            raise ValueError("topics_file must have columns: id,name,capacity")

        for row in reader:
            if not row:
                continue

            raw_id = (row.get("id") or "").strip()
            name = (row.get("name") or "").strip()
            cap_raw = (row.get("capacity") or "").strip()

            if not raw_id and not name:
                continue
            if not raw_id:
                raise ValueError(f"Topic with name {name!r} is missing an 'id'.")
            if not name:
                raise ValueError(f"Topic with id {raw_id!r} is missing a 'name'.")

            try:
                tid = int(raw_id)
            except ValueError:
                raise ValueError(f"Invalid topic id {raw_id!r} (must be integer).")

            if tid in seen_ids:
                raise ValueError(f"Duplicate topic id {tid} in topics file.")
            seen_ids.add(tid)

            cap = int(cap_raw) if cap_raw else 1
            if cap <= 0:
                raise ValueError(
                    f"Topic id {tid} must have a positive capacity, got {cap}."
                )

            topic_ids.append(tid)
            topics.append(name)
            capacities.append(cap)

    if not topic_ids:
        raise ValueError("No topics found in topics file.")

    return topic_ids, topics, capacities


def parse_priorities(path, valid_topic_ids):
    """
    Parse priorities from a CSV file with header:

        name,prio1,prio2,prio3,...

    - name:   string, required
    - prioX:  integer topic IDs; each must be in valid_topic_ids

    Returns:
        students    : list[str]
        preferences : list[list[int]]  (topic IDs in ranked order)
    """
    students = []
    prefs = []

    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        if "name" not in reader.fieldnames:
            raise ValueError("priorities_file must have a 'name' column.")

        for row in reader:
            if not row:
                continue

            student = (row.get("name") or "").strip()
            if not student:
                continue

            prio_ids = []
            for key, value in row.items():
                if key == "name":
                    continue
                cell = (value or "").strip()
                if not cell:
                    continue
                try:
                    tid = int(cell)
                except ValueError:
                    raise ValueError(
                        f"Invalid topic id {cell!r} in priorities for student "
                        f"{student!r} (must be an integer)."
                    )
                if tid not in valid_topic_ids:
                    raise ValueError(
                        f"Student {student!r} refers to unknown topic id {tid} "
                        "in priorities."
                    )
                prio_ids.append(tid)

            if not prio_ids:
                raise ValueError(f"Student {student!r} has no priorities specified.")
            if len(prio_ids) != len(set(prio_ids)):
                raise ValueError(
                    f"Duplicate topic ids in priorities for student {student!r}: "
                    f"{prio_ids}"
                )

            students.append(student)
            prefs.append(prio_ids)

    if not students:
        raise ValueError("No students found in priorities file.")

    return students, prefs


def build_cost_matrix(preferences, topic_ids):
    """
    Build base cost matrix C (without capacities).

    topic_ids: list[int] - determines the column order.

    C[i, j] = rank (1 = best) of topic_ids[j] for student i,
    or np.inf if the student did not list that topic.
    """
    id_to_index = {tid: j for j, tid in enumerate(topic_ids)}
    n, m = len(preferences), len(topic_ids)
    C = np.full((n, m), np.inf)

    for i, prefs in enumerate(preferences):
        for rank, topic_id in enumerate(prefs, start=1):
            j = id_to_index.get(topic_id)
            if j is None:
                raise ValueError(
                    f"Preference topic id {topic_id} not found in topics list."
                )
            C[i, j] = rank

    return C


def expand_cost_matrix_with_capacities(C_base, capacities):
    """
    Expand a base cost matrix C_base (N x M) into a slot-based matrix (N x S),
    where each topic j is replicated capacities[j] times.

    Returns:
        C_slots       : np.ndarray, shape (N, S)
        slot_to_topic : np.ndarray, shape (S,), mapping slot index -> topic index j
    """
    cols = []
    slot_to_topic = []
    for j, cap in enumerate(capacities):
        for _ in range(cap):
            cols.append(C_base[:, [j]])
            slot_to_topic.append(j)

    if not cols:
        raise ValueError(
            "No topic capacity available (all capacities are non-positive)."
        )

    C_slots = np.hstack(cols)
    slot_to_topic = np.array(slot_to_topic, dtype=int)
    return C_slots, slot_to_topic


def compute_metrics(C_base, assignment_slots, slot_to_topic):
    """
    Compute average, worst, and standard deviation of ranks for a slot assignment.

    Returns:
        avg_rank      : float
        max_rank      : float
        std_rank      : float
        topic_indices : np.ndarray of length N (topic index per student)
    """
    assignment_slots = np.asarray(assignment_slots)
    topic_indices = slot_to_topic[assignment_slots]
    ranks = np.array([C_base[i, j] for i, j in enumerate(topic_indices)])
    avg = ranks.mean()
    max_ = ranks.max()
    std = ranks.std(ddof=0)
    return avg, max_, std, topic_indices


def main():
    p = argparse.ArgumentParser(
        prog="main.py",
        description="Assign topics to students via LSAP & LBAP",
    )
    p.add_argument(
        "topics_file",
        help="CSV with header: id,name,capacity (capacity optional, defaults to 1)",
    )
    p.add_argument(
        "priorities_file",
        help=(
            "CSV with header: name,prio1,prio2,... "
            "(each prio is a topic id from topics_file)"
        ),
    )
    p.add_argument(
        "-o",
        "--output",
        help="output file to write results to (default: stdout)",
        type=str,
        default=None,
    )
    args = p.parse_args()

    topic_ids, topics, capacities = parse_topics(args.topics_file)
    valid_topic_ids = set(topic_ids)
    students, preferences = parse_priorities(args.priorities_file, valid_topic_ids)

    expected = len(preferences[0])
    for student, prefs in zip(students, preferences):
        if len(prefs) != expected:
            raise ValueError(
                f"Student {student!r} has {len(prefs)} priorities; expected {expected}."
            )

    C_base = build_cost_matrix(preferences, topic_ids)

    num_students = len(students)
    total_capacity = sum(capacities)
    if total_capacity < num_students:
        raise ValueError(
            f"Total topic capacity ({total_capacity}) is smaller than the number "
            f"of students ({num_students}). Matching is impossible."
        )

    C_slots, slot_to_topic = expand_cost_matrix_with_capacities(C_base, capacities)

    lsap_assign_slots, _ = solve_lsap(C_slots)
    lbap_assign_slots, _ = solve_lbap(C_slots)

    lsap_avg, lsap_max, lsap_std, lsap_topic_indices = compute_metrics(
        C_base, lsap_assign_slots, slot_to_topic
    )
    lbap_avg, lbap_max, lbap_std, lbap_topic_indices = compute_metrics(
        C_base, lbap_assign_slots, slot_to_topic
    )

    lines = []

    lines.append("=== LSAP Assignment ===")
    for i, student in enumerate(students):
        j = int(lsap_topic_indices[i])
        topic_name = topics[j]
        rank = int(C_base[i, j])
        lines.append(f"  {student:10s} → {topic_name:10s}   (prio {rank})")
    lines.append(
        f"Avg prio: {lsap_avg:.2f}, Std prio: {lsap_std:.2f}, Worst prio: {lsap_max}"
    )
    lines.append("")

    lines.append("=== LBAP Assignment ===")
    for i, student in enumerate(students):
        j = int(lbap_topic_indices[i])
        topic_name = topics[j]
        rank = int(C_base[i, j])
        lines.append(f"  {student:10s} → {topic_name:10s}   (prio {rank})")
    lines.append(
        f"Avg prio: {lbap_avg:.2f}, Std prio: {lbap_std:.2f}, Worst prio: {lbap_max}"
    )

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
