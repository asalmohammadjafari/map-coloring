from __future__ import annotations

from typing import Dict, Iterable, List

from CSP import CSP


def build_neq_csp(graph: Dict[str, Iterable[str]], domains: Dict[str, List[str]]) -> CSP:
    csp = CSP()
    csp.unassigned_var = list(graph.keys())

    for variable, domain in domains.items():
        csp.add_variable(variable, domain)

    neq = lambda x, y: x != y
    for variable, neighbors in graph.items():
        for neighbor in neighbors:
            csp.add_constraint(neq, [variable, neighbor])

    return csp


def is_complete_assignment(csp: CSP, assignment: Dict[str, str]) -> bool:
    return set(assignment.keys()) == set(csp.variables)


def has_no_neighbor_conflicts(csp: CSP, assignment: Dict[str, str]) -> bool:
    for variable, neighbors in csp.neighbors.items():
        for neighbor in neighbors:
            if assignment[variable] == assignment[neighbor]:
                return False
    return True


def assignment_satisfies_constraints(csp: CSP, assignment: Dict[str, str]) -> bool:
    for variable, constraints in csp.var_constraints.items():
        for constraint_fn, neighbor in constraints:
            if not constraint_fn(assignment[variable], assignment[neighbor]):
                return False
    return True


def domains_non_empty(csp: CSP) -> bool:
    return all(len(domain) > 0 for domain in csp.domains.values())
