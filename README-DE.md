# Thesis-Matching

In einer Klasse mit $N$ Studenten steht eine Menge von $M$ Themen zur Auswahl. Jeder Student muss genau **ein** Thema erhalten, jedes Thema darf von **höchstens einem** Studenten belegt werden.

Jeder Student reicht dafür eine Prioritätenliste ein (Platz 1 = höchste Präferenz, Platz $K$ = niedrigste). Aus diesen Angaben soll ein *optimales Matching* Student → Thema bestimmt werden.

Das Dokument beschreibt zwei gebräuchliche Fairness-Kriterien, ordnet sie in der Optimierungs-Literatur ein – **Linear Sum Assignment Problem** (LSAP) und **Linear Bottleneck Assignment Problem** (LBAP) – und zeigt, wie man beide Fälle in Python löst.

---

## 1  Fairness-Varianten

### 1.1  Gesamtzufriedenheit (Summe der Ränge)

Für jeden Studenten wird der Rang des tatsächlich zugewiesenen Themas addiert. Ziel: **Minimierung der Summe** – je kleiner, desto höher die durchschnittliche Zufriedenheit.

Beispiel

```
Student A → Thema C  (Rang 4)
Student B → Thema B  (Rang 1)
------------------------------
Gesamtsumme              = 5
```

### 1.2  Worst-Case-Zufriedenheit (schlechtester Rang)

Hier interessiert nur der unzufriedenste Student. Ziel: **Minimierung des maximalen Rangs**.

Beispiel

```
Student A → Thema C  (Rang 4)
Student B → Thema B  (Rang 1)
------------------------------
Maximaler Rang           = 4
```

---

## 2  Mathematische Modellierung

Die Prioritäten der Studenten können mit einer Kostenmatrix $C$ encodiert werden:

$$
C \in \{1,\dots,K,\infty\}^{N\times M}, \quad \text{mit} \quad C_{i,j} := \text{Rang von Student }i\text{ für Thema }j\quad(\text{oder} =\infty \text{ falls keine Priorität}).
$$

Ein Matching kann mit Entscheidungsvariablen $x_{i,j} \in \{0,1\}$ mit $x_{i,j}=1$, wenn Student $i$ Thema $j$ erhält, encodiert werden.

Es gelten folgende Bedingugne:
* Jeder Student genau ein Thema: $\sum_{j} x_{i,j} = 1$
* Jedes Thema höchstens ein Student: $\sum_{i} x_{i,j} \le 1$

Bei Ziel (1.1) ergibt das ein **linear sum assignment problem (LSAP)** (Gewichtssumme minimieren).

Bei Ziel (1.2) entsteht ein **linear bottleneck assignment problem (LBAP)** (maximales Gewicht minimieren).

Effiziente Algorithmen finden für beide Probleme in Polynomzeit die optimale Lösung.

---

## 3  Python-Lösungen

Zum Lösen des LSAP nutzen wir die Implementation des Jonker-Volgenant Algorithmus in SciPy (siehe solve_lsap.py).

Um das LBAP zu lösen, nutzen wir Binärsuche und Hopcroft-Karp-Matching in NetworkX, um den kleinsten Graphen zu finden, welcher ein perfektes Matching hat – „klein“ im Sinne von, er enthält nur Kanten mit hoher Priorität (siehe solve_lbap.py).



## 4 Installation

1. Repository klonen:

   ```bash
   git clone https://github.com/dein-nutzername/thesis-matching.git
   cd thesis-matching
   ```
2. Virtuelle Umgebung anlegen (optional, aber empfohlen):

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Abhängigkeiten installieren:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Mit dem Hauptskript `main.py` kann man Themen zu Studenten zuweisen. Die Syntax lautet:

```bash
python main.py [OPTIONS] <topics_file> <priorities_file>
```

* `<topics_file>`: Eine Textdatei, in der jede Zeile ein Thema enthält
* `<priorities_file>`: Eine Textdatei, in der jede Zeile eine Prioritätenliste eines Studenten angibt, z. B. `Alice: 4, 5, 2`.

### Optionen

* `-o, --output <output_file>`: Speichert die Ausgabe in `<output_file>`

### Beispiele

Im Ordner `examples/` befinden sich zwei Beispiel-Dateien:

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

Zuweisung auf der Konsole anzeigen:

```bash
python main.py examples/topics.txt examples/prios.txt
```

Zuweisung zusätlich in eine Datei speichern:

```bash
python main.py -o out.txt examples/topics.txt examples/prios.txt
```

