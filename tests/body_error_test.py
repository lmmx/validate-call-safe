from pytest import importorskip


def test_signature_ok_body_ve():
    importorskip("examples.body_errors.signature_ok_body_ve")


def test_signature_ok_body_nameerror():
    importorskip("examples.body_errors.signature_ok_body_nameerror")


def test_signature_ok_body_nameerror_captured():
    importorskip("examples.body_errors.signature_ok_body_nameerror_captured")
