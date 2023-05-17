import pytest


from eBCSgen.Errors.ComplexParsingError import ComplexParsingError
from eBCSgen.Parsing.ParseBCSL import Parser, TransformAbstractSyntax


def test_insert_atomic_to_complex_unspecified_first():
    parser_atomic = Parser("atomic")
    parser_value = Parser("value")

    string_atomic = "A{i}"
    string_value = "B(S{p}).A{_}.A{d}"

    result_atomic = parser_atomic.syntax_check(string_atomic).data.children[0]
    result_value = parser_value.syntax_check(string_value).data.children[0]

    transformer = TransformAbstractSyntax(set())
    transformed_value = transformer.insert_atomic_to_complex(result_atomic, result_value)

    string_expected = "B(S{p}).A{i}.A{d}"
    result_expected = parser_value.syntax_check(string_expected).data.children[0]

    assert transformed_value == result_expected


def test_insert_atomic_to_complex_specified():
    parser_atomic = Parser("atomic")
    parser_value = Parser("value")

    string_atomic = "A{i}"
    string_value = "B(S{p}).A{a}.A{d}"

    result_atomic = parser_atomic.syntax_check(string_atomic).data.children[0]
    result_value = parser_value.syntax_check(string_value).data.children[0]

    transformer = TransformAbstractSyntax(set())

    with pytest.raises(ComplexParsingError):
        _ = transformer.insert_atomic_to_complex(result_atomic, result_value)


def test_insert_atomic_to_complex_unspecified_second():
    parser_atomic = Parser("atomic")
    parser_value = Parser("value")

    string_atomic = "A{i}"
    string_value = "B(S{p}).A{d}.A{_}"

    result_atomic = parser_atomic.syntax_check(string_atomic).data.children[0]
    result_value = parser_value.syntax_check(string_value).data.children[0]

    transformer = TransformAbstractSyntax(set())
    transformed_value = transformer.insert_atomic_to_complex(result_atomic, result_value)

    string_expected = "B(S{p}).A{d}.A{i}"
    result_expected = parser_value.syntax_check(string_expected).data.children[0]

    assert transformed_value == result_expected
