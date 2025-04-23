from __future__ import annotations

import argparse

import main
from map_generator import generate_borders_by_continent


def test_fill_csp_uses_exact_requested_domain_size() -> None:
    borders = generate_borders_by_continent("Europe")
    csp = main.fill_csp(main.CSP(), borders, 3)
    assert all(len(domain) == 3 for domain in csp.domains.values())


def test_solve_map_respects_requested_color_count() -> None:
    solution, _, _ = main.solve_map(
        continent="Europe",
        color_num=3,
        neighborhood_distance=1,
        use_lcv=True,
        use_mrv=True,
        use_ac3=True,
    )

    if solution is not None:
        assert len(set(solution.values())) <= 3


def test_main_unsat_path_does_not_plot_and_reports_exact_color(monkeypatch, capsys) -> None:
    args = argparse.Namespace(
        map=main.Continent.europe,
        lcv=True,
        mrv=True,
        arc_consistency=True,
        neighborhood_distance=1,
        color_num=3,
    )

    draw_called = {"called": False}

    def fake_draw(**kwargs):
        draw_called["called"] = True

    def fake_solve_map(**kwargs):
        return None, 5, 0.02

    monkeypatch.setattr(main, "parse_args", lambda: args)
    monkeypatch.setattr(main, "solve_map", fake_solve_map)
    monkeypatch.setattr(main, "draw", fake_draw)

    exit_code = main.main()
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "No solution found" in output
    assert "using exactly 3 colors" in output
    assert not draw_called["called"]


def test_main_solution_path_plots_and_reports_exact_color(monkeypatch, capsys) -> None:
    args = argparse.Namespace(
        map=main.Continent.europe,
        lcv=True,
        mrv=True,
        arc_consistency=True,
        neighborhood_distance=1,
        color_num=3,
    )

    captured = {"called": False, "solution": None}

    def fake_draw(**kwargs):
        captured["called"] = True
        captured["solution"] = kwargs["solution"]

    def fake_solve_map(**kwargs):
        return {"A": "red", "B": "green", "C": "blue"}, 7, 0.03

    monkeypatch.setattr(main, "parse_args", lambda: args)
    monkeypatch.setattr(main, "solve_map", fake_solve_map)
    monkeypatch.setattr(main, "draw", fake_draw)

    exit_code = main.main()
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Solved Europe" in output
    assert "using 3 colors" in output
    assert captured["called"]
    assert set(captured["solution"].values()) == {"red", "green", "blue"}
