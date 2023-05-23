import pytest


from eBCSgen.Errors.ComplexParsingError import ComplexParsingError
from eBCSgen.Parsing.ParseBCSL import Parser, TransformAbstractSyntax


@pytest.mark.parametrize('string_atomic, string_structure, string_expected', [
    ["A{i}", "B(S{p})", "B(S{p},A{i})"],
    ["A{i}", "B()", "B(A{i})"]
])
def test_insert_atomic_to_struct_correct_input(string_atomic, string_structure, string_expected):
    parser_atomic = Parser("atomic")
    parser_structure = Parser("structure")

    result_atomic = parser_atomic.syntax_check(string_atomic).data.children[0]
    result_structure = parser_structure.syntax_check(string_structure).data.children[0]

    transformer = TransformAbstractSyntax(set())
    transformed_value = transformer.insert_atomic_to_struct(result_atomic, result_structure)

    result_expected = parser_structure.syntax_check(string_expected).data.children[0]

    assert transformed_value == result_expected


@pytest.mark.parametrize('string_atomic, string_structure', [
    ["A{i}", "B(A{a})"],
    ["A{i}", "B(A{i})"]
])
def test_insert_atomic_to_struct_incorrect_input(string_atomic, string_structure):
    parser_atomic = Parser("atomic")
    parser_structure = Parser("structure")

    result_atomic = parser_atomic.syntax_check(string_atomic).data.children[0]
    result_structure = parser_structure.syntax_check(string_structure).data.children[0]

    transformer = TransformAbstractSyntax(set())

    with pytest.raises(ComplexParsingError):
        _ = transformer.insert_atomic_to_struct(result_atomic, result_structure)
