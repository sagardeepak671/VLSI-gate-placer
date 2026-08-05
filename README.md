# VLSI Gate Placer

Three progressively harder takes on the **physical design** problem at the heart of chip layout:
given a set of rectangular logic gates, where do you put them on the die?

| Stage | Objective | Approach |
|---|---|---|
| **1. Gate Packing** | Minimise bounding-box **area** | Greedy skyline packing, widest-first |
| **2. Wiring-Aware Positioning** | Minimise total **wire length** | Connectivity-driven placement from the most-connected gate outward |
| **3. Timing Optimisation** | Minimise **critical-path delay** | Longest-path analysis over the gate graph, placement guided by timing |

Each stage is a self-contained Python program reading `input.txt` and writing `output.txt`, with
sample test cases and a Tkinter visualiser.

> Built for **COL215 – Digital Logic and System Design** at IIT Delhi (software assignments 1–3).

---

## Table of Contents

- [Why This Problem Matters](#why-this-problem-matters)
- [Environment Setup](#environment-setup)
- [Running](#running)
- [Stage 1 — Gate Packing](#stage-1--gate-packing)
- [Stage 2 — Wiring-Aware Gate Positioning](#stage-2--wiring-aware-gate-positioning)
- [Stage 3 — Timing Optimisation](#stage-3--timing-optimisation)
- [Visualisation](#visualisation)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

---

## Why This Problem Matters

Placement is one of the classic NP-hard steps in the VLSI design flow, and the three objectives here
genuinely conflict:

- Packing tightly minimises **area**, but can force connected gates far apart.
- Placing connected gates together minimises **wire length**, but wastes area.
- Neither optimises **delay**, which depends only on the *longest* path through the circuit — a
  single badly placed gate on the critical path costs more than a hundred well-placed ones off it.

Real EDA tools attack this with simulated annealing, analytical placement and partitioning. These
solutions use fast constructive heuristics, which makes the trade-offs easy to see and easy to
measure against the provided test cases.

---

## Environment Setup

| Requirement | Needed for |
|---|---|
| Python 3.8+ | All three solutions |
| `tkinter` | Visualisers |
| `pillow` | Visualisers (transparency) |

The solvers themselves use **only the standard library** — no numpy, no external packages.

<details open>
<summary><b>Set up a virtual environment</b></summary>

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install pillow                 # only if you want the visualisers
```
</details>

<details>
<summary><b>Installing tkinter</b></summary>

```bash
# Debian / Ubuntu
sudo apt install -y python3-tk

# macOS (Homebrew Python)
brew install python-tk

# Windows — bundled with the python.org installer
```
</details>

Verify:

```bash
python3 -c "import tkinter, PIL; print('ok')"
```

---

## Running

Every solution reads `input.txt` from the **current working directory** and writes `output.txt`
there. So copy a test case in first:

```bash
cd "1-Gate Packing"
cp sample_test_case_1/input.txt .
python3 code.py
cat output.txt
```

Compare against the expected result:

```bash
diff output.txt sample_test_case_1/output.txt
```

Run every case for a stage:

```bash
cd "1-Gate Packing"
for tc in sample_test_case_*; do
  cp "$tc/input.txt" .
  python3 code.py
  echo "== $tc"; head -1 output.txt
done
```

---

## Stage 1 — Gate Packing

Pack rectangles into the smallest possible bounding box. No rotation, no overlap.

### Input

```
g1 3 10
g2 8 3
g3 6 6
```

`<gate-id> <width> <height>`

### Output

```
bounding_box 11 10
g1 0 0
g2 3 7
g3 3 1
```

### Algorithm

A **skyline / shelf** heuristic:

1. Sort gates by width, **widest first** — large pieces are hardest to place later.
2. Place the first gate at the origin; it seeds the bounding box and the initial free-space list.
3. For each subsequent gate, evaluate every candidate free space plus the option of extending the
   bounding box in width, and pick whichever yields the **smallest resulting area**.
4. Update the free-space list and the bounding box.

`O(n log n)` for the sort plus `O(n · |spaces|)` for placement — fast, and within a few percent of
optimal on the sample cases. It is a greedy heuristic, so it offers no optimality guarantee; that is
the honest trade for the speed.

---

## Stage 2 — Wiring-Aware Gate Positioning

Now gates have **pins** at fixed offsets, and **wires** connect pin to pin. Minimise total wire
length, measured as Manhattan distance between connected pins.

### Input

```
g1 3 3
pins g1 0 1 0 2 3 1 3 2
g2 4 1
pins g2 0 1 4 0
...
wire g3.p2 g7.p1
wire g7.p2 g3.p1
wire g5.p5 g3.p1
```

- `g<id> <width> <height>` — gate dimensions
- `pins g<id> x1 y1 x2 y2 …` — pin offsets relative to the gate's lower-left corner; pins are
  numbered `p1`, `p2`, … in order
- `wire g<a>.p<i> g<b>.p<j>` — a connection

### Output

```
bounding_box 18 12
g1 0 0
g2 2 6
...
wire_length 51
```

### Algorithm

**Connectivity-first constructive placement:**

1. Count each gate's connections and sort **descending** — the most-connected gate is the natural
   anchor, since misplacing it costs the most.
2. Place that pivot, then walk its neighbours. For each unplaced neighbour, try candidate positions
   around the already-placed cluster and keep the one minimising the incremental Manhattan wire
   length across all its existing connections.
3. Recurse outward until the whole netlist is placed.
4. Report the bounding box and the total wire length.

The insight is that wire length is dominated by a handful of high-fanout gates, so placing them
first and letting everything else fall into place around them beats optimising uniformly.

---

## Stage 3 — Timing Optimisation

Gates now have an intrinsic **delay**, and wires add delay proportional to their length. Minimise
the **critical-path delay** — the longest delay from any primary input to any primary output.

### Input

```
g1 4 3 2                  # width, height, gate delay
pins g1 0 2 4 1
g2 3 2 1
pins g2 0 0 3 2
...
wire_delay 2              # delay per unit of wire length
wire g1.p2 g3.p2
wire g2.p2 g3.p1
```

### Output

```
bounding_box 14 5
critical_path g1.p1 g1.p2 g3.p2 g3.p3 g4.p1 g4.p2 g5.p1 g5.p2
critical_path_delay 37
g1 0 0
g2 1 3
...
```

### Algorithm

1. Build the circuit as a **directed graph**: gates are nodes, wires are edges, each carrying a
   delay of `gate_delay + wire_delay × manhattan_length`.
2. Compute the **longest path** through the DAG — the critical path. On a DAG this is linear-time
   via topological order; unlike shortest-path problems, the *longest* path is what matters here.
3. Place gates so that critical-path edges are short, using a `Part`-based recursive partitioning
   that keeps timing-critical clusters physically close.
4. Re-evaluate after placement and emit the realised critical path and its delay.

The key asymmetry: shortening a wire off the critical path does nothing for delay. Only the longest
path matters — which is why timing optimisation and wire-length optimisation give different layouts.

---

## Visualisation

Both visualisers open a Tkinter window rendering gates as translucent rectangles, with pins and
wires drawn on top.

```bash
cd "1-Gate Packing"
python3 visualize_gates.py --input input.txt --output output.txt

cd "../2-Wiring-aware Gate Positioning/visualization program"
python3 visualization.py
```

Run `python3 visualize_gates.py --help` for the exact flags.

---

## Project Structure

```
.
├── 1-Gate Packing/
│   ├── code.py                 # 112 lines — skyline packing
│   ├── visualize_gates.py      # Tkinter renderer
│   ├── sample_test_case_1-5/   # input.txt + expected output.txt
│   └── COL215_SW_1_v2.pdf
│
├── 2-Wiring-aware Gate Positioning/
│   ├── main.py                 # 193 lines — connectivity-driven placement
│   ├── visualization program/visualization.py
│   ├── sample_test_case_1-4/
│   ├── COL215_SW_2-1.pdf
│   └── Readme.pdf              # design write-up
│
└── 3-Timing Optimisation in Gate/
    ├── main.py                 # 488 lines — timing graph + partitioned placement
    ├── Sample_test_case_1-2/
    ├── COL215_SW_3.pdf
    └── ReadMe.pdf              # design write-up
```

Each stage's PDF holds the original problem statement; the `Readme.pdf` files contain the design
rationale and complexity analysis submitted with the assignment.

---

## Contributing

Contributions are welcome. Good first issues:

- Accept input/output paths as CLI arguments instead of hard-coded `input.txt` / `output.txt`
- Add a **simulated annealing** post-pass over the greedy placement and measure the improvement
- Add a scoring script that runs all test cases and reports area / wire length / delay in a table
- Allow 90° gate rotation in stage 1 — often a significant area win
- Replace the Tkinter visualisers with an SVG writer so results can be embedded in a README
- Add unit tests for the critical-path computation in stage 3

```bash
git checkout -b feat/your-change
cd "1-Gate Packing" && cp sample_test_case_1/input.txt . && python3 code.py
diff output.txt sample_test_case_1/output.txt
git commit -m "feat: describe your change"
```

Any change to a heuristic should come with before/after objective values on every sample test case.

---

## License

Released for educational use. Problem statements belong to their original authors.
