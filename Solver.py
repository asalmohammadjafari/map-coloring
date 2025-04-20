from collections import deque
from typing import Callable, List, Tuple
from CSP import CSP


class Solver(object):

    def __init__(self, csp: CSP, domain_heuristics: bool = False, variable_heuristics: bool = False, AC_3: bool = False) -> None:
        """
        Initializes the Solver object with CSP and heuristics flags.

        Args:
            csp (CSP): The CSP to be solved.
            domain_heuristics (bool, optional): Flag to use domain heuristics. Defaults to False.
            variable_heuristics (bool, optional): Flag to use variable heuristics. Defaults to False.
            AC_3 (bool, optional): Flag to use AC-3 algorithm. Defaults to False.
        """
        self.domain_heuristic = domain_heuristics
        self.variable_heuristic = variable_heuristics
        self.AC_3 = AC_3
        self.csp = csp

    def backtrack_solver(self) -> List[Tuple[str, str]]:
        def backtrack(assignment):
            # If assignment is complete, return it
            if self.csp.is_complete():
                return assignment
            
            var = self.select_unassigned_variable()
            for value in self.ordered_domain_value(var):
                # Check consistency with constraints
                if self.csp.is_consistent(var, value):
                    self.csp.assign(var, value)
                    if self.AC_3:
                        self.apply_AC3()
                    self.csp.assignments_number += 1
                    
                    result = backtrack(assignment + [(var, value)])
                    # If a solution is found, return it
                    if result is not None:
                        return result
                    
                    # Unassign if no solution
                    self.csp.unassign(value, var)
            return None

        # Start backtracking with an empty assignment
        return backtrack([])

    def select_unassigned_variable(self) -> str:
        """Selects an unassigned variable using MRV heuristic."""
        if self.variable_heuristic:
            return self.MRV() 
        return self.csp.unassigned_var[0]

    def ordered_domain_value(self, variable: str) -> List[str]:
        """Returns domain values for a variable in a specific order."""
        if self.domain_heuristic:
            return self.LCV(variable)
        return self.csp.variables[variable]

    def arc_reduce(self, x, y, consistent) -> List[str]:
        """
        Reduces the domain of variable x based on constraints between x and y.
        """
        result = self.revise(x, y, consistent)
        return list(self.csp.variables[x]) if result else None

    def revise(self, xi, xj, consistent) -> bool:
        """Revises the domain of variable xi based on constraints with xj."""
        revised = False
        removed = []
        for vi in self.csp.variables[xi]:
            if not any(consistent(vi, vj) for vj in self.csp.variables[xj]):
                removed.append(vi)
                revised = True
        self.csp.variables[xi] = [i for i in self.csp.variables[xi] if i not in removed]
        return revised

    def apply_AC3(self) -> None:
        """
        Applies the AC3 algorithm to reduce the domains of variables.
        """
        queue = deque(self.csp.constraints)
        while queue:
            (xi, xj) = queue.popleft()
            if self.revise(xi, xj, lambda a, b: a != b):
                if len(self.csp.variables[xi]) == 0:
                    return False
                for xk in [i for i in self.csp.var_constraints[xi] if i[1] != xj]:
                    queue.append((xk[1], xi))
        return True

    def MRV(self) -> str:
        """Selects the variable with Minimum Remaining Values (MRV)."""
        return min(self.csp.unassigned_var, key=lambda var: len(self.csp.variables[var]))

    def LCV(self, variable: str) -> List[str]:
        """Returns domain values for a variable ordered by Least Constraining Value (LCV)."""
        conflicts_count = {}
        for value in self.csp.variables[variable]:
            conflicts = 0
            for neighbor in self.csp.var_constraints.get(variable, []):
                if not any(constraint[0](self.csp.assignments[neighbor[1]], value) for constraint in self.csp.var_constraints[neighbor[1]]):
                    conflicts += 1
            conflicts_count[value] = conflicts
        return sorted(self.csp.variables[variable], key=lambda value: conflicts_count[value])
