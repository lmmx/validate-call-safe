from pytest import importorskip


def test_example_simple():
    importorskip("examples.simple_safe")
