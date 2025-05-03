# Thesis matching

In a class with $N$ students, there is a set of $M$ topics to choose from. Each student must receive exactly **one** topic, each topic may be taken by **at most one** student.

Each student submits a list of priorities (place 1 = highest preference, place $K$ = lowest). From this information, an *optimal matching* student → subject is to be determined.

The document describes two common fairness criteria, classifies them in the optimization literature - **Linear Sum Assignment Problem** (LSAP) and **Linear Bottleneck Assignment Problem** (LBAP) - and shows how to solve both cases in Python.

---

## 1 Fairness variants

### 1.1 Overall satisfaction (sum of ranks)

For each student, the rank of the topic actually assigned is added up. Goal: **minimize the sum** - the smaller, the higher the average satisfaction.

Example

```
Student A → Subject C (rank 4)
Student B → Topic B (rank 1)
------------------------------
Total sum = 5
```

### 1.2 Worst-case satisfaction (worst rank)

Only the most dissatisfied student is of interest here. Goal: **Minimization of the maximum rank**.

Example

```
Student A → Subject C (rank 4)
Student B → Subject B (rank 1)
------------------------------
Maximum rank = 4
```

---

## 2 Mathematical modeling

The students' priorities can be encoded with a cost matrix $C$:

$$
C \in \{1,\dots,K,\infty\}^{N\times M}, \quad \text{with} \quad C_{i,j} = \text{rank of student }i\text{ for topic }j\quad(\text{or} =\infty \text{ if no priority}).
$$

Matching can be performed with decision variables $x_{i,j} \in \{0,1\}$ with $x_{i,j}=1$ if student $i$ receives topic $j$.

The following conditions apply:
* Each student exactly one topic: $\sum_{j} x_{i,j} = 1$
* Each topic at most one student: $\sum_{i} x_{i,j} \le 1$

For objective (1.1), this results in a **linear sum assignment problem (LSAP)** (minimize weight sum).

Objective (1.2) results in a **linear bottleneck assignment problem (LBAP)** (minimize maximum weight).

Efficient algorithms find the optimal solution for both problems in polynomial time.

---

## 3 Python solutions

To solve the LSAP we use the implementation of the Jonker-Volgenant algorithm in SciPy (see solve_lsap.py).

To solve the LBAP, we use binary search and Hopcroft-Karp matching in NetworkX to find the smallest graph that has a perfect matching - “small” in the sense that it only contains edges with high priority (see solve_lbap.py).


## 4 Installation

1. clone repository:

   ```bash
   git clone https://github.com/dein-nutzername/thesis-matching.git
   cd thesis-matching
   ```
2. create a virtual environment (optional, but recommended):

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

The main script `main.py` can be used to assign topics to students. The syntax is

```bash
python main.py [OPTIONS] <topics_file> <priorities_file>
```

* `<topics_file>`: A text file in which each line contains a topic
* `<priorities_file>`: A text file in which each line specifies a student's priority list, e.g. `Alice: 4, 5, 2`.

### Options

* `-o, --output <output_file>`: Saves the output in `<output_file>`

### Examples

There are two example files in the `examples/` folder:

* `examples/topics.txt`:

  ```
  1. Alpha
  2. Beta
  3. Gamma
  ...
  ```
* `examples/prios.txt`:

  ```
  Alice:    6, 7, 8, 9, 10, 1, 2, 3, 4, 5
  Bob:      6, 8, 7, 10, 9, 11, 12, 13, 14, 15
  Charly:   6, 7, 9, 8, 10, 16, 17, 18, 19, 20
  ...
  ```

Show assignment on the console:

```bash
python main.py examples/topics.txt examples/prios.txt
```

Save the assignment to a file:

```bash
python main.py -o out.txt examples/topics.txt examples/prios.txt
```
