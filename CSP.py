from collections import deque
from typing import Callable, List, Tuple
import random
import matplotlib.colors as mcolors

class CSP(object):
    """
    Represents a Constraint Satisfaction Problem (CSP).

    Attributes:
        variables (dict): A dictionary that maps variables to their domains.
        constraints (list): A list of constraints in the form of [constraint_func, *variables].
        unassigned_var (list): A list of unassigned variables.
        var_constraints (dict): A dictionary that maps variables to their associated constraints.

    Methods:
        add_constraint(constraint_func, variables): Adds a constraint to the CSP.
        add_variable(variable, domain): Adds a variable to the CSP with its domain.
    """

    def __init__(self, *args, **kwargs) -> None:
        """ Initializes the CSP object with its attributes. """
        self.variables = {}
        self.constraints = []
        self.unassigned_var = []
        self.var_constraints = {}
        self.assignments = {}
        self.assignments_number = 0
        self.complete_domain = None

    def add_constraint(self, constraint_func: Callable, variables: List[str]) -> None:
        """ Adds a constraint between two variables. """
        if variables[0] not in self.var_constraints:
            self.var_constraints[variables[0]] = [(constraint_func, variables[1])]
        else:
            self.var_constraints[variables[0]].append((constraint_func, variables[1]))
        if variables[1] not in self.var_constraints:
            self.var_constraints[variables[1]] = [(constraint_func, variables[0])]
        else:
            self.var_constraints[variables[1]].append((constraint_func, variables[0]))

    def add_variable(self, variable: str, domain: List) -> None:
        """ Adds a variable to the CSP with its domain. """
        self.variables[variable] = domain
        self.complete_domain = domain

    def assign(self, variable: str, value) -> bool:
        """ Assigns a value to a variable and checks consistency. """
        self.assignments[variable] = value
        self.unassigned_var.remove(variable)
        self.variables[variable] = [value]
        return self.is_consistent(variable, value)

    def is_consistent(self, variable: str, value) -> bool:
        """ Checks if a value assignment violates any constraints. """
        constraints = self.var_constraints.get(variable, [])
        if value not in self.variables[variable]:
            return False
        if variable not in self.var_constraints:
            return True  # No constraints, so the assignment is always consistent
        for constraint in constraints:
            if not constraint[0](self.assignments[constraint[1]], value):
                return False
        return True
    
    def is_complete(self) -> bool:
        """ Checks if all variables have been assigned. """
        return len(self.unassigned_var) == 0

    def is_assigned(self, variable: str) -> bool:
        """ Checks if a variable has been assigned a value. """
        return self.assignments.get(variable) is not None

    def unassign(self, removed_values_from_domain: List[Tuple[str, any]], variable: str) -> None:
        """ Unassigns a variable and restores its domain. """
        if variable in self.assignments:
            self.assignments[variable] = None
            self.unassigned_var.append(variable)
        self.variables[variable] = self.complete_domain
