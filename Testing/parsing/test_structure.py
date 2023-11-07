import Testing.parsing.objects_testing as objects
from eBCSgen.Parsing.ParseBCSL import Parser


parser = Parser("structure")


def test_parser():
    assert parser.parse("B(T{s})").data == objects.s1
    assert parser.parse("D()").data == objects.s2
    assert parser.parse("K(T{s}, S{s}, S{_})").data == objects.s3
    assert parser.parse("B(T{_})").data == objects.s4
    assert parser.parse("D(S{_},T{p})").data == objects.s5
    assert parser.parse("K()").data == objects.s6
    assert parser.parse("K(S{a},T{_})").data == objects.s7
