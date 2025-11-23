# Thesis Matching

This project assigns $N$ students to a set of $M$ topics based on submitted preference lists.
Each student must receive **exactly one** topic.

Unlike classical one-to-one assignment, topics may now have **capacities**
(e.g. group size 1, 2, 3, …).
A topic with capacity 3 may be assigned to three different students.

Topics are referenced by **unique topic IDs**, not by row number.

Two fairness objectives are supported:

- **LSAP (Linear Sum Assignment Problem):** minimize total dissatisfaction
- **LBAP (Linear Bottleneck Assignment Problem):** minimize the worst individual dissatisfaction

Both objectives are solved optimally using polynomial-time algorithms.

---

## 1 Fairness criteria

### 1.1 Sum of ranks (overall satisfaction)

For each student, take the rank of their assigned topic.
Goal: **minimize the total sum of ranks**.

Example:

```text

Student A → Topic C (rank 4)
Student B → Topic B (rank 1)
----------------------------

Total sum = 5

```

### 1.2 Minimize the worst rank (worst-case fairness)

Only the most dissatisfied student matters.
Goal: **minimize the maximum assigned rank**.

Example:

```text

Student A → Topic C (rank 4)
Student B → Topic B (rank 1)
----------------------------

Worst rank = 4

```

---

## 2 Mathematical model

Student preferences define a cost matrix:

$$
C \in \{1,\dots,K,\infty\}^{N \times M},
\quad
C\_{i,j} = \text{rank of student } i \text{ for topic } j
$$

Decision variables:

$$
x\_{i,j} = 1 \text{ if student } i \text{ receives topic } j
$$

Constraints:

- Every student receives **exactly one** topic: $\sum_j x_{i,j} = 1$

- Every topic receives at most **its capacity**: $\sum_i x_{i,j} \le \text{capacity}(j)$

### Slot expansion

To apply standard LSAP/LBAP solvers, each topic is expanded into as many
**slots** as its capacity (e.g. capacity 3 → A₁, A₂, A₃).

The assignment becomes a one-to-one matching between:

- **N students**
- **S = sum(capacities)** topic-slots

The LSAP/LBAP solvers can then be used unchanged.

---

## 3 Algorithms & Python implementation

### LSAP (minimize total dissatisfaction)

Implemented using SciPy’s **Jonker–Volgenant algorithm**.
See `solve_lsap.py`.

### LBAP (minimize worst dissatisfaction)

Implemented using:

1. Binary search on the maximum allowed rank
2. Hopcroft–Karp bipartite matching via NetworkX

See `solve_lbap.py`.

---

## 4 Installation

```bash
git clone https://github.com/your-user/thesis-matching.git
cd thesis-matching

python3 -m venv venv        # optional
source venv/bin/activate

pip install -r requirements.txt
```

---

## 5 CSV input formats (with explicit IDs)

### 5.1 Topics file: `topics.csv`

Must contain a header:

```csv
id,name,capacity
1,Alpha,1
2,Beta,1
3,Gamma,2
4,Delta,1
...
```

- `id` must be unique
- `capacity` may be empty → defaults to **1**
- Order of rows does **not** matter

### 5.2 Priorities file: `priorities.csv`

Must contain a header:

```csv
name,prio1,prio2,prio3,...
Alice,6,7,8,9,10,1
Bob,6,8,7,10,9,11
...
```

Each `prioX` is a **topic id** referring to the `id` column in `topics.csv`.

---

## 6 Usage

```bash
python main.py [OPTIONS] topics.csv priorities.csv
```

### Options

- `-o FILE` — write output to file as well as printing it

### Example

```bash
python main.py examples/topics.csv examples/priorities.csv
```

Save output:

```bash
python main.py -o out.txt examples/topics.csv examples/priorities.csv
```

---

## 7 Fairness note

The algorithm is **order-independent**:

- student names do not matter
- CSV row order does not matter
- topic order does not matter
- topic IDs do **not** need to be consecutive

Only the **preference ranks** determine the matching.
