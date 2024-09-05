from pytest import importorskip
from inline_snapshot import snapshot


def test_unbracketted():
    importorskip("examples.simple.default_error_model.unbracketted")


def test_empty_brackets():
    importorskip("examples.simple.default_error_model.bracketted")


def test_bad_return_type():
    importorskip("examples.simple.default_error_model.bad_return_type")


def test_custom_error_model():
    importorskip("examples.simple.custom_error_model")


def test_reporter_simple_print(capsys):
    importorskip("examples.reporting.simple_print")
    stdout, stderr = capsys.readouterr()
    assert stdout == snapshot(
        """\
foo received *(1,), **{}
bar received *(1,), **{}
bar -> int: 1
""",
    )
    assert stderr == snapshot("")


def test_reporter_happy():
    importorskip("examples.reporting.happy")


def test_reporter_custom_error():
    importorskip("examples.reporting.custom_error")


def test_reporter_bad_return():
    importorskip("examples.reporting.bad_return")
