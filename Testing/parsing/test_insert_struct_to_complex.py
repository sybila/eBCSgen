import pytest


from eBCSgen.Errors.ComplexParsingError import ComplexParsingError
from eBCSgen.Parsing.ParseBCSL import Parser, TransformAbstractSyntax


@pytest.mark.parametrize('string_structure, string_value, string_expected', [
    ["B(S{i})", "B().A{_}.B(S{a}).A{d}", "B(S{i}).A{_}.B(S{a}).A{d}"],
    ["B()", "B().A{_}.B(S{a}).A{d}", "B().A{_}.B(S{a}).A{d}"],
    ["B(S{i})", "B(S{a}).A{_}.B().A{d}", "B(S{a}).A{_}.B(S{i}).A{d}"],
    ["B(S{i})", "B(T{a}).A{_}.B().A{d}", "B(T{a},S{i}).A{_}.B().A{d}"]
])
def test_insert_struct_to_complex_correct_input(string_structure, string_value, string_expected):
    parser_structure = Parser("structure")
    parser_value = Parser("value")

    result_structure = parser_structure.syntax_check(string_structure).data.children[0]
    result_value = parser_value.syntax_check(string_value).data.children[0]

    transformer = TransformAbstractSyntax(set())
    transformed_value = transformer.insert_struct_to_complex(result_structure, result_value)

    result_expected = parser_value.syntax_check(string_expected).data.children[0]

    assert transformed_value == result_expected


@pytest.mark.parametrize('string_structure, string_value', [
    ["B()", "F(S{p}).A{a}.A{d}"],
    ["B(S{i})", "B(S{p}).A{d}.A{a}"],
    ["B(S{i})", "B(S{p}).A{d}.B(S{i}).A{a}"]
])
def test_insert_struct_to_complex_incorrect_input(string_structure, string_value):
    parser_structure = Parser("structure")
    parser_value = Parser("value")

    result_structure = parser_structure.syntax_check(string_structure).data.children[0]
    result_value = parser_value.syntax_check(string_value).data.children[0]

    transformer = TransformAbstractSyntax(set())

    with pytest.raises(ComplexParsingError):
        _ = transformer.insert_struct_to_complex(result_structure, result_value)
