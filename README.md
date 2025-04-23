# 🗺️ Map Coloring with CSP

An extensible implementation of the map coloring problem using **Constraint Satisfaction Problems (CSP)**.

The solver colors countries so that neighboring regions do not share the same color, with optional heuristics and inference for faster search.

## 🧭 Overview

This project models map coloring as a binary CSP:
- Variables: countries
- Domains: available colors
- Constraints: adjacent countries must have different colors

Supports neighborhood-distance expansion beyond direct borders.

## ⚙️ Features

- Backtracking search
- MRV (Minimum Remaining Values) variable selection
- LCV (Least Constraining Value) value ordering
- Forward checking with safe domain rollback
- AC-3 arc consistency propagation
- Continent-level solving (`Asia`, `Africa`, `America`, `Europe`)
- Map visualization with country labels
- Pytest suite for solver correctness and visualization smoke checks

## 🚀 Usage

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

### 2) Run solver

```bash
python main.py -m Europe -mrv -lcv -ac3 -ND 1 -cn 4
```

### CLI options

- `-m, --map`: continent (`Asia`, `Africa`, `America`, `Europe`) (required)
- `-mrv, --mrv`: enable MRV
- `-lcv, --lcv`: enable LCV
- `-ac3, --arc-consistency`: enable AC-3
- `-ND, --neighborhood-distance`: adjacency distance threshold (default `1`)
- `-cn, --color-num`: exact number of colors to use (default `4`)

## 💡 Example

```bash
python main.py -m Asia -mrv -lcv -ac3
```

## 📂 Project Structure

- `main.py`: CLI and solve loop
- `CSP.py`: CSP state and constraints model
- `Solver.py`: backtracking, MRV, LCV, forward checking, AC-3
- `map_generator.py`: builds borders graph from dataset
- `graphics.py`: map visualization
- `countries_dataset.csv`: country geometry + neighbor data
- `tests/`: automated tests

## 🧪 Tests

Run:

```bash
python -m pytest -q
```