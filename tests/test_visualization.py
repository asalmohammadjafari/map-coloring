from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import graphics
from graphics import draw


def test_visualization_smoke() -> None:
    solution = {
        "USA": "red",
        "CAN": "green",
        "MEX": "blue",
    }
    fig, _ = draw(continent="America", solution=solution, assignments_number=3, show=False)
    assert fig is not None


def test_show_called_in_interactive_mode(monkeypatch) -> None:
    called = {"show": False}

    def fake_show() -> None:
        called["show"] = True

    monkeypatch.setattr(graphics, "_is_non_interactive_backend", lambda: False)
    monkeypatch.setattr(graphics.plt, "show", fake_show)

    draw(continent="America", solution={"USA": "red"}, assignments_number=1, show=True)
    assert called["show"]


def test_show_not_called_in_non_interactive_mode(monkeypatch) -> None:
    called = {"show": False}

    def fake_show() -> None:
        called["show"] = True

    monkeypatch.setattr(graphics, "_is_non_interactive_backend", lambda: True)
    monkeypatch.setattr(graphics.plt, "show", fake_show)

    draw(continent="America", solution={"USA": "red"}, assignments_number=1, show=True)
    assert not called["show"]
