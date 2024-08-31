from pytest import importorskip


def test_unbracketted():
    importorskip("examples.non_validation_error.unbracketted")


def test_allowed_raise():
    importorskip("examples.non_validation_error.allowed_raise")
