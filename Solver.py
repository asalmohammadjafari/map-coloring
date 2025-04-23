from __future__ import annotations

from collections import deque
from typing import Dict, List, Optional, Tuple

from CSP import CSP


class Solver:
    """Backtracking CSP solver with MRV, LCV, forward checking, and AC-3."""

    def __init__(
        self,
        csp: CSP,
        domain_heuristics: bool = False,
        variable_heuristics: bool = False,
        AC_3: bool = False,
        forward_checking: bool = True,
    ) -> None:
        self.domain_heuristic = domain_heuristics
        self.variable_heuristic = variable_heuristics
        self.AC_3 = AC_3
        self.forward_checking = forward_checking
        self.csp = csp

    def backtrack_solver(self) -> Optional[List[Tuple[str, str]]]:
        if self.AC_3 and not self.apply_AC3():
            return None

        result = self._backtrack()
        if result is None:
            return None
        return [(var, value) for var, value in result.items()]

    def _backtrack(self) -> Optional[Dict[str, str]]:
        if self.csp.is_complete():
            return {
                var: self.csp.assignments[var]
                for var in self.csp.variables
                if self.csp.assignments[var] is not None
            }

        variable = self.select_unassigned_variable()
        domain_values = self.ordered_domain_value(variable)

        for value in domain_values:
            if not self.csp.is_consistent(variable, value):
                continue

            self.csp.assign(variable, value)
            self.csp.assignments_number += 1

            changes: List[Tuple[str, str, int]] = []
            self._restrict_assigned_domain(variable, value, changes)
            assignment_valid = True

            if self.forward_checking:
                assignment_valid = self.forward_check(variable, value, changes)

            ac3_valid = True
            if assignment_valid and self.AC_3:
                ac3_valid, ac3_changes = self.apply_AC3(collect_changes=True)
                changes.extend(ac3_changes)

            if assignment_valid and ac3_valid:
                result = self._backtrack()
                if result is not None:
                    return result

            self.restore_domains(changes)
            self.csp.unassign(variable)

        return None

    def select_unassigned_variable(self) -> str:
        if self.variable_heuristic:
            return self.MRV()
        return self.csp.unassigned_var[0]

    def ordered_domain_value(self, variable: str) -> List[str]:
        if self.domain_heuristic:
            return self.LCV(variable)
        return list(self.csp.domains[variable])

    def forward_check(
        self,
        variable: str,
        value: str,
        changes: List[Tuple[str, str, int]],
    ) -> bool:
        """Prune inconsistent values from unassigned neighbors."""
        for neighbor in self.csp.neighbors.get(variable, []):
            if self.csp.is_assigned(neighbor):
                continue

            for neighbor_value in list(self.csp.domains[neighbor]):
                if not self._satisfies_pair(variable, value, neighbor, neighbor_value):
                    removal_index = self.csp.domains[neighbor].index(neighbor_value)
                    self.csp.domains[neighbor].remove(neighbor_value)
                    changes.append((neighbor, neighbor_value, removal_index))

            if not self.csp.domains[neighbor]:
                return False
        return True

    def restore_domains(self, changes: List[Tuple[str, str, int]]) -> None:
        """Undo domain pruning in reverse order."""
        for variable, value, index in reversed(changes):
            if value not in self.csp.domains[variable]:
                insert_at = min(index, len(self.csp.domains[variable]))
                self.csp.domains[variable].insert(insert_at, value)

    def apply_AC3(
        self,
        collect_changes: bool = False,
    ) -> bool | Tuple[bool, List[Tuple[str, str, int]]]:
        queue = deque(self.csp.constraints)
        changes: List[Tuple[str, str, int]] = []

        while queue:
            xi, xj = queue.popleft()
            revised, removed = self.revise(xi, xj)
            if revised:
                changes.extend((xi, value, index) for value, index in removed)
                if not self.csp.domains[xi]:
                    if collect_changes:
                        return False, changes
                    return False
                for xk in self.csp.neighbors.get(xi, set()):
                    if xk != xj:
                        queue.append((xk, xi))

        if collect_changes:
            return True, changes
        return True

    def revise(self, xi: str, xj: str) -> Tuple[bool, List[Tuple[str, int]]]:
        """Remove values in domain[xi] unsupported by domain[xj]."""
        revised = False
        removed: List[Tuple[str, int]] = []
        for value_i in list(self.csp.domains[xi]):
            if not any(self._satisfies_pair(xi, value_i, xj, value_j) for value_j in self.csp.domains[xj]):
                removal_index = self.csp.domains[xi].index(value_i)
                self.csp.domains[xi].remove(value_i)
                removed.append((value_i, removal_index))
                revised = True
        return revised, removed

    def MRV(self) -> str:
        candidates = [var for var in self.csp.unassigned_var if not self.csp.is_assigned(var)]
        return min(candidates, key=lambda var: len(self.csp.domains[var]))

    def LCV(self, variable: str) -> List[str]:
        """Order values by how little they constrain unassigned neighbors."""
        value_conflicts = {}
        for value in self.csp.domains[variable]:
            conflicts = 0
            for neighbor in self.csp.neighbors.get(variable, []):
                if self.csp.is_assigned(neighbor):
                    continue
                conflicts += sum(
                    not self._satisfies_pair(variable, value, neighbor, neighbor_value)
                    for neighbor_value in self.csp.domains[neighbor]
                )
            value_conflicts[value] = conflicts

        return sorted(self.csp.domains[variable], key=lambda val: value_conflicts[val])

    def _restrict_assigned_domain(
        self,
        variable: str,
        value: str,
        changes: List[Tuple[str, str, int]],
    ) -> None:
        """Keep only the assigned value in the variable domain for this branch."""
        for other in list(self.csp.domains[variable]):
            if other == value:
                continue
            removal_index = self.csp.domains[variable].index(other)
            self.csp.domains[variable].remove(other)
            changes.append((variable, other, removal_index))

    def _satisfies_pair(self, left: str, left_value: str, right: str, right_value: str) -> bool:
        """Evaluate all binary constraints between two variables."""
        constraints = self.csp.var_constraints.get(left, [])
        for constraint_fn, neighbor in constraints:
            if neighbor == right and not constraint_fn(left_value, right_value):
                return False
        return True
