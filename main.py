from __future__ import annotations

import argparse
import random
import time
from collections import deque
from enum import Enum
from typing import Dict, List, Optional

import matplotlib.colors as mcolors

from CSP import CSP
from Solver import Solver
from graphics import draw
from map_generator import generate_borders_by_continent


class Continent(Enum):
    asia = "Asia"
    africa = "Africa"
    america = "America"
    europe = "Europe"

    def __str__(self) -> str:
        return self.value


def available_colors(color_num: int) -> List[str]:
    palette = sorted(dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS).keys())
    if color_num > len(palette):
        raise ValueError(f"Requested {color_num} colors, but only {len(palette)} are available.")
    return random.sample(palette, color_num)


def fill_csp(csp: CSP, borders: Dict[str, List[str]], color_num: int) -> CSP:
    """Populate CSP from borders graph and uniform color domain."""
    countries = list(borders.keys())
    csp.unassigned_var = list(countries)
    color_domain = available_colors(color_num)

    for country in countries:
        csp.add_variable(country, color_domain)

    constraint_func = lambda x, y: x != y
    seen_edges = set()
    for country, neighbors in borders.items():
        for neighbor in neighbors:
            if neighbor not in borders:
                continue
            edge = tuple(sorted((country, neighbor)))
            if edge in seen_edges:
                continue
            seen_edges.add(edge)
            csp.add_constraint(constraint_func, [country, neighbor])

    return csp


def bfs(adj_list: Dict[str, List[str]], start_node: str, max_depth: int) -> List[str]:
    visited = {start_node}
    queue = deque([(start_node, 0)])
    result: List[str] = []

    while queue:
        node, depth = queue.popleft()
        if depth == max_depth:
            continue

        for neighbor in adj_list.get(node, []):
            if neighbor in visited:
                continue
            visited.add(neighbor)
            result.append(neighbor)
            queue.append((neighbor, depth + 1))

    return result


def n_distance_neighborhood(adj_list: Dict[str, List[str]], max_depth: int) -> Dict[str, List[str]]:
    return {node: bfs(adj_list, node, max_depth) for node in adj_list}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="Map Coloring",
        description="Utilizing CSP to solve map coloring problem",
    )
    parser.add_argument(
        "-m",
        "--map",
        type=Continent,
        choices=list(Continent),
        required=True,
        help="Map must be: [Asia, Africa, America, Europe]",
    )
    parser.add_argument("-lcv", "--lcv", action="store_true", help="Enable least constraining value (LCV)")
    parser.add_argument("-mrv", "--mrv", action="store_true", help="Enable minimum remaining values (MRV)")
    parser.add_argument("-ac3", "--arc-consistency", action="store_true", help="Enable AC-3 arc consistency")
    parser.add_argument(
        "-ND",
        "--neighborhood-distance",
        "--Neighborhood-distance",
        dest="neighborhood_distance",
        type=int,
        default=1,
        help="Include neighbors up to this distance (default: 1)",
    )
    parser.add_argument("-cn", "--color-num", type=int, default=4, help="Exact number of colors to use")
    return parser.parse_args()


def solve_map(
    continent: str,
    color_num: int,
    neighborhood_distance: int,
    use_lcv: bool,
    use_mrv: bool,
    use_ac3: bool,
) -> tuple[Optional[Dict[str, str]], int, float]:
    """Solve a continent map with an exact color count."""
    borders = generate_borders_by_continent(continent=continent)
    if neighborhood_distance > 1:
        borders = n_distance_neighborhood(borders, neighborhood_distance)

    csp = fill_csp(CSP(), borders, color_num)
    solver = Solver(
        csp=csp,
        domain_heuristics=use_lcv,
        variable_heuristics=use_mrv,
        AC_3=use_ac3,
        forward_checking=True,
    )

    start_time = time.time()
    result = solver.backtrack_solver()
    elapsed = time.time() - start_time

    if result is None:
        return None, solver.csp.assignments_number, elapsed

    final_result = {country: color for country, color in result}
    return final_result, solver.csp.assignments_number, elapsed


def main() -> int:
    args = parse_args()
    if args.neighborhood_distance < 1:
        raise ValueError("Neighborhood distance must be >= 1.")
    if args.color_num < 1:
        raise ValueError("Color count must be >= 1.")

    solution, assignments_number, elapsed = solve_map(
        continent=str(args.map),
        color_num=args.color_num,
        neighborhood_distance=args.neighborhood_distance,
        use_lcv=args.lcv,
        use_mrv=args.mrv,
        use_ac3=args.arc_consistency,
    )

    if solution is None:
        print(
            f"No solution found for {args.map} with neighborhood distance {args.neighborhood_distance} "
            f"using exactly {args.color_num} colors in {elapsed:.3f}s "
            f"({assignments_number} assignments)."
        )
        return 1

    print(
        f"Solved {args.map} with neighborhood distance {args.neighborhood_distance} "
        f"using {args.color_num} colors in {elapsed:.3f}s "
        f"({assignments_number} assignments)."
    )
    draw(solution=solution, continent=str(args.map), assignments_number=assignments_number)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
