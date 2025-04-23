from __future__ import annotations

from copy import deepcopy

from Solver import Solver
from map_generator import generate_borders_by_continent
from tests.helpers import (
    assignment_satisfies_constraints,
    build_neq_csp,
    has_no_neighbor_conflicts,
    is_complete_assignment,
)


def _result_to_dict(result):
    return {var: value for var, value in result}


def test_backtracking_finds_valid_solution_on_triangle() -> None:
    graph = {
        "A": ["B", "C"],
        "B": ["A", "C"],
        "C": ["A", "B"],
    }
    domains = {var: ["red", "green", "blue"] for var in graph}
    csp = build_neq_csp(graph, domains)

    result = Solver(csp, domain_heuristics=True, variable_heuristics=True, AC_3=True).backtrack_solver()

    assert result is not None
    assignment = _result_to_dict(result)
    assert is_complete_assignment(csp, assignment)
    assert has_no_neighbor_conflicts(csp, assignment)
    assert assignment_satisfies_constraints(csp, assignment)


def test_unsatisfiable_triangle_with_two_colors_returns_none() -> None:
    graph = {
        "A": ["B", "C"],
        "B": ["A", "C"],
        "C": ["A", "B"],
    }
    domains = {var: ["red", "green"] for var in graph}
    csp = build_neq_csp(graph, domains)
    original_domains = deepcopy(csp.domains)

    result = Solver(csp, domain_heuristics=True, variable_heuristics=True, AC_3=True).backtrack_solver()

    assert result is None
    assert csp.domains == original_domains


def test_mrv_picks_smallest_domain() -> None:
    graph = {"A": ["B"], "B": ["A"], "C": []}
    domains = {
        "A": ["red", "green", "blue"],
        "B": ["red"],
        "C": ["red", "green"],
    }
    csp = build_neq_csp(graph, domains)

    solver = Solver(csp, variable_heuristics=True)
    assert solver.select_unassigned_variable() == "B"


def test_lcv_orders_less_constraining_value_first() -> None:
    graph = {
        "A": ["B", "C"],
        "B": ["A"],
        "C": ["A"],
    }
    domains = {
        "A": ["1", "2"],
        "B": ["1"],
        "C": ["1", "2"],
    }
    csp = build_neq_csp(graph, domains)

    solver = Solver(csp, domain_heuristics=True)
    assert solver.ordered_domain_value("A") == ["2", "1"]


def test_ac3_detects_inconsistency() -> None:
    graph = {
        "X": ["Y"],
        "Y": ["X", "Z"],
        "Z": ["Y"],
    }
    domains = {
        "X": ["red"],
        "Y": ["red", "green"],
        "Z": ["green"],
    }
    csp = build_neq_csp(graph, domains)

    solver = Solver(csp, AC_3=True)
    assert solver.apply_AC3() is False


def test_real_map_subgraph_solution_is_valid() -> None:
    borders = generate_borders_by_continent("Europe")
    selected = sorted(list(borders.keys()))[:12]
    subgraph = {country: [n for n in borders[country] if n in selected] for country in selected}
    domains = {country: ["red", "green", "blue", "yellow"] for country in selected}
    csp = build_neq_csp(subgraph, domains)

    result = Solver(csp, domain_heuristics=True, variable_heuristics=True, AC_3=True).backtrack_solver()

    assert result is not None
    assignment = _result_to_dict(result)
    assert is_complete_assignment(csp, assignment)
    assert has_no_neighbor_conflicts(csp, assignment)
