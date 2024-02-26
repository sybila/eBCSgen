import pytest

from Testing.models.get_model_str import get_model_str
import Testing.objects_testing as objects


def test_complexes_in_abstract_sequence():
    # is allowed
    model = get_model_str("model_cmplx_in_abstr_seq1")
    ret1 = objects.model_parser.parse(model)
    assert ret1.success

    # should be allowed
    model = get_model_str("model_cmplx_in_abstr_seq2")
    ret2 = objects.model_parser.parse(model)
    assert ret2.success
    assert ret1.data == ret2.data
