import argparse
from enum import Enum
from CSP import CSP
import time
from Solver import Solver
from map_generator import generate_borders_by_continent
from graphics import draw
from collections import deque
import random
import matplotlib.colors as mcolors

class Continent(Enum):
    asia = "Asia"
    africa = "Africa"
    america = "America"
    europe = "Europe"

    def __str__(self):
        return self.value

def fill_csp(csp: CSP, countries, borders, color_num):
    all_colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)
    constraint_func = lambda x, y: x != y
    seed = random.randint(1, 1000000)

    csp.unassigned_var = countries
    for country in countries:
        neighbor_removed = []
        for neighbor in borders[country]:
            if neighbor not in countries:
                neighbor_removed.append(neighbor)
            else:
                csp.add_constraint(constraint_func, [country, neighbor])
                csp.constraints.append((country, neighbor))

        borders[country] = [i for i in borders[country] if i not in neighbor_removed]

    for country in countries:
        random.seed(seed)
        csp.add_variable(country, random.sample(list(all_colors.keys()), color_num))
        csp.assignments[country] = None

    return csp

def bfs(adj_list, start_node, n):
    visited = set()
    queue = deque([(start_node, 0)])
    layer_dict = {}

    while queue:
        node, layer = queue.popleft()
        if layer not in layer_dict:
            layer_dict[layer] = []
        if node not in visited:
            visited.add(node)
            layer_dict[layer].append(node)
            if layer < n:
                for neighbor in adj_list.get(node, []):
                    queue.append((neighbor, layer + 1))

    result = []
    for key, value in layer_dict.items():
        if key != 0:
            result.extend(value)
    return result

def n_distance_neighborhood(adj_list, n):
    nth_layer_dict = {}
    for node in adj_list:
        nth_layer_dict[node] = bfs(adj_list, node, n)
    return nth_layer_dict

def main():
    """
    Main function to solve the map coloring problem using CSP.
    """
    parser = argparse.ArgumentParser(
        prog="Map Coloring",
        description="Utilizing CSP to solve map coloring problem",
    )
    parser.add_argument("-m", "--map", type=Continent, choices=list(Continent),
                        help="Map must be: [Asia, Africa, America, Europe]")
    parser.add_argument("-lcv", "--lcv", action="store_true", help="Enable least constraint value (LCV) as an optimizer")
    parser.add_argument("-mrv", "--mrv", action="store_true", help="Enable minimum remaining values (MRV) as an optimizer")
    parser.add_argument("-ac3", "--arc-consistency", action="store_true", help="Enable arc consistency to optimize solution")
    parser.add_argument("-ND", "--Neighborhood-distance", type=int, default=1,
                        help="Threshold for neighboring regions' color similarity.")
    parser.add_argument("-cn", "--color-num", type=int, default=4, help="Number of colors to be used for coloring.")

    args = parser.parse_args()
    borders = generate_borders_by_continent(continent=str(args.map))
    countries = list(borders.keys())
    color_num = 3

    if args.Neighborhood_distance > 1:
        borders = n_distance_neighborhood(borders, args.Neighborhood_distance)

    while True:
        color_num += 1
        csp = CSP()
        csp = fill_csp(csp, countries, borders, color_num)

        solver = Solver(csp=csp, domain_heuristics=args.lcv, variable_heuristics=args.mrv, AC_3=args.arc_consistency)
        start = time.time()
        result = solver.backtrack_solver()
        end = time.time()
        t = end - start
        assignments_number = solver.csp.assignments_number
        csv_data = {
            'lcv': args.lcv,
            'mrv': args.mrv,
            'ac3': args.arc_consistency,
            'ND': args.Neighborhood_distance,
            'cn': args.color_num,
            'assignment_number': assignments_number,
            'time': t
        }

        if result:
            print(f"{color_num} colors needed for coloring {str(args.map)} with neighborhood distance {args.Neighborhood_distance}")
            finalresult = {i[0]: i[1] for i in result}
            csv_data["is_solvable"] = True
            csv_filename = f"{args.map}_data.csv"
            draw(solution=finalresult, continent=str(args.map), assignments_number=assignments_number)
            break
        else:
            csv_data["is_solvable"] = False
            csv_filename = f"{args.map}_data.csv"

if __name__ == '__main__':
    main()
