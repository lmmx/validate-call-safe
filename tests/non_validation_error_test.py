from pytest import importorskip

def test_unbracketted():
    importorskip("examples.non_validation_error.unbracketted")
