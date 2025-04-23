from __future__ import annotations

from collections import defaultdict
from typing import Callable, Dict, Iterable, List, Optional, Set, Tuple

ConstraintFn = Callable[[str, str], bool]


class CSP:
    """Binary-constraint CSP container used by the map-coloring solver."""

    def __init__(self) -> None:
        self.variables: List[str] = []
        self.domains: Dict[str, List[str]] = {}
        self.neighbors: Dict[str, Set[str]] = defaultdict(set)
        self.var_constraints: Dict[str, List[Tuple[ConstraintFn, str]]] = defaultdict(list)
        self.constraints: List[Tuple[str, str]] = []

        self.assignments: Dict[str, Optional[str]] = {}
        self.unassigned_var: List[str] = []
        self.assignments_number: int = 0

    def add_variable(self, variable: str, domain: Iterable[str]) -> None:
        """Register a variable with an independent mutable domain list."""
        domain_list = list(domain)
        self.variables.append(variable)
        self.domains[variable] = domain_list
        self.assignments[variable] = None

    def add_constraint(self, constraint_func: ConstraintFn, variables: List[str]) -> None:
        """Register an undirected binary constraint between exactly two variables."""
        if len(variables) != 2:
            raise ValueError("Only binary constraints are supported.")

        left, right = variables
        self.var_constraints[left].append((constraint_func, right))
        self.var_constraints[right].append((constraint_func, left))
        self.neighbors[left].add(right)
        self.neighbors[right].add(left)

        # Store both arc directions once for AC-3 queue initialization.
        if (left, right) not in self.constraints:
            self.constraints.append((left, right))
        if (right, left) not in self.constraints:
            self.constraints.append((right, left))

    def is_assigned(self, variable: str) -> bool:
        return self.assignments.get(variable) is not None

    def is_complete(self) -> bool:
        return all(self.assignments[var] is not None for var in self.variables)

    def is_consistent(self, variable: str, value: str) -> bool:
        """Check if assigning value to variable is consistent with assigned neighbors."""
        for constraint_fn, neighbor in self.var_constraints.get(variable, []):
            neighbor_value = self.assignments.get(neighbor)
            if neighbor_value is None:
                continue
            if not constraint_fn(value, neighbor_value):
                return False
        return True

    def assign(self, variable: str, value: str) -> None:
        self.assignments[variable] = value
        if variable in self.unassigned_var:
            self.unassigned_var.remove(variable)

    def unassign(self, variable: str) -> None:
        if variable in self.assignments:
            self.assignments[variable] = None
        if variable not in self.unassigned_var:
            self.unassigned_var.append(variable)
