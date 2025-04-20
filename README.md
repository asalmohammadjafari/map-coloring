# 🌍 **Advanced Map Coloring with Neighborhood Awareness**

This project provides a solution to the **map coloring problem** using **Constraint Satisfaction Problems (CSP)**. The goal is to color continents such that no two adjacent countries share the same color. You can also define the **Neighbourhood-distance** parameter to include neighbors' neighbors, extending adjacency relationships for more complex constraints.

## 🚀 **Installation**

**Recommended Python version: Python 3.10.9**

To install dependencies, run:

```bash
pip install -r requirements.txt
```

## 📂 **Contents**

- **CSP.py**: Defines the `CSP` class to represent the problem and manage variables, constraints, and assignments.
- **graphics.py**: Functions for visualizing the colored map. 🎨
- **map_generator.py**: Generates a dictionary of countries and their borders for CSP constraints.
- **Solver.py**: Contains the `Solver` class with algorithms for **MRV**, **LCV**, and **AC-3** heuristics.
- **main.py**: The executable to run the program with various parameters.

## ⚙️ **Parameters**

- `-m, --map`: Choose the continent (Asia, Africa, America, Europe).
- `-lcv, --lcv`: Enable the **Least Constraining Value (LCV)** heuristic.
- `-mrv, --mrv`: Enable the **Minimum Remaining Values (MRV)** heuristic.
- `-ac3, --arc-consistency`: Enable the **AC-3** algorithm for arc consistency.
- `-ND, --Neighbourhood-distance`: Set the threshold for neighboring regions' similarity in color (default: `1`).

## 🏃‍♂️ **Running the Code**

### Examples:
- **Color Asia with LCV and MRV**:
  ```bash
  python main.py -m Asia -lcv -mrv
  ```

- **Enable Arc-Consistency with LCV and MRV**:
  ```bash
  python main.py -m Europe -lcv -mrv -ac3
  ```

- **Add Neighbourhood-distance** (e.g., `2` for neighbors' neighbors):
  ```bash
  python main.py -m Europe -lcv -mrv -ac3 -ND 2
  ```

You can also track the number of assignments made during each run to compare algorithm performance. 📊

