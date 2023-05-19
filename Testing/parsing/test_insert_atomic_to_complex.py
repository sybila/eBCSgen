import pytest


from eBCSgen.Errors.ComplexParsingError import ComplexParsingError
from eBCSgen.Parsing.ParseBCSL import Parser, TransformAbstractSyntax


@pytest.mark.parametrize('string_atomic, string_value, string_expected', [
    ["A{i}", "B(S{p}).A{_}.A{d}", "B(S{p}).A{i}.A{d}"],
    ["A{i}", "B(S{p}).A{d}.A{_}", "B(S{p}).A{d}.A{i}"]
])
def test_insert_atomic_to_complex_correct_input(string_atomic, string_value, string_expected):
    parser_atomic = Parser("atomic")
    parser_value = Parser("value")

    result_atomic = parser_atomic.syntax_check(string_atomic).data.children[0]
    result_value = parser_value.syntax_check(string_value).data.children[0]

    transformer = TransformAbstractSyntax(set())
    transformed_value = transformer.insert_atomic_to_complex(result_atomic, result_value)

    result_expected = parser_value.syntax_check(string_expected).data.children[0]

    assert transformed_value == result_expected


@pytest.mark.parametrize('string_atomic, string_value', [
    ["A{i}", "B(S{p}).A{a}.A{d}"],
    ["A{_}", "B(S{p}).A{d}.A{a}"]
])
def test_insert_atomic_to_complex_incorrect_input(string_atomic, string_value):
    parser_atomic = Parser("atomic")
    parser_value = Parser("value")

    result_atomic = parser_atomic.syntax_check(string_atomic).data.children[0]
    result_value = parser_value.syntax_check(string_value).data.children[0]

    transformer = TransformAbstractSyntax(set())

    with pytest.raises(ComplexParsingError):
        _ = transformer.insert_atomic_to_complex(result_atomic, result_value)
